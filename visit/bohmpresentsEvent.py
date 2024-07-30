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

    raws = soup.find_all('div', class_='block widget', attrs={'data-loaded': 'true'})
    articles = []

    for item in raws:
        a_tag = item.find('a')
        img_tag = item.find('img')
        info_div = item.find('div', class_='info')

        if a_tag and img_tag and info_div:
            event_url = a_tag['href']
            event_imgurl = img_tag['src']
            event_tile = info_div.get_text(strip=True)

            articles.append(
                {
                    "target_id": "bohmpresentsEvent",
                    "target_url": "https://www.bohmpresents.com/current-events/",
                    "event_title": event_tile,
                    "event_category": 'Show',
                    "event_imgurl": event_imgurl,
                    "event_url": event_url,
                    "event_category": "show",
                }
            )

    return articles

# Function to scrape the detail page for image URL
def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = soup.find("div", class_="description").get_text(separator="\n").strip()
    return article_content

def scrape_stime_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    first_aside = soup.find('aside', class_='event-venue-info')

    # Extract the required information
    date_text = first_aside.find('li', class_='date').text

    # Parse the date and time
    date_time_str = date_text.split('@')
    time_str = date_time_str[1].strip()

    # Convert to datetime objects
    start_time = datetime.strptime(time_str, '%I:%M%p').time()
    
    return start_time

def scrape_sdate_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    first_aside = soup.find('aside', class_='event-venue-info')

    # Extract the required information
    date_text = first_aside.find('li', class_='date').text

    # Parse the date and time
    date_time_str = date_text.split('@')
    date_str = date_time_str[0].strip().split(', ')[1].strip()

    # Convert to datetime objects
    start_date = datetime.strptime(date_str, '%d %B %Y').date()
    
    return start_date

def scrape_location_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    first_aside = soup.find('aside', class_='event-venue-info')

    # Extract the required information
    title = first_aside.find('li', class_='title').text
    date_text = first_aside.find('li', class_='date').text
    venue = first_aside.find('li', class_='venue').text

    # Parse the date and time
    date_time_str = date_text.split('@')
    date_str = date_time_str[0].strip().split(', ')[1].strip()
    time_str = date_time_str[1].strip()

    # Convert to datetime objects
    start_date = datetime.strptime(date_str, '%d %B %Y').date()
    start_time = datetime.strptime(time_str, '%I:%M%p').time()
    
    location = {
        "title" : title,
        "street" : "",
        "region" : venue,
        "country" : "Australia"
    }
    
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

    # Convert date and time to string for comparison and insertion
    date_str = date.strftime('%Y-%m-%d')
    time_str = time.strftime('%H:%M:%S')

    # Check for existing article in Supabase
    existing_article = (
        supabase.table("guideEvent").select("*").eq("event_title", title).eq("start_date", date_str).eq("start_time", time_str).execute()
    )

    if not existing_article.data:
        # Update article dict with string representations of date and time
        article["start_date"] = date_str
        article["start_time"] = time_str
        response = supabase.table("guideEvent").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")

def get_event_from_bohmpresents():
    main_page_url = "https://www.bohmpresents.com/current-events/"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        article["event_description"] = scrape_detail_page(article["event_url"])
        article["start_time"] = scrape_stime_page(article["event_url"])
        article["start_date"] = scrape_sdate_page(article["event_url"])
        article["event_location"] = scrape_location_page(article["event_url"])
        article["end_date"] = ""
        article["end_time"] = ""
        save_to_supabase(article)