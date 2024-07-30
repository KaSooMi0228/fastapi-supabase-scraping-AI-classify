import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("div", class_="b-accordion__item")
    articles = []

    for item in raws:
        image_url = item.find("img", class_="b-accordion__newsheader__image")["src"]

        # Extract the title
        title = item.find("h2").text.strip()

        # Extract the date
        date_text = item.find("h5").text.strip()
        # Convert date format from "Posted on February 7, 2024" to "07-02-2024"
        date = datetime.strptime(
            date_text.replace("Posted on ", ""), "%B %d, %Y"
        ).strftime("%d-%m-%Y")

        # Extract the content
        content_div = item.find("div", class_="b-accordion__content")
        content_paragraphs = content_div.find_all("p")
        content = "\n".join(
            [
                p.get_text(strip=True)
                for p in content_paragraphs
                if p.get_text(strip=True)
            ]
        )

        articles.append(
            {
                "target_id": "greenstoneentertainmentNews",
                "target_url": "https://greenstoneentertainment.co.nz/news-categories/2024/",
                "title": title,
                "news_url": "https://greenstoneentertainment.co.nz/news-categories/2024/",
                "imageUrl": image_url,
                "date": date,
                "content": content,
            }
        )

    return articles


# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Function to check for duplication and insert if not duplicated
def save_to_supabase(article):
    title = article["title"]
    date = article["date"]
    existing_article = (
        supabase.table("News").select("*").eq("title", title).eq("date", date).execute()
    )

    if not existing_article.data:
        response = supabase.table("News").insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")


def get_news_from_greenstoneentertainment():
    main_page_url = "https://greenstoneentertainment.co.nz/news-categories/2024/"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        save_to_supabase(article)
