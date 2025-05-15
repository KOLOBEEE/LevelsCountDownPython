# scheduler.py

import schedule
import time
from progress_report import send_progress_report

def schedule_progress_reports():
    schedule.every().monday.at("08:00").do(send_progress_report)
    schedule.every().monday.at("17:00").do(send_progress_report)
    schedule.every().wednesday.at("08:00").do(send_progress_report)
    schedule.every().wednesday.at("17:00").do(send_progress_report)
    schedule.every().friday.at("08:00").do(send_progress_report)
    schedule.every().friday.at("17:00").do(send_progress_report)

    print("Scheduler started for progress reports...")

    while True:
        schedule.run_pending()
        time.sleep(1)

# Do NOT run scheduler here when imported — will be managed in main.py
