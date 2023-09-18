#**********spark 관련**********
from pyspark.sql import *
from pyspark.sql.functions import regexp_replace
from pyspark.sql.functions import col
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
import pandas as pd
from datetime import datetime, timedelta
import csv
import re
import time


#**********기본경로,파일명선언**********
path='/home/napetservicecloud'
time_stamp_format=datetime.now().strftime('%y%m%d_%H')


#**********SPARK 세션생성**********

spark = SparkSession.builder.config("spark.jars", "mysql-connector-java-8.0.33.jar").master("yarn").getOrCreate()


#**********파일 로드**********

#daliygewon pandas read
daliygaewon_read_pd=pd.read_csv(f"{path}/crawling/dailygawon_csv_{time_stamp_format}.csv")
dailygaewon_data= spark.createDataFrame(daliygaewon_read_pd)
dailygaewon_data.createOrReplaceTempView("dailygaewon_news")
#dailygaewon_data.show()

#kbs pandas read
kbs_read_pd=pd.read_csv(f"{path}/crawling/kbs_csv_{time_stamp_format}.csv")
kbs_data= spark.createDataFrame(kbs_read_pd)
kbs_data.createOrReplaceTempView("Kbs_news")
#kbs_data.show()

#sbs pandas read
sbs_read_pd=pd.read_csv(f"{path}/crawling/sbs_csv_{time_stamp_format}.csv")
sbs_data= spark.createDataFrame(sbs_read_pd)
sbs_data.createOrReplaceTempView("sbs_news")
#sbs_data.show()

#kukmin pandas read
kukmin_read_pd=pd.read_csv(f"{path}/crawling/kukmin_csv_{time_stamp_format}.csv")
kukmin_data= spark.createDataFrame(kukmin_read_pd)
kukmin_data.createOrReplaceTempView("Kukmin_news")
#kukmin_data.show()


#**********daliygewon 가공,전처리부분**********

#main컬럼
diy_main_p=dailygaewon_data.select(col("title"),regexp_replace(col("main"),'[▷■\n※-▶◆▼©●▲『』]'," ").alias("main"),col("press"),col("url"),regexp_replace(col("write_date"),'승인',"").alias("write_date"))

#title컬럼
diy_title_p=diy_main_p.select(regexp_replace(col("title"),'\[[^)]*\]',"").alias("title"),col("main"),col("press"),col("url"),regexp_replace(col("write_date"),'\[[^)]*\]',"").alias("write_date"))
#diy_title_p.show()

#특정문자를 삭제하고 DF에 id를 부여
dailygaewon_wordcount_x=diy_title_p.rdd.zipWithIndex().toDF()
final_dailygaewon_df_wordx=dailygaewon_wordcount_x.select((col("_2")+1).alias("id"),col("_1.*")) #_2가 id. id가앞에오게 _2를 먼저부름
final_dailygaewon_df_wordx.show()

#dailygaewon//하둡에저장할때 파티션을 나누지않고 병합
final_dailygaewon_df_wordx.coalesce(1).write.options(header='True', delimiter=',', encoding="cp949").csv(f"/user/crawling/dailygaewon_final_url{time_stamp_format}.csv")



#**********Kukmin Ilbo 가공,전처리부분**********

#main컬럼 전처리 ex)[\n▶▲■▷▼●]'," "
kuk_main_p=kukmin_data.select(col("title"),regexp_replace(col("main"),'[▷■\n※-▶◆▼©●▲『』]'," ").alias("main"),col("press"),col("url"),regexp_replace(col("write_date"),'승인',"").alias("write_date"))

# title 컬럼
kuk_title_p=kuk_main_p.select(regexp_replace(col("title"),'\[[^),]*\]',"").alias("title"),col("main"),col("press"),col("url"),regexp_replace(col("write_date"),'\[[^)]*\]',"").alias("write_date"))
#kuk_title_p.show()

# #id생성문
kukmin_wordcount_x=kuk_title_p.rdd.zipWithIndex().toDF()
final_kukmin_df_wordx=kukmin_wordcount_x.select((col("_2")+1).alias("id"),col("_1.*"))
final_kukmin_df_wordx.show()

