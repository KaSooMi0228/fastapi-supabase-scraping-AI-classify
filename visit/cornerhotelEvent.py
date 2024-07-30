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

    raws = soup.find_all("a", class_="calendar__item clearfix")
    articles = []

    for item in raws:
        event_url = item['href']

        event_title = item.find('h1', class_='calendar__item-title').text.strip()

        # Extract image URL
        image_url = item.find('div', class_='calendar__item-image').find('img')['src']

        # Extract date information
        date_text = item.find('div', class_='calendar__item-date').text.strip()
        # Extract date components
        day = date_text[3:5].strip()
        month = date_text[5:].strip()

        # Create a date object
        date_string = f"2024-{month}-{day}"
        date = datetime.strptime(date_string, "%Y-%b-%d").date()

        # Format the date as YYYY-MM-DD
        formatted_date = date.strftime('%Y-%m-%d')

        articles.append(
            {
                "target_id": "cornerhotelEvent",
                "target_url": "http://cornerhotel.com/events-and-specials/",
                "event_title": event_title,
                "event_category": 'Shows',
                "event_imgurl": image_url,
                "event_url": event_url,
                "start_date": formatted_date,
                "end_date": formatted_date,
                "start_time": "23:00:00.0000000",
                "end_time": "23:00:00.0000000",
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = soup.find("div", class_="page__aside").get_text(separator="\n").strip()
    return article_content

def scrape_location_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    content = soup.find("h2", class_="page__subheading").get_text().strip()
    
    location = []
    
    location.append(
            {
                "title" : "cornerhotel",
                "street" : "Street Not Found",
                "region" : content,
                "country" : "Australia"
            }
        )
    
    return location

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


def get_event_from_cornerhotel():
    main_page_url = "http://cornerhotel.com/events-and-specials/"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        article["event_description"] = scrape_detail_page(article["event_url"])
        article["event_location"] = scrape_location_page(article["event_url"])
        save_to_supabase(article)
