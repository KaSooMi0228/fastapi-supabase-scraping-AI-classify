from fastapi import FastAPI, HTTPException, status, Query, Response  # type: ignore
from pydantic import BaseModel  # type: ignore
import os
from supabase import create_client, Client  # type: ignore
from dotenv import load_dotenv  # type: ignore
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from datetime import datetime
import uvicorn  # type: ignore
import threading
from Utils.convert import convert_func

# import each scraping function for all sites.
from visit.visitperth import get_events_from_visitperth
from visit.eventfinda import get_events_from_eventfinda
from visit.undertheradar import get_events_from_undertheradar
from visit.nzso import get_events_from_nzso
from visit.mytauranga import get_events_from_mytauranga
from visit.jazz import get_events_from_jazz
from visit.atc import get_events_from_atc
from visit.comedyfestival import get_events_from_comedyfestival
from visit.festivaloflights import get_events_from_festivaloflights
from visit.taupowinterfestival import get_events_from_taupowinterfestival
from visit.aaaticketing import get_events_from_aaaticketing
from visit.audiology import get_events_from_audiology
from visit.humanitix import get_events_from_humanitix
from visit.whakatance import get_events_from_whakatance
from visit.crankworx import get_events_from_crankworx
from visit.wellingtonnz import get_events_from_wellingtonnz
from visit.heartofthecity import get_events_from_heartofthecity
from visit.Rotoruanui import get_events_from_rotoruanui
from visit.hawkesbaynz import get_events_from_hawkesbaynz
from visit.venuesotautahi import get_events_from_venuesotautahi
from visit.dunedinnz import get_events_from_dunedinnz
from visit.northlandnz import get_events_from_northlandnz
from visit.livenation import get_events_from_livenation
from visit.frontiertouring import get_events_from_frontiertouring
from visit.voicesnz import get_events_from_voicesnz
from visit.nzopera import get_events_from_nzopera
from visit.aucklandlive import get_events_from_aucklandlive
from visit.dingdongloungenz import get_events_from_dingdongloungenz
from visit.totarastreet import get_events_from_totarastreet

from visit.powerstation import get_events_from_powerstation
from visit.theincubator import get_events_from_theincubator
from visit.bayvenues import get_events_from_bayvenues
from visit.skycityauckland import get_events_from_skycityauckland
from visit.galatos import get_events_from_galatos
from visit.hollywoodavondale import get_events_from_hollywoodavondale
from visit.thistlehall import get_events_from_thistlehall
from visit.cabana import get_events_from_cabana
from visit.wunderbar import get_events_from_wunderbar
from visit.crownrangelounge import get_events_from_crownrangelounge
from visit.valhallatavern import get_events_from_valhallatavern
from visit.arollingstone import get_events_from_arollingstone
from visit.tuningfork import get_events_from_tuningfork
from visit.neckofthewoods import get_events_from_neckofthewoods

# News
from visit.totarastreetNews import get_news_from_totarastreet
from visit.eventfindaNews import get_news_from_eventfinda
from visit.flicketNews import get_news_from_flicket
from visit.undertheradarNews import get_news_from_undertheradar
from visit.christchurchnzNews import get_news_from_christchurchnz
from visit.voicesnzNews import get_news_from_voicesnz
from visit.aucklandliveNews import get_news_from_aucklandlive
from visit.taupowinterfestivalNews import get_news_from_taupowinterfestival
from visit.comedyfestivalNews import get_news_from_comedyfestival
from visit.neckofthewoodsNews import get_news_from_neckofthewoods
from visit.rotoruanzNews import get_news_from_rotoruanz
from visit.greenstoneentertainmentNews import get_news_from_greenstoneentertainment
from visit.wellingtonnzNews import get_news_from_wellingtonnz

# Events
# from visit.forummelbourneEvent import get_event_from_forummelbourne
from visit.cornerhotelEvent import get_event_from_cornerhotel
from visit.thetotehotelEvent import get_event_from_thetotehotel
from visit.hotelesplanadeEvent import get_event_from_hotelesplanade
from visit.brisbaneEvent import get_event_from_brisbane
from visit.destinationgoldcoastEvent import get_event_from_destinationgoldcoast
from visit.bohmpresentsEvent import get_event_from_bohmpresents
from visit.ticketfairyEvent import get_event_from_ticketfairy
from visit.bigfanEvent import get_event_from_bigfan
from visit.yonderqtEvent import get_event_from_yonderqt
from visit.iticketEvent import get_event_from_iticket
from visit.eventbriteEvent import get_event_from_eventbrite
from visit.livenationEvent import get_event_from_livenation
from visit.tuningforkEvent import get_event_from_tuningfork
from visit.powerstationEvent import get_event_from_powerstation
from visit.sanfranEvent import get_event_from_sanfran
# -------- END --------

