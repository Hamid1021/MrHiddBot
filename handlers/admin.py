# handlers\admin.py
from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from config import OWNER_ID
from myapp import logger
from database.models import Permission, BotStatus
from utils.decorators import require_permission, register_command



@register_command("بات خاموش", "")
@require_permission(level=3)
async def bot_off_handler(client: Client, message: Message):
    """خاموش کردن ربات"""
    BotStatus.update(is_active=False).where(BotStatus.id == 1).execute()
    await message.reply("🔴 ربات خاموش شد!")


@register_command("بات روشن", "")
@require_permission(level=3)
async def bot_on_handler(client: Client, message: Message):
    """روشن کردن ربات"""
    BotStatus.update(is_active=True).where(BotStatus.id == 1).execute()
    await message.reply("🟢 ربات روشن شد!")


@register_command("کاربر ادمین", "")
@require_permission(level=3)
async def promote_admin_handler(client: Client, message: Message):
    """تبدیل کاربر به ادمین (با ریپلای یا آیدی/یوزرنیم)"""
    try:
        target = await get_target_user(client, message)
        if not target:
            return await message.reply("⚠️ لطفاً به پیام کاربر ریپلای کنید یا آیدی/یوزرنیم را وارد کنید\nمثال:\n`کاربر ادمین 12345678`\n`کاربر ادمین @username`")

        if target.id == OWNER_ID:
            return await message.reply("⛔ این کاربر مالک ربات است و نمی‌توان تغییر داد")

        permission, created = Permission.get_or_create(
            user_id=target.id,
            defaults={'status': 2}
        )

        if not created:
            permission.status = 2
            permission.save()

        await message.reply(f"✅ کاربر {target.first_name} ({target.id}) با موفقیت ادمین شد!")
    except Exception as e:
        logger.error(f"Error promoting admin: {e}")
        await message.reply("⚠️ خطا در ارتقای کاربر به ادمین")


@register_command("کاربر ویژه", "")
@require_permission(level=2)
async def promote_staff_handler(client: Client, message: Message):
    """تبدیل کاربر به ویژه (با ریپلای یا آیدی/یوزرنیم)"""
    try:
        # تشخیص کاربر هدف
        target = await get_target_user(client, message)
        if not target:
            return await message.reply("⚠️ لطفاً به پیام کاربر ریپلای کنید یا آیدی/یوزرنیم را وارد کنید\nمثال:\n`کاربر ویژه 12345678`\n`کاربر ویژه @username`")

        if target.id == OWNER_ID:
            return await message.reply("⛔ این کاربر مالک ربات است و نمی‌توان تغییر داد")

        permission, created = Permission.get_or_create(
            user_id=target.id,
            defaults={'status': 1}
        )

        if not created:
            permission.status = 1
            permission.save()

        await message.reply(f"✅ کاربر {target.first_name} ({target.id}) با موفقیت کاربر ویژه شد!")
    except Exception as e:
        logger.error(f"Error promoting staff: {e}")
        await message.reply("⚠️ خطا در ارتقای کاربر به ویژه")


@register_command("کاربر عادی", "")
@require_permission(level=2)
async def demote_user_handler(client: Client, message: Message):
    """تبدیل کاربر به عادی (با ریپلای یا آیدی/یوزرنیم)"""
    try:
        target = await get_target_user(client, message)
        if not target:
            return await message.reply("⚠️ لطفاً به پیام کاربر ریپلای کنید یا آیدی/یوزرنیم را وارد کنید\nمثال:\n`کاربر عادی 12345678`\n`کاربر عادی @username`")

        if target.id == OWNER_ID:
            return await message.reply("⛔ این کاربر مالک ربات است و نمی‌توان تغییر داد")

        permission, created = Permission.get_or_create(
            user_id=target.id,
            defaults={'status': 0}
        )

        if not created:
            permission.status = 0
            permission.save()

        await message.reply(f"✅ کاربر {target.first_name} ({target.id}) با موفقیت به کاربر عادی تبدیل شد!")
    except Exception as e:
        logger.error(f"Error demoting user: {e}")
        await message.reply("⚠️ خطا در تبدیل کاربر به عادی")


async def get_target_user(client: Client, message: Message):
    """دریافت کاربر هدف از ریپلای یا آیدی/یوزرنیم"""
    # اگر ریپلای شده باشد
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    # اگر آیدی یا یوزرنیم وارد شده باشد
    if len(message.command) > 1:
        user_input = message.command[1].strip()

        # حذف @ از اول یوزرنیم اگر وجود دارد
        if user_input.startswith('@'):
            user_input = user_input[1:]

        try:
            # اگر عدد باشد (آیدی کاربر)
            if user_input.isdigit():
                user_id = int(user_input)
                return await client.get_users(user_id)
            # اگر یوزرنیم باشد
            else:
                return await client.get_users(user_input)
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    return None


def register_admin_handlers(app: Client):
    """ثبت تمام هندلرهای مدیریتی"""
    handlers = [
        (bot_off_handler, filters.command("بات خاموش", "")),
        (bot_on_handler, filters.command("بات روشن", "")),
        (promote_admin_handler, filters.command("کاربر ادمین", "")),
        (promote_staff_handler, filters.command("کاربر ویژه", "")),
        (demote_user_handler, filters.command("کاربر عادی", ""))
    ]

    for handler, filter in handlers:
        app.add_handler(MessageHandler(handler, filter))
