import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://galatos.co.nz/"
target_id = 'galatos'
target_url = 'https://galatos.co.nz/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_events_from_galatos():
    result = []
    while True:
        raw = requests.get(Server_API_URL, headers=headers)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            links = soup.find_all('a', class_='woocommerce-loop-product__link')
            if not links:
                break
            for link in links:
                # Get the href attribute
                event_url = link.get('href')
                
                raw = requests.get(event_url, headers=headers)
                if raw.status_code == 200:
                    soup = BeautifulSoup(raw.content, 'html.parser')
                    # Extracting the event time
                    event_time = soup.select_one('.custom_ticket_venue_header .venue .doors').text.strip()
                    # Extracting the event location
                    event_location = soup.select_one('.custom_ticket_venue_header .venue .addr').text.strip()
                    # Extracting the event image URL
                    event_img_url = soup.select_one('.woocommerce-product-gallery__image img')['src']
                    # Extracting the event title
                    event_title = soup.select_one('.custom_ticket_event_header .title h1').text.strip()
                    event_title += ", " + soup.select_one('.custom_ticket_event_header .title h2').text.strip()
                    # Extracting the event description
                    description_paragraphs = soup.select('.summary.entry-summary p')
                    event_description = "\n\n".join(p.text.strip() for p in description_paragraphs)

                    if not check_duplicate_data({'target_id': target_id, 'event_title':event_title, "event_time": event_time}):

                        #save data in database
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
                        print(f'++++++++++++++++ {result}')
                        print(f'-----{event_title}------', result[-1])
                    else:
                        continue
        else:
            break
        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_galatos())