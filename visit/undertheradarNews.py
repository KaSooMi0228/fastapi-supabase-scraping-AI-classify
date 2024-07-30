import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import urllib.parse
import re


# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    raws = soup.find_all("a", attrs={"title": "click here for more"})
    articles = []

    for item in raws:
        # Extracting the imageUrl
        image_tag = item.find("img", class_="lazy")
        if image_tag and "data-original" in image_tag.attrs:
            image_url = image_tag["data-original"]
        else:
            continue  # Skip this item if no image is found

        href = item["href"]
        parsed_url = urllib.parse.urlparse(href)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if "url" in query_params and query_params["url"]:
            news_url = query_params["url"][0]

        # Extracting the title from the URL
        parsed_news_url = urllib.parse.urlparse(news_url)
        path_segments = parsed_news_url.path.split("/")
        title = path_segments[-1].replace("-", " ").replace(".utr", "")

        articles.append(
            {
                "target_id": "undertheradarNews",
                "target_url": "https://www.undertheradar.co.nz/utr/news",
                "title": title,
                "news_url": news_url,
                "imageUrl": image_url,
                "date": "Date not Found",
                "content": "Fetch Content Exception",
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_content = soup.find("div", class_="article_text").get_text(
        separator="\n", strip=True
    )
    return article_content


def scrape_detail_date_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, "html.parser")

    raw = soup.find("div", "col-md-10 conte nt-col")
    date_span = raw.find("span", class_="date")

    # Extract the text content from the span
    date_text = date_span.get_text(strip=True)

    # Use regular expression to find the date in the text
    date_match = re.search(r"\b(\d{1,2}th\s\w+,\s\d{4})\b", date_text)

    # Extract the date string
    date_str = date_match.group(1)

    # Convert it to a datetime object
    date_obj = datetime.strptime(date_str, "%dth %B, %Y")

    # Reformat the date to 'DD-MM-YYYY'
    formatted_date = date_obj.strftime("%d-%m-%Y")

    return formatted_date


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


def get_news_from_undertheradar():
    main_page_url = "https://www.undertheradar.co.nz/utr/news"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        # article["content"] = scrape_detail_page(article["news_url"])
        # article["date"] = scrape_detail_date_page(article["news_url"])
        save_to_supabase(article)
