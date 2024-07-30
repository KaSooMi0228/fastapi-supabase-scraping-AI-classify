import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
import re
from urllib.parse import urljoin


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("li", class_="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiCard-root ns-9jdmtw")
    articles = []

    for item in raws:
        event_url = item.find('a', class_='MuiButtonBase-root MuiCardActionArea-root ns-bmjbd8')['href']

        # Extract the event title
        event_title = item.find('h3', class_='MuiTypography-root MuiTypography-header3 ns-fq3fbe').text

        # Extract the date
        date_text = item.find('small', class_='MuiTypography-root MuiTypography-smallParagraph ns-1q3svv7').text
        # date = datetime.strptime(date_text, '%a %d %b %Y').strftime('%Y-%m-%d')
        # fullurl = urljoin("https://www.tuningfork.co.nz", event_url)
        
        img_tag = item.find('img')

        # Extract the value of the 'src' attribute
        event_imgurl = img_tag['src']
    
        articles.append(
            {
                "target_id": "tuningforkEvent",
                "target_url": "https://www.tuningfork.co.nz/",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
                "event_title": event_title,
                "start_date": date_text,
                "end_date": date_text,
                "event_description": "ENTRY INFO \n We'd prefer it if you leave your bags at home, but if you do need to bring one, please keep it small. Bags will be subject to a quick inspection before you enter. \n Remember to bring your photo ID (a valid NZ driver's license, passport or Kiwi Access Card) if you'd like to drink as ID is required for all alcohol purchases. We’ll need to see your ID otherwise we are unable to serve them to you or refund your purchase if you do not have your ID with you. \n This is a cashless event. \n FOOD & DRINKS \n A range of food and drinks will be available in the venue. \n Alcohol Policy",
                "start_time": "18:30:00.0000000",
                "end_time": "00:00:00.0000000",
                "event_location": {
                    "title" : "Tuning Fork",
                    "street" : "Street",
                    "region" : "Region",
                    "country" : "New Zealand",
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


def get_event_from_tuningfork():
    main_page_url = "https://www.tuningfork.co.nz/"

    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)