scheduler = BackgroundScheduler()
app = FastAPI()
load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))  # type: ignore


# HTTP Request
@app.get("/events/{target_id}")
def retrieve_event(target_id: str, offset: int, limit: int):
    print("target_id", target_id, "----", datetime.now())
    response = (
        supabase.from_("Event1")
        .select(
            "event_title, event_category, event_description, event_location, event_imgurl, start_date, start_time, end_date, end_time"
        )
        .eq("target_id", target_id)
        .offset(offset)
        .limit(limit)
        .execute()
    )
    return response


# HTTP Request
@app.get("/news/{target_id}")
def retrieve_news(target_id: str, offset: int, limit: int):
    print("target_id", target_id, "----", datetime.now())
    response = (
        supabase.from_("News")
        .select("title, imageUrl, content, date, news_url")
        .eq("target_id", target_id)
        .offset(offset)
        .limit(limit)
        .execute()
    )
    return response

# HTTP Request
@app.get("/event/{target_id}")
def retrieve_events(target_id: str, offset: int, limit: int):
    print("target_id", target_id, "----", datetime.now())
    response = (
        supabase.from_("guideEvent")
        .select(
            "event_title, event_category, event_description, event_location, event_imgurl, start_date, start_time, end_date, end_time"
        )
        .eq("target_id", target_id)
        .offset(offset)
        .limit(limit)
        .execute()
    )
    return response


# CronJob function
async def cronjob():
    # await get_events_from_visitperth()
    # await get_events_from_eventfinda()
    # await get_events_from_undertheradar()
    # await get_events_from_nzso()
    # await get_events_from_mytauranga()
    # await get_events_from_jazz()
    # await get_events_from_atc()
    # await get_events_from_comedyfestival()
    # await get_events_from_festivaloflights()
    # await get_events_from_taupowinterfestival()
    # await get_events_from_aaaticketing()
    # await get_events_from_audiology()
    # get_events_from_humanitix()
    # get_events_from_whakatance()
    # await get_events_from_hawkesbaynz()
    # await get_events_from_venuesotautahi()
    # get_events_from_dunedinnz()
    # get_events_from_northlandnz()
    # get_events_from_livenation()
    # await get_events_from_frontiertouring()
    # await get_events_from_voicesnz()
    # await get_events_from_nzopera()
    # await get_events_from_aucklandlive()
    # get_events_from_dingdongloungenz()
    # get_events_from_totarastreet()

    # get_events_from_powerstation()
    # get_events_from_theincubator()
    # get_events_from_bayvenues()
    # get_events_from_skycityauckland()
    # get_events_from_galatos()
    # get_events_from_hollywoodavondale()
    # await get_events_from_thistlehall()
    # get_events_from_cabana()
    # get_events_from_wunderbar()
    # get_events_from_crownrangelounge()
    # get_events_from_valhallatavern()
    # get_events_from_arollingstone()
    # get_events_from_tuningfork()
    # get_events_from_neckofthewoods()

    # get_news
    # get_news_from_totarastreet()
    # get_news_from_eventfinda()
    # get_news_from_flicket()
    # get_news_from_undertheradar()
    # get_news_from_christchurchnz()
    # get_news_from_voicesnz()
    # get_news_from_aucklandlive()
    # get_news_from_taupowinterfestival()
    # get_news_from_comedyfestival()
    # get_news_from_neckofthewoods()
    # get_news_from_rotoruanz()
    # get_news_from_greenstoneentertainment()
    # get_news_from_wellingtonnz()
    
    # get_event
    # get_event_from_forummelbourne()
    # get_event_from_cornerhotel()
    # get_event_from_thetotehotel()
    get_event_from_hotelesplanade()
    # get_event_from_brisbane()
    # get_event_from_destinationgoldcoast()
    # get_event_from_bohmpresents()
    # get_event_from_ticketfairy()
    # get_event_from_bigfan()
    # get_event_from_yonderqt()
    # get_event_from_iticket()
    # get_event_from_eventbrite()
    # get_event_from_livenation()
    # get_event_from_tuningfork()
    # get_event_from_powerstation()
    # get_event_from_sanfran()


if __name__ == "__main__":
    load_dotenv()
    print("mode:", os.getenv("DEVELOP_MODE"))

    if os.getenv("DEVELOP_MODE") == "production":
        print("Running Cronjob")
        scheduler.add_job(cronjob, "interval", minutes=60)
        scheduler.start()
    elif os.getenv("DEVELOP_MODE") == "develop":
        print("Running Thread")
        thread = threading.Thread(target=lambda: asyncio.run(cronjob()))
        thread.start()
    elif os.getenv("DEVELOP_MODE") == "database":
        success_count = asyncio.run(convert_func(target_id="theincubator"))  # type: ignore
        print(f"----success_count---{success_count}")

    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
