import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    response = requests.get(f"{url}&p={page}&is_v=1")
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="ais-hits--item event-container")
    articles = []

    for item in raws:
        event_url = item.find('a', href=True)['href']

        # Extract the date
        day = item.find('span', class_='day').text
        date = item.find('span', class_='date').text
        month = item.find('span', class_='month').text

        # Convert to full date
        event_date = datetime.strptime(f"2024 {month} {date}", '%Y %b %d').date()

        # Extract the event title
        event_title = item.find('h3', class_='event-name').text.strip()

        # Extract the image URL
        image_url = item.find('img')['src']

        articles.append(
            {
                "target_id": "thetotehotelEvent",
                "target_url": "https://thetotehotel.com/gig-guide",
                "event_title": event_title,
                "event_category": 'Gigs',
                "event_imgurl": image_url,
                "event_url": event_url,
                "start_date": event_date,
                "end_date": event_date,
                "end_time": "End Time not found",
                "event_location": {
                    "title" : "thetotehotel",
                    "street" : "The Tote",
                    "region" : "Upstairs (Collingwood, VIC)",
                    "country" : "Australia"
                }
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = soup.find("div", class_="event-description").get_text(separator="\n").strip()
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


def get_event_from_thetotehotel():
    main_page_url = "https://thetotehotel.com/gig-guide/#q=&hPP=20"
    page = 0
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            article["event_description"] = scrape_detail_page(article["event_url"])
            article["start_time"] = scrape_stime_page(article["event_url"])
            save_to_supabase(article)

        page += 1
