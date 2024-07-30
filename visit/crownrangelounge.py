import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://crownrangelounge.co.nz/live-music%2Fgig-guide"
target_id = 'crownrangelounge'
target_url = 'https://crownrangelounge.co.nz/home'

def get_events_from_crownrangelounge():
    result = []
    while True:
        raw = requests.get(Server_API_URL)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            articles = soup.select('div[data-ux="GridCell"]')
            if not articles:
                break
            for article in articles:
                title_tag = article.find('h4', {'data-aid': 'MENU_SECTION0_ITEM1_TITLE'})
                if not title_tag:
                    continue

                title_text = title_tag.text.split(' - ')
                if len(title_text) < 2:
                    continue

                event_title = title_text[1]

                # Extract event time
                event_time = title_text[0]
                time_tag = article.find('p', text='8pm till 11pm')
                if time_tag:
                    event_time += ", " + time_tag.text

                # Extract event description
                desc_div = article.find('div', {'data-aid': 'MENU_SECTION0_ITEM1_DESC'})
                if desc_div:
                    description_paragraphs = desc_div.find_all('p')
                    event_description = "\n".join([para.text for para in description_paragraphs])
                else:
                    event_description = ""

                # Extract event image URL
                img_tag = article.find('img', {'data-aid': 'MENU_SECTION0_ITEM1_IMAGE'})
                if img_tag and 'src' in img_tag.attrs:
                    event_img_url = "https:" + img_tag['src']
                else:
                    event_img_url = ""

                # Extract event URL
                url_tag = article.find('a', {'data-aid': 'MENU_SECTION0_ITEM1_TITLE'})
                if url_tag and 'href' in url_tag.attrs:
                    event_url = url_tag['href']
                else:
                    event_url = ""

                if not check_duplicate_data({'target_id': target_id, 'event_title': event_title, 'event_time': event_time}):
                    result.append({
                        'target_id': target_id,
                        'target_url': target_url,
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
                    print(f'+++++++++++++++++++++ {result}')
                else:
                    continue
        else:
            break
        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_crownrangelounge())