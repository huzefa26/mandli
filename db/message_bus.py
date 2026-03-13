# SQLite schema: messages(id, agent, role, content, timestamp)
'''
Currently reading - https://dev.to/breda/creating-a-simple-message-bus-episode-1-2hjm - Go, not needed.
Next, read https://bytepawn.com/writing-a-simple-python-async-message-queue-server.html - this is a pub/sub tcp server. msgs are not persisted.
'''
import os
import sqlite3

MESSAGES_DB_PATH = os.path.join(os.path.dirname(__file__), 'messages.db')

def get_connection():
    return sqlite3.connect(MESSAGES_DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        from_agent TEXT,
        to_agent TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
        )''')
    conn.commit()
    conn.close()

def insert_message(from_agent, to_agent, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO messages(from_agent, to_agent, content) VALUES(?,?,?)''',
        (from_agent, to_agent, content)
    )
    conn.commit()
    conn.close()

def get_messages(from_agent=None, to_agent=None):
    query = 'SELECT from_agent, to_agent, content, timestamp FROM messages'
    params = ()
    if from_agent is not None and to_agent is not None:
        query += ' WHERE from_agent=? AND to_agent=?'
        params = (from_agent, to_agent)
    elif from_agent is not None:
        query += ' WHERE from_agent=?'
        params = (from_agent, )
    elif to_agent is not None:
        query += ' WHERE to_agent=?'
        params = (to_agent, )
    query += ' ORDER BY timestamp DESC'
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    yield from cursor
    conn.close()
