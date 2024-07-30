import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://www.dingdongloungenz.com/events-1"
target_id = 'dingdongloungenz'
target_url = 'https://www.dingdongloungenz.com/'

def get_events_from_dingdongloungenz():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            articles = soup.find_all('li', class_='LFRKo9 Lgwamt')
            if not articles:
                break
            for article in articles:
                event_title = article.select_one('[data-hook="ev-list-item-title"]').text.strip()
                event_time = article.select_one('[data-hook="date"]').text.strip()
                event_location = article.select_one('[data-hook="location"]').text.strip()
                event_img_url = article.select_one('wow-image img')['src']
                event_url = article.select_one('[data-hook="ev-rsvp-button"]')['href']
                event_description = article.select_one('[data-hook="ev-list-item-description"]').text.strip()
                
                if not check_duplicate_data({'target_id': target_id, 'event_time':event_time}):
                    result.append({
                        'target_id': target_id,
                        'target_url': event_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': 'DING DONG',
                        'event_time': event_time,
                        'event_imgurl': event_img_url,
                        'event_location': event_location,
                        'json_data': {
                            'target_id': target_id,
                            'target_url': event_url,
                            'event_title': event_title,
                            'event_description': event_description,
                            'event_category': 'DING DONG',
                            'event_time': event_time,
                            'event_imgurl': event_img_url,
                            'event_location': event_location,
                        }
                    })
                else: continue
        else: break
        print(f'page----------------------------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_dingdongloungenz())