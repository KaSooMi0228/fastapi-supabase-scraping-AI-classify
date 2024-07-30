import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    # response = requests.get(url)
    response = requests.get(f"{url}&page={page}")
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="card-image card-image__secondary")
    articles = []

    for item in raws:
        title = item.find("h3").get_text(strip=True)
        date_raw = item.find("p").find("span").get_text(strip=True)
        news_url = item.find("a", class_="card-image__image")["href"]
        img_full_url = urljoin("https://www.rotoruanz.com", news_url)
        image_url = item.find("img")["src"]

        date_obj = datetime.strptime(date_raw, "%B %d, %Y")
        formatted_date = date_obj.strftime("%d-%m-%Y")

        articles.append(
            {
                "target_id": "rotoruanzNews",
                "target_url": "https://www.rotoruanz.com/stories-articles?type=news",
                "title": title,
                "news_url": img_full_url,
                "imageUrl": image_url,
                "date": formatted_date,
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")
    article_content = soup.find(
        "div", class_="inner-page__content bullet-points--active"
    )
    text = article_content.get_text(separator="\n", strip=True)

    return text


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


def get_news_from_rotoruanz():
    main_page_url = "https://www.rotoruanz.com/stories-articles?type=news"
    page = 1
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            article["content"] = scrape_detail_page(article["news_url"])
            save_to_supabase(article)

        page += 1
