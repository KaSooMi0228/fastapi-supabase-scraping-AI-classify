import requests
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client
import os

# Function to scrape the main page and get article details
def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.select('.items .item'):
        title_element = item.select_one('h3.item-title.h3')
        if title_element:
            title = title_element.get_text(strip=True)
            news_url = item.select_one('.item-title-wrap')['href']
            date_text = item.select_one('time[itemprop="datePublished"]')
            if date_text:
                date_span = date_text.find('span', {'class': 'date'})
                if date_span:
                    date = date_span.text
                    parsed_date = datetime.strptime(date, "%d %b %Y")
                    output_date = parsed_date.strftime("%d-%m-%Y")
                    
                    content = " ".join([p.get_text(strip=True) for p in item.select('.item-text p')])

                    articles.append({
                        'target_id': 'totarastreetNews',
                        'target_url': 'https://totarastreet.co.nz/news',
                        'title': title,
                        'news_url': news_url,
                        'content': content,
                        'date': output_date
                    })
    
    return articles

# Function to scrape the detail page for image URL
def scrape_detail_page(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    img_url = soup.select_one('.grid-image img')['src'] if soup.select_one('.grid-image img') else None
    return img_url

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Function to check for duplication and insert if not duplicated
def save_to_supabase(article):
    title = article['title']
    date = article['date']
    existing_article = supabase.table('News').select("*").eq('title', title).eq('date', date).execute()

    if not existing_article.data:
        response = supabase.table('News').insert(article).execute()
        print(f"Inserted: {response.data}")
    else:
        print(f"Duplicate found for {title}")

def get_news_from_totarastreet():
    main_page_url = "https://totarastreet.co.nz/news"
    articles = scrape_main_page(main_page_url)

    for article in articles:
        article['imageUrl'] = scrape_detail_page(article['news_url'])
        save_to_supabase(article)