#하둡저장
final_kukmin_df_wordx.coalesce(1).write.options(header='True', delimiter=',', encoding="cp949").csv(f"/user/crawling/kukmin_final_url{time_stamp_format}.csv")

#**********KBS 가공,전처리부분**********

#main컬럼 전처리
kb_main_p=kbs_data.select(col("title"),regexp_replace(col("main"),'[▷■\n※-▶◆▼©●▲『』]'," ").alias("main"),col("press"),col("url"),regexp_replace(col("write_date"),'입력',"").alias("write_date"))

#title컬럼 전처리
kb_title_p=kb_main_p.select(regexp_replace(col("title"),'\[[^),]*\]',"").alias("title"),col("main"),col("press"),col("url"),regexp_replace(col("write_date"),'\([^)]*\)',"").alias("write_date"))
#kb_title_p.show()

#ID생성,CSV파일생성
kbs_wordcount_x=kb_title_p.rdd.zipWithIndex().toDF()
final_kbs_df_wordx=kbs_wordcount_x.select((col("_2")+1).alias("id"),col("_1.*"))
final_kbs_df_wordx.show()

final_kbs_df_wordx.coalesce(1).write.options(header='True', delimiter=',', encoding="cp949").csv(f"/user/crawling/kbs_final_url{time_stamp_format}.csv")


#**********SBS 가공,전처리부분**********


#main컬럼 전처리
sb_main_p=sbs_data.select(col("title"),regexp_replace(col("main"),'[\n▶▲■▷▼●\[\]『』©※]'," ").alias("main"),col("press"),col("url"),col("write_date"))

# title 컬럼에대하여 정규식을 사용해 여러문자 제거. []는 특수한문자이므로 이스케이프가 필요하여 앞에 \를 사용. []안에있는 문자들과 일치하면 모두 공백으로변경
sb_title_p=sb_main_p.select(regexp_replace(col("title"),'[\[,"\]+]',"").alias("title"),col("main"),col("press"),col("url"),regexp_replace(col("write_date"),'\[[^)]*\]',"").alias("write_date"))
sb_title_p.show()

#id생성,csv파일 생성

sbs_rdd_id=sb_title_p.rdd.zipWithIndex().toDF()
final_sbs_wordx=sbs_rdd_id.select((col("_2")+1).alias("id"),col("_1.*"))
final_sbs_wordx.show()
final_sbs_wordx.coalesce(1).write.options(header='True', delimiter=',', encoding="cp949").csv(f"/user/crawling/sbs_final_url{time_stamp_format}.csv")


#**********Mysql드라이버**********

user='db_user'
password='password'
url='jdbc:mysql://host:port/db_name'
driver='com.mysql.cj.jdbc.Driver'
dbtable='db_table'


#**********병합을위한 ID제거**********
kbs_idx=final_kbs_df_wordx.select(col("title"),col("main"),col("press"),col("url"),col("write_date"))
sbs_idx=final_sbs_wordx.select(col("title"),col("main"),col("press"),col("url"),col("write_date"))
kukmin_idx=final_kukmin_df_wordx.select(col("title"),col("main"),col("press"),col("url"),col("write_date"))
daily_idx=final_dailygaewon_df_wordx.select(col("title"),col("main"),col("press"),col("url"),col("write_date"))


#**********병합작업**********
result_kbs = kbs_idx.select("*").toPandas()
result_sbs = sbs_idx.select("*").toPandas()
result_kukmin = kukmin_idx.select("*").toPandas()
result_daily = daily_idx.select("*").toPandas()

concatDF=pd.concat([result_daily,result_kukmin,result_sbs,result_kbs])
news_concatdf = spark.createDataFrame(concatDF)

###ID재부여

news_concat_id=news_concatdf.rdd.zipWithIndex().toDF()
final_newsDF=news_concat_id.select((col("_2")+1).alias("id"),col("_1.*"))

#HDFS에 저장

final_newsDF.coalesce(1).write.options(header='True', delimiter=',', encoding="cp949").csv(f"/user/crawling/news_final_{time_stamp_format}.csv")

## Mysql에 저장

final_newsDF.write.jdbc(url,dbtable,"overwrite",properties={"driver":driver, "user":user,"password":password})


#스파크 세션종료
spark.stop()