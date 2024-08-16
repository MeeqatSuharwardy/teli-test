#The is_dnc_date function checks if a given date matches any entry in the "DNC_dates" table column "dateid".
#The is_within_time_range function now includes the check to skip execution on Sundays and DNC dates before processing the time range comparison.
#The script ensures that it does not execute on Sundays or DNC dates listed in the "DNC_dates" table, in addition to the existing restrictions based on time zones and states.
# To run the app, use the command: uvicorn script_name:app --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import pytz
import asyncpg
import asyncio

app = FastAPI()

class Timestamp(BaseModel):
    unix_time: int
    state: str

async def get_timezone(state: str):
    conn = await asyncpg.connect(user='your_user', password='your_password',
                                 database='your_database', host='your_host')
    timezone_info = await conn.fetchrow("SELECT zone FROM timezones WHERE state = $1", state)
    await conn.close()
    return timezone_info['zone'] if timezone_info else None

async def get_profile_times(state: str):
    conn = await asyncpg.connect(user='your_user', password='your_password',
                                 database='your_database', host='your_host')
    row = await conn.fetchrow("SELECT starttime, endtime FROM profile WHERE state = $1", state)
    await conn.close()
    return row

async def is_dnc_date(date_to_check: str):
    conn = await asyncpg.connect(user='your_user', password='your_password',
                                 database='your_database', host='your_host')
    dnc_date = await conn.fetchval("SELECT dateid FROM DNC_dates WHERE dateid = $1", date_to_check)
    await conn.close()
    return dnc_date is not None

def is_within_time_range(unix_time: int, state: str):
    state_timezone = asyncio.run(get_timezone(state))
    
    if state_timezone:
        est = pytz.timezone(state_timezone)
        utc_time = datetime.fromtimestamp(unix_time, tz=timezone.utc)
        state_time = utc_time.astimezone(est)

        # Check if the current day is Sunday (0 is Monday, 6 is Sunday) or a DNC date
        if state_time.weekday() == 6 or asyncio.run(is_dnc_date(state_time.strftime('%Y-%m-%d'))):
            return False

        start_time, end_time = asyncio.run(get_profile_times(state))
        
        if not start_time or not end_time:
            start_time = state_time.replace(hour=8, minute=0, second=0, microsecond=0)
            end_time = state_time.replace(hour=21, minute=0, second=0, microsecond=0)
        else:
            start_time = datetime.strptime(start_time['starttime'], "%H:%M:%S")
            end_time = datetime.strptime(end_time['endtime'], "%H:%M:%S")

        return start_time <= state_time <= end_time
    else:
        return False

@app.post("/check-time/")
async def check_time(timestamp: Timestamp):
    if is_within_time_range(timestamp.unix_time, timestamp.state):
        return {"message": f"The given time is within the range of specified start and end times or defaults to 8 AM to 9 PM in {timestamp.state} time zone on a non-Sunday and non-DNC date."}
    else:
        raise HTTPException(status_code=400, detail=f"The given time is outside the specified time range or defaults to 8 AM to 9 PM in {timestamp.state} time zone, or it's a Sunday or a DNC date.")

# To run the app, use the command: uvicorn script_name:app --reload