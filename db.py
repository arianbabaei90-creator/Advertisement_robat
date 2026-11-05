import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import config

_pool = None

def init_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1, maxconn=10,
            host=config.DB_HOST, port=config.DB_PORT, dbname=config.DB_NAME,
            user=config.DB_USER, password=config.DB_PASSWORD
        )

@contextmanager
def get_cursor():
    init_pool()
    conn = _pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        _pool.putconn(conn)

def get_or_create_user(tg_id, username=None, full_name=None, phone=None):
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO users (tg_id, username, full_name, phone_number)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tg_id) DO UPDATE SET
                username = COALESCE(EXCLUDED.username, users.username),
                full_name = COALESCE(EXCLUDED.full_name, users.full_name),
                phone_number = COALESCE(EXCLUDED.phone_number, users.phone_number)
            RETURNING *
        """, (tg_id, username, full_name, phone))
        return cur.fetchone()

def get_user_by_id(user_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()

def insert_ad(user_id, game_category, title, description, price, photo_path):
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO ads (user_id, game_category, title, description, price, photo_path, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending') RETURNING id
        """, (user_id, game_category, title, description, price, photo_path))
        return cur.fetchone()["id"]

def get_ad(ad_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM ads WHERE id = %s", (ad_id,))
        return cur.fetchone()

def get_ads_by_user(user_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM ads WHERE user_id = %s AND status != 'deleted' ORDER BY id DESC", (user_id,))
        return cur.fetchall()

def get_pending_ads(limit=5, offset=0):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM ads WHERE status = 'pending' ORDER BY id ASC LIMIT %s OFFSET %s", (limit, offset))
        return cur.fetchall()

def count_pending_ads():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM ads WHERE status = 'pending'")
        return cur.fetchone()["c"]

def update_ad_status(ad_id, status, reason=None):
    with get_cursor() as cur:
        cur.execute("UPDATE ads SET status = %s, rejection_reason = %s WHERE id = %s", (status, reason, ad_id))

def set_ad_wp_post_id(ad_id, wp_id):
    with get_cursor() as cur:
        cur.execute("UPDATE ads SET wp_post_id = %s WHERE id = %s", (wp_id, ad_id))

def set_ad_channel_msg_id(ad_id, msg_id):
    with get_cursor() as cur:
        cur.execute("UPDATE ads SET channel_msg_id = %s WHERE id = %s", (msg_id, ad_id))

def update_ad_price(ad_id, new_price):
    with get_cursor() as cur:
        cur.execute("UPDATE ads SET price = %s WHERE id = %s", (new_price, ad_id))
async def get_db():
    global pool

    async with pool.get_cursor() as cur:
        yield cur
    