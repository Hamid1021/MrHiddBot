# -*- coding: utf-8 -*-
from functools import wraps
from pyrogram import filters
from pyrogram.types import Message
from typing import Callable, Optional
from database.models import BotStatus, Permission
from database.utils import get_user_permission
from config import OWNER_ID
import logging

logger = logging.getLogger(__name__)


def register_command(
        commands: str | list,
        prefixes: str | list = "/",
        case_sensitive: bool = False,
        group: int = 0,
        critical: bool = False  # اضافه کردن پارامتر جدید برای دستورات حیاتی
):
    """
    دکوراتور برای ثبت خودکار هندلرهای کامند

    Parameters:
        critical: اگر True باشد حتی اگر ربات خاموش باشد اجرا می‌شود
    """

    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(client, message: Message, *args, **kwargs):
            # بررسی فعال بودن ربات (مگر برای دستورات حیاتی)
            if not critical and not BotStatus.get_or_create(id=1)[0].is_active:
                return

            try:
                return await func(client, message, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                await message.reply("⚠️ خطایی در پردازش دستور رخ داد")

        # ثبت خودکار هندلر
        wrapper.handler = filters.command(commands=commands,
                                          prefixes=prefixes,
                                          case_sensitive=case_sensitive)
        wrapper.group = group

        return wrapper

    return decorator


def require_permission(level: int = 0):
    """
    دکوراتور برای بررسی سطح دسترسی کاربر
    سطوح دسترسی:
        0: کاربر عادی
        1: کاربر ویژه
        2: ادمین
        3: مالک
    """

    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(client, message: Message, *args, **kwargs):
            user_id = message.from_user.id

            # مالک همیشه دسترسی دارد
            if user_id == OWNER_ID:
                return await func(client, message, *args, **kwargs)

            permission = get_user_permission(user_id)

            if permission < level:
                await message.reply("⛔ شما دسترسی لازم برای این کار را ندارید!"
                                    )
                return

            return await func(client, message, *args, **kwargs)

        return wrapper

    return decorator


def rate_limit(limit: int = 3, interval: int = 10):
    """
    دکوراتور برای محدود کردن تعداد درخواست‌ها
    """
    from collections import defaultdict
    import time

    user_timestamps = defaultdict(list)

    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(client, message: Message, *args, **kwargs):
            user_id = message.from_user.id
            now = time.time()

            # حذف درخواست‌های قدیمی
            user_timestamps[user_id] = [
                t for t in user_timestamps[user_id] if now - t < interval
            ]

            if len(user_timestamps[user_id]) >= limit:
                await message.reply(
                    f"⏳ لطفاً {interval} ثانیه صبر کنید قبل از ارسال درخواست جدید"
                )
                return

            user_timestamps[user_id].append(now)
            return await func(client, message, *args, **kwargs)

        return wrapper

    return decorator


def only_admins(func: Callable):
    """دکوراتور اختصاصی برای دستورات ادمین"""
    return require_permission(level=2)(func)


def only_owner(func: Callable):
    """دکوراتور اختصاصی برای دستورات مالک"""
    return require_permission(level=3)(func)


def database_required(func: Callable):
    """
    دکوراتور برای اطمینان از اتصال به دیتابیس
    """

    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        from database.models import db

        try:
            if db.is_closed():
                db.connect()
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            await message.reply("⚠️ خطایی در ارتباط با دیتابیس رخ داد")
        finally:
            if not db.is_closed():
                db.close()

    return wrapper
