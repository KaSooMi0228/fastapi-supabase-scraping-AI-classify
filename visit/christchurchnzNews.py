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
    response = requests.get(f"{url}?page={page}")
    soup = BeautifulSoup(response.content, "html.parser")
    raws_prefix = soup.find("article", class_="c-card_news--featured")
    raws = soup.find_all("article", class_="c-card_news--large")
    articles = []

    title_element = raws_prefix.find("h2", class_="c-card_news__title")
    title = title_element.text.strip() if title_element else None

    news_element = raws_prefix.find("a", class_="c-card_news__img_link")
    news_url = news_element["href"] if news_element else None
    news_full_url = urljoin("https://www.christchurchnz.com/", news_url)

    img_element = raws_prefix.find("img", class_="c-card_news__img")
    img_url = img_element["src"] if img_element else None
    img_full_url = urljoin("https://www.christchurchnz.com/", img_url)

    date_element = raws_prefix.find("time", class_="c-card_news__date")
    date = date_element.text.strip() if date_element else None
    date_obj = datetime.strptime(date, "%A, %d %B %Y")
    formatted_date = date_obj.strftime("%d-%m-%Y")

    articles.append(
        {
            "target_id": "christchurchnzNews",
            "target_url": "https://www.christchurchnz.com/about-us/news",
            "title": title,
            "news_url": news_full_url,
            "imageUrl": img_full_url,
            "date": formatted_date,
        }
    )

    for item in raws:
        title_element = item.find("h2", class_="c-card_news__title")
        title = title_element.text.strip() if title_element else None

        news_element = item.find("a", class_="c-card_news__img_link")
        news_url = news_element["href"] if news_element else None
        news_full_url = urljoin("https://www.christchurchnz.com/", news_url)

        img_element = item.find("img", class_="c-card_news__img")
        img_url = img_element["src"] if img_element else None
        img_full_url = urljoin("https://www.christchurchnz.com/", img_url)

        date_element = item.find("time", class_="c-card_news__date")
        date = date_element.text.strip() if date_element else None
        date_obj = datetime.strptime(date, "%A, %d %B %Y")
        formatted_date = date_obj.strftime("%d-%m-%Y")

        articles.append(
            {
                "target_id": "christchurchnzNews",
                "target_url": "https://www.christchurchnz.com/about-us/news",
                "title": title,
                "news_url": news_full_url,
                "imageUrl": img_full_url,
                "date": formatted_date,
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")
    article_content = soup.find("div", class_="t-rich_text  t-rich_text--editorial")
    if article_content is not None:
        article_div = article_content.find_all("p")
        # if article_content:
        # extracted_text = article_content.get_text(separator=" ", strip=True)
        paragraph_content = [p.get_text(separator=" ") for p in article_div]
        result = "\n\n".join(paragraph_content)
    else:
        result = "No content found"

    return result


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


def get_news_from_christchurchnz():
    main_page_url = "https://www.christchurchnz.com/about-us/news"
    page = 1
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            article["content"] = scrape_detail_page(article["news_url"])
            save_to_supabase(article)

        page += 1
