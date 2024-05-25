from fastapi import APIRouter
from models.events import EventModel
from starlette.responses import JSONResponse

router = APIRouter()
event_model = EventModel()

@router.get("/events/today")
def get_events_today():
    rows = event_model.get_events_today()
    columns = [col[0] for col in event_model.cursor.description]
    events = [dict(zip(columns, row)) for row in rows]
    return JSONResponse(content={"events": events})

@router.get("/events/brief-month")
def get_brief_month():
    rows = event_model.get_brief_month()
    dates = [row[0].isoformat() for row in rows]
    return JSONResponse(content={"dates": dates})

@router.post("/events/complete")
def complete_event(event_id: int):
    event_model.complete_event(event_id)
    return JSONResponse(content={"success": True})

@router.get("/events/date/{date}")
def get_events_by_date(date: str):
    rows = event_model.get_events_by_date(date)
    columns = [col[0] for col in event_model.cursor.description]
    events = [dict(zip(columns, row)) for row in rows]
    return JSONResponse(content={"events": events})
