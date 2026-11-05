from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- (فقط برای شماره موبایل - اجبار تلگرام) ---
def phone_request_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="ارسال شماره موبایل 📱", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

# --- منوی اصلی (شیشه‌ای) ---
def main_menu_inline(is_admin: bool = False):
    keyboard = [
        [InlineKeyboardButton(text="➕ افزودن آگهی تازه", callback_data="menu_add_ad")],
        [InlineKeyboardButton(text="🧑‍🎨 مدیریت آگهی‌ها و اصلاحیه قیمت", callback_data="menu_manage_ads")],
        [InlineKeyboardButton(text="✍️ قوانین سایت", callback_data="menu_rules")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(text="👑 پنل مدیریت", callback_data="menu_admin")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- قوانین ---
def rules_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✔️ خواندم و موافقم", callback_data="agree_rules")],
        [InlineKeyboardButton(text="❌ نخواندم و موافق نیستم", callback_data="reject_rules")]
    ])

# --- انتخاب بازی ---
def games_menu_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 اکانت کلش آف کلنز", callback_data="game_coc")],
        [InlineKeyboardButton(text="👑 اکانت کلش رویال", callback_data="game_cr")],
        [InlineKeyboardButton(text="⛺️ قبیله کلش آف کلنز", callback_data="game_tribe")],
        [InlineKeyboardButton(text="🔫 اکانت کالاف دیوتی", callback_data="game_cod")],
        [InlineKeyboardButton(text="⚔️ اکانت موبایل لجندز", callback_data="game_ml")],
        [InlineKeyboardButton(text="🔥 اکانت فری فایر", callback_data="game_ff")],
        [InlineKeyboardButton(text="🔙 برگشت به منو اصلی", callback_data="back_to_main")]
    ])
def user_ad_keyboard(ad):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ تغییر قیمت", callback_data=f"edit_price:{ad['id']}")],
        [InlineKeyboardButton(text="🗑 حذف آگهی", callback_data=f"del:{ad['id']}")]
    ])
# --- دکمه لغو در مراحل ثبت ---
def cancel_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ لغو و بازگشت", callback_data="back_to_main")]
    ])

#

# --- پنل ادمین ---
def admin_ad_keyboard(ad):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأیید", callback_data=f"approve:{ad['id']}"),
            InlineKeyboardButton(text="❌ رد", callback_data=f"reject:{ad['id']}")
        ]
    ])

def back():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به منو",callback_data="back_to_main")]
    ])

