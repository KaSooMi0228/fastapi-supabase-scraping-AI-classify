import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data
import json

Server_API_URL = "http://www.cabana.net.nz/"
target_id = 'cabana'
target_url = 'http://www.cabana.net.nz/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_events_from_cabana():
    result = []
    while True:
        raw = requests.get(Server_API_URL, headers=headers)
        if raw.status_code == 200:
            soup = BeautifulSoup(raw.content, 'lxml')
            links = soup.find_all('div', class_='ev2page-col')
            if not links:
                break
            for link in links:
                day = link.find('div', class_='ev2page-day')
                month = link.find('div', class_='ev2page-month')
                year = link.find('div', class_='ev2page-year')
                time = link.find('div', class_='ev2page-hour')
                weekday = link.find('div', class_='ev2page-week')

                day = day.text.strip() if day else "N/A"
                month = month.text.strip() if month else "N/A"
                year = year.text.strip() if year else "N/A"
                time = time.text.strip() if time else "N/A"
                weekday = weekday.text.strip() if weekday else "N/A"

                event_time = f"{time}, {day} {month.upper()} {year}, {weekday.upper()}"

                # Extracting the event title
                event_title_tag = link.find('h2', class_='ev2page-title')
                event_title = event_title_tag.a.text.strip() if event_title_tag and event_title_tag.a else "N/A"

                # Extracting the event image URL
                event_img_tag = link.find('div', class_='ev2page-cover')
                event_img_url = event_img_tag.img['src'] if event_img_tag and event_img_tag.img else "N/A"

                # Extracting the event URL
                event_url = event_title_tag.a['href'] if event_title_tag and event_title_tag.a else ""

                # Initialize event_description with a default value
                event_description = "Description not available."

                if event_url:
                    raw = requests.get(event_url)
                    if raw.status_code == 200:
                        soup1 = BeautifulSoup(raw.content, 'lxml')

                        # Extract event details safely
                        time_info = soup1.find('div', class_='evsng-cell-info')
                        time = time_info.get_text() if time_info else "N/A"

                        price_info = soup1.find_all('div', class_='evsng-cell-info')
                        price = price_info[1].get_text() if len(price_info) > 1 else "N/A"

                        title_info = soup1.find('h2', class_='event-title')
                        title = title_info.get_text() if title_info else "N/A"

                        description_info = soup1.find_all('p')
                        description = description_info[1].get_text() if len(description_info) > 1 else "N/A"

                        # Combine extracted information into a single string
                        event_description = f"Time - {time}\nPrice - {price}\n{title}\n{description}"

                if not check_duplicate_data({'target_id': target_id, 'event_title': event_title, "event_time": event_time}):

                    # Save data in database
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
                    print(f'+++++++++++++++++++ {result}')
                    result.append(event_data)
                    print(f'-----{event_title}------', result[-1])
                else:
                    continue
        else:
            break
        print(f'page--------result: {len(result)}')
        store_events_data(result)
    return result

if __name__ == '__main__':
    print(get_events_from_cabana())