import requests
from bs4 import BeautifulSoup
from Utils.supa_base import check_duplicate_data, store_events_data

Server_API_URL = "https://www.arollingstone.co.nz/gig-guide"
target_id = 'arollingstone'
target_url = 'https://www.arollingstone.co.nz/'

def get_events_from_arollingstone():
    result = []
    
    raw = requests.get(Server_API_URL)
    if raw.status_code == 200:
        soup = BeautifulSoup(raw.content, 'lxml')
        p_elements = soup.find_all('p', style='white-space:pre-wrap;')
        
        if not p_elements:
            print("No <p> elements found with the specified style.")
            return result
        
        for p_element in p_elements:
            strong_text = ""
            rest_of_text = ""
            
            strong_tag = p_element.find('strong')
            if strong_tag:
                strong_text = strong_tag.get_text()
                rest_of_text = p_element.get_text().replace(strong_text, '').strip()
            else:
                rest_of_text = p_element.get_text().strip()
            
            if not check_duplicate_data({'target_id': target_id, 'event_time': strong_text}):
                event_data = {
                    'target_id': target_id,
                    'target_url': target_url,
                    'event_title': target_id,
                    'event_description': rest_of_text,
                    'event_category': 'GIG',
                    'event_time': strong_text,
                    'event_imgurl': '',
                    'event_location': 'New Zealand',
                    'json_data': {
                        'target_id': target_id,
                        'target_url': target_url,
                        'event_title': target_id,
                        'event_description': rest_of_text,
                        'event_category': 'GIG',
                        'event_time': strong_text,
                        'event_imgurl': '',
                        'event_location': 'New Zealand',
                    }
                }
                result.append(event_data)
                print(f'Event added: {event_data}')
            else:
                print(f'Duplicate event found: {strong_text}')
        
        store_events_data(result)
    else:
        print(f"Failed to retrieve content from {Server_API_URL}. Status code: {raw.status_code}")

    return result

if __name__ == '__main__':
    events = get_events_from_arollingstone()
    print(f'Total events: {len(events)}')