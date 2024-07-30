import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import time
import json

Server_API_URL = "https://wunderbar.co.nz/whats-on/"
target_id = 'wunderbar'
target_url = 'https://wunderbar.co.nz/'

def get_events_from_wunderbar():
    result = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    session = requests.Session()
    session.headers.update(headers)

    retries = 3
    retry_delay = 5  # seconds

    while True:
        try:
            response = session.get(Server_API_URL, timeout=10)  # 10 seconds timeout
            print(f'^^^^^^^^^^^^ {response}')
        except requests.exceptions.RequestException as e:
            retries -= 1
            if retries > 0:
                print(f"Request failed, retrying in {retry_delay} seconds... ({retries} retries left)")
                time.sleep(retry_delay)
                continue
            else:
                print(f"Request failed after multiple retries: {e}")
                break

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f'***************   {soup}')
            articles = soup.find_all('div', class_='fl-row fl-row-fixed-width fl-row-bg-none')
            print(f'***************   {articles}')
            if not articles:
                break
            for index, article in enumerate(articles):
                if index % 2 == 1:
                    print(f'@@@@@@@@@@@@@@@@@@@@@@@@ {article}')
                    event_title = article.find('h1', class_='p-name summary value-title').get_text(strip=True)

                    # Extracting the event time
                    event_time = article.find('h4').get_text(strip=True)

                    # Extracting the event description
                    description_div = article.find('div', class_='fl-module fl-module-rich-text fl-node-6iork9yv48ha')
                    event_description = description_div.get_text(separator='\n', strip=True)

                    # Extracting the event image URL
                    event_img_url = article.find('img', class_='fl-photo-img')['src']

                    # Extracting the event URL
                    event_url = article.find('a', class_='fl-button')['href']
                    
                    if not check_duplicate_data({'target_id': target_id, 'event_time': event_time}):
                        result.append({
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
                        })
                        print(f'+++++++++++++ {result}')
                    else:
                        continue
        else:
            print(f"Failed to retrieve data: HTTP {response.status_code}")
            break

        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_wunderbar())