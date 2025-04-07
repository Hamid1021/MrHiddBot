import datetime
from pyrogram.types import Message
from utils.converters import persian_numbers


def format_response(text: str, message: Message) -> str:
    """قالب‌بندی پاسخ‌ها"""
    jalali_date = persian_numbers.to_jalali(datetime.datetime.now())
    return f"""
🌸 دوست من {message.from_user.first_name}:

{text}

📅 تاریخ: {jalali_date}
    """


def extract_user_info(message: Message) -> dict:
    """استخراج اطلاعات کاربر از پیام"""
    user = message.from_user
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name or '',
        'username': user.username or '',
        'is_bot': user.is_bot
    }


def split_long_text(text: str, max_length: int = 4000) -> list[str]:
    """تقسیم متن طولانی به بخش‌های کوچکتر"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]
