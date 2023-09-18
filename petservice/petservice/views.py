import glob

from django.shortcuts import render, redirect
from django.template import loader
import templates
from .models import ImageFile, Article, Member, MediclaConv
from datetime import datetime, timedelta
import cv2, os
import numpy as np
from werkzeug.utils import secure_filename
from django.core.files.storage import FileSystemStorage
import tensorflow as tf
import json
from django.core.paginator import Paginator
import hdfs
from hdfs import InsecureClient
from requests.adapters import HTTPAdapter
import time
from urllib.error import HTTPError




def index(request, msg=''):
    results = get_summary() # DB에서 뉴스요약문 읽어오는 함수 실행함. (코드 길어져서 함수로 뺌)
    # print(f'### index 로그,  results : {results}, msg : {msg}')
    return render(request, 'index.html', {'results':results, 'msg':msg})


# DB에서 뉴스 요약문을 읽어오는 함수
def get_summary():
    # DB에 저장된 요약문을 가져와 request 객체에 담아 index.html에 전달한다.

    # Mysql 디비에서 오늘 기사만 불러오기
    today = datetime.now().date()
    # article = Article.objects.filter(pub_date__range=(today, today)) # 오늘 날짜의 기사만 가져오기 (일단 지금 안씀, 나중에 쓸수도)
    article = Article.objects.all().order_by("-writedate") # 기사 Table에서 요약문이 있는 데이터들만 가져온다.

    # 결과를 저장할 results 변수 생성
    results = []

    for i, item in enumerate(article):
        if len(results)==10: #요약문 10개가 저장되면 for 문 종료
            break

        if len(item.summary)<10: # 요약문이 10글자 이하면 건너뜀
            print(f'####{i} 번째는 10글자 이하여서 건너뜀')
            continue
        print('#### 글자수 : ',len(item.summary))

        temp = dict() # 결과 dict 형태로 저장해서 list 에 쌓기.
        temp['title'] = item.title                               # 뉴스 제목
        temp['summary'] = item.summary         # 요약문
        if item.img_path:                                        # 뉴스에 사진 있으면 사진 path 전달
            temp['img_path'] = item.img_path

        if item.publisher:                                        # 뉴스 발행사 정보 있으면 전달
            temp['publisher'] = item.publisher

        if item.category:                                         # 뉴스 카테고리 정보 있으면 전달
            temp['category'] = item.category

        if item.url:                                                    # 뉴스 URL 정보 있으면 전달
            temp['url'] = item.url

        temp['writedate'] = item.writedate.strftime('%Y년 %m월 %d일')  # 뉴스 작성일자
        results.append(temp)                # results 리스트에 dict 데이터들을 쌓는다. (html에서 장고 템플릿 문법으로 읽어오기 쉽게)
    return results   # 함수 호출한 곳으로 결과 리턴


# login.html 에서 로그인 요청 들어온 경우 실행됨.
def login(request):
    if request.method == 'POST':          # POST 요청인 경우: 입력한 id와 pw를 통해 로그인 여부 판단
        msg = ''                                                 # 로그인 성공 및 실패 메세지를 담을 변수
        id = request.POST['id']                       # 사용자가 입력한 ID
        password = request.POST['password']  # 사용자가 입력한 Password

        # 유효성 검사 (빈칸 검사는 html에서 진행함)

        # DB에 회원정보가 등록되어 있는지 확인
        user_info = Member.objects.filter(id=id) # 사용자가 입력한 ID가 가입되어있는 ID라면, 그 회원정보를 받아옴
        print('user_info : ', user_info) # 가입안되어있으면 null 값

        # 로그인 분기 1-1. DB에 회원정보가 있는 경우
        if user_info:
            user = user_info[0]

            # 로그인 분기 2-1. 회원정보 맞게 입력함 => 로그인 성공
            if user.password == password:
                msg = user.name + '님, 안녕하세요^^!'

                # 로그인 성공시 request 객체에 session 정보를 기록하고, index로 넘긴다. (session 정보가 있다면 로그인 된 것으로 판단함)
                request.session['id'] = id
                request.session['name'] = user.name
                print(f'### login 성공, session-id:{request.session["id"]}, session-name:{request.session["name"]}, msg :  {msg}')

                

                # 로그인 성공시 index.html 파일이 바로 렌더링되어 오류 발생되었는데,
                # views.py의 index 함수가 바로 실행되도록 변경함. (요약문 안보이는 에러 수정 완료)
                return index(request, msg)

            # 로그인 분기 2-2. 비밀번호만 잘못 입력함 => 로그인 실패
            else:
                msg = '비밀번호를 다시 입력해주세요.'
                print('### login 비번 잘못 입력함 , ', msg)
                return render(request, 'login.html', {'msg': msg, 'data': {'id': id}})

        # 로그인 분기 1-2. DB에 회원정보가 없는 경우 (가입안되어있음)
        else:
            msg = '등록되지 않은 ID입니다. 다시 입력해주세요.'
            print('### login ID 잘못입력, msg : ', msg)
            return render(request, 'login.html', {'msg': msg, 'data': {'id': id}})

    else:         # GET 요청인 경우 login.html 보여줌 (그냥 로그인 메뉴만 누른 경우)
        return render(request, 'login.html')


