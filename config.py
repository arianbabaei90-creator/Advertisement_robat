import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
CHANNEL_ID = os.getenv("CHANNEL_ID")
WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_TOKEN = os.getenv("WP_TOKEN")
WP_USERNAME=os.getenv("WP_USERNAME")
WP_PASSWORD=os.getenv("WP_PASSWORD")
UPLOADS = "uploads"
WP_TIMEOUT = 30
CLASH_API_TOKEN=os.getenv("CLASH_API_TOKEN")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "clashone")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

os.makedirs(UPLOADS, exist_ok=True)
def is_admin(tg_id: int) -> bool: return tg_id in ADMIN_IDS