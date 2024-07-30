import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
def save_to_supabase(article):
    title = article["title"]
    targetId = article["target_id"]
    date = article["date"]
    existing_article = (
        supabase.table("News").select("*").eq("target_id", targetId).eq("title", title).eq("date", date).execute()
    )

    if not existing_article.data:
        response = supabase.table("News").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")


def get_news_from_wellingtonnz():
    article = {
                "target_id": "wellingtonnzNews",
                "target_url": "https://www.wellingtonnz.com/venues-wellington/our-venues",
                "date": "Date Not Found",
                'title': 'TSB Arena',
                'imageUrl': 'https://wellingtonnz.bynder.com/transform/b951f231-da92-4426-9e10-99f84fa88987/TSB-Arena-52?io=transform:fill,width:230,height:230',
                'content': '4 Queens Wharf, Wellington Central, Wellington\nThe TSB Arena is Wellington’s biggest indoor venue. It’s a go-to venue choice for conferences, public exhibitions, international concerts and indoor sporting events. Our venues, Wellington',
                'news_url': 'https://www.wellingtonnz.com/venues-wellington/our-venues/tsb-arena'
            }

    save_to_supabase(article)
