import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data

Server_API_URL = "https://thistlehall.org.nz/activities"
target_id = 'thistlehall'
target_url = 'https://thistlehall.org.nz/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def get_events_from_thistlehall():
    result = []
    while True:
        raw = requests.get(Server_API_URL, headers=headers)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'html.parser')
            links = soup.find_all('div', class_='view-mode-full ds-2col-stacked clearfix')
            if not links:
                break
            for link in links:
                # Get the event title
                event_title = link.find('div', class_='field--name-node-title').get_text(strip=True)
                # Extract the event time
                event_time = link.find('div', class_='field--name-field-time').find('div', class_='field__item').get_text(strip=True)
                # Extract the event location
                event_location = link.find('div', class_='field--name-field-where').find('div', class_='field__item').get_text(strip=True)
                # Extract the event description
                description_parts = []
                for field in link.find_all('div', class_='group-footer')[0].find_all('div', class_='field'):
                    label = field.find('div', class_='field__label').get_text(strip=True).upper()
                    item = field.find('div', class_='field__item').get_text(" ", strip=True)
                    description_parts.append(f"{label}\n{item}")

                event_description = "\n\n".join(description_parts)
                
                if not check_duplicate_data({'target_id': target_id, 'event_title': event_title, "event_time": event_time}):
                    # Save data in the database
                    result.append({
                        'target_id': target_id,
                        'target_url': target_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': 'Show',
                        'event_time': event_time,
                        'event_imgurl': '',
                        'event_location': event_location,
                        'json_data': {
                            'target_id': target_id,
                            'target_url': target_url,
                            'event_title': event_title,
                            'event_description': event_description,
                            'event_category': 'Show',
                            'event_time': event_time,
                            'event_imgurl': '',
                            'event_location': event_location,
                        }
                    })
                    print(f'+++++++++++++ {result}')
                    print(f'-----{event_title}------', result[-1])
                else:
                    continue
        else:
            break
        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_thistlehall())