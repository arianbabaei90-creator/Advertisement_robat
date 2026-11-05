from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
import config, db
from bot_instance import bot
from keyboard import admin_ad_keyboard, main_menu_inline
from stats import RejectFSM
from utils import user_display, publish_telegram, publish_wordpress

router = Router()

# برای کلیک روی دکمه شیشه‌ای پنل مدیریت
@router.callback_query(F.data == "menu_admin")
async def cb_menu_admin(call: CallbackQuery):
    if not config.is_admin(call.from_user.id): 
        await call.answer("شما ادمین نیستید!", show_alert=True)
        return
    await call.answer()
    await call.message.delete()
    await show_pending(call.message)

# برای دستور /admin
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not config.is_admin(message.from_user.id): return
    await show_pending(message)

# تابع مشترک برای نمایش آگهی‌های در انتظار
async def show_pending(message: Message):
    total = db.count_pending_ads()
    if total == 0:
        await message.answer("آگهی در انتظار تأیید وجود ندارد.", reply_markup=main_menu_inline(True))
        return
    rows = db.get_pending_ads()
    await message.answer(f"آگهی‌های در انتظار: {total}")
    for ad in rows:
        seller = db.get_user_by_id(ad["user_id"])
        caption = f"#{ad['id']} — {ad['title']}\nقیمت: {ad['price']:,}\nفروشنده: {user_display(seller)}"
        if ad["photo_path"]:
            await message.answer_photo(FSInputFile(ad["photo_path"]), caption=caption, reply_markup=admin_ad_keyboard(ad))
        else:
            await message.answer(caption, reply_markup=admin_ad_keyboard(ad))
    
    # دکمه بازگشت به منو
    from keyboard import back
    await message.answer("برای بازگشت کلیک کنید:", reply_markup=back())

@router.callback_query(F.data.startswith("approve:"))
async def cb_approve(call: CallbackQuery):
    if not config.is_admin(call.from_user.id): return
    ad_id = int(call.data.split(":")[1])
    ad = db.get_ad(ad_id)
    
    await call.answer("در حال انتشار...")
    tg_ok = await publish_telegram(ad)
    wp_ok = publish_wordpress(ad)
    
    if tg_ok and wp_ok:
        db.update_ad_status(ad_id, "approved")
        try:
            await call.message.edit_caption(caption=call.message.caption + "\n\n✅ منتشر شد.")
        except:
            await call.message.edit_text(text=call.message.text + "\n\n✅ منتشر شد.")
        
        seller = db.get_user_by_id(ad["user_id"])
        if seller:
            try:
                await bot.send_message(seller["tg_id"], f"آگهی شما #{ad_id} تایید و منتشر شد.")
            except Exception as e:
                print("Could not send message to seller:", e)
    else:
        await call.message.answer("خطا در انتشار. دوباره تلاش کنید.")

@router.callback_query(F.data.startswith("reject:"))
async def cb_reject(call: CallbackQuery, state: FSMContext):
    if not config.is_admin(call.from_user.id): return
    ad_id = int(call.data.split(":")[1])
    await state.update_data(ad_id=ad_id)
    await call.message.answer("دلیل رد را بنویسید:")
    await state.set_state(RejectFSM.reason)

@router.message(RejectFSM.reason)
async def apply_reject(message: Message, state: FSMContext):
    data = await state.get_data()
    db.update_ad_status(data["ad_id"], "rejected", message.text)
    await message.answer("آگهی رد شد.")
    await state.clear()