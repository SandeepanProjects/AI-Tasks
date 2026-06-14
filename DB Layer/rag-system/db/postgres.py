# db/postgres.py

import psycopg2
from config import POSTGRES_URL

conn = psycopg2.connect(POSTGRES_URL) # Creates PostgreSQL connection.
cursor = conn.cursor() # Creates SQL executor.

# Called after LLM generates answer.
def save_chat(user_id, query, response):
    cursor.execute("""
        INSERT INTO chat_history (user_id, query, response)
        VALUES (%s, %s, %s)
    """, (user_id, query, response))
    conn.commit()


def get_chat_history(user_id):
    cursor.execute("""
        SELECT query, response FROM chat_history
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))
    return cursor.fetchall()