from fastapi import FastAPI
from datetime import date
import psycopg2
from psycopg2.extensions import AsIs
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

conn = psycopg2.connect(dbname='user', user='user', password='123',
                        host='localhost', port=5432)
cursor = conn.cursor()  

app = FastAPI()

@app.get("/events/today")
def get_events_today():
    today = date.today()

    cursor.execute(
        """
        SELECT * FROM events WHERE startDate::date = %s;
        """,
        (today,)
    )

    events = []
    columns = [col[0] for col in cursor.description]
    for row in cursor.fetchall():
        event = dict(zip(columns, row))
        events.append(event)

    return events


"""Return an array of iso dates where there is atleast 1 event"""
@app.get("/events/brief-month")
def get_brief_month():
    cursor.execute(
        """
        SELECT DISTINCT startDate FROM events;
        """
    )

    dates = []
    for row in cursor.fetchall():
        dates.append(row[0].isoformat())

    return { "data": dates }
         
@app.post("/events/complete")
def complete_event(event_id: int):
    cursor.execute(
        """
        UPDATE events SET iscompleted = TRUE WHERE id = %s;
        """,
        (event_id,)
    )
    conn.commit()

    return { "success": True }

@app.get("/events/date/{date}")
def get_events_by_date(date: str):
    cursor.execute(
        """
        SELECT * FROM events WHERE startDate::date = %s;
        """,
        (date,)
    )

    events = []
    columns = [col[0] for col in cursor.description]
    for row in cursor.fetchall():
        event = dict(zip(columns, row))
        events.append(event)

    return events

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)