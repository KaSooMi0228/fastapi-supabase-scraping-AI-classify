import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    response = requests.get(f"{url}?Page={page}")
    soup = BeautifulSoup(response.content, "html.parser")

    raws = soup.find_all("li", class_="MuiButtonBase-root MuiListItem-root MuiListItem-dense MuiListItem-gutters MuiListItem-padding MuiListItem-button prisma31 ns-13zeyb5")
    articles = []

    for item in raws:
        # Extract the event URL
        event_url = item.find('a', class_='MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways prisma46 prisma39 event-ticket-link prisma32 ns-1sb55b8')['href']
        # Extract the date and time
        time_element = item.find('time', class_='ns-rpxx7c')
        day = time_element.find('span', class_='ns-1x6z45a').text
        month = time_element.contents[2].strip()
        year = '2024'  # Assuming the year is known
        date_str = f'{year}-{month}-{day}'
        start_date = datetime.strptime(date_str, '%Y-%b-%d').date()
        start_time = time_element.find('span', class_='ns-irfbko').text.strip() if time_element.find('span', class_='ns-irfbko') else None
        # Extract the event title
        event_title = item.find('p', class_='MuiTypography-root MuiTypography-paragraph prisma55 ns-1lo656q').text
        # Extract the event image URL
        event_imgurl = item.find('img', class_='ns-v7vbs9')['src']

        articles.append(
            {
                "event_title": event_title,
                "start_date" : start_date,
                "start_time" : start_time,
                "end_date" : "",
                "end_time" : "",
                "event_category": "Venue",
                "event_imgurl": event_imgurl,
                "event_url": event_url,
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the section with the specific class
    section = soup.find('section', class_='ns-ohmmtl')
    if not section:
        return {"error": "Section not found"}
    # Extract text from the <p> tag within the specified section
    rich_text_module = section.find('div', class_='prisma2 rich-text-module')
    if not rich_text_module:
        return {"error": "Rich text module not found"}
    # Extract the text from the <p> tag
    p_tag = rich_text_module.find('p')
    if not p_tag:
        return {"error": "Paragraph tag not found"}
    # Get the formatted text
    extracted_text = p_tag.get_text(separator="\n").strip()
        
    return extracted_text

def scrape_cart_url(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    anchor_tag = soup.find('a', {'data-testid': 'aedp-event-single-ticket-action-button-or-status'})
    if not anchor_tag:
        return {"error": "Anchor tag not found"}
    # Extract the href attribute
    url = anchor_tag.get('href')
    if not url:
        return {"error": "URL not found in the anchor tag"}
    
    return url

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


def get_event_from_sanfran():
    main_page_url = "https://www.sanfran.co.nz/whats-on"
    page = 1
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            article["event_description"] = scrape_detail_page(article["event_url"])
            article["add_to_cart_url"] = scrape_cart_url(article["event_url"])
            save_to_supabase(article)

        page += 1
