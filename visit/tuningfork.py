import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "https://www.tuningfork.co.nz/whats-on?Page={}"
target_id = 'tuningfork'
target_url = 'https://www.tuningfork.co.nz/whats-on'

def get_events_from_tuningfork():
    result = []
    page = 1  # Initialize page here so it does not reset in the loop

    while page < 3:
        raw = requests.get(Server_API_URL.format(page))
        soup = BeautifulSoup(raw.text, 'lxml')  # Use raw.text instead of raw
        links = soup.find_all('li', class_='ns-lsp86a')
        if not links:
            break
        for link in links:
            event_title = link.find('p', class_='ns-1lo656q').text

            # Extract event time
            time_tag = link.find('time', class_='ns-rpxx7c')
            day = time_tag.find('span', class_='ns-1x6z45a').text
            month = time_tag.contents[2].strip()
            time = time_tag.find('span', class_='ns-irfbko').text.strip()
            day_name = time_tag.contents[0].strip()
            event_time = f"{time}, {month}{day} 2024, {day_name}"

            # Extract event image URL
            event_img_url = link.find('img', class_='ns-v7vbs9')['src']

            # Extract event URL
            base_url = "https://www.tuningfork.co.nz"
            event_url = base_url + link.find('a', class_='MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways prisma48 prisma41 event-ticket-link prisma34 ns-1i3v6r1')['href']
            
            raw = requests.get(event_url)
            if raw.status_code == 200:
                soup1 = BeautifulSoup(raw.content, 'lxml')

                content = soup1.find('section', class_='ns-1b51gyu')
                paragraphs = content.find_all('p')

                # Combine the text from all <p> tags into one string
                event_description = '\n\n'.join([p.get_text() for p in paragraphs])

                if not check_duplicate_data({'target_id': target_id, 'event_title':event_title, "event_time": event_time}):
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
                            'target_url': target_url,
                            'event_title': event_title,
                            'event_description': event_description,
                            'event_category': 'Show',
                            'event_time': event_time,
                            'event_imgurl': event_img_url,
                            'event_location': 'New Zealand',
                        }
                    })
                    print(f'+++++++++++++++ {result}')
                else: continue

        page += 1  # Increment the page number to fetch the next page
        print(f'page--------result: {len(result)}')
    store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_tuningfork())