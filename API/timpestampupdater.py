

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from sqlmodel import select
from datetime import datetime
import pytz

from .models import tblCategory
from .database import Session, engine
from .auth import database_save

scheduler = AsyncIOScheduler()
Almaty = pytz.timezone("Asia/Almaty")

def get_current_period():
    time = datetime.now(Almaty)
    if 5 <= time.hour < 13:
        return "morning"
    if 13 <= time.hour < 17:
        return "afternoon"
    if 17 <= time.hour < 24:
        return "evening"
    if time.hour < 5: 
        return "night"


@scheduler.scheduled_job(CronTrigger(hour="8,12,17,21", timezone=Almaty))
def reset_period():
    with Session(engine) as session:
        categories = session.exec(select(tblCategory)).all()
        
        for category in categories:
            category.PeopleClicked = 0
            database_save(session=session, dbinstance=category)
        
        


        
