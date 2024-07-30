import os
from openai import AsyncOpenAI
import asyncio
import ast
import json

client = AsyncOpenAI(
    api_key='',
)

obj_template = {
                'target_id': 'rotoruanui',
                'target_url': 'https://www.rotoruanui.nz',
                "event_title": "Government Gardens Guided Tours (2024)",
                "start_date" : "2024-06-25",
                "start_time" : "19:00:00.0000000",
                "end_date" : "2024-06-25",
                "end_time" : "21:00:00.0000000",
                "event_category": "Outdoors, Tours, Rotorua CBD, Family, Learning, Māori Culture",
                "event_description": "Rotorua Museum is fortunate to be housed in an area rich in history. Following the closure of the Bath House building in November 2016 for seismic strengthening, Rotorua Museum is offering free ‘outside the walls’ guided tours around Government Gardens. Take in the Museum grounds, learn about the old Bath house days and some of the interesting history of battles, buildings and the Government Gardens which were transformed from, as the Victorians said, “a wilderness of scrub, hot pools and geyser” into an oasis of charm. Call or email Julie, see below, to book your tour. Wear good walking shoes and clothing suitable for the weather. Tours depart from the top of the stairs in front of the Bath House in Government Gardens – weather dependent. Daily Tours at 11am (Mon – Sat) and 11:30am on Sunday – NO TOUR Christmas Day Meet at the top of the steps in front of the Bath House Bookings are advised: julie.parsons@rotorualc.nz or call 027-2424-132 The walking tours are a great way to learn some of the lesser known stories and about the geothermal nature of the area. Tours are tailored to your interests, can take up to 1 – 1.5 hours and include the fascinating history of the area including historical buildings, gardens, art and Māori carvings. Tags / Keywords Outdoors Tours Rotorua CBD Family Learning Māori Culture",
                "event_location": {
                    "title" : "event_title",
                    "street" : "Government Gardens 9 Queens Drive",
                    "region" : "Rotorua 3010",
                    "country" : "New Zealand"
                },
                "event_imgurl": "https://www.rotoruanui.nz/wp-content/uploads/2021/07/Rotorua-Government-Gardens-Tours-370x211.jpg",
                }



async def customize(object) -> None:

    chat_completion = await client.chat.completions.create(
        messages=[
            {
            "role": "system",
            "content": "Provide an object and I'll update its fields according to the provided template:{}- `start_date` and `start_time` are derived from `event_time`.- `event_location` fields (`title`, `street`, `region`, `country`) are updated with known info or looked up if unknown.- Fields inside `json_data` are prioritized over top-level fields in case of duplication.- Exclude all fields not mentioned in the template object.- If response is too long, send keys with omitted values.No additional explanations needed (e.x. '// Updated with assumed time' comments) , just the updated object. I don't need assumed data especially time. If any value of certain key is null or unknow, then fill empty string".format(obj_template)
            },
            {
                "role": "user",
                "content": "{}".format(object)
            }
            ],
        model="gpt-4o",
        max_tokens=4096,
        response_format={ "type": "json_object" }
    )
    temp = chat_completion.choices[0].message.content
    print('temp ============================>', temp)
    
    try:
        object_dict = ast.literal_eval(chat_completion.choices[0].message.content[temp.find('{'): temp.rfind('}')+1])
        return object_dict
    except ValueError as e:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Error converting the string to dictionary:", e)
        return None
# asyncio.run(call())

def customizable(temp):
    dict1 = {}
    for key, value in temp.items():
        if key in obj_template:
            dict1[key] = value
        else: continue
        
    return dict1