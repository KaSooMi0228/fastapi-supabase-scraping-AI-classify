import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    # response = requests.get(url)
    response = requests.get(f"{url}?start={page}")
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all("div", class_="grid-article-tile-container")
    articles = []

    for item in raws:
        article = item.find("a", class_="grid-article-tile")

        # Extract the required information
        news_url = article["href"]
        news_full_url = urljoin("https://www.comedyfestival.co.nz", news_url)
        title = article.find("span", class_="title").get_text(strip=True)
        date = article.find("span", class_="subtitle").get_text(strip=True)
        image_style = article.find("span", class_="image")
        style_attr = image_style.get("style")

        # Use a regular expression to extract the URL from the background-image property
        url_match = re.search(r"url\('(.+?)'\)", style_attr)
        image_url = url_match.group(1)

        date_obj = datetime.strptime(date, "%d %b %Y")
        formatted_date = date_obj.strftime("%d-%m-%Y")

        articles.append(
            {
                "target_id": "comedyfestivalNews",
                "target_url": "https://www.comedyfestival.co.nz/news-feed/",
                "title": title,
                "news_url": news_full_url,
                "imageUrl": image_url,
                "date": formatted_date,
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    news_section = soup.find("section", class_="news-page")
    starting_point = news_section.find("p", class_="date")

    if not starting_point:
        starting_point = news_section.find("h1")

    info = []
    if starting_point:
        for sibling in starting_point.find_next_siblings():
            if sibling.name in ["p", "h1"]:
                info.append(sibling.get_text(strip=True))

            if sibling.name == "h1" and sibling != starting_point:
                break

    info_text = "\n\n".join(info)

    return info_text


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


def get_news_from_comedyfestival():
    main_page_url = "https://www.comedyfestival.co.nz/news-feed/filter"
    page = 0
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            article["content"] = scrape_detail_page(article["news_url"])
            save_to_supabase(article)

        page += 9
