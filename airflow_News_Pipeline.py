#/*****셀레니움 관련******/

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxOptions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

#/*****에어플로우 관련*****/

from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
import csv
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup


#=============================================================

#airflow 기본 args 선언

default_args = { 
    'owner' : 'gcp_master', 
    'depends_on_past': False,
    'retires': 1
    #'retry_delay': timedelta(minutes=5)
}

#경로,현재시간 포맷지정
path='/home/napetservicecloud'
time_stamp_format=datetime.now().strftime('%y%m%d_%H')

#=============Daily Gaewon 크롤링 =============

#시간측정
start_time=time.time()

#크롤링 드라이버
opts = FirefoxOptions()
opts.add_argument("--headless")

#크롤링용 변수

pagenum=[1,11,21,31,41,51,61,71,81,91,101]

def dailygaewonc():

    browser = webdriver.Firefox(options=opts)

    # 한 페이지내에서 모든 뉴스의 갯수만큼 타이틀 / 링크를 따로추출하여 두개의 리스트에 저장.
    dailygaewon_list=[] #뉴스정보를 저장할 리스트
    dailygawon_link=[] #본문링크만 저장할 리스트(본문크롤링에 필요하기에 따로 저장)

    #페이지를 순환할 for문 / 데일리개원에 미디어 페이지를 크롤링해온다.
    for pages in range(1,8):
        base_url = f"http://www.dailygaewon.com/news/articleList.html?page={pages}&sc_section_code=&sc_sub_section_code=S2N30&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&box_idxno=&sc_multi_code=&sc_is_image=&sc_is_movie=&sc_order_by=E"
        browser.get(base_url)

        #페이지 내의 모든 기사의 갯수를추출하여 변수로 저장
        all_news=browser.find_elements(By.CLASS_NAME,"table-row")
        all_news_num=len(all_news)
        
        #기사의 길이만큼 for문을 반복해서 타이틀, 링크를 따로 추출
        for all_news_n in range(1,all_news_num+1): #1~19까지만 작동되니까 +1을해서 갯수를맞춰줌
            news_title=browser.find_element(By.XPATH,f"//*[@id='user-container']/div[3]/div[2]/section/article/div[2]/section/div[{all_news_n}]/div[1]/a/strong").text
            news_link=browser.find_element(By.XPATH,f"//*[@id='user-container']/div[3]/div[2]/section/article/div[2]/section/div[{all_news_n}]/div[1]/a").get_attribute("href")
            dailygaewon_list.append([news_title,news_link])
            dailygawon_link.append(news_link)
    #print(len(dailygaewon_list))
    print(len(news_link))


    #타이틀/ 본문 / 언론사/ url / 작성날짜

    dailygawon_contents=[]
    for dailygawon_links in dailygawon_link:
        browser.get(dailygawon_links)
        news_cont_title=browser.find_element(By.XPATH,f"//*[@id='user-container']/div[3]/header/div/div").text
        news_cont=browser.find_element(By.CSS_SELECTOR,"div#article-view-content-div").text
        news_date=browser.find_element(By.XPATH,f"//*[@id='user-container']/div[3]/header/section/div/ul/li[2]").text
        news_press="DailyGaewon" #뉴스사 추가
        dailygawon_contents.append([news_cont_title,news_cont,news_press,dailygawon_links,news_date])
    print(dailygawon_contents)
        

    dailygaewon_index = ["title","main","press","url","write_date"]
    daliygaewon_csv=pd.DataFrame(dailygawon_contents,columns=dailygaewon_index)
    daliygaewon_csv.to_csv(f'{path}/crawling/dailygawon_csv_{time_stamp_format}.csv', index=False,encoding="utf-8")
   
    browser.quit()

#=============Kukmin Ilbo 크롤링 =============
	
def kukminc():

    browser = webdriver.Firefox(options=opts)

