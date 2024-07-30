import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://www.neckofthewoods.co.nz/events"
target_id = 'neckofthewoods'
target_url = 'https://www.neckofthewoods.co.nz/'

def get_events_from_neckofthewoods():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            articles = soup.find_all('article', class_='eventlist-event eventlist-event--upcoming eventlist-event--multiday')
            if not articles:
                break
            for article in articles:
                event_title = article.find('h1', class_='eventlist-title').get_text(strip=True).upper()

                # Extract event location and map link
                event_location = article.find('li', class_='eventlist-meta-item eventlist-meta-address event-meta-item').get_text(strip=True)
                event_location_map = article.find('li', class_='eventlist-meta-item eventlist-meta-address event-meta-item').find('a')['href']
                event_location_full = f"{event_location}, {event_location_map}"

                # Extract event time
                event_time_start_month = article.find('div', class_='eventlist-datetag-startdate--month').get_text(strip=True)
                event_time_start_day = article.find('div', class_='eventlist-datetag-startdate--day').get_text(strip=True)
                event_time_end = article.find('div', class_='eventlist-datetag-enddate').get_text(strip=True)
                event_time = f"{event_time_start_month} {event_time_start_day} {event_time_end}"

                # Extract event image URLs
                img_tag = article.find('img', {'data-image': True})
                event_img_url = img_tag['srcset'] if img_tag else ""

                # Extract event description
                description_blocks = article.find_all('div', class_='sqs-block-content')
                event_description = ""
                for block in description_blocks:
                    event_description += block.get_text(strip=True) + "\n"
                event_description = event_description.strip()

                # Extract event URL
                event_url = article.find('div', class_='sqs-block-button-container').find('a')['href']
                
                if not check_duplicate_data({'target_id': target_id, 'event_title': event_title, 'event_time':event_time}):
                    result.append({
                        'target_id': target_id,
                        'target_url': event_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': 'Show',
                        'event_time': event_time,
                        'event_imgurl': event_img_url,
                        'event_location': event_location_full,
                        'json_data': {
                            'target_id': target_id,
                            'target_url': event_url,
                            'event_title': event_title,
                            'event_description': event_description,
                            'event_category': 'Show',
                            'event_time': event_time,
                            'event_imgurl': event_img_url,
                            'event_location': event_location_full,
                        }
                    })
                else: continue
        else: break
        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_neckofthewoods())