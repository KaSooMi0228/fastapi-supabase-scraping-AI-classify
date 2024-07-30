import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://skycityauckland.co.nz/whats-on"
target_id = 'skycityauckland'
target_url = 'https://skycityauckland.co.nz/whats-on'

def get_events_from_skycityauckland():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            links = soup.find_all('a', class_='hover whats-on-flex item thisclass')
            if not links:
                break
            for link in links:
                # Get the href attribute
                event_url = link.get('href')
                # Get the text content
                event_title = link.find('h3').get_text()

                raw = requests.get(event_url)
                if raw.status_code == 200:
                    soup = BeautifulSoup(raw.content, 'lxml')

                    # Initialize variables
                    event_time = None
                    event_location = None
                    event_description = None
                    event_img_url = None

                    event_time_div = soup.find('div', class_='h3')
                    event_time = soup.find('p', class_='lead').text + " " + event_time_div.text.strip()
                    # Extract event location
                    event_location = soup.find('div', itemprop='location').find('span', itemprop='name').text
                    # Extract event description
                    description_paragraphs = soup.find_all('p')[1:4]
                    event_description = "\n\n".join(p.text for p in description_paragraphs)

                    
                    if not check_duplicate_data({'target_id': target_id, 'event_title':event_title, "event_time": event_time}):
                        result.append({
                            'target_id': target_id,
                            'target_url': event_url,
                            'event_title': event_title,
                            'event_description': event_description,
                            'event_category': 'Show',
                            'event_time': event_time,
                            'event_imgurl': event_img_url,
                            'event_location': event_location,
                            'json_data': {
                                'target_id': target_id,
                                'target_url': event_url,
                                'event_title': event_title,
                                'event_description': event_description,
                                'event_category': 'Show',
                                'event_time': event_time,
                                'event_imgurl': event_img_url,
                                'event_location': event_location,
                            }
                        })
                        print(f'++++++++++++++++++ {result}')
                    print(f'--------------------{event_title}------', result[-1])
                else:
                    continue
        else:
            break
        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_skycityauckland())