import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://totarastreet.co.nz/events"
target_id = 'totarastreet'
target_url = 'https://totarastreet.co.nz/events'

def get_events_from_totarastreet():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            a_tags = soup.find_all('a', class_='item-title-wrap')
            if not a_tags:
                break
            for a_tag in a_tags:
                # Extract the detail URL from the <a> tag
                detail_url = a_tag.get('href')
                
                # Extract the event title from the <h3> tag
                title_tag = a_tag.find('h3', class_='item-title')
                event_title = title_tag.get_text(strip=True) if title_tag else ""
                
                # Extract the event date from the <time> tag
                date_tag = a_tag.find('time')
                event_time = date_tag.find('span', class_='date').get_text(strip=True) if date_tag else ""
                
                # Extract the author from the <span> tag inside the author-link span
                author_tag = a_tag.find('span', class_='author-link')
                event_author = author_tag.find('span').get_text(strip=True) if author_tag else ""
                
                # Extract the image URL from the <img> tag inside the <figure>
                img_tag = a_tag.find('img')
                event_imgurl = img_tag.get('src').strip() if img_tag else ""
                
                if not check_duplicate_data({'target_id': target_id, 'event_time': event_time}):
                    raw1 = requests.get(detail_url)
                    if raw1.status_code == 200:
                        soup1 = BeautifulSoup(raw1.content, 'lxml')
                        description_div = soup1.find('div', class_='grid-text')
                        description_tags = description_div.find_all('p')
                        event_description = '\n'.join(tag.get_text(strip=True) for tag in description_tags)
                        
                        # Extract the location from all <a> tags within <div> elements with class "grid-btn"
                        location_divs = soup1.find_all('div', class_='grid-btn')
                        event_location = '\n'.join(a_tag.get_text(strip=True) for div in location_divs for a_tag in div.find_all('a'))
                        
                        event_data = {
                            'target_id': target_id,
                            'target_url': detail_url,
                            'event_title': event_title,
                            'event_description': event_description,
                            'event_category': 'Show',
                            'event_time': event_time,
                            'event_imgurl': event_imgurl,
                            'event_location': event_location,
                            'json_data': {
                                'target_id': target_id,
                                'target_url': target_url,
                                'event_title': event_title,
                                'event_description': event_description,
                                'event_category': 'Show',
                                'event_author': event_author,
                                'event_time': event_time,
                                'event_imgurl': event_imgurl,
                                'event_location': event_location
                            }
                        }
                        result.append(event_data)
                else:
                    continue
        else:
            break
        print(f'Page result:---------------------------------------------- {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_totarastreet())