import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://www.valhallatavern.com/events-1"
target_id = 'valhallatavern'
target_url = 'https://www.valhallatavern.com/'

def get_events_from_valhallatavern():
    result = []
    raw = requests.get(Server_API_URL)
    if raw.status_code == 200:
        soup = BeautifulSoup(raw.content, 'lxml')
        articles = soup.find_all('article', class_='eventlist-event eventlist-event--upcoming eventlist-event--hasimg eventlist-hasimg')
        for article in articles:
            event_title = article.find('h1', class_='eventlist-title').get_text(strip=True)

            # Extract event time
            event_date = article.find('div', class_='eventlist-datetag-startdate--month').text
            event_day = article.find('div', class_='eventlist-datetag-startdate--day').text
            event_time_start = article.find('time', class_='event-time-localized-start').text
            event_time = f"{event_date} {event_day}, {event_time_start}"

            # Extract event description
            description_div = article.find('div', class_='image-subtitle-wrapper')
            description_paragraphs = description_div.find_all('p')
            event_description = "\n\n".join(p.get_text(strip=True) for p in description_paragraphs)

            # Extract event image URL with checks
            img_tag = article.find('img', class_='sqs-block-image-figure')
            if img_tag and 'src' in img_tag.attrs:
                event_img_url = img_tag['src']
            else:
                event_img_url = None  # or some default value

            # Extract event URL
            event_url = article.find('a', class_='eventlist-title-link')['href']
            event_url = target_url + event_url

            if not check_duplicate_data({'target_id': target_id, 'event_title': event_title, 'event_time': event_time}):
                event_data = {
                    'target_id': target_id,
                    'target_url': event_url,
                    'event_title': event_title,
                    'event_description': event_description,
                    'event_category': 'Show',
                    'event_time': event_time,
                    'event_imgurl': event_img_url,
                    'event_location': 'New Zealand',
                    'json_data': {
                        'target_id': target_id,
                        'target_url': event_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': 'Show',
                        'event_time': event_time,
                        'event_imgurl': event_img_url,
                        'event_location': 'New Zealand',
                    }
                }
                result.append(event_data)
                print(f'Added event: {event_data}')
            else:
                print(f'Duplicate event found: {event_title}')
    else:
        print(f'Failed to retrieve events page, status code: {raw.status_code}')
    
    # Store the events data
    if result:
        store_events_data(result)
        print(f'Stored {len(result)} events.')
    else:
        print('No new events to store.')

    return result

if __name__ == '__main__':
    events = get_events_from_valhallatavern()
    print(f'Total events retrieved: {len(events)}')