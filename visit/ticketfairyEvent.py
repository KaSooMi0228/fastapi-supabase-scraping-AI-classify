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

    raws = soup.find_all("div", class_="owl-carousel events-carousel mobile type_upcoming")
    articles = []

    for item in raws:
        event_url = item.select_one('a[target="_self"]')['href']
        event_imgurl = item.select_one('img.owl-image')['src']

        # Extract event title
        event_title = item.select_one('a[target="_self"]').text.strip()

        # Extract date and time
        date_str = item.select_one('.col-60 .orange').text.strip()
        time_str = item.select_one('.col-60 .light-color').text.strip().split('/')[1].strip()

        # Convert date and time to required format
        start_date = datetime.strptime(date_str, '%d %B %Y').date()
        start_time = datetime.strptime(time_str, '%I:%M %p').time()

        # Extract region and country
        region = item.select_one('.event-location span').text.strip()
        country = item.select_one('.event-location span').text.strip()
    
        articles.append(
            {
                "target_id": "ticketfairyEvent",
                "target_url": "https://www.ticketfairy.com/search-results?type=upcoming",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": start_date.isoformat(),  # Convert to string
                "end_date": "",
                "event_description": "",
                "start_time": start_time.isoformat(),  # Convert to string
                "end_time": "",
                "event_location": {
                    "title" : "",
                    "street" : "",
                    "region" : region,
                    "country" : country
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


def get_event_from_ticketfairy():
    main_page_url = "https://www.ticketfairy.com/search-results?type=upcoming"

    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)