import os
import time
import httpx
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, FSInputFile, 
    InlineKeyboardMarkup, InlineKeyboardButton
)

import config
import db
from bot_instance import bot
from keyboard import games_menu_inline, main_menu_inline, cancel_inline, user_ad_keyboard
from stats import AdFSM, EditFSM  # ایمپورت به بالا منتقل شد
from utils import notify_admins, user_display # ایمپورت به بالا منتقل شد

router = Router()

# ================= ثبت آگهی جدید =================

@router.callback_query(F.data == "menu_add_ad")
async def ask_game(call: CallbackQuery, state: FSMContext):
    await call.answer() 
    await state.clear()
    
    await call.message.edit_text(
        "لطفاً نوع آگهی خود را از لیست زیر انتخاب کنید:", 
        reply_markup=games_menu_inline()
    )
    await state.set_state(AdFSM.game)

@router.callback_query(AdFSM.game, F.data.startswith("game_"))
async def get_game_inline(call: CallbackQuery, state: FSMContext):
    await call.answer()
    
    game_map = {
        "game_coc": "اکانت کلش آف کلنز",
        "game_cr": "اکانت کلش رویال",
        "game_tribe": "قبیله کلش آف کلنز",
        "game_cod": "اکانت کالاف دیوتی موبایل",
        "game_ml": "اکانت موبایل لجندز",
        "game_ff": "اکانت فری فایر"
    }
    
    game_name = game_map.get(call.data)
    
    if game_name:
        await state.update_data(game=game_name)
        await call.message.edit_text(f"شما {game_name} را انتخاب کردید.")
        await call.message.answer(
            "لطفن تگ اکانت را وارد کنید.\nنمونه تگ:\n#ZOLPGPMX\n\nاز درون بازی می‌توانید این تگ را کپی کنید.",
            reply_markup=cancel_inline()
        )
        await state.set_state(AdFSM.title)

@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    try:
        await call.message.delete()
    except:
        pass
    await call.message.answer(
        "به منوی اصلی برگشتید.", 
        reply_markup=main_menu_inline(config.is_admin(call.from_user.id))
    )

