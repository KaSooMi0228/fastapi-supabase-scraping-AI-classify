import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all("div", class_="slide")
    
    articles = []

    for item in raws:
        # Extract the news URL
        news_url_tag = item.find('a', href=True)
        news_url = news_url_tag['href'] if news_url_tag else None

        # Extract the date from the news URL
        date_match = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', news_url)
        date = f"{date_match.group(3).zfill(2)}-{date_match.group(2).zfill(2)}-{date_match.group(1)}" if date_match else None

        # Extract the title from the news URL
        title_match = re.search(r'-artist-(.+)', news_url)
        title = title_match.group(1).replace('-', ' ') if title_match else None

        # Extract the image URL
        image_tag = item.find('img', {'class': 'thumb-image'})
        image_url = image_tag['data-src'] if image_tag else None

        articles.append(
            {
                "target_id": "neckofthewoodsNews",
                "target_url": "https://www.neckofthewoods.co.nz/#artist-programme-section",
                "title": title,
                "news_url": news_url,
                "imageUrl": image_url,
                "date": date,
                "content": "No content Found",
            }
        )

    return articles

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


def get_news_from_neckofthewoods():
    main_page_url = "https://www.neckofthewoods.co.nz/#artist-programme-section"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)
