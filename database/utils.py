# database\utils.py
import datetime
from database.models import User, Permission, GeminiUsage
from config import OWNER_ID
from typing import Optional


def get_or_create_user(user_id: int, first_name: str, last_name: Optional[str],
                       username: Optional[str]) -> User:
    """ذخیره یا بازیابی کاربر از دیتابیس"""
    return User.get_or_create(id=user_id,
                              defaults={
                                  'first_name': first_name,
                                  'last_name': last_name,
                                  'username': username
                              })[0]


def get_user_permission(user_id: int) -> int:
    """دریافت وضعیت سطح دسترسی کاربر"""
    if user_id == OWNER_ID:
        return 3  # مالک
    try:
        return Permission.get(Permission.user_id == user_id).status
    except Permission.DoesNotExist:
        return 0  # کاربر عادی


def get_permission_by_id(user_id: int):
    """دریافت سطح دسترسی کاربر"""
    try:
        return Permission.get(Permission.user_id == user_id)
    except Permission.DoesNotExist:
        pass


def can_use_gemini(user_id: int) -> bool:
    """بررسی سهمیه استفاده از Gemini"""
    if user_id == OWNER_ID:
        return True

    today = datetime.date.today()
    try:
        usage = GeminiUsage.get((GeminiUsage.user_id == user_id)
                                & (GeminiUsage.date == today))
        return usage.count < 30
    except GeminiUsage.DoesNotExist:
        return True


def increment_gemini_usage(user_id: int):
    """افزایش تعداد استفاده از Gemini"""
    if user_id == OWNER_ID:
        return

    today = datetime.date.today()
    try:
        usage = GeminiUsage.get((GeminiUsage.user_id == user_id)
                                & (GeminiUsage.date == today))
        usage.count += 1
        usage.save()
    except GeminiUsage.DoesNotExist:
        GeminiUsage.create(user_id=user_id, date=today, count=1)