@router.message(AdFSM.title)
async def get_title(message: Message, state: FSMContext):
    user_input = message.text.strip()
    if user_input.startswith('/'): return

    player_tag = user_input.replace("#", "").strip().upper()
    data = await state.get_data()
    game_name = data.get("game", "")

    if "کلش آف کلنز" in game_name:
        wait_msg = await message.answer("⏳ در حال بررسی تگ در سرور بازی...")
        url = f"https://api.clashofclans.com/v1/players/%23{player_tag}"
        headers = {
            "Authorization": f"Bearer {config.CLASH_API_TOKEN}",
            "Accept": "application/json"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

            if response.status_code == 200:
                await wait_msg.delete()
                await state.update_data(title=player_tag)
                await message.answer("✅ تگ شما تایید شد.\nحالا لطفاً توضیحات آگهی خود را بنویسید:", reply_markup=cancel_inline())
                await state.set_state(AdFSM.desc)
            elif response.status_code == 404:
                await wait_msg.delete()
                await message.answer("❌ تگ وارد شده در بازی کلش آف کلنز وجود ندارد!\nلطفاً تگ صحیح اکانت خود را وارد کنید:", reply_markup=cancel_inline())
            elif response.status_code == 403:
                await wait_msg.delete()
                await message.answer("⚠️ خطای ارتباط با سرور بازی (IP یا توکن). لطفاً بعداً تلاش کنید.", reply_markup=cancel_inline())
                print("API Error 403: Check CLASH_API_TOKEN or Allowed IP")
            else:
                await wait_msg.delete()
                await message.answer("⚠️ خطای نامشخص رخ داد.", reply_markup=cancel_inline())
        except Exception as e:
            await wait_msg.delete()
            await message.answer("⚠️ خطا در برقراری ارتباط با سرورهای بازی.", reply_markup=cancel_inline())


@router.message(AdFSM.desc)
async def get_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await message.answer("قیمت را به تومان و فقط عدد وارد کنید:", reply_markup=cancel_inline())
    await state.set_state(AdFSM.price)

@router.message(AdFSM.price)
async def get_price(message: Message, state: FSMContext):
    raw = (message.text or "").strip().replace(",", "")
    if not raw.isdigit():
        await message.answer("فقط عدد مثبت وارد کنید. مثلاً: 850000", reply_markup=cancel_inline())
        return
    await state.update_data(price=int(raw))
    await message.answer("عکس آگهی را ارسال کنید:", reply_markup=cancel_inline())
    await state.set_state(AdFSM.photo)

@router.message(AdFSM.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    file = await bot.get_file(message.photo[-1].file_id)
    path = os.path.join(config.UPLOADS, f"{message.from_user.id}_{int(time.time())}.jpg")
    await bot.download_file(file.file_path, destination=path)
    await state.update_data(photo_path=path)
    
    data = await state.get_data()
    preview = (
        f"👁 پیش‌نمایش آگهی شما:\n\n"
        f"🎮 بازی: {data['game']}\n"
        f"🏷 تگ: {data['title']}\n"
        f"📝 توضیحات: {data['desc']}\n"
        f"💰 قیمت: {data['price']:,} تومان\n\n"
        "آیا آگهی را تایید می‌کنید؟"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تایید و ارسال برای ادمین", callback_data="confirm_ad")],
        [InlineKeyboardButton(text="❌ لغو", callback_data="back_to_main")]
    ])
    await message.answer_photo(FSInputFile(path), caption=preview, reply_markup=kb)
    await state.set_state(AdFSM.preview)

@router.callback_query(AdFSM.preview, F.data == "confirm_ad")
async def confirm_ad(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    user = db.get_or_create_user(call.from_user.id)
    ad_id = db.insert_ad(user["id"], data['game'], data['title'], data['desc'], data['price'], data['photo_path'])
    
    await call.message.delete() 
    await call.message.answer(
        f"آگهی شما با شناسه #{ad_id} ثبت شد و در انتظار تایید ادمین است.",
        reply_markup=main_menu_inline(config.is_admin(call.from_user.id))
    )
    await state.clear()
    await notify_admins(f"آگهی جدید #{ad_id} در انتظار تأیید است.")

# ================= ویرایش قیمت آگهی =================

@router.callback_query(F.data.startswith("edit_price:"))
async def cb_edit_price(call: CallbackQuery, state: FSMContext):
    await call.answer()
    ad_id = int(call.data.split(":")[1])
    await state.update_data(edit_ad_id=ad_id)
    await call.message.answer("لطفاً قیمت جدید را به تومان و فقط عدد وارد کنید:", reply_markup=cancel_inline())
    await state.set_state(EditFSM.value)

@router.message(EditFSM.value)
async def apply_new_price(message: Message, state: FSMContext):
    raw = (message.text or "").strip().replace(",", "")
    if not raw.isdigit():
        await message.answer("فقط عدد مثبت وارد کنید. مثلاً: 850000", reply_markup=cancel_inline())
        return
        
    new_price = int(raw)
    data = await state.get_data()
    ad_id = data.get("edit_ad_id")
    
    db.update_ad_price(ad_id, new_price)
    
    ad = db.get_ad(ad_id)
    if ad and ad["status"] == "approved" and ad["channel_msg_id"]:
        seller = db.get_user_by_id(ad["user_id"])
        new_caption = f"🛒 آگهی جدید\n{ad['title']}\n\n{ad['description']}\n\nقیمت: {new_price:,} تومان\nفروشنده: {user_display(seller)}"
        try:
            await bot.edit_message_caption(
                chat_id=config.CHANNEL_ID,
                message_id=ad["channel_msg_id"],
                caption=new_caption
            )
        except Exception as e:
            print("Error editing channel msg:", e)

    await message.answer(f"✅ قیمت آگهی شما با موفقیت به {new_price:,} تومان تغییر کرد.", 
        reply_markup=main_menu_inline(config.is_admin(message.from_user.id))
    )
    await state.clear()

# ================= مدیریت آگهی‌ها =================

@router.callback_query(F.data == "menu_manage_ads")
async def show_my_ads(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    user = db.get_or_create_user(call.from_user.id)
    rows = db.get_ads_by_user(user["id"])
    
    if not rows:
        await call.message.edit_text(
            "شما هنوز آگهی ثبت نکرده‌اید.", 
            reply_markup=main_menu_inline(config.is_admin(call.from_user.id))
        )
        return
        
    await call.message.delete() 
    
    for ad in rows:
        caption = f"#{ad['id']} — {ad['title']}\nقیمت: {ad['price']:,} تومان\nوضعیت: {ad['status']}"
        kb = user_ad_keyboard(ad)
        if ad["photo_path"] and os.path.exists(ad["photo_path"]):
            await call.message.answer_photo(FSInputFile(ad["photo_path"]), caption=caption, reply_markup=kb)
        else:
            await call.message.answer(caption, reply_markup=kb)
            
    from keyboard import back
    await call.message.answer("برای بازگشت به منو کلیک کنید:", reply_markup=back())

# ================= حذف آگهی =================
@router.callback_query(F.data.startswith("del:"))
async def cb_del(call: CallbackQuery):
    await call.answer()
    ad_id = int(call.data.split(":")[1])
    
    ad = db.get_ad(ad_id)
    user = db.get_or_create_user(call.from_user.id)
    if not ad or ad["user_id"] != user["id"]:
        await call.answer("دسترسی ندارید.", show_alert=True)
        return
        
    db.update_ad_status(ad_id, "deleted")
    await call.answer("آگهی با موفقیت حذف شد.", show_alert=True)
    await call.message.delete()