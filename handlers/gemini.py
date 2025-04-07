from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client
from google import genai
from typing import Optional
from config import GEMINI_API_KEY, GEMINI_MODEL
from database.utils import can_use_gemini, increment_gemini_usage
from utils.helpers import format_response
from utils.decorators import register_command, rate_limit, require_permission
import logging
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
import re

# تنظیمات لاگ
logger = logging.getLogger(__name__)


class GeminiBot:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    async def generate_response(self, prompt: str) -> Optional[str]:
        """تولید پاسخ از Gemini با مدیریت خطا"""
        try:
            response = self.client.models.generate_content(model=self.model,
                                                           contents=prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return None


gemini_bot = GeminiBot()


@register_command(["هیدن", "gemini", "جمنای"], "")
@rate_limit(limit=5, interval=60)
@require_permission(level=1)
async def gemini_handler(client: Client, message: Message):
    """
    مدیریت هوشمند درخواست‌های Gemini
    """
    # اگر فقط دستور ارسال شده باشد (بدون متن)
    if len(message.text.split()) == 1:
        await send_welcome_message(client, message)
        return

    await process_gemini_request(client, message)


async def send_welcome_message(client: Client, message: Message):
    """ارسال پیام خوشآمدگویی با دکمه‌های تعاملی"""
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🧠 پرسش سریع",
                             switch_inline_query_current_chat="")
    ], [InlineKeyboardButton("📚 آموزش استفاده", callback_data="gemini_help")]])

    welcome_text = """
✨ <b>به هوش مصنوعی Gemini خوش آمدید!</b> ✨

🤖 من می‌توانم به سوالات شما پاسخ دهم:

🔹 <i>روش‌های پرسش:</i>
1. ارسال <code>هیدن سوال شما</code>
3. کلیک روی دکمه «پرسش سریع»

📌 <i>مثال‌ها:</i>
<code>هیدن چگونه ربات بسازم؟</code>
<code>هیدن معنی زندگی چیست؟</code>
"""
    await message.reply(welcome_text,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML)


async def process_gemini_request(client: Client, message: Message):
    """پردازش اصلی درخواست‌های Gemini"""
    if not await check_gemini_usage(message):
        return

    query = extract_query(message)
    if not validate_query(query):
        await message.reply("⚠️ لطفاً سوال معتبری وارد کنید (حداقل ۳ کاراکتر)")
        return

    # نمایش پیام در حال پردازش با انیمیشن
    processing_msg = await message.reply("🌌 در حال پردازش سوال شما...")

    try:
        response = await gemini_bot.generate_response(query)
        if response:
            formatted_response = format_response(response, message)
            # ارسال پاسخ با قالب زیبا
            await processing_msg.edit_text(
                f"💎 <b>پاسخ به سوال شما:</b>\n\n{formatted_response}",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True)
        else:
            await processing_msg.edit_text(
                "⚠️ خطا در پردازش سوال. لطفاً مجدد تلاش کنید.")
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        await processing_msg.edit_text("⚠️ خطای سیستمی. لطفاً بعداً تلاش کنید."
                                       )


@register_command("فارسیش", "")
@rate_limit(limit=3, interval=30)
@require_permission(level=1)
async def translate_fa_handler(client: Client, message: Message):
    """ترجمه متن به فارسی"""
    await handle_translation(message, "این متن را به فارسی ترجمه کن")


@register_command("انگلیسیش", "")
@rate_limit(limit=3, interval=30)
@require_permission(level=1)
async def translate_en_handler(client: Client, message: Message):
    """ترجمه متن به انگلیسی"""
    await handle_translation(message, "Translate this text to English")


@register_command("ژاپنیش", "")
@rate_limit(limit=3, interval=30)
@require_permission(level=1)
async def translate_jp_handler(client: Client, message: Message):
    """ترجمه متن به ژاپنی"""
    await handle_translation(message, "Translate this text to Japanese")


# توابع کمکی
async def check_gemini_usage(message: Message) -> bool:
    """بررسی سهمیه استفاده از Gemini"""
    if not can_use_gemini(message.from_user.id):
        await message.reply("⚠️ سهمیه روزانه شما تمام شده است!")
        return False
    increment_gemini_usage(message.from_user.id)
    return True


def extract_query(message: Message) -> str:
    """استخراج متن سوال از پیام"""
    if message.text.startswith(("هیدن ", "gemini ", "جمنای ")):
        return message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        return message.reply_to_message.text
    return message.text


def validate_query(query: str) -> bool:
    """اعتبارسنجی متن سوال"""
    return query and len(query.strip()) >= 3


async def handle_response(temp_msg: Message, original_msg: Message,
                          response: Optional[str]):
    """مدیریت پاسخ و خطاها"""
    if response:
        await temp_msg.edit_text(format_response(response, original_msg))
    else:
        await temp_msg.edit_text(
            "⚠️ خطا در پردازش درخواست. لطفاً بعداً تلاش کنید.")


async def handle_translation(message: Message, prompt: str):
    """مدیریت ترجمه متون"""
    if not message.reply_to_message:
        await message.reply("⚠️ لطفاً به پیام مورد نظر ریپلای کنید")
        return

    if not await check_gemini_usage(message):
        return

    temp_msg = await message.reply("🔍 در حال ترجمه...")
    text_to_translate = f"{prompt}:\n{message.reply_to_message.text}"
    translated_text = await gemini_bot.generate_response(text_to_translate)

    await handle_response(temp_msg, message, translated_text)


# هندلر جدید برای مدیریت ریپلای‌ها
@rate_limit(limit=5, interval=60)
async def gemini_reply_handler(client: Client, message: Message):
    """مدیریت درخواست‌های ریپلای شده به Gemini"""
    if not await check_gemini_usage(message):
        return

    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply("⚠️ لطفاً به یک پیام متنی ریپلای کنید")
        return

    temp_msg = await message.reply("🔮 در حال پردازش...")
    response = await gemini_bot.generate_response(message.reply_to_message.text
                                                  )

    await handle_response(temp_msg, message, response)



def register_gemini_handlers(app: Client):
    """ثبت تمام هندلرهای Gemini"""
    # هندلر دستورات اصلی
    app.add_handler(MessageHandler(
        gemini_handler,
        filters.command(["هیدن", "gemini", "جمنای"], prefixes=["", "/", "!"])
    ))

    # هندلر ترجمه‌ها
    for cmd, handler in [("فارسیش", translate_fa_handler),
                        ("انگلیسیش", translate_en_handler),
                        ("ژاپنیش", translate_jp_handler)]:
        app.add_handler(MessageHandler(
            handler,
            filters.command(cmd, prefixes=["", "/", "!"])
        ))

    # هندلر ریپلای‌ها
    app.add_handler(MessageHandler(
        gemini_reply_handler,
        filters.reply & filters.command(
            ["هیدن", "gemini", "جمنای"], prefixes=["", "/", "!"])
    ))
