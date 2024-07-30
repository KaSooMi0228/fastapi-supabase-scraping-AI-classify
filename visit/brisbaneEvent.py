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

    articles = []
    
    # Find the target element (div with class 'slick-track')
    slick_track_div = soup.find('div', class_='slick-track')

    # Find all child divs of the target element
    child_divs = slick_track_div.find_all('div', recursive=False)

    # Loop through each child div and extract information
    for index, child in enumerate(child_divs):

        # Extract event URL
        event_url_tag = child.find('a', class_='card__overlay')
        event_url = event_url_tag['href'] if event_url_tag else 'N/A'

        # Extract image URL
        image_tag = child.find('img')
        image_url = image_tag['src'] if image_tag else 'N/A'

        # Extract event category
        event_category_tag = child.find('div', class_='card__category')
        event_category = event_category_tag.get_text(strip=True) if event_category_tag else 'N/A'

        # Extract event title
        event_title_tag = child.find('div', class_='card__title')
        event_title = event_title_tag.get_text(strip=True) if event_title_tag else 'N/A'

        # Extract event description
        event_description_tag = child.find('div', class_='card__body-text')
        event_description = event_description_tag.get_text(strip=True) if event_description_tag else 'N/A'
        
        articles.append(
            {
                "target_id": "brisbaneEvent",
                "target_url": "https://visit.brisbane.qld.au/places-to-go",
                "event_title": event_title,
                "event_category": event_category,
                "event_imgurl": image_url,
                "event_url": event_url,
                "event_description": event_description,
                "start_date": "",
                "end_date": "",
                "start_time": "00:00:00.0000000",
                "end_time": "00:00:00.0000000",
                "event_location": {
                    "title" : "",
                    "street" : "",
                    "region" : "",
                    "country" : "Australia"
                }
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


def get_event_from_brisbane():
    main_page_url = "https://visit.brisbane.qld.au/places-to-go"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)
