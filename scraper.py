import feedparser
from db import save_news
from bs4 import BeautifulSoup

SECTOR_FEEDS = {
    "technology": [
        "https://techcrunch.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/index"
    ],
    "finance": [
        "https://www.ft.com/rss/home"
    ],
    "world news": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    # "sports": [
    #     "https://www.skysports.com/rss/12040",
    # ],
    # "healthcare": [
    #     "https://thehealthcareblog.com/feed/",
    # ],
    "energy": [
        "https://www.energyglobal.com/rss/energyglobal.xml"
    ]
    # "consumer goods": [
    #     "https://fmcggurus.com/feed/"
    # ]
}

def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(" ", strip=True)  # converts <p>, <br> to spaces

def scrape_sector(sector, urls):
    news_items = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:50]:  # limit 50 per feed
            title = entry.title
            link = entry.link
            raw_summary = getattr(entry, 'summary', '')
            summary = clean_html(raw_summary)[:500]  # clean + truncate
            published = getattr(entry, 'published', 'N/A')
            
            save_news(sector, title, link, summary, published)
            news_items.append((title, link))
    return news_items

def scrape_all():
    for sector, urls in SECTOR_FEEDS.items():
        scrape_sector(sector, urls)

if __name__ == "__main__":
    scrape_all()
