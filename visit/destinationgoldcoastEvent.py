import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    response = requests.get(f"{url}?page={page}")
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="img-cont listing-cont")
    articles = []

    for item in raws:
        a_tag = item.find('a')

        # Extract the event URL
        event_url = a_tag['href']

        # Locate the <img> tag within the <a> tag
        img_tag = a_tag.find('img')

        # Extract the image URL
        event_imgurl = img_tag['src']
        
        desc_div = soup.find('a', href=event_url)

        # Find the direct child <div> with the class name "desc"
        if desc_div:
            event_title = desc_div.find('h3').text.strip() if desc_div.find('h3') else "No Title"

            # Extract the date range and split into start and end dates
            date_range = desc_div.find('h2').find('span').text.strip() if desc_div.find('h2') and desc_div.find('h2').find('span') else "From now until 01 January 2000"
            start_date, end_date = re.match(r'From (now) until (\d{2} \w+ \d{4})', date_range).groups()

            # Convert end date to YYYY-MM-DD format
            end_date = datetime.strptime(end_date, '%d %B %Y').strftime('%Y-%m-%d')

            # Extract the event description
            event_description = desc_div.find('p', class_='event-desc').text.strip() if desc_div.find('p', class_='event-desc') else "No Description"

            articles.append(
                {
                    "target_id": "destinationgoldcoastEvent",
                    "target_url": "https://www.destinationgoldcoast.com/events/all",
                    "event_imgurl": event_imgurl,
                    "event_url": event_url,
                    "event_title": event_title,
                    "start_date": start_date,
                    "end_date": end_date,
                    "event_description": event_description,
                    "start_time": "",
                    "end_time": "",
                    "event_location": {
                        "title" : "",
                        "street" : "",
                        "region" : "",
                        "country" : "Australia"
                    },
                }
            )
        else:
            print(f"No desc div found for event URL: {event_url}")

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


def get_event_from_destinationgoldcoast():
    main_page_url = "https://www.destinationgoldcoast.com/events/all"
    page = 1
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            save_to_supabase(article)

        page += 1