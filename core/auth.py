import hashlib
from core.database import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, hash_password(password)))

        conn.commit()
        return True

    except:
        return False

    finally:
        conn.close()


def login_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, password
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    user_id, stored_password = user

    if stored_password == hash_password(password):
        return user_id

    return None


def is_admin(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT is_admin
        FROM users
        WHERE id = ?
    """, (user_id,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return False

    return bool(row[0])