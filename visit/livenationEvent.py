import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
import json


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    
    script_tags = soup.find_all('script', type='application/ld+json')
    
    articles = []

    for item in script_tags:
        json_data = json.loads(item.string)
        event_title = json_data.get('name', 'N/A')
        event_imgurl = json_data.get('image', 'N/A')
        event_url = json_data.get('url', 'N/A')
        start_date = json_data.get('startDate', 'N/A')
        end_date = json_data.get('endDate', 'N/A')
        location = json_data.get('location', {})
        location_title = location.get('name', 'N/A')
        location_region = location.get('address', {}).get('addressLocality', 'N/A')
        description = json_data.get('offers', {}).get('name', 'N/A')
    
        articles.append(
            {
                "target_id": "livenationEvent",
                "target_url": "https://www.livenation.co.nz/event/allevents",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": start_date,
                "end_date": end_date,
                "event_description": description,
                "start_time": "00:00:00.0000000",
                "end_time": "00:00:00.0000000",
                "event_location": {
                    "title" : location_title,
                    "street" : "Street",
                    "region" : location_region,
                    "country" : "New Zealand"
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


def get_event_from_livenation():
    main_page_url = "https://www.livenation.co.nz/event/allevents"

    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)