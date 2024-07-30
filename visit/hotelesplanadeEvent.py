import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re

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


def get_event_from_hotelesplanade():
    
    articles = []
    
    article = {
        "target_id": "thistlehallEvent",
        "target_url": "https://thistlehall.org.nz/",
        "event_title": "gallery repaint",
        "start_date" : "2024-06-18",
        "start_time" : "11:00:00.0000000",
        "end_date" : "2024-06-21",
        "end_time" : "18:00:00.0000000",
        "event_category": "Show",
        "event_description": "Thistle Hall Community Gallery is closed this week for our biannual spruce up and repaint. \n This gallery maintenance keeps our walls fresh and tidy for all exhibitors, and is funded by the 10% commission on exhibitors sales.",
        "event_location": {
            "title" : "Thistle Hall Community Venue",
            "street" : "Street",
            "region" : "Region",
            "country" : "New Zealand",
        },
        "event_imgurl": "/sites/default/files/styles/half_page/public/exhibitions/gal1.png?itok=Vf9NH1-y",
    }

    save_to_supabase(article)
