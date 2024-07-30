import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://www.theincubator.co.nz/whats-on"
target_id = 'theincubator'
target_url = 'https://www.theincubator.co.nz/whats-on'

def get_events_from_theincubator():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            links = soup.find_all('a', class_='DjQEyU')
            if not links:
                break
            for link in links:
                # Get the href attribute
                event_url = link.get('href')
                # Get the text content
                event_title = link.text

                raw = requests.get(event_url)
                if raw.status_code == 200:
                    soup = BeautifulSoup(raw.content, 'lxml')

                    # Initialize variables
                    event_time = None
                    event_location = None
                    event_description = None
                    event_img_url = None

                    date_element = soup.find('p', {'data-hook': 'event-full-date'})
                    if date_element:
                        event_time = date_element.text

                    location_element = soup.find('p', {'data-hook': 'event-full-location'})
                    if location_element:
                        event_location = location_element.text

                    about_section = soup.find('div', {'data-hook': 'about-section-text'})
                    if about_section:
                        event_description = about_section.get_text(separator="\n").strip()

                    img_element = soup.find('img', {
                        'style': 'width: 979px; height: 552px; object-fit: contain; object-position: center center;',
                        'fetchpriority': 'high'
                    })
                    if img_element:
                        event_img_url = img_element['src']

                # Ensure values are not None
                event_title = event_title or ""
                event_time = event_time or ""

                if not check_duplicate_data({'target_id': target_id, 'event_title': event_title, 'event_time': event_time}):

                    # Save data in database
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
                    print(f'-----{event_title}------', result[-1])
                else:
                    continue
        else:
            break
        print(f'page-----------------------------------------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_theincubator())