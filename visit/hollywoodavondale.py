import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://ticketing.oz.veezi.com/sessions/?siteToken=fpnccxy3ma159g7z8a3e95asy8"
target_id = 'hollywoodavondale'
target_url = 'https://www.hollywoodavondale.nz/'

def get_events_from_hollywoodavondale():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            links = soup.find_all('div', class_='film')
            if not links:
                break
            for link in links:
                # Extract event title
                title_tag = link.find('h3', class_='title')
                event_title = title_tag.get_text(strip=True) if title_tag else 'No Title'

                # Extract event time and date
                date_tag = link.find('h4', class_='date')
                time_tag = link.find('time')
                event_date = date_tag.get_text(strip=True) if date_tag else 'No Date'
                event_time = time_tag.get_text(strip=True) if time_tag else 'No Time'
                event_datetime = f"{event_date}, {event_time}"

                # Extract event description
                censor_tag = link.find('span', class_='censor')
                description_tag = link.find('p', class_='film-desc')
                censor_rating = censor_tag.get_text(strip=True) if censor_tag else 'No Rating'
                description = description_tag.get_text(strip=True) if description_tag else 'No Description'
                event_description = f"{censor_rating}\n\n{description}"

                # Extract event image URL
                img_tag = link.find('img', class_='poster')
                if img_tag and 'src' in img_tag.attrs:
                    base_url = "https://ticketing.oz.veezi.com"
                    relative_img_url = img_tag['src']
                    event_img_url = base_url + relative_img_url.replace('&amp;', '&')
                else:
                    event_img_url = ''

                event_url_tag = link.find('a', href=True)
                if event_url_tag and 'href' in event_url_tag.attrs:
                    relative_event_url = event_url_tag['href']
                    event_url = base_url + relative_event_url
                else:
                    event_url = ''


                if not check_duplicate_data({'target_id': target_id, 'event_title':event_title, "event_time": event_time}):

                    #save data in database
                    result.append({
                        'target_id': target_id,
                        'target_url': event_url,
                        'event_title': event_title,
                        'event_description': event_description,
                        'event_category': 'Film',
                        'event_time': event_datetime,
                        'event_imgurl': event_img_url,
                        'event_location': "HollyWood",
                        'json_data': {
                            'target_id': target_id,
                            'target_url': event_url,
                            'event_title': event_title,
                            'event_description': event_description,
                            'event_category': 'Film',
                            'event_time': event_datetime,
                            'event_imgurl': event_img_url,
                            'event_location': "HollyWood",
                        }
                    })
                    print(f'+++++++++++++++++++ {result}')
                    print(f'-----{event_title}------', result[-1])
                else:
                    continue
        else:
            break
        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_hollywoodavondale())