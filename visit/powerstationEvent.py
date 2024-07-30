import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os
from urllib.parse import urljoin
import re
import json


# Function to scrape the main page and get article details
def scrape_main_page(url, page):
    response = requests.get(f"{url}&page={page}&_drupal_ajax=1&ajax_page_state%5Btheme%5D=powerstation&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=eJx1kOEOgyAMhF9I5JFIkarNoDUUZvb2c8ISl7g_5LjvUq6AdwkDgaMEC9od_TaAd-LnqhMUErYXfSBQtD7K9LjqUV9aMBmfgQPx0tlMGEPXSxQPsV8YnrScE8eEXIdNdsxa2nttIjBL5QkPXvQu4I8E5juiq-wmkpZf2Bv8eCwBx1USbsf2N6hIzeZa5V-mt2n_YD9LDk_CXe15jklCjd1yxDMxFXQ6ZYmxRczXNc19Ayfnn_8")
    json_response = json.loads(response.content)
    
    # Extract the HTML content from the JSON
    html_content = None
    for command in json_response:
        if command.get('command') == 'insert' and command.get('method') == 'replaceWith':
            html_content = command.get('data')
            break

    if not html_content:
        print("No HTML content found in the response.")
        return []

    # Parse the extracted HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    articles = []
    
    announcements = soup.find_all('article', class_='node--announcement')

    for announcement in announcements:
        # Extract the image URL
        image_div = announcement.find('div', class_='announcement-image')
        image_url = image_div.find('img')['src'] if image_div else None

        # Extract the announcement title
        title = announcement.find('h2').text.strip() if announcement.find('h2') else None

        # Extract the date of the event
        date_time = announcement.find('time')
        event_date = date_time.text.strip() if date_time else None

        # Extract the show and ticket info link
        ticket_info_link = announcement.find('a', class_='more-link')['href'] if announcement.find('a', class_='more-link') else None

        # Extract the announcement description
        description_div = announcement.find('div', class_='announcement-text')
        description = description_div.text.strip() if description_div else None

        articles.append(
            {
                "target_id": "powerstationEvent",
                "target_url": "https://www.powerstation.net.nz/",
                "event_title": title,
                "event_category": 'Show',
                "event_imgurl": image_url,
                "event_url": "https://www.powerstation.net.nz/",
                "start_date": event_date,
                "start_time" : "19:00:00.0000000",
                "end_date": event_date,
                "end_time": "00:00:00.0000000",
                "event_description": description,
                "event_ticket": ticket_info_link,
                "event_location": {
                    "title" : "",
                    "street" : "",
                    "region" : "",
                    "country" : "New Zealand"
                }
            }
        )

    return articles


# Function to scrape the detail page for image URL
def scrape_detail_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    article_div = soup.find("div", class_="event-rich-body w-richtext")
    if article_div:
        article_content = article_div.get_text(separator="\n").strip()
    else:
        article_content = None
        
    return article_content

def scrape_stime_page(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.content, "html.parser")

    time_div = soup.find_all('div', class_='event-details-item')[1]

    # Extract the time text from the span
    time_text = time_div.find('span').text.strip()

    # Extract the time part from the text
    time_match = re.search(r'\d{1,2}:\d{2} [apm]{2}', time_text)

    if time_match:
        time_str = time_match.group()
        # Convert time to 24-hour format and add microseconds
        from datetime import datetime
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        formatted_time = time_obj.strftime('%H:%M:%S.%f')
    
    return formatted_time

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


def get_event_from_powerstation():
    main_page_url = "https://www.powerstation.net.nz/views/ajax?_wrapper_format=drupal_ajax&view_name=ps_tours&view_display_id=block_announcements&view_args=&view_path=%2Fnode%2F1&view_base_path=shows%2Fcoming&view_dom_id=32addd6541669e3f10934a2628ae94af3113dc78ace1df9fa716a9e2e402d3ba&pager_element=0"
    page = 0
    while True:
        articles = scrape_main_page(main_page_url, page)
        if not articles:
            break

        for article in articles:
            save_to_supabase(article)

        page += 1
