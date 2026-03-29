import schedule, time
from scraper import scrape_all
from summarizer import perform_summarization
from emailer import send_email

def job():
    print("⏳ Running daily job...")
    scrape_all()
    perform_summarization()
    send_email()

def run_job():
    print("⏳ Running daily job...")
    scrape_all()
    perform_summarization()
    send_email()

#schedule.every().day.at("08:00").do(job)

if __name__ == "__main__":
    print("Bot running...")
    run_job()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
