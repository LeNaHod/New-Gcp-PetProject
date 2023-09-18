from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_api, check_running

def start():
    print("### 기사 요약 스케줄러 시작...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_api, 'interval', hours=1) # 1시간마다 반복
    scheduler.add_job(check_running, 'interval', minutes=5)  # 5분마다 반복
    scheduler.start()