# logout 요청시 request 객체에 저장된 session 정보를 삭제한다.
def logout(request):
    
    try:
        del request.session['id'] # 세션에 저장된 고객아이디 삭제
        del request.session['name'] # 세션에 저장된 고객 이름삭제
    except KeyError: # 에러날 경우 넘김
        pass
    msg = '로그아웃되었습니다.'
    return index(request, msg)  # views.py의 index 함수 실행하도록 변경함. (요약문 안보이는 에러 수정 완료)


# 회원가입 POST 요청시
def join(request):
    msg = '' # 결과 메세지를 저장할 msg 변수 생성

    if request.method == 'POST': # POST 요청인 경우

        # 고객이 입력한 값들을 읽는다.
        id = request.POST['id']
        password = request.POST['password']
        password_check = request.POST['password_check']
        name = request.POST['name']
        email = request.POST['email']
        birthday = request.POST['birthday']

        # 유효성 검사 (빈칸 검사는 html에서 진행함)

        # 비밀번호와 비밀번호 재확인이 일치하는지 확인한다.
        if password != password_check: # 다르게 입력했다면
            msg = '비밀번호가 일치하지 않습니다. 다시 입력해주세요.' # 오류 메세지 리턴함.
            print('### join 비밀번호 재확인 다르게 입력 ', msg)
            return render(request, 'member.html', # 고객이 입력했던 값 그대로 보내준다.
                          {'msg': msg, 'data': {'id': id, 'name': name, 'email': email, 'birthday': birthday}})

        # DB에서 중복 id 가 가입되어 있는지 확인
        duplicated_id = Member.objects.filter(id=id)

        # id 가 DB에 있는 경우
        if duplicated_id:
            msg = '이미 등록된 아이디입니다. 다른 아이디를 입력해주세요.'
            print('### join 회원가입 되어있음', msg)
            return render(request, 'member.html', {'msg':msg, 'data':{'id':id, 'name':name, 'email':email, 'birthday':birthday}})

        # id가 DB에 없는 경우 (회원가입 진행하기)
        else:
            result = Member.objects.create(id=id, password=password, name=name, email=email, birthday = birthday)
            print('### join 회원가입 결과 : ', str(result))

            if result:  # 회원가입 성공시
                msg = '회원가입이 완료되었습니다. 로그인 후 이용해주세요.'
                print('### join  DB 생성 성공 : ', msg)
                return render(request, 'login.html', {'msg': msg, 'data': {'id': id}})
            else: # 회원가입 실패시
                msg = '회원가입이 정상적으로 완료되지 않았습니다. 잠시 후 다시 이용해주세요.'
                print('### join DB 생성 실패', msg)
                return render(request, 'member.html', {'msg':msg, 'data':{'id':id, 'name':name, 'email':email, 'birthday':birthday}})
    return render(request, 'member.html')


# [회원가입] 메뉴 클릭시 member.html 렌더링한다.
def member(request):
    return render(request, 'member.html')

# [약국 상세 위치] 메뉴 클릭시
def Medical(request):
    hospital_list=MediclaConv.objects.only("name", "address","tel").order_by('id') #필요한컬럼만 추출하여 id로정렬
    page =request.GET.get('page','1') #페이징처리를위한부분
    paginator =Paginator(hospital_list,10)
    page_obj = paginator.get_page(page)

    #카카오지도마커찍기. 가공한 json파일을 불러와 for문으로 페이지를만들어 정보를뿌림
    with open('/home/napetservicecloud/petservice/static/js/medical_list.json', encoding='utf-8') as json_file:
        lotlat = json.load(json_file)
        lotlatdict = []
    for lotlats in lotlat:
        if lotlats.get('lot'):
            content = {
                "name": lotlats['name'],
                "lot": str(lotlats['lot']),
                "lat": str(lotlats['lat']),
                "address": str(lotlats['address']),
            }
            if lotlats.get('tel'):
                content['tel'] = str(lotlats['tel'])
            else:
                content['tel'] = ''
            lotlatdict.append(content)
    lotlatlist = json.dumps(lotlatdict, ensure_ascii=False)

    return render(request,'Medical.html',{'hospital_list':page_obj,'lotlatlist':lotlatlist}) #결과
    

# [안구질환 검사] 메뉴 클릭시
def services(request):
    return render(request, 'services.html')


