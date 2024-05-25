import psycopg2
from datetime import date

class EventModel:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='user', user='user', password='123', host='localhost', port=5432)
        self.cursor = self.conn.cursor()

    def get_events_today(self):
        today = date.today()
        self.cursor.execute("SELECT * FROM events WHERE startDate::date = %s;", (today,))
        return self.cursor.fetchall()

    def get_brief_month(self):
        self.cursor.execute("SELECT DISTINCT startDate FROM events;")
        return self.cursor.fetchall()

    def complete_event(self, event_id: int):
        self.cursor.execute("UPDATE events SET iscompleted = TRUE WHERE id = %s;", (event_id,))
        self.conn.commit()

    def get_events_by_date(self, query_date: str):
        self.cursor.execute("SELECT * FROM events WHERE startDate::date = %s;", (query_date,))
        return self.cursor.fetchall()
        
    def add_event(self, user_id, event):
        self.cursor.execute("INSERT INTO events (userId, eventTitle, startDate, endDate, location, description, status, isCompleted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (user_id, event.title, event.start, event.end, event.location, event.description, event.status, False))
        self.conn.commit()

    def complete_event(self, event_id):
        self.cursor.execute("UPDATE events SET isCompleted = TRUE WHERE id = %s", (event_id,))
        self.conn.commit()

    def get_event_by_id(self, event_id):
        self.cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        return self.cursor.fetchone()
    
