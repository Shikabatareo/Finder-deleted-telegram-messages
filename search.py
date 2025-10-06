import sqlite3
from telethon import TelegramClient, events
from datetime import datetime
import asyncio
from dotenv import load_dotenv
import os
import vew


load_dotenv()


API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME')
                         
def init_db():
    try:
        conn = sqlite3.connect('deleted_messages.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deleted_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                chat_title TEXT,
                sender_id INTEGER,
                sender_username TEXT,
                sender_first_name TEXT,
                sender_last_name TEXT,
                message_id INTEGER,
                message_text TEXT,
                deletion_time TIMESTAMP
            )
        ''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS all_messages (
                message_id INTEGER,
                chat_id INTEGER,
                chat_title TEXT,
                sender_id INTEGER,
                sender_username TEXT,
                sender_first_name TEXT,
                sender_last_name TEXT,
                message_text TEXT,
                timestamp TIMESTAMP,
                PRIMARY KEY (message_id, chat_id)
                )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print('Не удалось инициализировать базу данных')
 

def save_deleted_message(chat_id, chat_title, sender_id, sender_username, sender_first_name, sender_last_name, message_id,message_text):
    try:
        conn=sqlite3.connect('deleted_messages.db')
        cursor = conn.cursor()
        cursor.execute('''
        
        INSERT INTO deleted_messages (chat_id, chat_title, sender_id, sender_username, sender_first_name, sender_last_name, message_id, message_text, deletion_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',(chat_id, chat_title, sender_id, sender_username, sender_first_name, sender_last_name, message_id, message_text, datetime.now()))
        conn.commit()
        conn.close()
        return True      
    except Exception as e:
        print('Ошибка сохранения в базу данных',e)
        return False


def save_all_message(message_id, chat_id, chat_title, sender_id, sender_username, sender_first_name, sender_last_name, message_text):
    try:
        conn=sqlite3.connect('deleted_messages.db')
        cursor = conn.cursor()
        cursor.execute('''
        
        INSERT OR REPLACE INTO all_messages 
            (message_id, chat_id, chat_title, sender_id, sender_username, sender_first_name, sender_last_name, message_text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',(chat_id, chat_title, sender_id, sender_username, sender_first_name, sender_last_name, message_id, message_text, datetime.now()))
        conn.commit()
        conn.close()
        return True      
    except Exception as e:
        print('Ошибка сохранения в базу данных',e)
        return False

def get_message_from_db(message_id, chat_id):
    try:
        conn = sqlite3.connect('deleted_messages.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM all_messages WHERE message_id = ? AND chat_id = ?
        ''', (message_id, chat_id))
        result = cursor.fetchone()
        conn.close()
        
        if result: 
            return {
                'chat_id': result[1],
                'chat_title': result[2],
                'sender_id': result[3],
                'sender_username': result[4],
                'sender_first_name': result[5],
                'sender_last_name': result[6],
                'message_text': result[7]
            }
        return None
    except Exception as e:
        print('Ошибка поиска сообщения в базе', e)
        return None

recent_messages = {}

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.MessageDeleted)
async def deleted_messages(event):
    try:
        saved_count = 0
        for message_id in event.deleted_ids:
            message_data = recent_messages.get(message_id)
            #print(message_data)
            if not message_data:
                message_data = get_message_from_db(message_id, event.chat_id)
            if message_data:
                chat_id = message_data['chat_id']
                chat_entity = message_data.get('chat_entity')
                #print(chat_entity)

                if chat_entity:
                    if hasattr(chat_entity, 'title'):
                        continue
                    else:
                        sender_first_name = getattr(chat_entity,'first_name', '')
                        sender_last_name = getattr(chat_entity, 'last_name', '')
                        sender_username = getattr(chat_entity, 'username', '')
                        chat_title = f'{sender_first_name} {sender_last_name}'.strip()
                        print(chat_title)
                        if sender_username:
                            chat_title+= f' (@{sender_username})'
                        if not chat_title:
                            chat_title = f'User {chat_id}'
                else:
                    chat_title = f'User {chat_id}'
                if save_deleted_message(chat_id=chat_id,chat_title=chat_title, sender_id=message_data['sender_id'],sender_username = message_data['sender_username'], sender_first_name=sender_first_name,sender_last_name=sender_last_name,message_id=message_id, message_text=message_data['message_text']):
                    saved_count+=1
                    print(f'Сохранено сообщений  {saved_count}')
                else: 
                    print('Сообщение не сохраненно')
    except Exception as e:
        print('Ошибка в поиске удаленного сообщения',e)
        


@client.on(events.NewMessage)
async def new_message_handler(event):
    try:
        if event.is_private:
            chat = await event.get_chat()
            sender = await event.get_sender()
            #print(sender)

            message_text = event.message.text
            if not message_text:
                if event.message.media:
                    message_text = '[Media]'
                else:
                    message_text = '[Void]'
            if hasattr(chat, 'title'):
                chat_title = chat.title
            else:
                sender_first_name = getattr(chat, 'first_name', '')
                sender_last_name = getattr(chat, 'last_name', '')
                sender_username = getattr(chat, 'username', '')
                chat_title = f'{sender_first_name} {sender_last_name}'.strip()
                if sender_username:
                    chat_title += f' (@{sender_username})'
                if not chat_title:
                    chat_title = f'User {event.chat_id}'
                message_data = {
                'chat_id': event.chat_id,
                'chat_entity': chat,
                'message_text': message_text,
                'sender_id': sender.id if sender else None,
                'sender_username': getattr(sender, 'username', ''),
                'sender_first_name': getattr(sender, 'first_name', ''),
                'sender_last_name': getattr(sender, 'last_name', ''),
                'timestamp': datetime.now()
                }
                recent_messages[event.message.id] = message_data
                
                save_all_message(
                    message_id=event.message.id,
                    chat_id=event.chat_id,
                    chat_title=chat_title,
                    sender_id=sender.id if sender else None,
                    sender_username=getattr(sender, 'username', ''),
                    sender_first_name=getattr(sender, 'first_name', ''),
                    sender_last_name=getattr(sender, 'last_name', ''),
                    message_text=message_text
            )
                
            #print(recent_messages)
    except Exception as e:
        print('Ошибка получения нового сообщения')
        
async def main():
    await client.start()
    print('Бот запущен и отслеживает сообщения')
    me = await client.get_me()
    print(f'Авторизован {me.first_name} - {me.username}')

    await client.run_until_disconnected()
if __name__ == '__main__':
    init_db()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен')
    except Exception as e:
        print('Критическа ошибка: {e}')

