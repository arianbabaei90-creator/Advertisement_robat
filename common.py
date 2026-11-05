from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
import config, db
from keyboard import phone_request_keyboard, rules_inline_keyboard, main_menu_inline,back

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    db.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        "به ربات کلشاپ خوش آمدید 💙\n\nجهت تکمیل ثبت نام روی دکمه زیر کلیک کنید.",
        reply_markup=phone_request_keyboard()
    )

@router.message(F.contact)
async def handle_contact(message: Message, state: FSMContext):
    # ذخیره شماره
    db.get_or_create_user(message.from_user.id, phone=message.contact.phone_number)
    
    # پاک کردن کیبورد پایین صفحه
    msg = await message.answer("در حال بررسی...", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    
    # متن کامل هشدارها دقیقاً طبق عکس‌هایی که فرستادی
    rules_text = (
        "🔴 <b>مهم:</b> برای اطمینان از اصل بودن ادمین، شماره ما را درون مخاطبین خود ذخیره کنید، یا اینکه فقط روی این لینک ها کلیک کنید:\n"
        "t.me/+989\n"
        "t.me/+989\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🔴 <b>مهم:</b> اگر در تلگرام کسی پیام داد و خود را ادمین کلشاپ معرفی کرد تحویل ندهید و ابتدا از درون سایت چک میکنم.\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🔴 <b>مهم:</b> میدانم که ممکن است کلاهبردار ها شماره ادمین هارا روی اسم پروفایلشان در تلگرام قرار دهند.\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🔴 <b>مهم:</b> قبل از تحویل اکانتم، از درون سایت روی لینک ادمین کلیک میکنم.\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🔴 <b>مهم:</b> وقتی آگهی من فروش شود، برایم از سامانه پیامکی به شماره من پیام ارسال میشود.\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n\n"
        "🔴 <b>مهم:</b> ادمین کلشاپ به من پیام نمیدهد و در زمان تحویل خودم باید به ادمین پیام بدم.\n\n"
        "✔️ <b>لطفا جهت ادامه، قوانین را تایید کنید:</b>"
    )
    
    # ارسال متن با دکمه‌های شیشه‌ای تایید/رد
    await message.answer(rules_text, reply_markup=rules_inline_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "agree_rules")
async def cb_agree(call: CallbackQuery):
    await call.answer()
    await call.message.delete()
    is_admin = config.is_admin(call.from_user.id)
    await call.message.answer(
        "احراز شما با موفقیت انجام شد 💙\n\nاز منوی زیر انتخاب کنید:",
        reply_markup=main_menu_inline(is_admin)
    )

@router.callback_query(F.data == "reject_rules")
async def cb_reject(call: CallbackQuery):
    await call.answer("برای استفاده باید قوانین را بپذیرید.", show_alert=True)


@router.callback_query(F.data == "menu_rules")
async def show_rules(call: CallbackQuery):
    await call.answer()
    rules_text = (
        "✍️ <b>قوانین سایت کلشاپ:</b>\n\n"
        "۱. مسئولیت صحت اطلاعات اکانت با فروشنده است.\n"
        "۲. از معامله خارج از سیستم خودداری کنید.\n"
        "۳. در صورت کلاهبرداری، اکانت شما مسدود خواهد شد.\n\n"
        "برای بازگشت به منو روی دکمه زیر کلیک کنید:"
    )

    await call.message.edit_text(rules_text, parse_mode="HTML",reply_markup=back())
@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await call.message.delete()
    is_admin = config.is_admin(call.from_user.id)
    await call.message.answer("منوی اصلی:", reply_markup=main_menu_inline(is_admin))