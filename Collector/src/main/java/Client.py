from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
 
def schedulerJob():
    # 실행할 프로세스
    subprocess.run(['/bin/sh', './radio.sh', 'MBC FM4U', '이석훈의 브런치 카페', '30'])
    
def backgroundScheduler():
    scheduler = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')
    scheduler.start()
    scheduler.add_job(schedulerJob, 'cron', hour=2, minute=59)  # schedulerJob을 오전 11시마다 실행
 
if __name__ == '__main__':
    backgroundScheduler()