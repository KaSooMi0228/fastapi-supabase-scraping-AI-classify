import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://www.powerstation.net.nz/"
target_id = 'powerstation'
target_url = 'https://www.powerstation.net.nz/'

def get_events_from_powerstation():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            articles = soup.find_all('article', class_='node node--announcement node--tour node--tour--announcement announcement')
            if not articles:
                break
            for article in articles:
                title_tag = article.find('h2')
                event_title = title_tag.get_text(strip=True) if title_tag else ""
                time_tag = article.find('time')
                event_time = time_tag.get_text(strip=True) if time_tag else ""
                description_tags = article.find('div', class_='announcement-text').find_all('p')
                event_description = ' '.join(tag.get_text(strip=True) for tag in description_tags)
                img_tag = article.find('img')
                event_img_url = img_tag.get('src') if img_tag else ""
                
                if not check_duplicate_data({'target_id': target_id, 'event_title': event_title, 'event_time':event_time}):
                    result.append({
                        'target_id': target_id,
                        'target_url': target_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': 'Show',
                        'event_time': event_time,
                        'event_imgurl': event_img_url,
                        'event_location': 'New Zealand',
                        'json_data': {
                            'target_id': target_id,
                            'target_url': target_url,'event_title': event_title,
                            'event_description': event_description,
                            'event_category': "Show",
                            'event_time': event_time,
                        }
                    })
                else: continue
        else: break
        print(f'page--------------------------------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_powerstation())