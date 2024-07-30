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
    # p_element = soup.find("p", class_="preFade fadeIn")
    # p_date = p_element.get_text()
    # date_match = re.search(r"(\d{1,2})(?:st|nd|rd|th) (\w+) (\d{4})", p_date)

    # if date_match:
    #     day = date_match.group(1)
    #     month = date_match.group(2)
    #     year = date_match.group(3)

    #     # Convert month name to month number
    #     month_number = {
    #         "January": "01",
    #         "February": "02",
    #         "March": "03",
    #         "April": "04",
    #         "May": "05",
    #         "June": "06",
    #         "July": "07",
    #         "August": "08",
    #         "September": "09",
    #         "October": "10",
    #         "November": "11",
    #         "December": "12",
    #     }[month]

    #     # Format the date as "DD-MM-YYYY"
    #     formatted_date = f"{day.zfill(2)}-{month_number}-{year}"
    # else:
    #     print("Date not found")
    raws = soup.find_all("article", class_="blog-basic-grid--container entry blog-item")
    articles = []

    for item in raws:
        news_url = item.find("a", class_="image-wrapper")["href"]
        image_url = (
            item.find("img", class_="image")["srcset"]
            .split(",")[-1]
            .strip()
            .split(" ")[0]
        )
        title = item.find("h1", class_="blog-title").get_text(strip=True)
        full_url = urljoin("https://www.taupowinterfestival.co.nz", news_url)

        articles.append(
            {
                "target_id": "taupowinterfestivalNews",
                "target_url": "https://www.taupowinterfestival.co.nz/news-updates",
                "title": title,
                "news_url": full_url,
                "imageUrl": image_url,
                "date": "Not Found Date",
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = (
        soup.find("div", class_="sqs-html-content").get_text(separator="\n").strip()
    )
    return article_content


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


def get_news_from_taupowinterfestival():
    main_page_url = "https://www.taupowinterfestival.co.nz/news-updates"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        article["content"] = scrape_detail_page(article["news_url"])
        save_to_supabase(article)
