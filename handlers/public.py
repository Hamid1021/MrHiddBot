# handlers\public.py
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from config import OWNER_ID
from database.models import User, Permission, GeminiUsage
from utils.decorators import register_command
from utils.helpers import format_response, persian_numbers
from datetime import datetime
from pyrogram.handlers import MessageHandler


@register_command("start")
async def start_handler(client, message: Message):
    """دستور شروع کار با ربات"""
    welcome_text = f"""
سلام {message.from_user.first_name}!
به ربات هوشمند خوش آمدید ✨

برای مشاهده دستورات از /help استفاده کنید
    """
    await message.reply(welcome_text)


@register_command(["help", "راهنما", "راهنما بات"], "")
async def help_handler(client, message: Message):
    """نمایش راهنمای کامل ربات"""
    help_text = """
🌟 راهنمای کامل ربات 🌟

🔸 دستورات عمومی:
/start - شروع کار با ربات
/help - نمایش این راهنما
/ping - نمایش سلامت ربات
وضعیت - نمایش وضعیت حساب شما

🔸 دستورات جستجو:
/google [متن] - جستجوی گوگل
/g [متن] - جستجوی سریع

🔸 هوش مصنوعی Gemini:
هیدن [سوال] - پرسش از هوش مصنوعی
فارسیش - ترجمه متن (با ریپلای)
انگلیسیش - ترجمه به انگلیسی
ژاپنیش - ترجمه به ژاپنی

🔸 مدیریت کاربران:
کاربر ادمین [ریپلای] - ارتقا به ادمین
کاربر ویژه [ریپلای] - ارتقا به ویژه
کاربر عادی [ریپلای] - تنزل به کاربر عادی

🔸 مدیریت ربات:
بات روشن - روشن کردن ربات
بات خاموش - خاموش کردن ربات

📊 هر کاربر مجاز به ۲۰ درخواست روزانه است
    """
    await message.reply(help_text)


@register_command(["status", "وضعیت"], "")
async def status_handler(client, message: Message):
    """نمایش وضعیت کاربر و اطلاعات حساب"""
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user

    # دریافت اطلاعات سطح دسترسی
    perm = Permission.get_or_none(user_id=target.id)
    status_level = ("مالک 👑" if target.id == OWNER_ID else
                    "ادمین ⭐" if perm and perm.status == 2 else
                    "ویژه ✨" if perm and perm.status == 1 else "عادی 👤")

    # دریافت اطلاعات استفاده از Gemini
    today = datetime.now().date()
    gemini_usage = GeminiUsage.get_or_none((GeminiUsage.user_id == target.id)
                                           & (GeminiUsage.date == today))

    remaining_requests = max(0,
                             20 - (gemini_usage.count if gemini_usage else 0))

    # دریافت تعداد عکس‌های پروفایل
    try:
        photos_count = 0
        async for _ in client.get_chat_photos(target.id):
            photos_count += 1
    except Exception:
        photos_count = 0

    # ساخت لینک یوزرنیم
    username_link = f"@{target.username}" if target.username else "ندارد"
    if target.username:
        username_link = f'<a href="https://t.me/{target.username}">@{target.username}</a>'

    # ساخت متن وضعیت
    status_text = f"""
📊 <b>وضعیت حساب کاربری</b>

👤 <b>اطلاعات کاربر:</b>
├─ نام: {target.first_name}
├─ آیدی: <code>{target.id}</code>
├─ یوزرنیم: {username_link}
├─ تعداد پروفایل: {photos_count}
└─ سطح دسترسی: {status_level}

📊 <b>آمار فعالیت:</b>
└─ وضعیت: {'آنلاین 🟢' if target.status == 'online' else 'آفلاین 🔴' if target.status == 'offline' else 'اخیراً آنلاین 🟡'}

📅 <b>تاریخ امروز:</b> {persian_numbers.format_jalali(datetime.now())}

🔮 <b>استفاده از Gemini:</b>
├─ درخواست‌های امروز: {gemini_usage.count if gemini_usage else 0}
└─ باقیمانده: {remaining_requests}
"""

    await message.reply(persian_numbers.persian_numbers(status_text),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True)


def register_public_handlers(app):
    """ثبت تمام هندلرهای اطلاعاتی"""
    app.add_handler(MessageHandler(start_handler, filters.command("start")))
    app.add_handler(
        MessageHandler(help_handler,
                       filters.command(["help", "راهنما", "راهنما بات", ""])))
    app.add_handler(
        MessageHandler(status_handler, filters.command(["status", "وضعیت"],
                                                       "")))
