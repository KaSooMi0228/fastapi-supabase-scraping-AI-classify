import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data

Server_API_URL = "https://www.bayvenues.co.nz/what-s-on"
target_id = 'bayvenues'
target_url = 'https://www.bayvenues.co.nz/what-s-on'

def get_events_from_bayvenues():
    result = []

    page = 1
    page_url = 'https://www.bayvenues.co.nz/search/event?q=&type=&date=&location=&site=default&sort=date_when&limit=6&page={}'
    page_response = requests.get(page_url.format(page))
    if page_response.status_code == 200:
        page_data = page_response.json()
        last_page = page_data.get('last_page', None)
    else:
        print("Failed to get the first page")
        return result

    while page <= last_page:
        print(f'Processing page: {page}')
        raw = requests.get(page_url.format(page))
        if raw.status_code == 200:
            page_data = raw.json()
            html_content = page_data['html']
            soup = BeautifulSoup(html_content, 'html.parser')
            events = soup.find_all('div', class_='w-full mb-4')
            for event_div in events:
                event_title = event_div.find('h2').text.strip()
                event_time = event_div.select_one('.card-details p:nth-of-type(1)').text.strip()
                event_location = event_div.select_one('.card-details p:nth-of-type(2)').text.strip()
                event_description = event_div.select_one('.card-details p:nth-of-type(3)').text.strip()
                event_img_url = event_div.find('img')['src']
                
                result.append({
                    'target_id': target_id,
                    'target_url': target_url,
                    'event_title': event_title,
                    'event_description': event_description,
                    'event_category': 'Show',
                    'event_time': event_time,
                    'event_imgurl': event_img_url,
                    'event_location': event_location,
                    'json_data': {
                        'target_id': target_id,
                        'target_url': target_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': 'Show',
                        'event_time': event_time,
                        'event_imgurl': event_img_url,
                        'event_location': event_location,
                    }
                })
                print(f'+++++++++++++++++ {result}')
            print(f'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Page {page} processed, {len(events)} events found.')
        else:
            print(f"Failed to get data from page {page}")
            break
        
        store_events_data(result)
        page += 1
        
    return result

if __name__ == '__main__':
    events = get_events_from_bayvenues()
    print(events)