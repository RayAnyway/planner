import telebot
from icalevents.icalevents import events as sync
from telebot import types
import psycopg2
import schedule
import time
from datetime import datetime, timedelta
import threading


token = '5000021070:AAGTdn4oTXc5w50so3LYVOi-zfab-tneSxo/test'

bot = telebot.TeleBot(token)

conn = psycopg2.connect(dbname='user', user='user', password='123',
                        host='localhost', port=5432)
cursor = conn.cursor()  

# DB SCHEMA
# CREATE TABLE events (
#   id SERIAL PRIMARY KEY,
#   userId INTEGER NOT NULL,
#   eventTitle VARCHAR(255) NOT NULL,
#   startDate TIMESTAMP NOT NULL,
#   endDate TIMESTAMP NOT NULL,
#   location VARCHAR(255),
#   description TEXT,
#   attendees TEXT[],
#   status VARCHAR(20),
#   priority INTEGER,
#   created TIMESTAMP NOT NULL,
#   lastModified TIMESTAMP NOT NULL,
#   organizer VARCHAR(255),
#   recurrenceRule TEXT,
#   timeZone VARCHAR(50),
#   url TEXT,
#   classification VARCHAR(20),
#   transparency VARCHAR(20),
#   tags TEXT[],
#   isCompleted BOOLEAN DEFAULT FALSE
# );

help_message = """
📅 /sync <ссылка на календарь> - синхронизировать события на неделю
📅 /today - показать события на сегодня
📅 /complete - завершить событие
📅 /create - создать событие
"""

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Я - бот планнер. Я помогу тебе синхронизировать события из календаря и создавать новые. Для получения списка команд введи /help')
    

@bot.message_handler(content_types=['text'])
def sync_calendar(message):
    if message.text == '/id':
        bot.send_message(message.chat.id, message.chat.id)
    elif message.text == '/feedback':
        msg = bot.send_message(message.chat.id, 'Напишите отзыв, и мы обязательно станем лучше:')
        bot.register_next_step_handler(msg, process_feedback_step)
    elif message.text == '/help':
        bot.send_message(message.chat.id, help_message)
    elif message.text[:5] == '/sync':
        link = message.text[6:]
        es = sync(link)

        bot.send_message(message.chat.id, 'ℹ️ Синхронизуем события на неделю:')

        for e in es:
            msg = e.summary + '\n'
            msg += '📅 ' + e.start.strftime('%d.%m.%Y') + '\n'
            msg += '🕐 ' + e.start.strftime('%H:%M') + ' - ' + e.end.strftime('%H:%M') + '\n'

            if e.location:
                msg += '📍 ' + e.location + '\n'
            
            cursor.execute("INSERT INTO events (userId, eventTitle, startDate, endDate, location, description, attendees, status, priority, created, lastModified, organizer, recurrenceRule, timeZone, url, classification, transparency) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now(), %s, %s, %s, %s, %s, %s)", (message.chat.id, e.summary, e.start, e.end, e.location, e.description, None, e.status, None, None, None, None, e.url, None, None))
            bot.send_message(message.chat.id, msg, disable_notification=True)
            
        conn.commit()

        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        webAppTest = types.WebAppInfo("https://planner-webview.vercel.app/")

        item1 = types.KeyboardButton('Открыть события', web_app=webAppTest)
        markup.add(item1)

        bot.send_message(message.chat.id, '✅ Синхронизация завершена', reply_markup=markup)
    elif message.text[:7] == '/create':
        msg = bot.send_message(message.chat.id, 'Введите название события:')
        bot.register_next_step_handler(msg, process_name_step)
    elif message.text[:6] == '/today':
        today = datetime.today().strftime('%Y-%m-%d')
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

        msg = ''
        for e in events:
            msg += e['eventtitle'] + '\n'
            msg += '📅 ' + e['startdate'].strftime('%d.%m.%Y') + '\n'
            msg += '🕐 ' + e['startdate'].strftime('%H:%M') + ' - ' + e['enddate'].strftime('%H:%M') + '\n'

            if e['location']:
                msg += '📍 ' + e['location'] + '\n'

            msg += '\n'

        bot.send_message(message.chat.id, msg)
    elif message.text[:9] == '/complete':
        today = datetime.today().strftime('%Y-%m-%d')
        cursor.execute(
            """
            SELECT * FROM events WHERE startDate::date = %s AND iscompleted = FALSE;
            """,
            (today,)
        )

        events = []
        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            event = dict(zip(columns, row))
            events.append(event)
            
        markup=types.InlineKeyboardMarkup(row_width=1)

        for e in events:
            start_time = e['startdate'].strftime('%H:%M')
            markup.add(types.InlineKeyboardButton(f"[{start_time}] {e['eventtitle']}", callback_data=f"cb_{e['id']}"))
        
        bot.send_message(message.chat.id, 'Выберите событие для завершения:', reply_markup=markup)
        

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data[:3] == 'cb_':
            id = call.data[3:]
            cursor.execute(
                """
                UPDATE events SET iscompleted = TRUE WHERE id = %s;
                """,
                (id,)
            )
            conn.commit()

            bot.send_message(call.message.chat.id, '🚀 Событие завершено!')