# [안구질환 검사] 페이지에서 고객이 사진업로드하면 실행되는 함수
# 사진을 서버에 따로 저장하고, 그 경로를 DB에 저장한다.
def img_upload(request):

    if request.method == 'POST' and request.FILES['img']: # 고객이 사진을 업로드하고, 업로드버튼을 누른 경우
        img = request.FILES['img'] # services.html 의 form 태그에서 넘어온 파일 읽기

        #TODO 서버에 이미지 저장할 dir 지정하기 (서버 컴에 맞게 지정해주세요)#하둡에 저장하기
        fs = FileSystemStorage(location='static/upload_imgs', base_url='static/upload_imgs') #  static 폴더 안에 저장해야 html에서 출력가능함.

        # 파일명을 업로드 시간으로 변경한 후, 서버에 저장한다.
        now = datetime.now()  # + timedelta(hours=9) # 미국시간 기준이면 9시간 추가하기
        filename = 'img_'+now.strftime('%y%m%d_%H%M%S')+'.'+img.name.split('.', 1)[1] # 저장할 파일명 통일 → img_현재시간.확장자
        filename = fs.save(filename, img) # 서버에 사진 저장
        uploaded_file_url = fs.url(filename)

        # 이미지 파일의 path를 DB에 저장한다.
        img_path = os.path.abspath(uploaded_file_url) # 절대경로를 반환하는 함수 : os.path.abspath
        
        # 만약 HttpconnectionPool오류를 만난다면,500번상태면 예외처리
        # 서버에 이미지가 저장되면, 바로 하둡으로올리기
        client_hdfs = InsecureClient("http://master:50010", user="root",timeout=1)
        try: #로그인된 상태라면 세션에저장된 id를 가져와서 .mkdir를 이용하여 디렉터리를만든다.
            hdfs_dir_id=request.session['id']
            try: 
                client_hdfs.makedirs('/user/'+str(hdfs_dir_id))
                client_hdfs.upload('/user'+'/'+hdfs_dir_id, uploaded_file_url,temp_dir='/user')
            except:
                pass
        except: #로그인 안된상태라면 id의값을 게스트로지정
            hdfs_dir_id='guest'
            try: 
                client_hdfs.makedirs('/user/'+str(hdfs_dir_id))
                client_hdfs.upload('/user'+'/'+hdfs_dir_id, uploaded_file_url,temp_dir='/user')
            except:
                pass

        try: # 로그인된 상태라면 회원 아이디도 DB에 함께 저장함 (마이페이지 기능을 위해서)
            id=request.session['id'] # 세선에 저장된 id 를 불러온다.
        except: # 로그인 안된 상태라면
            id=''   # id는 빈 값으로 저장함
        image = ImageFile(path=img_path, user_id=id)  # DB - ImageFile 테이블에 데이터 생성하기.
        image.save() #  DB 저장.

        # DB 저장 성공시
        if image:   # 딥러닝 모델로 안구질환을 분석하는 함수를 실행한다. (이미지 파일 경로도 함수에 전달)
            return img_analysis(request, img_path)
        else:
            pass   # DB 저장 실패일 경우 services.html 로 돌아감
    return render(request, 'services.html')


