import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws_prefix = soup.select_one("div.module.news.clearfix")
    raws = soup.select_one("div.module.listings-basic.news.clearfix").select(
        "div.col-lg-4.col-md-6.col-12"
    )
    articles = []

    title_prefix = raws_prefix.select_one(
        "h2.p-summary.p-name a.url.summary"
    ).get_text()
    date_prefix = raws_prefix.select_one("p.meta-date").get_text().strip()
    date_pre = datetime.strptime(date_prefix, "%A  %d %B %Y").strftime("%Y-%m-%d")
    img_prefix = raws_prefix.select_one("img.card-img-top")["src"]
    news_prefix = raws_prefix.select_one("p.read-more a")["href"]
    full_prefix = urljoin("https://www.eventfinda.co.nz", news_prefix)
    articles.append(
        {
            "target_id": "eventfindaNews",
            "target_url": "https://www.eventfinda.co.nz/news",
            "title": title_prefix,
            "news_url": full_prefix,
            "imageUrl": img_prefix,
            "date": date_pre,
        }
    )

    for item in raws:
        title_element = item.select_one("h2.p-summary.p-name a.url.summary")
        title = title_element.get_text()

        # Extract the date
        date_element = item.select_one("p.meta-date")
        date_text = date_element.get_text().strip()
        date = datetime.strptime(date_text, "%A  %d %B %Y").strftime("%Y-%m-%d")

        # Extract the image URL
        img_element = item.select_one("img.card-img-top")
        imgUrl = img_element["src"]

        # Extract the news URL
        news_url_element = item.select_one("p.read-more a")
        news_url = news_url_element["href"]
        full_url = urljoin("https://www.eventfinda.co.nz", news_url)

        articles.append(
            {
                "target_id": "eventfindaNews",
                "target_url": "https://www.eventfinda.co.nz/news",
                "title": title,
                "news_url": full_url,
                "imageUrl": imgUrl,
                "date": date,
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = soup.find("article").get_text(separator="\n").strip()
    return article_content


# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
def save_to_supabase(article):
    title = article["title"]
    date = article["date"]
    existing_article = (
        supabase.table("News").select("*").eq("title", title).eq("date", date).execute()
    )

    if not existing_article.data:
        response = supabase.table("News").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")


def get_news_from_eventfinda():
    main_page_url = "https://www.eventfinda.co.nz/news"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        article["content"] = scrape_detail_page(article["news_url"])
        save_to_supabase(article)