admin_id = 2200647378

def process_feedback_step(message):
    try:
        chat_id = message.chat.id
        feedback = message.text
        bot.send_message(chat_id, 'Спасибо за отзыв! Мы обязательно учтем его.')
        bot.send_message(admin_id, f'Отзыв от пользователя {chat_id}:\n{feedback}')
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Попробуйте еще раз.')

class Event:
    def __init__(self, name):
        self.name = name
        self.date = None
        self.time = None
        self.location = None
        self.description = None
        self.attendees = None
        self.status = None
        self.priority = None
        self.organizer = None
        self.recurrenceRule = None
        self.timeZone = None
        self.url = None
        self.classification = None
        self.transparency = None
        self.tags = None
        self.notifyMinutes = None
        
event_dict = {}

def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    event = Event(name)
    event_dict[chat_id] = event
    msg = bot.send_message(chat_id, 'Введите дату события в формате ДД.ММ.ГГГГ:')
    bot.register_next_step_handler(msg, process_date_step)

def process_date_step(message):
    try:
        chat_id = message.chat.id
        date = message.text
        if (len(date) != 10):
            msg = bot.send_message(chat_id, 'Неверный формат даты. Введите дату события в формате ДД.ММ.ГГГГ:')
            bot.register_next_step_handler(msg, process_date_step)
            return
        event = event_dict[chat_id]
        event.date = date
        msg = bot.send_message(chat_id, 'Введите время события в формате ЧЧ:ММ:')
        bot.register_next_step_handler(msg, process_time_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Попробуйте еще раз.')

# Convert HH:MM to posgtres timestamp
def convert_time(time):
    return datetime.strptime(time, "%H:%M")

def process_time_step(message):
    try:
        chat_id = message.chat.id
        time = message.text
        if (len(time) != 5):
            msg = bot.send_message(chat_id, 'Неверный формат времени. Введите время события в формате ЧЧ:ММ:')
            bot.register_next_step_handler(msg, process_time_step)
            return
        event = event_dict[chat_id]
        event.time = time
        msg = bot.send_message(chat_id, 'Введите теги для события, через пробел:')
        bot.register_next_step_handler(msg, process_tags_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Попробуйте еще раз.')
        print(e)
        
def process_tags_step(message):
    try:
        chat_id = message.chat.id
        tags = message.text
        event = event_dict[chat_id]
        event.tags = tags.split(' ')
        msg = bot.send_message(chat_id, 'Введите описание события:')
        bot.register_next_step_handler(msg, process_description_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Попробуйте еще раз.')
        
def process_description_step(message):
    try:
        chat_id = message.chat.id
        description = message.text
        event = event_dict[chat_id]
        event.description = description
        msg = bot.send_message(chat_id, 'За сколько минут напомнить о событии?')
        bot.register_next_step_handler(msg, process_notify_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Попробуйте еще раз.')
        print(e)


def notify_event(event):
    chat_id = event['chat_id']
    bot.send_message(chat_id, 'Event is starting soon')

def process_notify_step(message):
    try:
        chat_id = message.chat.id
        notify = message.text
        event = event_dict[chat_id]
        event.notifyMinutes = notify

        event.date = datetime.strptime(event.date + ' ' + event.time, '%d.%m.%Y %H:%M')
        cursor.execute("INSERT INTO events (userId, eventTitle, startDate, endDate, location, description, attendees, status, priority, created, lastModified, organizer, recurrenceRule, timeZone, url, classification, transparency, isCompleted, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now(), %s, %s, %s, %s, %s, %s, %s, %s)", (message.chat.id, event.name, event.date, event.date, event.location, event.description, event.attendees, event.status, event.priority, event.organizer, event.recurrenceRule, event.timeZone, event.url, event.classification, event.transparency, False, event.tags,))
        conn.commit()
        bot.send_message(chat_id, 'Событие создано')
        
        notify_time = event.date - timedelta(minutes=int(event.notifyMinutes))

        # Schedule the notification
        schedule.every().day.at(notify_time.strftime('%H:%M')).do(notify_event, event=event)
    except Exception as e:
        bot.reply_to(message, 'Ошибка. Попробуйте еще раз.')
        print(e)

def run_schedule():
    print('[i] Starting scheduler')
    while True:
        schedule.run_pending()
        time.sleep(1)

# Create a new thread for the scheduler
scheduler_thread = threading.Thread(target=run_schedule)

# Start the scheduler thread
scheduler_thread.start()

print('[i] Bot started')
bot.infinity_polling()