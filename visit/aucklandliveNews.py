import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import json


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response1 = requests.get(f"{url}&category={1}")
    response2 = requests.get(f"{url}&category={5}")
    response3 = requests.get(f"{url}&category={7}")
    response4 = requests.get(f"{url}&category={6}")
    response5 = requests.get(f"{url}&category={2}")
    soup1 = response1.json()
    soup2 = response2.json()
    soup3 = response3.json()
    soup4 = response4.json()
    soup5 = response5.json()
    articles = []

    parsed1 = soup1["data"]
    parsed2 = soup2["data"]
    parsed3 = soup3["data"]
    parsed4 = soup4["data"]
    parsed5 = soup5["data"]

    for item1 in parsed1:
        if item1["type"] == "news":
            # Since the provided JSON does not have "attributes", I'm assuming you intended to have "attributes" in your JSON.
            # If "attributes" is indeed present, you should update the sample JSON accordingly.
            attributes = item1.get("attributes", {})
            name = attributes.get("name", "No Title")
            thumbnail = attributes.get("thumbnail", "No Thumbnail")
            content = next(
                (
                    block["data"]["content"]
                    for block in attributes.get("blocks", [])
                    if block["type"] == "content"
                ),
                "No Content",
            )
            self_url = item1.get("links", {}).get("self", "No URL")

            articles.append(
                {
                    "target_id": "aucklandliveNews",
                    "target_url": "https://www.aucklandlive.co.nz/news",
                    "title": name,
                    "news_url": self_url,
                    "imageUrl": thumbnail,
                    "content": content,
                    "date": "Date not found",
                }
            )

    for item2 in parsed2:
        if item2["type"] == "news":
            # Since the provided JSON does not have "attributes", I'm assuming you intended to have "attributes" in your JSON.
            # If "attributes" is indeed present, you should update the sample JSON accordingly.
            attributes = item2.get("attributes", {})
            name = attributes.get("name", "No Title")
            thumbnail = attributes.get("thumbnail", "No Thumbnail")
            content = next(
                (
                    block["data"]["content"]
                    for block in attributes.get("blocks", [])
                    if block["type"] == "content"
                ),
                "No Content",
            )
            self_url = item2.get("links", {}).get("self", "No URL")

            articles.append(
                {
                    "target_id": "aucklandliveNews",
                    "target_url": "https://www.aucklandlive.co.nz/news",
                    "title": name,
                    "news_url": self_url,
                    "imageUrl": thumbnail,
                    "content": content,
                    "date": "Date not found",
                }
            )

    for item3 in parsed3:
        if item3["type"] == "news":
            # Since the provided JSON does not have "attributes", I'm assuming you intended to have "attributes" in your JSON.
            # If "attributes" is indeed present, you should update the sample JSON accordingly.
            attributes = item3.get("attributes", {})
            name = attributes.get("name", "No Title")
            thumbnail = attributes.get("thumbnail", "No Thumbnail")
            content = next(
                (
                    block["data"]["content"]
                    for block in attributes.get("blocks", [])
                    if block["type"] == "content"
                ),
                "No Content",
            )
            self_url = item3.get("links", {}).get("self", "No URL")

            articles.append(
                {
                    "target_id": "aucklandliveNews",
                    "target_url": "https://www.aucklandlive.co.nz/news",
                    "title": name,
                    "news_url": self_url,
                    "imageUrl": thumbnail,
                    "content": content,
                    "date": "Date not found",
                }
            )

    for item4 in parsed4:
        if item4["type"] == "news":
            # Since the provided JSON does not have "attributes", I'm assuming you intended to have "attributes" in your JSON.
            # If "attributes" is indeed present, you should update the sample JSON accordingly.
            attributes = item4.get("attributes", {})
            name = attributes.get("name", "No Title")
            thumbnail = attributes.get("thumbnail", "No Thumbnail")
            content = next(
                (
                    block["data"]["content"]
                    for block in attributes.get("blocks", [])
                    if block["type"] == "content"
                ),
                "No Content",
            )
            self_url = item4.get("links", {}).get("self", "No URL")

            articles.append(
                {
                    "target_id": "aucklandliveNews",
                    "target_url": "https://www.aucklandlive.co.nz/news",
                    "title": name,
                    "news_url": self_url,
                    "imageUrl": thumbnail,
                    "content": content,
                    "date": "Date not found",
                }
            )

    for item5 in parsed5:
        if item5["type"] == "news":
            # Since the provided JSON does not have "attributes", I'm assuming you intended to have "attributes" in your JSON.
            # If "attributes" is indeed present, you should update the sample JSON accordingly.
            attributes = item5.get("attributes", {})
            name = attributes.get("name", "No Title")
            thumbnail = attributes.get("thumbnail", "No Thumbnail")
            content = next(
                (
                    block["data"]["content"]
                    for block in attributes.get("blocks", [])
                    if block["type"] == "content"
                ),
                "No Content",
            )
            self_url = item5.get("links", {}).get("self", "No URL")

            articles.append(
                {
                    "target_id": "aucklandliveNews",
                    "target_url": "https://www.aucklandlive.co.nz/news",
                    "title": name,
                    "news_url": self_url,
                    "imageUrl": thumbnail,
                    "content": content,
                    "date": "Date not found",
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


def get_news_from_aucklandlive():
    main_page_url = "https://www.aucklandlive.co.nz/api/live/news?is_published=true&featured=false&page=1"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        # article["content"] = scrape_detail_page(article["news_url"])
        # article["date"] = scrape_detail_date_page(article["news_url"])
        save_to_supabase(article)