#링크 크롤링

    Kukmin_link=[] #국민일보 본문링크만 담을 리스트

    for links in pagenum:
        Kukmin_pagelink=f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EB%B0%98%EB%A0%A4%EB%8F%99%EB%AC%BC%20%EB%B3%B5%EC%A7%80&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=20&mynews=1&office_type=1&office_section_code=1&news_office_checked=1005&nso=so:r,p:all,a:all&start={links}"
        browser.get(Kukmin_pagelink)
        all_page_lang=browser.find_elements(By.CLASS_NAME,"dsc_thumb")
        for cont in all_page_lang:
            Kukmin_content_link=cont.get_attribute("href") #본문페이지 링크 추출
            Kukmin_link.append(Kukmin_content_link)
    #print(len(Kukmin_link))


    #타이틀/ 본문 / 언론사/ url / 작성날짜

    Kukmin_main_text=[]

    for Kukmin_links in Kukmin_link:
        browser.get(Kukmin_links) #본문페이지로 변경
        try:
            Kukmin_title=browser.find_element(By.CSS_SELECTOR, "div.nwsti h3").text
            time.sleep(1)#로딩으로인해 발생하는 error를 줄이기위해 1초 대기
            Kukmin_main=browser.find_element(By.CLASS_NAME, "tx").text
            Kukmin_date=browser.find_element(By.CLASS_NAME, "t11").text
            Kukmin_news_press="KukminIlbo"
            Kukmin_main_text.append([Kukmin_title,Kukmin_main,Kukmin_news_press,Kukmin_links,Kukmin_date])
            #print(Kukmin_main_text)
        except:
            pass
    #print(Kukmin_main_text)
    #print(len(Kukmin_main_text))

    Kukmin_index = ["title","main","press","url","write_date"]
    Kukmin_csv=pd.DataFrame(Kukmin_main_text,columns=Kukmin_index)
    Kukmin_csv.to_csv(f'{path}/crawling/kukmin_csv_{time_stamp_format}.csv', index=False,encoding="utf-8")

    browser.quit()

#============= KBS =============

def kbsc():

    browser = webdriver.Firefox(options=opts)

    kbs_link=[] # KBS 본문링크만 담을 리스트
    for links in pagenum:
        kbs_pagelink=f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EB%B0%98%EB%A0%A4%EB%8F%99%EB%AC%BC%20%EB%B3%B5%EC%A7%80&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=28&mynews=1&office_type=1&office_section_code=2&news_office_checked=1056&nso=so:r,p:all,a:all&start={links}"
        browser.get(kbs_pagelink)
        all_page_lang=browser.find_elements(By.CLASS_NAME,"dsc_thumb")
        for cont in all_page_lang:
            kbs_content_link=cont.get_attribute("href")
            kbs_link.append(kbs_content_link)

    #타이틀/ 본문 / 언론사/ URL / 작성날짜

    Kbs_main_text=[]

    for kbs_links in kbs_link:
        try:
            browser.get(kbs_links) #본문페이지로 변경
            time.sleep(1)#로딩으로인해 발생하는 error를 줄이기위해 1초 대기
            kbs_title=browser.find_element(By.CLASS_NAME, "headline-title").text
            kbs_main=browser.find_element(By.ID, "cont_newstext").text
            kbs_date=browser.find_element(By.CLASS_NAME, "input-date").text
            kbs_news_press="KBS"
            Kbs_main_text.append([kbs_title,kbs_main,kbs_news_press,kbs_links,kbs_date])
        except:
            pass
    #print(Kbs_main_text)
    Kbs_index = ["title","main","press","url","write_date"]
    Kbs_csv=pd.DataFrame(Kbs_main_text,columns=Kbs_index)
    Kbs_csv.to_csv(f'{path}/crawling/kbs_csv_{time_stamp_format}.csv', index=False,encoding="utf-8")

    browser.quit()


#============= SBS =============

def sbsc():

    browser = webdriver.Firefox(options=opts)

    sbs_link=[] 
    for links in pagenum:
        sbs_pagelink=f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EB%B0%98%EB%A0%A4%EB%8F%99%EB%AC%BC%20%EB%B3%B5%EC%A7%80&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=22&mynews=1&office_type=1&office_section_code=2&news_office_checked=1055&nso=so:r,p:all,a:all&start={links}"
        browser.get(sbs_pagelink)
        all_page_lang=browser.find_elements(By.CLASS_NAME,"dsc_thumb")
        for cont in all_page_lang:
            sbs_content_link=cont.get_attribute("href") 
            sbs_link.append(sbs_content_link)

    # #======1-2. SBS 크롤링 / 본문내용=============

    # #타이틀/ 본문 / 입력날짜 /URL

    sbs_main_text=[]

    for sbs_links in sbs_link:
        try:
            browser.get(sbs_links) 
            time.sleep(1)
            sbs_title=browser.find_element(By.ID, "news-title").text
            sbs_main=browser.find_element(By.CLASS_NAME, "text_area").text
            sbs_date=browser.find_element(By.CSS_SELECTOR, "div.date_area span").text
            sbs_press="SBS"
            sbs_main_text.append([sbs_title,sbs_main,sbs_press,sbs_links,sbs_date])
        except:
            pass
    #print(sbs_main_text)

    sbs_index = ["title","main","press","url","write_date"]
    sbs_csv=pd.DataFrame(sbs_main_text,columns=sbs_index)
    sbs_csv.to_csv(f'{path}/crawling/sbs_csv_{time_stamp_format}.csv', index=False,encoding="utf-8")

    browser.quit()


