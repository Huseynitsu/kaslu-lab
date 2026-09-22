import uuid
from core.database import get_connection


def create_session(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    token = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO sessions (user_id, token)
        VALUES (?, ?)
    """, (user_id, token))

    conn.commit()
    conn.close()

    return token


def get_user_by_token(token):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id
        FROM sessions
        WHERE token = ?
    """, (token,))

    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None


def delete_session(token):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM sessions
        WHERE token = ?
    """, (token,))

    conn.commit()
    conn.close()