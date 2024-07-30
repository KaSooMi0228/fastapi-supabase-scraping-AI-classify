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

    raws = soup.find_all("div", class_="w-52 max-sm:snap-center shrink-0")
    articles = []

    for item in raws:

        event_url = item.find('a', {'data-testid': True})['href']

        # Extract event image URL
        event_img = item.find('img', {'alt': True})
        event_imgurl = event_img['srcset'].split(',')[0].strip().split(' ')[0]

        # Extract event title
        event_title = item.find('p', {'class': 'text-lg font-semibold text-black'}).text.strip()

        # Extract event location
        event_location = item.find('span', {'class': 'flex gap-0.5 items-center p-1 rounded-lg w-fit text-sm bg-gray-100 text-gray-800 max-w-full'}).text.strip()
        date_span = item.find('div', {'class': 'hidden sm:flex items-center absolute bottom-2 right-2 ml-2 p-1 rounded-lg text-sm bg-indigo-100 text-indigo-800'})
        date = date_span.find('span').text.strip()
    
        articles.append(
            {
                "target_id": "iticketEvent",
                "target_url": "https://www.iticket.co.nz/",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": date,
                "end_date": date,
                "event_description": "event_title",
                "start_time": "00:00:00.0000000",
                "end_time": "00:00:00.0000000",
                "event_location": {
                    "title" : event_location,
                    "street" : "Street",
                    "region" : "Region",
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


def get_event_from_iticket():
    main_page_url = "https://www.iticket.co.nz/"

    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)