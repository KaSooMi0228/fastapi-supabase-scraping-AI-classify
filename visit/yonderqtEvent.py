import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="bloglistinner topup")
    articles = []

    for item in raws:
        start_date_str = item.find('span').text

        # Formatting the date
        start_date = datetime.strptime(start_date_str, '%B %d, %Y').strftime('%Y-%m-%d')

        # Extracting the event title and URL
        event_title_tag = item.find('h2').find('a')
        event_title = event_title_tag.text
        event_url = event_title_tag['href']
        event_description = soup.find('p').text
    
        articles.append(
            {
                "target_id": "yonderqtEvent",
                "target_url": "https://www.yonderqt.co.nz/blog/",
                "event_url": event_url,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": start_date,
                "event_imgurl": "https://www.yonderqt.co.nz/blog/",
                "event_description": event_description,
                "end_time" : "00:00:00.0000000",
                "start_time" : "00:00:00.0000000",
                "event_location": {
                    "title" : "yonderqt",
                    "street" : "street",
                    "region" : "region",
                    "country" : "Australia"
                },
            }
        )

    return articles

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
def save_to_supabase(article):
    title = article["event_title"]
    date = article["start_date"]
    time = article["start_time"]
    existing_article = (
        supabase.table("guideEvent").select("*").eq("event_title", title).eq("start_date", date).eq("start_time", time).execute()
    )

    if not existing_article.data:
        response = supabase.table("guideEvent").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")


def get_event_from_yonderqt():
    main_page_url = "https://www.yonderqt.co.nz/blog/"

    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)