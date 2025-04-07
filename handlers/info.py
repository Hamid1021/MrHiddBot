# handlers\info.py
from pyrogram import filters
from pyrogram.types import Message, User
from pyrogram.enums import ParseMode
from utils.converters import persian_numbers
from utils.decorators import register_command, rate_limit
from utils.helpers import format_response
from typing import Optional
import logging
from pyrogram import Client
from pyrogram.handlers import MessageHandler

# تنظیمات لاگ‌گیری
logger = logging.getLogger(__name__)


@register_command(["آیدی", "id", "شناسه"], prefixes=["/", "!", ""])
@rate_limit(limit=5, interval=30)
async def user_info_handler(client: Client, message: Message):
    """
    نمایش کامل اطلاعات کاربر
    روش‌های استفاده:
    1. آیدی [ریپلای به کاربر]
    2. آیدی [آیدی کاربر]
    3. آیدی [یوزرنیم کاربر]
    """
    try:
        target = await resolve_target_user(client, message)
        if not target:
            return

        user_info = await generate_user_info(client, target)
        await send_user_info(client, message, target, user_info)

    except Exception as e:
        logger.error(f"User info error: {str(e)}")
        await message.reply("⚠️ خطا در دریافت اطلاعات کاربر")


async def resolve_target_user(client: Client,
                              message: Message) -> Optional[User]:
    """تعیین کاربر هدف بر اساس پیام ورودی"""
    # اگر به پیامی ریپلای شده باشد
    if message.reply_to_message:
        return message.reply_to_message.from_user

    # اگر آیدی یا یوزرنیم همراه دستور ارسال شده باشد
    if len(message.command) > 1:
        input_data = message.command[1].strip("@")

        try:
            # اگر عدد باشد (آیدی کاربر)
            user_id = int(input_data)
            return await client.get_users(user_id)
        except ValueError:
            # اگر یوزرنیم باشد
            return await client.get_users(input_data)
        except Exception:
            return None

    # اگر هیچکدام، اطلاعات خود کاربر
    return message.from_user


async def generate_user_info(client: Client, user: User) -> str:
    """تولید متن اطلاعات کاربر"""
    try:
        # دریافت تعداد عکس‌های پروفایل
        photos_count = 0
        async for _ in client.get_chat_photos(user.id):
            photos_count += 1
    except Exception:
        photos_count = 0

    # دریافت اطلاعات بیشتر از کاربر
    try:
        full_user = await client.get_users(user.id)
    except Exception:
        full_user = user

    # ساخت لینک یوزرنیم (با Markdown V2)
    username_link = f"[@{user.username}](https://t.me/{user.username})" if user.username else "ندارد"

    # وضعیت آنلاین بودن
    status_emoji = {
        "online": "🟢 آنلاین",
        "offline": "🔴 آفلاین",
        "recently": "🟡 اخیراً آنلاین",
        "last_week": "⚪ هفته گذشته",
        "last_month": "⚫ ماه گذشته"
    }.get(getattr(full_user, 'status', 'offline'), "🔴 آفلاین")

    # ساخت متن اطلاعات (بدون استفاده از بک‌اسلش برای خطوط جدید)
    info_lines = ["👤 **اطلاعات کاربر**", "", f"▫️ **نام:** {user.first_name}"]

    if user.last_name:
        info_lines.append(f"▫️ **نام خانوادگی:** {user.last_name}")

    info_lines.extend([
        f"▫️ **آیدی عددی:** `{user.id}`", f"▫️ **یوزرنیم:** {username_link}",
        f"▫️ **وضعیت حساب:** {'ربات 🤖' if user.is_bot else 'کاربر معمولی 👤'}",
        f"▫️ **وضعیت آنلاین:** {status_emoji}",
        f"▫️ **تعداد عکس‌های پروفایل:** {photos_count}"
    ])

    info_text = "\n".join(info_lines)

    # تبدیل اعداد به فارسی
    return persian_numbers.persian_numbers(info_text)


async def send_user_info(client: Client, message: Message, user: User,
                         info_text: str):
    """ارسال اطلاعات کاربر با بهترین روش"""
    try:
        # دریافت آخرین عکس پروفایل
        async for photo in client.get_chat_photos(user.id, limit=1):
            await message.reply_photo(
                photo.file_id,
                caption=info_text,
                parse_mode=ParseMode.MARKDOWN,  # تغییر از HTML به MARKDOWN
                reply_to_message_id=message.id)
            return

    except Exception as e:
        logger.warning(f"Couldn't get user photo: {str(e)}")

    # اگر عکس پیدا نشد یا خطا داشت
    await message.reply(
        info_text,
        parse_mode=ParseMode.MARKDOWN,  # تغییر از HTML به MARKDOWN
        reply_to_message_id=message.id)


def register_info_handlers(app: Client):
    """ثبت تمام هندلرهای اطلاعاتی"""
    app.add_handler(
        MessageHandler(
            user_info_handler,
            filters.command(["آیدی", "id", "شناسه"], prefixes=["/", "!", ""])))
