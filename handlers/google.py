# handlers\google.py
import requests
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message
from typing import List, Dict, Optional
from config import GOOGLE_API_KEY, GOOGLE_CX
from utils.decorators import register_command, rate_limit
from utils.helpers import format_response, split_long_text
import logging
from pyrogram.handlers import MessageHandler

# تنظیمات لاگ‌گیری
logger = logging.getLogger(__name__)


class GoogleSearch:
    def __init__(self):
        self.base_url = "https://customsearch.googleapis.com/customsearch/v1"
        self.timeout = 15
        self.max_results = 10

    async def search(self, query: str) -> Optional[Dict]:
        """انجام جستجوی گوگل با مدیریت خطا"""
        params = {
            'cx': GOOGLE_CX,
            'q': query,
            'key': GOOGLE_API_KEY,
            'num': self.max_results
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Google search error: {str(e)}")
            return None


google_searcher = GoogleSearch()


@register_command(["گوگل", "جستجو", "search"])
@rate_limit(limit=3, interval=30)
async def google_search_handler(client: Client, message: Message):
    """
    جستجوی پیشرفته در گوگل
    استفاده:
    /گوگل [عبارت جستجو]
    مثال:
    /گوگل بهترین رستوران تهران
    """
    # استخراج عبارت جستجو
    query = extract_search_query(message)
    if not query:
        await message.reply("⚠️ لطفاً عبارت جستجو را وارد کنید")
        return

    # نمایش وضعیت جستجو
    temp_msg = await message.reply("🔍 در حال جستجو در گوگل...")

    # انجام جستجو
    search_results = await google_searcher.search(query)
    if not search_results:
        await temp_msg.edit_text("⚠️ خطا در اتصال به سرویس گوگل")
        return

    # پردازش نتایج
    formatted_results = format_search_results(query, search_results)
    if not formatted_results:
        await temp_msg.edit_text("⚠️ نتیجه‌ای برای جستجوی شما یافت نشد")
        return

    # ارسال نتایج
    await send_search_results(client, temp_msg, message, formatted_results)


# توابع کمکی
def extract_search_query(message: Message) -> Optional[str]:
    """استخراج عبارت جستجو از پیام"""
    command = message.text.split(maxsplit=1)
    return command[1].strip() if len(command) > 1 else None


def format_search_results(query: str, results: Dict) -> Optional[List[str]]:
    """قالب‌بندی نتایج جستجو"""
    if 'items' not in results or not results['items']:
        return None

    formatted = [f"🔍 نتایج جستجو برای: <b>{query}</b>\n"]

    for idx, item in enumerate(results['items'], 1):
        title = item.get('title', 'بدون عنوان')
        link = item.get('link', '#')
        snippet = item.get('snippet', 'بدون توضیحات')

        formatted.append(
            f"{idx}. <a href='{link}'><b>{title}</b></a>\n"
            f"{snippet}\n"
        )

    return formatted


async def send_search_results(
    client: Client,
    temp_msg: Message,
    original_msg: Message,
    results: List[str]
):
    """ارسال نتایج جستجو با مدیریت پیام‌های طولانی"""
    full_text = '\n'.join(results)

    # اگر متن خیلی طولانی باشد، آن را تقسیم می‌کنیم
    if len(full_text) > 4000:
        parts = split_long_text(full_text, 4000)
        await temp_msg.delete()

        for part in parts:
            await client.send_message(
                chat_id=original_msg.chat.id,
                text=format_response(part, original_msg),
                disable_web_page_preview=True
            )
    else:
        await temp_msg.edit_text(
            format_response(full_text, original_msg),
            disable_web_page_preview=True
        )


def register_google_handlers(app: Client):
    """ثبت تمام هندلرهای جستجوی گوگل"""
    handlers = [
        # هندلر اصلی جستجو
        (
            google_search_handler,
            filters.command(["گوگل", "جستجو", "search"], "")
        ),
    ]

    for handler, filter in handlers:
        app.add_handler(
            MessageHandler(
                handler,
                filter,
            ),
            group=2  # گروه متوسط برای اولویت اجرا
        )
