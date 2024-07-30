import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    response = requests.get(f"{url}?b138d03a_page={page}")
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="events-item w-dyn-item")
    articles = []

    for item in raws:
        base_url = 'https://www.bigfan.co.nz'

        # Extract the event title
        event_title = item.find('a', class_='event-title w-inline-block').find_all('div')[1].text.strip()

        # Extract the start date and format it as required
        start_date_raw = item.find('div', class_='event__date').text.strip()
        start_date = datetime.strptime(f"{start_date_raw} 2024", "%d %b %Y").strftime("%Y-%m-%d")

        # Extract the event link and join with the base URL
        relative_event_link = item.find('a', class_='event-link-block w-inline-block')['href']
        event_link = urljoin(base_url, relative_event_link)
        
        event_imgurl = soup.find('a', class_='event-link-block w-inline-block').find('img')['src']

        articles.append(
            {
                "target_id": "bigfanEvent",
                "target_url": "https://www.bigfan.co.nz/events",
                "event_title": event_title,
                "event_category": 'Event',
                "event_imgurl": event_imgurl,
                "event_url": event_link,
                "start_date": start_date,
                "start_time" : "19:00:00.0000000",
                "end_date": start_date,
                "end_time": "00:00:00.0000000",
                "event_location": {
                    "title" : "Hard Rock/Grunge Specialists",
                    "street" : "Awhitu Peninsulas finest",
                    "region" : "Auckland",
                    "country" : "Australia"
                }
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_div = soup.find("div", class_="event-rich-body w-richtext")
    if article_div:
        article_content = article_div.get_text(separator="\n").strip()
    else:
        article_content = None
        
    return article_content

def scrape_stime_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    time_div = soup.find_all('div', class_='event-details-item')[1]

    # Extract the time text from the span
    time_text = time_div.find('span').text.strip()

    # Extract the time part from the text
    time_match = re.search(r'\d{1,2}:\d{2} [apm]{2}', time_text)

    if time_match:
        time_str = time_match.group()
        # Convert time to 24-hour format and add microseconds
        from datetime import datetime
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        formatted_time = time_obj.strftime('%H:%M:%S.%f')
    
    return formatted_time

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


def get_event_from_bigfan():
    main_page_url = "https://www.bigfan.co.nz/events"
    page = 0
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            article["event_description"] = scrape_detail_page(article["event_url"])
            save_to_supabase(article)

        page += 1