#Airflow dag

with DAG( 
    'News_pipline', #dag id
    default_args = default_args,
    schedule = '@daily',
    start_date = datetime(2023, 9, 16),
    catchup = False,
    tags = ['pip_line','spark-submit','spark']

)as dag:

    Start = DummyOperator(
        task_id = "start",
        queue = "airflow-master"
    )
    
    End = DummyOperator(
        task_id = "end",
        trigger_rule = "all_success"
    )
    Master_spark = BashOperator(
        task_id = "crawling_spark_sbumit",
        bash_command =f"spark-submit --name 'crawling_spark_submit' --master yarn --deploy-mode cluster {path}/airflow-spark-submit.py",
        queue="airflow-master"
    )
    Worker1_4 = BashOperator(
        task_id = "worker1_rm_file",
        bash_command = f"rm {path}/crawling/*.csv",
        queue = "airflow-worker-1"
    )

    Worker2_4 = BashOperator(
        task_id = "worker2_rm_file",
        bash_command = f"rm {path}/crawling/*.csv",
        queue = "airflow-worker-2"
    )    

    with TaskGroup(group_id='group_crawling') as Group1:
        Worker1_1 = PythonOperator(
            task_id = "daliygawon_crawling",
            python_callable = dailygaewonc,
            queue = "airflow-worker-1"
        )

        Worker1_2 = PythonOperator(
            task_id = "kbs_crawling",
            python_callable = kbsc,
            queue = "airflow-worker-1"
        )

        Worker2_1 = PythonOperator(
            task_id = "sbs_crawling",
            python_callable = sbsc,
            queue = "airflow-worker-2"
        )

        Worker2_2 = PythonOperator(
            task_id = "kukmin_crawling",
            python_callable = kukminc,
            queue = "airflow-worker-2"
        )

        Worker1_3 = SSHOperator(
            task_id ="worker1_scp",
            ssh_conn_id="ssh_master",
            command=f"""
            scp -T slave01:{path}/crawling/dailygawon_csv_{time_stamp_format}.csv {path}/crawling/
            scp -T slave01:{path}/crawling/kbs_csv_{time_stamp_format}.csv {path}/crawling/
            scp -T {path}/crawling/kbs_csv_{time_stamp_format}.csv slave02:{path}/crawling/
            scp -T {path}/crawling/dailygawon_csv_{time_stamp_format}.csv slave02:{path}/crawling/
            """,
            queue = "airflow-worker-1"
        )

        Worker2_3 = SSHOperator(
            task_id ="worker2_scp",
            ssh_conn_id="ssh_master2",
            command=f"""
            scp -T slave02:{path}/crawling/sbs_csv_{time_stamp_format}.csv {path}/crawling/
            scp -T slave02:{path}/crawling/kukmin_csv_{time_stamp_format}.csv {path}/crawling/
            scp -T {path}/crawling/sbs_csv_{time_stamp_format}.csv slave01:{path}/crawling/
            scp -T {path}/crawling/kukmin_csv_{time_stamp_format}.csv slave01:{path}/crawling/
            """,
            queue = "airflow-worker-2"
        )


        Middle_check = DummyOperator(
            task_id = "middle_check_point",
            trigger_rule = "all_done"
        )

        [Worker1_1 >> Worker1_2 >> Worker1_3 , Worker2_1 >> Worker2_2 >> Worker2_3] >> Middle_check
        
    Start >> Group1 >>  Master_spark >> [Worker1_4,Worker2_4] >>  End