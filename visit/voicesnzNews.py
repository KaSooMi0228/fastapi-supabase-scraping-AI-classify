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

    raws = soup.select(
        "div.fl-post-grid-post.fl-post-grid-image-above-title.fl-post-align-default"
    )
    articles = []

    for item in raws:
        date = item.find("meta", itemprop="dateModified")["content"]
        title = item.find("h4", class_="fl-post-grid-title").a.text
        imageUrl = item.find("div", itemprop="image").find("meta", itemprop="url")[
            "content"
        ]
        news_url = item.find("a", class_="fl-post-grid-more")["href"]

        articles.append(
            {
                "target_id": "voicesnzNews",
                "target_url": "https://www.voicesnz.com/about/news/",
                "title": title,
                "news_url": news_url,
                "imageUrl": imageUrl,
                "date": date,
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = soup.find("div", class_="omni-post-content")
    text_content = soup.get_text(separator="\n", strip=True)
    return text_content


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


def get_news_from_voicesnz():
    main_page_url = "https://www.voicesnz.com/about/news/"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        article["content"] = scrape_detail_page(article["news_url"])
        save_to_supabase(article)
