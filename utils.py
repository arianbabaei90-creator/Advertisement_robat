import os
from aiogram.types import FSInputFile
import config
import db
from bot_instance import bot

def user_display(u):
    if not u: return "ناشناس"
    return f"@{u['username']}" if u['username'] else f"ID: {u['tg_id']}"

async def notify_admins(text):
    for aid in config.ADMIN_IDS:
        try: await bot.send_message(aid, text)
        except: pass

async def publish_telegram(ad):
    seller = db.get_user_by_id(ad["user_id"])
    caption = f"🛒 آگهی جدید\n{ad['title']}\n\n{ad['description']}\n\nقیمت: {ad['price']:,} تومان\nفروشنده: {user_display(seller)}"
    try:
        if ad["photo_path"] and os.path.exists(ad["photo_path"]):
            msg = await bot.send_photo(config.CHANNEL_ID, FSInputFile(ad["photo_path"]), caption=caption)
        else:
            msg = await bot.send_message(config.CHANNEL_ID, caption)
        db.set_ad_channel_msg_id(ad["id"], msg.message_id)
        return True
    except Exception as e:
        print("TG Error:", e)
        return False

def publish_wordpress(ad):
    import requests
    try:
        url = f"{config.WP_URL}/wp-json/wp/v2/posts" # یا آدرس سفارشی خودت
        headers = {"Authorization": f"Bearer {config.WP_TOKEN}"}
        data = {"title": ad["title"], "content": ad["description"], "status": "publish"}
        r = requests.post(url, json=data, headers=headers, timeout=10)
        if r.status_code in (200, 201):
            db.set_ad_wp_post_id(ad["id"], r.json().get("id"))
            return True
        return False
    except:
        return False