# 딥러닝 모델로 안구질환을 분석하는 함수
def img_analysis(request, img_path):

    start = datetime.now()  # 시작 시간 기록
    print('#### img_analysis 시작 시간 : ', start.strftime('%Y-%m-%d %H:%M:%S'))

    labels = ['증상없음', '초기', '미성숙', '성숙'] # 백내장 진행단계 리스트.


    # 1. 이미지 로드
    print('####로그1  이미지 파일경로 : ', img_path)
    img = cv2.imread(img_path)  # OpenCV 라이브러리로 이미지 데이터를 바이트 데이터로 읽어온다.

    # temp 이미지 저장 (분석을 위해 사용할 임시 파일을 temp라는 이름으로 static 폴더에 저장)
    img_src = "/home/napetservicecloud/petservice/static/temp_imgs/temp.jpg" # 경로는 서버 컴에 따라 바꿔주세요. (static 내부이기만 하면 됨)
    cv2.imwrite(img_src, img)

    # 색상채널 RGB로 변환
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV로 읽어온 이미지의 색상채널은 BGR 이므로 편의를 위해 RGB 로 바꿔준다.
    print(f'#### img_analysis 로그1 이미지 불러오기 완료 Shape : {img.shape}')


    # 2. 이미지 전처리
    #   2-1. 이미지 사이즈 변환하기 (모델 학습에 적합한 224 로 변환하기)
    img = cv2.resize(img, (224, 224))
    print('#### img_analysis 로그2 이미지 사이즈 변환 완료 Shape : ', img.shape)

    # 2-2. 차원 추가하기 (딥러닝 모델에 돌리기 위해서는 1차원 추가해줘야함)
    img = img.reshape(1, 224, 224, 3)
    print('#### img_analysis 로그3 이미지 차원 추가 완료 Shape : ', img.shape)


    # 3. 모델 로드 (전이학습된 이미지분류 딥러닝 모델 불러오기)
    model_filename = "{모델경로}static/model/EfficientNetB4_6000_tuning10.h5"  # efficientnetB4
    model = tf.keras.models.load_model(filepath=model_filename, compile=True)


    # 4. 예측
    pred = model.predict(img)[0]    # 딥러닝 모델을 사용하여, 고객이 업로드한 이미지의 분류 예측값을 받아온다.
    pred_class = np.argmax(pred)   # 확률 이 가장 큰 클래스의 인덱스를 구한다.
    proba = max(pred)                       # 확률이 가장 큰 값을 proba 변수에 저장한다.


    # 5. 분석 결과를 DB에 저장한다.
    imgfile = ImageFile.objects.filter(path=img_path) # DB에서 이미지 경로가 같은 데이터를 찾아온다.
    result_update = imgfile.update(                                  # 분석 결과를 업데이트 한다.
        result0=round(float(pred[0] * 100), 4),  # 증상없음
        result1=round(float(pred[1] * 100), 4),   # 초기
        result2=round(float(pred[2] * 100), 4),   # 미성숙
        result3=round(float(pred[3] * 100), 4))   # 성숙

    if result_update != 1: # DB 정보 수정 실패시 로그출력
        print(f'#### img_analysis DB 수정 실패!!')

    # 6. 결과를 results 변수에 저장한다.
    results = []
    for i, label in enumerate(labels): # 레이블 별로 확률 값을 저장함.
        temp = dict()
        temp['label'] = label
        temp['proba'] = round(float(pred[i] * 100), 4) # 소수점 4번째 자리까지 반올림
        results.append(temp)

    print('### img_analysis 로그, result : ', results)
    end = datetime.now()  # 분석 종료 시간
    print('#### img_analysis 종료 시간 : ', end.strftime('%Y-%m-%d %H:%M:%S'))
    print('#### img_analysis 소요 시간 : ', end - start)

    return render(request,'services_result.html',    # 결과를 html에 보내 출력한다.
                  {'results': results, 'label': labels[pred_class], 'proba': round(float(proba) * 100)})


#  mypage :  백내장 분석 내역들을 조회하는 페이지 (로그인 한 상태에서만 접근가능)
def mypage(request):
    output_msg = '' # 결과메세지를 담을 변수 생성.

    try:      # 세션에 ID 정상적으로 저장되어 있을 경우
        print('### 세션에 등록된 id : ', request.session['id'])

        # 결과 데이터를 저장하기 위한 results 변수를 생성한다.
        results = []

        # ImageFile Table 에서 고객 아이디로 저장된 분석결과 데이터가 있다면 가져오기
        imgs = ImageFile.objects.filter(user_id=request.session['id']).order_by("-upload_date") # 업로드 날짜는 최신순으로 정렬한다.

        if imgs:  # 백내장 분석 내역들이 DB에 저장되어 있다면, 반복문을 통해 결과를 results 변수에 추가한다.
            labels = ['증상없음', '초기', '미성숙', '성숙'] # labels list 선언

            for img in imgs: # DB에서 가져온 데이터 수 만큼 반복
                temp = dict() # 결과를 저장할 dict 변수 생성
                temp['path'] = img.path.replace('\\', '/').split('petservice/')[1]            # DB이미지 저장경로. DB에서 이미지경로를 불러와 뿌려줌
                temp['upload_date'] = (img.upload_date + timedelta(hours=9)).strftime('%Y년 %m월 %d일  %H시 %M분') # 업로드 날짜 (미국 기준일 경우 9시간 추가하기)
                img_result_list = [img.result0, img.result1, img.result2, img.result3] # 백내장 분석결과 - 증상없음/초기/미성숙/성숙
                proba_list = []                               # 라벨별 예측점수 dict를 저장할 변수 생성

                for i, label in enumerate(labels):
                    temp2 = dict()            # 각 라벨의 예측 점수를 저장할 dict 변수 생성
                    temp2['label'] = label      # 라벨 명
                    temp2['proba'] = img_result_list[i]     # 라벨별 예측 확률
                    proba_list.append(temp2)

                temp['proba_list'] = proba_list
                results.append(temp) # results list 변수에  temp dict를 추가한다.

        else: # 만약 DB에 이전 백내장 분석 내역이 없다면, 분석내역 없다는 msg 출력
            output_msg = '이전 분석 내역이 없습니다.'

        print(f'### mypage 로그, results : {results}')
        return render(request, 'mypage.html', {'results': results, 'output_msg': output_msg})

    # 로그인 안된 상태에서 mypage 접속시도 할 경우
    except KeyError:
        msg = '로그인 후 이용해주세요.'
        return index(request, msg)

