# myapp.py
# -*- coding: utf-8 -*-

from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from database.models import create_tables
from handlers import admin, gemini, google, info, public
from handlers.gemini import gemini_bot
import logging
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from pyrogram.handlers import MessageHandler, InlineQueryHandler, CallbackQueryHandler
from pyrogram.enums import ParseMode
import re

inline_queries = {}

# تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def register_handlers(app: Client) -> None:
    """ثبت تمام هندلرهای ربات"""
    admin.register_admin_handlers(app)
    gemini.register_gemini_handlers(app)
    google.register_google_handlers(app)
    info.register_info_handlers(app)
    public.register_public_handlers(app)

    @app.on_callback_query(filters.regex("^gemini_help$"))
    async def show_help(client: Client, callback_query: CallbackQuery):
        """نمایش راهنمای کامل"""
        help_text = """
    📖 <b>راهنمای کامل استفاده از Gemini</b>

    1. <b>پرسش مستقیم:</b>
    <code>هیدن سوال شما</code>

    2. <b>پرسش سریع:</b>
    از دکمه «🧠 پرسش سریع» استفاده کنید

    🔹 <i>ویژگی‌ها:</i>
    - پاسخ‌های هوشمند
    - ترجمه به سه زبان فارسی انگلیسی ژاپنی
    - محدودیت ۲۰ درخواست روزانه
    """
        await callback_query.answer()
        await callback_query.message.edit_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("بستن", callback_data="close_help")]]))

    @app.on_callback_query(filters.regex("^close_help$"))
    async def close_help(client: Client, callback_query: CallbackQuery):
        """بستن پیام راهنما"""
        await callback_query.message.delete()

    @app.on_inline_query()
    async def handle_inline_query(client: Client, inline_query: InlineQuery):
        """مدیریت کوئری‌های اینلاین"""
        if not inline_query.query:
            return

        # ذخیره کوئری برای استفاده بعدی
        inline_queries[inline_query.id] = inline_query.query

        results = [
            InlineQueryResultArticle(
                title=f"پرسش: {inline_query.query[:30]}...",
                input_message_content=InputTextMessageContent(
                    f"❓ سوال: {inline_query.query}"),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "🔍 نمایش پاسخ",
                        callback_data=f"show_answer:{inline_query.id}")
                ]]),
                description="برای مشاهده پاسخ کلیک کنید")
        ]

        await inline_query.answer(results, cache_time=1)

    @app.on_callback_query(filters.regex("^show_answer:"))
    async def show_inline_answer(client: Client,
                                 callback_query: CallbackQuery):
        """نمایش پاسخ به کوئری اینلاین"""
        try:
            query_id = callback_query.data.split(":")[1]
            question = inline_queries.get(query_id)

            if not question:
                await callback_query.answer("⚠️ سوال یافت نشد!",
                                            show_alert=True)
                return

            await callback_query.answer("در حال پردازش پاسخ...")

            # بررسی وجود پیام اصلی
            if not callback_query.message:
                # اگر پیام اصلی وجود ندارد، یک پیام جدید ارسال کنید
                processing_msg = await client.send_message(
                    callback_query.from_user.id, "🌌 در حال پردازش سوال شما...")
            else:
                # اگر پیام اصلی وجود دارد، به آن ریپلای کنید
                processing_msg = await callback_query.message.reply(
                    "🌌 در حال پردازش سوال شما...")

            try:
                response = await gemini_bot.generate_response(question)
                if not response:
                    await processing_msg.edit_text("⚠️ خطا در پردازش سوال")
                    return

                # تقسیم پاسخ اگر طولانی باشد
                if len(response) > 3900:
                    chunks = [
                        response[i:i + 3900]
                        for i in range(0, len(response), 3900)
                    ]
                    first_part = chunks[0]
                    remaining = "\n\n".join(chunks[1:])

                    await processing_msg.edit_text(
                        f"💎 <b>پاسخ به سوال شما:</b>\n\n{first_part}",
                        parse_mode=ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(
                                "📜 ادامه پاسخ",
                                callback_data=f"more_answer:{query_id}:1")
                        ]]))
                else:
                    await processing_msg.edit_text(
                        f"💎 <b>پاسخ به سوال شما:</b>\n\n{response}",
                        parse_mode=ParseMode.HTML)

            except Exception as e:
                logger.error(f"Error in inline answer: {str(e)}")
                await processing_msg.edit_text("⚠️ خطا در پردازش پاسخ")

        except Exception as e:
            logger.error(f"Error in show_inline_answer: {str(e)}")
            await callback_query.answer("⚠️ خطا در پردازش درخواست",
                                        show_alert=True)

    @app.on_callback_query(filters.regex("^more_answer:"))
    async def show_more_answer(client: Client, callback_query: CallbackQuery):
        """نمایش ادامه پاسخ طولانی"""
        _, query_id, chunk_idx = callback_query.data.split(":")
        chunk_idx = int(chunk_idx)
        question = inline_queries.get(query_id)

        if not question:
            await callback_query.answer("⚠️ سوال یافت نشد!", show_alert=True)
            return

        await callback_query.answer("در حال پردازش...")

        response = await gemini_bot.generate_response(question)
        chunks = [response[i:i + 3900] for i in range(0, len(response), 3900)]

        if chunk_idx >= len(chunks):
            await callback_query.answer("✅ به انتهای پاسخ رسیدید",
                                        show_alert=True)
            return

        current_chunk = chunks[chunk_idx]
        next_idx = chunk_idx + 1

        keyboard = []
        if next_idx < len(chunks):
            keyboard.append([
                InlineKeyboardButton(
                    "📜 ادامه پاسخ",
                    callback_data=f"more_answer:{query_id}:{next_idx}")
            ])

        await callback_query.message.edit_text(
            f"💎 <b>ادامه پاسخ:</b>\n\n{current_chunk}",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None)

    # هندلرهای اینلاین
    app.add_handler(InlineQueryHandler(handle_inline_query))
    app.add_handler(
        CallbackQueryHandler(show_inline_answer,
                             filters.regex("^show_answer:")))
    app.add_handler(
        CallbackQueryHandler(show_more_answer, filters.regex("^more_answer:")))
    app.add_handler(
        CallbackQueryHandler(show_help, filters.regex("^gemini_help$")))
    app.add_handler(
        CallbackQueryHandler(close_help, filters.regex("^close_help$")))

    # # هندلر برای پیام‌های غیرمنتظره
    # @app.on_message(filters.text & ~filters.command)
    # async def unknown_command(client, message):
    #     await message.reply("⚠️ دستور نامعتبر! برای مشاهده راهنما از /help استفاده کنید.")


def main():
    """تابع اصلی اجرای ربات"""
    try:
        # ایجاد جداول دیتابیس
        create_tables()
        logger.info("Database tables created/verified")

        # تنظیمات کلاینت Pyrogram
        app = Client(
            "mehrrp_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
        )

        # ثبت هندلرها
        register_handlers(app)
        logger.info("All handlers registered")

        # راه‌اندازی ربات
        logger.info("Starting bot...")
        app.run()

    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
        raise


if __name__ == "__main__":
    main()
