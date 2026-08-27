# bot.py - Telegram Planner Bot
# Multi-Language (Persian/English) with Jalali/Gregorian Calendar Support
# Version 4.2 - Bilingual Change Language Button

import os
import re
import asyncio
import json
import httpx
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import error as tg_error
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

# ============================================================
# Load Environment Variables
# ============================================================
load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    TOKEN = "8311183895:AAHTC9e-o0cYThepuh4VssU1ZU8PHGIfE4g"
    print("⚠️ BOT_TOKEN not found in .env, using hardcoded token.")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6JN2AS6v5Ag2ZIcstZdH1pAcM8e7r1A8KxflWdXSXGMGQ")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
CONSULTANT_GROUP_ID = os.environ.get("CONSULTANT_GROUP_ID")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "ngiga1")
OWNER_TOKEN = os.environ.get("OWNER_TOKEN", "MySecretOwnerToken123")

print(f"✅ Bot started successfully!")
print(f"👑 Owner: @{OWNER_USERNAME}")

# ============================================================
# Translations Dictionary
# ============================================================

LANG = {
    "fa": {
        "start_owner": "👑 به پنل مدیریت خوش آمدید!\n\nشما **مالک** ربات هستید و دسترسی کامل به تمام قابلیت‌ها دارید.\nاز منوی زیر استفاده کنید:",
        "start_user": "🎯 به ربات برنامه‌ریزی روزانه خوش آمدی!\n\nبرای استفاده از ربات باید توسط مالک به شما دسترسی داده شود.\nدر غیر این صورت، فقط می‌توانید این پیام را ببینید.\n\nاگر خودتان مالک هستید، از دستور `/claimtoken <توکن>` استفاده کنید.",
        "request_access": "📢 درخواست دسترسی",
        "request_sent": "✅ درخواست شما به مالک ارسال شد. منتظر تأیید باشید.",
        "request_error": "❌ خطا در ارسال درخواست: {error}",
        "access_denied": "⛔ شما دسترسی کامل به ربات ندارید.\nلطفاً از مالک درخواست دسترسی کنید.",
        "main_menu": "🎯 منوی اصلی:",
        "new_plan": "➕ برنامه جدید",
        "list_plans": "📋 لیست برنامه‌ها",
        "daily_report": "📝 ثبت گزارش روزانه",
        "today_schedule": "⏰ برنامه امروز (توسط AI)",
        "manage_tasks": "✅ مدیریت تسک‌های امروز",
        "test_log": "🧪 ثبت تست روزانه",
        "set_group": "👥 تنظیم گروه گزارش",
        "delete_plan": "❌ حذف برنامه",
        "change_lang": "🌐 تغییر زبان / Change Language",  # ← دو زبانه
        "select_lang": "🌐 لطفاً زبان خود را انتخاب کنید:\nPlease select your language:",
        "lang_changed": "✅ زبان به فارسی تغییر یافت.",
        "lang_changed_en": "✅ Language changed to English.",
        "no_access": "⛔ شما دسترسی لازم را ندارید.",
        "plan_title": "📝 [مرحله 1/4] عنوان برنامه رو وارد کن:",
        "plan_start_date": "📅 [مرحله 2/4] تاریخ شروع (به شمسی، مثلاً ۱۴۰۵/۰۶/۰۱):",
        "plan_end_date": "📅 [مرحله 3/4] تاریخ پایان (به شمسی):",
        "plan_tasks": "📚 [مرحله 4/4] وارد کردن تسک‌های روز {date}\nنام تسک رو وارد کن (یا «پایان روز» برای پایان این روز):",
        "invalid_date": "❌ فرمت اشتباه. (مثلاً ۱۴۰۵/۰۶/۰۱)",
        "invalid_range": "❌ تاریخ‌ها نامعتبر هستند.",
        "min_one_task": "❌ حداقل یک تسک اضافه کن!",
        "tasks_saved": "✅ تسک‌های روز {date} ذخیره شد.",
        "plan_saved": "✅ برنامه «{title}» با {days} روز ذخیره شد.",
        "task_added": "✅ تسک «{task}» اضافه شد.",
        "no_plans": "📭 هیچ برنامه‌ای ندارید.",
        "plan_list": "📋 *لیست برنامه‌های شما:*\n\n",
        "active": "✅ فعال",
        "completed": "🔴 تمام شده",
        "days_count": "تعداد روزها: {days} روز | کل تسک‌ها: {tasks}",
        "no_tasks_today": "📭 امروز ({date}) هیچ تسکی ندارید.",
        "manage_today": "📅 مدیریت تسک‌های امروز ({date})\n\nروی هر تسک کلیک کن:",
        "task_done": "✅ انجام شده",
        "task_pending": "⏳ انجام نشده",
        "status_changed": "✅ وضعیت تغییر کرد!",
        "schedule_need_log": "⏰ ابتدا گزارش روزانه را ثبت کن تا زمان بیداری و خواب مشخص شود.",
        "generating": "🧠 در حال تولید برنامه امروز... لطفاً صبر کنید.",
        "schedule_today": "📅 *برنامه امروز - {date}*\n\n⏰ بیداری: {wake} | خواب: {sleep}\n🧠 *تولید شده توسط:* {provider}\n\n",
        "schedule_error": "❌ خطا: {error}",
        "test_total": "🧪 *ثبت تست‌های امروز*\n\n🔹 تعداد کل تست‌هایی که امروز حل کردی رو وارد کن (عدد):",
        "test_wrong": "🔸 تعداد غلط‌های امروز رو وارد کن (عدد):",
        "test_saved": "✅ تست‌های امروز ثبت شد!\n📝 کل: {total}\n❌ غلط: {wrong}\n✅ صحیح: {correct}\n🎯 درصد صحت: {accuracy}%",
        "invalid_number": "❌ لطفاً یک عدد صحیح وارد کن.",
        "daily_wake": "⏰ [1/4] ساعت بیداری (مثلاً ۰۷:۰۰ یا 07:00):",
        "daily_sleep": "⏰ [2/4] ساعت خواب (مثلاً ۲۳:۰۰ یا 23:00):",
        "daily_mood": "😊 [3/4] وضعیت روحی امروز:",
        "daily_energy": "⚡ [4/4] میزان انرژی امروز:",
        "daily_questions": "📝 حالا سوالات دلخواه رو پاسخ بده.\nهر سوال رو با فرمت `سوال: پاسخ` بنویس.\nوقتی تمام شد «پایان» رو بفرست.",
        "daily_saved": "✅ گزارش روزانه ثبت شد!",
        "invalid_time": "❌ فرمت ساعت اشتباه. (مثلاً ۰۷:۰۰ یا 07:00)\nلطفاً دوباره وارد کن:",
        "qa_format": "❌ از «:» برای جدا کردن سوال و پاسخ استفاده کن.\nمثال: چقدر درس خوندم؟: ۳ ساعت",
        "qa_saved": "✅ سوال ذخیره شد. سوال بعدی یا «پایان»:",
        "set_group_info": "📢 برای تنظیم گروه مشاور، این مراحل رو انجام بده:\n\n1️⃣ ربات رو به گروه مورد نظر اضافه کن (فقط عضو باشه کافیست).\n2️⃣ در آن گروه، دستور `/setgroup` رو تایپ کن.\n3️⃣ ربات گروه رو شناسایی می‌کنه و از تو تأیید نهایی می‌گیره.\n\n✅ بعد از تنظیم، گزارش‌ها به آن گروه ارسال می‌شوند.\n❌ برای لغو، از دستور `/cleargroup` استفاده کن.",
        "group_set": "✅ این گروه به عنوان گروه مشاور شما تنظیم شد.\nگروه: {group}",
        "group_cleared": "✅ گروه مشاور لغو شد.",
        "delete_select": "❌ انتخاب برنامه برای حذف:",
        "deleted": "✅ «{title}» حذف شد.",
        "no_plans_delete": "📭 هیچ برنامه‌ای برای حذف نیست.",
        "ft_no_report": "📭 امروز گزارشی ثبت نشده است.",
        "ft_sent": "✅ گزارش فوری برای مشاور ارسال شد.",
        "ft_no_group": "❌ ابتدا گروه مشاور را تنظیم کنید.\nاز دکمه «👥 تنظیم گروه گزارش» استفاده کنید یا دستور /setgroup را در گروه مورد نظر بفرستید.",
        "owner_only": "⛔ فقط مالک ربات می‌تواند از این دستور استفاده کند.",
        "adduser_usage": "❌ لطفاً یک یوزرنیم یا آیدی وارد کنید.\nمثال: `/adduser @username`\nیا: `/adduser 123456789`",
        "user_added": "✅ کاربر {name} (@{username}) به عنوان **ادمین** اضافه شد.\n🆔 آیدی: `{id}`",
        "user_not_found": "❌ کاربر پیدا نشد. خطا: {error}",
        "notify_new_user": "👤 *کاربر جدید ربات را استارت کرد!*\n\n🆔 آیدی: `{id}`\n👤 نام: {name}\n🔹 یوزرنیم: @{username}\n📅 زمان: {time}\n\nبرای دادن دسترسی به این کاربر، از دستور زیر استفاده کنید:\n`/adduser {user}`",
        "access_granted": "🎉 شما توسط مالک به عنوان کاربر مجاز در ربات اضافه شدید!\nاکنون می‌توانید از تمام قابلیت‌های ربات استفاده کنید.\nدستور /start را بفرستید تا منوی اصلی را ببینید.",
        "claim_usage": "❌ لطفاً توکن را وارد کنید.\nمثال: `/claimtoken MySecretOwnerToken123`",
        "claim_success": "✅ شما با موفقیت به عنوان **مالک** ربات ثبت شدید!\nاکنون دسترسی کامل به تمام قابلیت‌ها دارید.\nدستور /start را بفرستید تا منوی اصلی را ببینید.",
        "claim_failed": "❌ توکن اشتباه است. لطفاً توکن معتبر را وارد کنید.",
        "state_info": "📌 وضعیت فعلی شما:\n{state}",
        "no_state": "📌 شما در هیچ فرایندی نیستید.",
        "debug_title": "🔍 *اطلاعات دیباگ*\n\n📅 تاریخ امروز (شمسی): {today_jalali}\n📅 تاریخ امروز (میلادی): {today_gregorian}\n📆 روز هفته: {day}\n\n📌 وضعیت کاربر:\n{state}\n\n📝 گزارش امروز:\n{log}",
        "no_log": "گزارشی ثبت نشده است.",
        "back": "🔙 بازگشت",
        "cancel": "❌ لغو",
        "done": "✅ انجام شد",
        "select": "انتخاب کنید",
        "end_day": "پایان روز",
        "in_progress": "🧠 در حال تولید برنامه امروز... لطفاً صبر کنید.",
        "lang_persian": "🇮🇷 فارسی",
        "lang_english": "🇬🇧 English",
        "no_plan_active": "📭 هیچ برنامه فعالی ندارید.",
        "task_toggle_done": "✅ انجام شد!",
    },
    "en": {
        "start_owner": "👑 Welcome to the admin panel!\n\nYou are the **owner** of the bot and have full access to all features.\nUse the menu below:",
        "start_user": "🎯 Welcome to the Daily Planner Bot!\n\nTo use this bot, you need to be granted access by the owner.\nOtherwise, you can only see this message.\n\nIf you are the owner, use `/claimtoken <token>`.",
        "request_access": "📢 Request Access",
        "request_sent": "✅ Your request has been sent to the owner. Please wait for approval.",
        "request_error": "❌ Error sending request: {error}",
        "access_denied": "⛔ You don't have full access to the bot.\nPlease request access from the owner.",
        "main_menu": "🎯 Main Menu:",
        "new_plan": "➕ New Plan",
        "list_plans": "📋 My Plans",
        "daily_report": "📝 Daily Report",
        "today_schedule": "⏰ Today's Schedule (AI)",
        "manage_tasks": "✅ Today's Tasks",
        "test_log": "🧪 Test Log",
        "set_group": "👥 Set Report Group",
        "delete_plan": "❌ Delete Plan",
        "change_lang": "🌐 تغییر زبان / Change Language",  # ← دو زبانه
        "select_lang": "🌐 Please select your language:\nلطفاً زبان خود را انتخاب کنید:",
        "lang_changed": "✅ Language changed to Persian.",
        "lang_changed_en": "✅ Language changed to English.",
        "no_access": "⛔ You don't have permission.",
        "plan_title": "📝 [Step 1/4] Enter plan title:",
        "plan_start_date": "📅 [Step 2/4] Start date (Gregorian, e.g., 2026-06-01):",
        "plan_end_date": "📅 [Step 3/4] End date (Gregorian):",
        "plan_tasks": "📚 [Step 4/4] Enter tasks for {date}\nEnter task name (or 'End Day' to finish this day):",
        "invalid_date": "❌ Invalid format. Please use YYYY-MM-DD (e.g., 2026-06-01).",
        "invalid_range": "❌ Invalid date range.",
        "min_one_task": "❌ Add at least one task!",
        "tasks_saved": "✅ Tasks for {date} saved.",
        "plan_saved": "✅ Plan '{title}' saved with {days} days.",
        "task_added": "✅ Task '{task}' added.",
        "no_plans": "📭 You have no plans.",
        "plan_list": "📋 *Your Plans:*\n\n",
        "active": "✅ Active",
        "completed": "🔴 Completed",
        "days_count": "Days: {days} | Total Tasks: {tasks}",
        "no_tasks_today": "📭 No tasks for today ({date}).",
        "manage_today": "📅 Today's Tasks ({date})\n\nClick each task to toggle status:",
        "task_done": "✅ Done",
        "task_pending": "⏳ Pending",
        "status_changed": "✅ Status changed!",
        "schedule_need_log": "⏰ Please submit your daily report first to set wake-up and sleep times.",
        "generating": "🧠 Generating today's schedule... Please wait.",
        "schedule_today": "📅 *Today's Schedule - {date}*\n\n⏰ Wake: {wake} | Sleep: {sleep}\n🧠 *Generated by:* {provider}\n\n",
        "schedule_error": "❌ Error: {error}",
        "test_total": "🧪 *Today's Test Log*\n\n🔹 Enter total number of tests you solved today (number):",
        "test_wrong": "🔸 Enter number of wrong answers today (number):",
        "test_saved": "✅ Test log saved!\n📝 Total: {total}\n❌ Wrong: {wrong}\n✅ Correct: {correct}\n🎯 Accuracy: {accuracy}%",
        "invalid_number": "❌ Please enter a valid number.",
        "daily_wake": "⏰ [1/4] Wake-up time (e.g., 07:00):",
        "daily_sleep": "⏰ [2/4] Sleep time (e.g., 23:00):",
        "daily_mood": "😊 [3/4] Today's mood:",
        "daily_energy": "⚡ [4/4] Today's energy level:",
        "daily_questions": "📝 Now answer your custom questions.\nWrite each as `Question: Answer`.\nWhen done, send 'End'.",
        "daily_saved": "✅ Daily report saved!",
        "invalid_time": "❌ Invalid time format. (e.g., 07:00)\nPlease try again:",
        "qa_format": "❌ Use ':' to separate question and answer.\nExample: How much did I study?: 3 hours",
        "qa_saved": "✅ Question saved. Next question or 'End':",
        "set_group_info": "📢 To set up the consultant group:\n\n1️⃣ Add the bot to your group (member only).\n2️⃣ In the group, type `/setgroup`.\n3️⃣ The bot will identify the group and ask for confirmation.\n\n✅ After setup, reports will be sent there.\n❌ To cancel, use `/cleargroup`.",
        "group_set": "✅ This group is set as your report group.\nGroup: {group}",
        "group_cleared": "✅ Report group cleared.",
        "delete_select": "❌ Select plan to delete:",
        "deleted": "✅ '{title}' deleted.",
        "no_plans_delete": "📭 No plans to delete.",
        "ft_no_report": "📭 No report for today.",
        "ft_sent": "✅ Instant report sent to consultant.",
        "ft_no_group": "❌ Please set up your report group first.\nUse the '👥 Set Report Group' button or /setgroup in the group.",
        "owner_only": "⛔ Only the bot owner can use this command.",
        "adduser_usage": "❌ Please enter a username or ID.\nExample: `/adduser @username`\nor: `/adduser 123456789`",
        "user_added": "✅ User {name} (@{username}) added as **admin**.\n🆔 ID: `{id}`",
        "user_not_found": "❌ User not found. Error: {error}",
        "notify_new_user": "👤 *New user started the bot!*\n\n🆔 ID: `{id}`\n👤 Name: {name}\n🔹 Username: @{username}\n📅 Time: {time}\n\nTo grant access:\n`/adduser {user}`",
        "access_granted": "🎉 You have been granted access to the bot by the owner!\nNow you can use all features.\nSend /start to see the main menu.",
        "claim_usage": "❌ Please enter the token.\nExample: `/claimtoken MySecretOwnerToken123`",
        "claim_success": "✅ You have been successfully registered as the **owner** of the bot!\nNow you have full access to all features.\nSend /start to see the main menu.",
        "claim_failed": "❌ Invalid token. Please enter the correct token.",
        "state_info": "📌 Your current state:\n{state}",
        "no_state": "📌 You are not in any process.",
        "debug_title": "🔍 *Debug Info*\n\n📅 Today (Jalali): {today_jalali}\n📅 Today (Gregorian): {today_gregorian}\n📆 Day: {day}\n\n📌 User state:\n{state}\n\n📝 Today's log:\n{log}",
        "no_log": "No log recorded.",
        "back": "🔙 Back",
        "cancel": "❌ Cancel",
        "done": "✅ Done",
        "select": "Select",
        "end_day": "End Day",
        "in_progress": "🧠 Generating today's schedule... Please wait.",
        "lang_persian": "🇮🇷 فارسی",
        "lang_english": "🇬🇧 English",
        "no_plan_active": "📭 No active plans found.",
        "task_toggle_done": "✅ Done!",
    }
}

# ============================================================
# Helper Functions
# ============================================================

def get_lang(chat_id: str) -> str:
    user = db.get_user(chat_id)
    return user["lang"] if user and user.get("lang") else "fa"

def get_text(chat_id: str, key: str, **kwargs) -> str:
    lang = get_lang(chat_id)
    text = LANG.get(lang, LANG["fa"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def persian_to_english_digits(text: str) -> str:
    persian_map = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    return ''.join(persian_map.get(c, c) for c in text)

def validate_time(time_str: str) -> bool:
    normalized = persian_to_english_digits(time_str)
    return bool(re.match(r"^([01]?[0-9]|2[0-3]):([0-5][0-9])$", normalized))

# ============================================================
# Date Utilities (Jalali & Gregorian)
# ============================================================

def get_today_jalali() -> str:
    try:
        import jdatetime
        today = jdatetime.date.today()
        return f"{today.year}/{str(today.month).zfill(2)}/{str(today.day).zfill(2)}"
    except:
        now = datetime.now()
        tehran = now + timedelta(hours=3, minutes=30)
        return f"{tehran.year - 621}/{str(tehran.month).zfill(2)}/{str(tehran.day).zfill(2)}"

def get_today_gregorian() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_today_date(chat_id: str) -> str:
    lang = get_lang(chat_id)
    if lang == "fa":
        return get_today_jalali()
    else:
        return get_today_gregorian()

def jalali_to_gregorian(jalali_date: str) -> Optional[datetime]:
    try:
        import jdatetime
        parts = jalali_date.split('/')
        if len(parts) != 3:
            return None
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        jd = jdatetime.date(year, month, day)
        gd = jd.togregorian()
        return datetime(gd.year, gd.month, gd.day)
    except:
        return None

def gregorian_to_jalali_display(gregorian_date: str) -> str:
    try:
        parts = gregorian_date.split('-')
        if len(parts) != 3:
            return gregorian_date
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        gd = datetime(year, month, day)
        import jdatetime
        jd = jdatetime.date.fromgregorian(date=gd.date())
        return f"{jd.year}/{str(jd.month).zfill(2)}/{str(jd.day).zfill(2)}"
    except:
        return gregorian_date

def validate_jalali_date(date_str: str) -> bool:
    try:
        import jdatetime
        parts = date_str.split('/')
        if len(parts) != 3:
            return False
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        jdatetime.date(year, month, day)
        return True
    except:
        return False

def validate_gregorian_date(date_str: str) -> bool:
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        datetime(year, month, day)
        return True
    except:
        return False

def validate_date(chat_id: str, date_str: str) -> bool:
    lang = get_lang(chat_id)
    if lang == "fa":
        return validate_jalali_date(date_str)
    else:
        return validate_gregorian_date(date_str)

def get_date_range(chat_id: str, start_date: str, end_date: str) -> List[str]:
    lang = get_lang(chat_id)
    dates = []
    if lang == "fa":
        start = jalali_to_gregorian(start_date)
        end = jalali_to_gregorian(end_date)
        if not start or not end:
            return []
        current = start
        while current <= end:
            dates.append(gregorian_to_jalali_display(current.strftime("%Y-%m-%d")))
            current += timedelta(days=1)
    else:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            current = start
            while current <= end:
                dates.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=1)
        except:
            return []
    return dates

def get_day_of_week(chat_id: str) -> str:
    lang = get_lang(chat_id)
    now = datetime.now()
    if lang == "fa":
        days = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
    else:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[now.weekday()]

# ============================================================
# AI Handler
# ============================================================

class AIHandler:
    def __init__(self):
        self.gemini_available = False
        self.openrouter_available = False
        self.tgpt_available = False
        self.current_provider = "None"

        try:
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                import google.generativeai as genai
                if GEMINI_API_KEY and "AIza" in GEMINI_API_KEY:
                    genai.configure(api_key=GEMINI_API_KEY)
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                    self.gemini_available = True
                    self.current_provider = "Gemini"
                    print("✅ Gemini AI initialized.")
        except Exception as e:
            print(f"⚠️ Gemini unavailable: {e}")

        if not self.gemini_available:
            try:
                import openai
                if OPENROUTER_API_KEY and "sk-or" in OPENROUTER_API_KEY:
                    self.openrouter_client = openai.OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=OPENROUTER_API_KEY,
                    )
                    self.openrouter_available = True
                    self.current_provider = "OpenRouter"
                    print("✅ OpenRouter AI initialized.")
            except Exception as e:
                print(f"⚠️ OpenRouter unavailable: {e}")

        if not self.gemini_available and not self.openrouter_available:
            try:
                from pytgpt.leo import LEO
                self.tgpt_bot = LEO()
                self.tgpt_available = True
                self.current_provider = "python-tgpt"
                print("✅ python-tgpt initialized.")
            except Exception as e:
                print(f"⚠️ python-tgpt unavailable: {e}")

    async def generate_schedule(self, tasks: List[str], wake_time: str, sleep_time: str, date: str, lang: str = "fa") -> str:
        if not tasks:
            return "امروز هیچ تسکی ندارید. روز خوبی داشته باشید!" if lang == "fa" else "No tasks for today. Have a great day!"

        prompt_lang = "Persian" if lang == "fa" else "English"
        prompt = f"""
Date: {date}
Wake time: {wake_time}
Sleep time: {sleep_time}
Today's tasks: {', '.join(tasks)}

Please create a logical and human-friendly schedule for these tasks. Follow these rules:
- After waking up, include at least 30 minutes for preparation (breakfast, prayer, planning).
- Lunch time around 12:30 - 13:30.
- Prayer time around 13:00.
- If a task requires more than 2 hours, split it into 2-hour sessions with **30-minute breaks** between sessions.
- Between any two study sessions, put at least **30 minutes break**.
- Maximum study time per day is 6 hours.
- Respond in {prompt_lang}.

Today's Schedule:
🕐 07:30 - 08:00: Preparation
🕘 08:00 - 10:00: [Task 1] (Session 1)
🕙 10:00 - 10:30: Break (30 min)
🕙 10:30 - 12:30: [Task 1] (Session 2)
🕧 12:30 - 13:30: Lunch & Prayer
🕜 13:30 - 15:30: [Task 2] (Session 1)
... etc.
"""

        if self.gemini_available:
            try:
                return self.gemini_model.generate_content(prompt).text
            except Exception as e:
                print(f"⚠️ Gemini error: {e}")

        if self.openrouter_available:
            try:
                completion = self.openrouter_client.chat.completions.create(
                    model="qwen/qwen-2.5-7b-instruct:free",
                    messages=[
                        {"role": "system", "content": f"You are a study planner assistant. Respond in {prompt_lang}."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"⚠️ OpenRouter error: {e}")

        if self.tgpt_available:
            try:
                return self.tgpt_bot.chat(prompt)
            except Exception as e:
                print(f"⚠️ python-tgpt error: {e}")

        return self._simple_schedule(tasks, wake_time, sleep_time, lang)

    def _simple_schedule(self, tasks: List[str], wake_time: str, sleep_time: str, lang: str = "fa") -> str:
        try:
            wh, wm = map(int, wake_time.split(':'))
            sh, sm = map(int, sleep_time.split(':'))
            total_minutes = (sh * 60 + sm) - (wh * 60 + wm)
            prep_time = 30
            lunch_time = 60
            total_available = total_minutes - prep_time - lunch_time
            study_time = min(360, max(0, total_available))
        except:
            study_time = 360
            wh, wm = 7, 0

        if not tasks:
            return "امروز هیچ تسکی ندارید. روز خوبی داشته باشید!" if lang == "fa" else "No tasks today. Have a great day!"

        minutes_per_task = max(30, study_time // len(tasks))
        
        if lang == "fa":
            schedule = f"📅 *برنامه امروز*\n\n"
            schedule += f"⏰ بیداری: {wake_time} | خواب: {sleep_time}\n\n"
            current = datetime.now().replace(hour=wh, minute=wm)
            schedule += f"🕐 {current.strftime('%H:%M')} - {(current + timedelta(minutes=prep_time)).strftime('%H:%M')}: آماده‌سازی (صبحانه، نماز)\n"
            current += timedelta(minutes=prep_time)
            for task in tasks:
                remaining = minutes_per_task
                session_num = 1
                while remaining > 0:
                    session = min(remaining, 120)
                    start = current.strftime("%H:%M")
                    current += timedelta(minutes=session)
                    end = current.strftime("%H:%M")
                    schedule += f"🕐 {start} - {end}: *{task}* (جلسه {session_num})\n"
                    remaining -= session
                    session_num += 1
                    if remaining > 0:
                        current += timedelta(minutes=30)
                        schedule += f"☕ {current.strftime('%H:%M')} - {(current + timedelta(minutes=30)).strftime('%H:%M')}: استراحت (۳۰ دقیقه)\n"
                        current += timedelta(minutes=30)
                    if current.hour == 12 and current.minute >= 30:
                        schedule += f"🍽️ {current.strftime('%H:%M')} - {(current + timedelta(minutes=60)).strftime('%H:%M')}: ناهار و نماز\n"
                        current += timedelta(minutes=60)
            schedule += f"\n📊 جمع ساعت مطالعه: {study_time // 60} ساعت و {study_time % 60} دقیقه"
        else:
            schedule = f"📅 *Today's Schedule*\n\n"
            schedule += f"⏰ Wake: {wake_time} | Sleep: {sleep_time}\n\n"
            current = datetime.now().replace(hour=wh, minute=wm)
            schedule += f"🕐 {current.strftime('%H:%M')} - {(current + timedelta(minutes=prep_time)).strftime('%H:%M')}: Preparation (Breakfast, Prayer)\n"
            current += timedelta(minutes=prep_time)
            for task in tasks:
                remaining = minutes_per_task
                session_num = 1
                while remaining > 0:
                    session = min(remaining, 120)
                    start = current.strftime("%H:%M")
                    current += timedelta(minutes=session)
                    end = current.strftime("%H:%M")
                    schedule += f"🕐 {start} - {end}: *{task}* (Session {session_num})\n"
                    remaining -= session
                    session_num += 1
                    if remaining > 0:
                        current += timedelta(minutes=30)
                        schedule += f"☕ {current.strftime('%H:%M')} - {(current + timedelta(minutes=30)).strftime('%H:%M')}: Break (30 min)\n"
                        current += timedelta(minutes=30)
                    if current.hour == 12 and current.minute >= 30:
                        schedule += f"🍽️ {current.strftime('%H:%M')} - {(current + timedelta(minutes=60)).strftime('%H:%M')}: Lunch & Prayer\n"
                        current += timedelta(minutes=60)
            schedule += f"\n📊 Total study time: {study_time // 60}h {study_time % 60}m"
        return schedule

ai_handler = AIHandler()

# ============================================================
# Data Models
# ============================================================

@dataclass
class Task:
    id: int
    name: str

@dataclass
class DayTasks:
    date: str
    tasks: List[Task] = field(default_factory=list)

@dataclass
class Plan:
    id: int
    chat_id: str
    title: str
    start_date: str
    end_date: str
    days: List[DayTasks] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = 'active'

@dataclass
class DailyLog:
    date: str
    wake_time: str = ""
    sleep_time: str = ""
    mood: str = ""
    energy: str = ""
    answers: Dict[str, str] = field(default_factory=dict)
    task_status: Dict[int, bool] = field(default_factory=dict)
    total_tests: int = 0
    wrong_tests: int = 0
    correct_tests: int = 0
    test_accuracy: int = 0
    submitted_to_consultant: bool = False

# ============================================================
# SQLite Database
# ============================================================

class Database:
    def __init__(self, db_path: str = "planner.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id TEXT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                role TEXT DEFAULT 'user',
                lang TEXT DEFAULT 'fa',
                report_group_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                title TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plan_days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_day_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (plan_day_id) REFERENCES plan_days(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                chat_id TEXT NOT NULL,
                date TEXT NOT NULL,
                wake_time TEXT DEFAULT '',
                sleep_time TEXT DEFAULT '',
                mood TEXT DEFAULT '',
                energy TEXT DEFAULT '',
                answers TEXT DEFAULT '{}',
                task_status TEXT DEFAULT '{}',
                total_tests INTEGER DEFAULT 0,
                wrong_tests INTEGER DEFAULT 0,
                correct_tests INTEGER DEFAULT 0,
                test_accuracy INTEGER DEFAULT 0,
                submitted_to_consultant INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, date)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_states (
                chat_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                data TEXT DEFAULT '{}',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ SQLite Database initialized.")

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    # ---------- User Management ----------
    def get_or_create_user(self, chat_id: str, username: str = None, first_name: str = None) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute(
                "UPDATE users SET username = COALESCE(?, username), first_name = COALESCE(?, first_name) WHERE chat_id = ?",
                (username, first_name, chat_id)
            )
            conn.commit()
            conn.close()
            return {
                "chat_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "role": row[3],
                "lang": row[4] if len(row) > 4 else "fa",
                "report_group_id": row[5] if len(row) > 5 else None,
                "created_at": row[6] if len(row) > 6 else datetime.now().isoformat()
            }
        else:
            role = 'owner' if username and username.lower() == OWNER_USERNAME.lower() else 'user'
            cursor.execute(
                "INSERT INTO users (chat_id, username, first_name, role, lang) VALUES (?, ?, ?, ?, ?)",
                (chat_id, username, first_name, role, "fa")
            )
            conn.commit()
            conn.close()
            return {
                "chat_id": chat_id,
                "username": username,
                "first_name": first_name,
                "role": role,
                "lang": "fa",
                "report_group_id": None,
                "created_at": datetime.now().isoformat()
            }

    def set_user_lang(self, chat_id: str, lang: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET lang = ? WHERE chat_id = ?", (lang, chat_id))
        conn.commit()
        conn.close()

    def set_user_role(self, chat_id: str, role: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE chat_id = ?", (role, chat_id))
        conn.commit()
        conn.close()

    def get_user_by_username(self, username: str) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "chat_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "role": row[3],
                "lang": row[4] if len(row) > 4 else "fa",
                "report_group_id": row[5] if len(row) > 5 else None,
                "created_at": row[6] if len(row) > 6 else datetime.now().isoformat()
            }
        return None

    def get_user(self, chat_id: str) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "chat_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "role": row[3],
                "lang": row[4] if len(row) > 4 else "fa",
                "report_group_id": row[5] if len(row) > 5 else None,
                "created_at": row[6] if len(row) > 6 else datetime.now().isoformat()
            }
        return None

    def is_authorized(self, chat_id: str) -> bool:
        user = self.get_user(chat_id)
        if not user:
            return False
        return user["role"] in ("owner", "admin")

    def is_owner(self, chat_id: str) -> bool:
        user = self.get_user(chat_id)
        if not user:
            return False
        return user["role"] == "owner"

    # ---------- Report Group ----------
    def set_report_group(self, chat_id: str, group_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET report_group_id = ? WHERE chat_id = ?", (group_id, chat_id))
        conn.commit()
        conn.close()

    def get_report_group(self, chat_id: str) -> Optional[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT report_group_id FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    # ---------- Plans ----------
    def add_plan(self, chat_id: str, plan: Plan) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO plans (chat_id, title, start_date, end_date, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, plan.title, plan.start_date, plan.end_date, plan.status, plan.created_at)
        )
        plan_id = cursor.lastrowid
        for day in plan.days:
            cursor.execute(
                "INSERT INTO plan_days (plan_id, date) VALUES (?, ?)",
                (plan_id, day.date)
            )
            day_id = cursor.lastrowid
            for task in day.tasks:
                cursor.execute(
                    "INSERT INTO tasks (plan_day_id, name) VALUES (?, ?)",
                    (day_id, task.name)
                )
        conn.commit()
        conn.close()
        return plan_id

    def get_plans(self, chat_id: str) -> List[Plan]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, start_date, end_date, status, created_at FROM plans WHERE chat_id = ? ORDER BY created_at DESC",
            (chat_id,)
        )
        plan_rows = cursor.fetchall()
        plans = []
        for plan_row in plan_rows:
            plan_id, title, start_date, end_date, status, created_at = plan_row
            cursor.execute("SELECT id, date FROM plan_days WHERE plan_id = ?", (plan_id,))
            day_rows = cursor.fetchall()
            days = []
            for day_row in day_rows:
                day_id, date = day_row
                cursor.execute("SELECT id, name FROM tasks WHERE plan_day_id = ?", (day_id,))
                task_rows = cursor.fetchall()
                tasks = [Task(id=t[0], name=t[1]) for t in task_rows]
                days.append(DayTasks(date=date, tasks=tasks))
            plans.append(Plan(
                id=plan_id,
                chat_id=chat_id,
                title=title,
                start_date=start_date,
                end_date=end_date,
                days=days,
                created_at=created_at,
                status=status
            ))
        conn.close()
        return plans

    def get_active_plans(self, chat_id: str) -> List[Plan]:
        return [p for p in self.get_plans(chat_id) if p.status == 'active']

    def get_plan_by_id(self, chat_id: str, plan_id: int) -> Optional[Plan]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, start_date, end_date, status, created_at FROM plans WHERE chat_id = ? AND id = ?",
            (chat_id, plan_id)
        )
        plan_row = cursor.fetchone()
        if not plan_row:
            conn.close()
            return None
        plan_id, title, start_date, end_date, status, created_at = plan_row
        cursor.execute("SELECT id, date FROM plan_days WHERE plan_id = ?", (plan_id,))
        day_rows = cursor.fetchall()
        days = []
        for day_row in day_rows:
            day_id, date = day_row
            cursor.execute("SELECT id, name FROM tasks WHERE plan_day_id = ?", (day_id,))
            task_rows = cursor.fetchall()
            tasks = [Task(id=t[0], name=t[1]) for t in task_rows]
            days.append(DayTasks(date=date, tasks=tasks))
        conn.close()
        return Plan(
            id=plan_id,
            chat_id=chat_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            days=days,
            created_at=created_at,
            status=status
        )

    def delete_plan(self, chat_id: str, plan_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plans WHERE chat_id = ? AND id = ?", (chat_id, plan_id))
        conn.commit()
        conn.close()

    def get_tasks_for_date(self, chat_id: str, date: str) -> List[Task]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.name FROM tasks t
            JOIN plan_days pd ON t.plan_day_id = pd.id
            JOIN plans p ON pd.plan_id = p.id
            WHERE p.chat_id = ? AND p.status = 'active' AND pd.date = ?
        ''', (chat_id, date))
        rows = cursor.fetchall()
        conn.close()
        return [Task(id=r[0], name=r[1]) for r in rows]

    # ---------- Daily Logs ----------
    def save_daily_log(self, chat_id: str, log: DailyLog):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_logs (
                chat_id, date, wake_time, sleep_time, mood, energy, answers,
                task_status, total_tests, wrong_tests, correct_tests,
                test_accuracy, submitted_to_consultant
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chat_id, log.date, log.wake_time, log.sleep_time, log.mood, log.energy,
            json.dumps(log.answers, ensure_ascii=False),
            json.dumps(log.task_status),
            log.total_tests, log.wrong_tests, log.correct_tests,
            log.test_accuracy, 1 if log.submitted_to_consultant else 0
        ))
        conn.commit()
        conn.close()
        print(f"📌 [DB] Daily log saved for {chat_id} on {log.date}")

    def get_daily_log(self, chat_id: str, date: str) -> Optional[DailyLog]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT wake_time, sleep_time, mood, energy, answers, task_status,
                   total_tests, wrong_tests, correct_tests, test_accuracy, submitted_to_consultant
            FROM daily_logs WHERE chat_id = ? AND date = ?
        ''', (chat_id, date))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return DailyLog(
            date=date,
            wake_time=row[0],
            sleep_time=row[1],
            mood=row[2],
            energy=row[3],
            answers=json.loads(row[4]),
            task_status={int(k): v for k, v in json.loads(row[5]).items()},
            total_tests=row[6],
            wrong_tests=row[7],
            correct_tests=row[8],
            test_accuracy=row[9],
            submitted_to_consultant=bool(row[10])
        )

    def get_today_log(self, chat_id: str) -> Optional[DailyLog]:
        today = get_today_date(chat_id)
        return self.get_daily_log(chat_id, today)

    def mark_log_submitted(self, chat_id: str, date: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE daily_logs SET submitted_to_consultant = 1 WHERE chat_id = ? AND date = ?",
            (chat_id, date)
        )
        conn.commit()
        conn.close()

    def get_all_chat_ids(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT chat_id FROM daily_logs")
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    # ---------- User States ----------
    def set_state(self, chat_id: str, state: str, data: dict = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_states (chat_id, state, data, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (chat_id, state, json.dumps(data or {}, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
        print(f"📌 [DB] State set for {chat_id}: {state}")

    def get_state(self, chat_id: str) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT state, data FROM user_states WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {"state": row[0], "data": json.loads(row[1])}

    def clear_state(self, chat_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_states WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        print(f"📌 [DB] State cleared for {chat_id}")

db = Database("planner.db")

# ============================================================
# Utility Functions for Reports & Display
# ============================================================

def mood_emoji(mood: str) -> str:
    emojis = {'bad': '😞', 'ok': '😐', 'good': '😊', 'excellent': '🤩'}
    return emojis.get(mood, '😐')

def energy_emoji(energy: str) -> str:
    emojis = {'low': '🔋 کم', 'medium': '🔋 متوسط', 'high': '🔋 زیاد'}
    return emojis.get(energy, '🔋')

def generate_daily_report(chat_id: str, date: str, log: DailyLog, tasks: List[Task]) -> str:
    lang = get_lang(chat_id)
    date_display = date
    
    if lang == "fa":
        msg = f"📊 *گزارش عملکرد روزانه - {date_display}*\n\n"
        msg += "─────────────────\n"
        msg += f"⏰ *ساعت بیداری:* {log.wake_time}\n"
        msg += f"🕛 *ساعت خواب:* {log.sleep_time}\n"
        msg += f"😊 *وضعیت روحی:* {mood_emoji(log.mood)}\n"
        msg += f"⚡ *انرژی:* {energy_emoji(log.energy)}\n\n"
        if tasks:
            msg += "📚 *وضعیت تسک‌های امروز:*\n"
            for task in tasks:
                status = "✅ انجام شده" if log.task_status.get(task.id, False) else "⏳ انجام نشده"
                msg += f"{status} - {task.name}\n"
            msg += "\n"
        else:
            msg += "📭 امروز هیچ تسکی نداشتید.\n\n"
        if log.total_tests > 0:
            msg += "🧪 *آمار تست‌های امروز:*\n"
            msg += f"📝 کل تست: {log.total_tests}\n"
            msg += f"❌ غلط: {log.wrong_tests}\n"
            msg += f"✅ صحیح: {log.correct_tests}\n"
            msg += f"🎯 درصد صحت: {log.test_accuracy}%\n\n"
        else:
            msg += "🧪 امروز تستی ثبت نشده است.\n\n"
        if log.answers:
            msg += "📝 *پاسخ به سوالات:*\n"
            for q, a in log.answers.items():
                msg += f"❓ {q}\n➡️ {a}\n"
            msg += "\n"
        msg += "─────────────────\n"
        msg += "🕛 این گزارش به‌صورت خودکار برای مشاور ارسال شد."
    else:
        msg = f"📊 *Daily Performance Report - {date_display}*\n\n"
        msg += "─────────────────\n"
        msg += f"⏰ *Wake-up:* {log.wake_time}\n"
        msg += f"🕛 *Sleep:* {log.sleep_time}\n"
        msg += f"😊 *Mood:* {mood_emoji(log.mood)}\n"
        msg += f"⚡ *Energy:* {energy_emoji(log.energy)}\n\n"
        if tasks:
            msg += "📚 *Today's Tasks:*\n"
            for task in tasks:
                status = "✅ Done" if log.task_status.get(task.id, False) else "⏳ Pending"
                msg += f"{status} - {task.name}\n"
            msg += "\n"
        else:
            msg += "📭 You had no tasks today.\n\n"
        if log.total_tests > 0:
            msg += "🧪 *Today's Test Stats:*\n"
            msg += f"📝 Total: {log.total_tests}\n"
            msg += f"❌ Wrong: {log.wrong_tests}\n"
            msg += f"✅ Correct: {log.correct_tests}\n"
            msg += f"🎯 Accuracy: {log.test_accuracy}%\n\n"
        else:
            msg += "🧪 No tests logged today.\n\n"
        if log.answers:
            msg += "📝 *Custom Questions:*\n"
            for q, a in log.answers.items():
                msg += f"❓ {q}\n➡️ {a}\n"
            msg += "\n"
        msg += "─────────────────\n"
        msg += "🕛 This report was automatically sent to your consultant."
    return msg

# ============================================================
# Keyboards (Multi-Language)
# ============================================================

def main_menu(chat_id: str = None):
    lang = get_lang(chat_id) if chat_id else "fa"
    
    if lang == "fa":
        keyboard = [
            [InlineKeyboardButton("➕ برنامه جدید", callback_data="new_plan")],
            [InlineKeyboardButton("📋 لیست برنامه‌ها", callback_data="list_plans")],
            [InlineKeyboardButton("📝 ثبت گزارش روزانه", callback_data="daily_report")],
            [InlineKeyboardButton("⏰ برنامه امروز (توسط AI)", callback_data="today_schedule")],
            [InlineKeyboardButton("✅ مدیریت تسک‌های امروز", callback_data="manage_tasks")],
            [InlineKeyboardButton("🧪 ثبت تست روزانه", callback_data="test_log")],
            [InlineKeyboardButton("👥 تنظیم گروه گزارش", callback_data="menu_set_group")],
            [InlineKeyboardButton("❌ حذف برنامه", callback_data="delete_plan")],
            [InlineKeyboardButton("🌐 تغییر زبان / Change Language", callback_data="change_lang")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("➕ New Plan", callback_data="new_plan")],
            [InlineKeyboardButton("📋 My Plans", callback_data="list_plans")],
            [InlineKeyboardButton("📝 Daily Report", callback_data="daily_report")],
            [InlineKeyboardButton("⏰ Today's Schedule (AI)", callback_data="today_schedule")],
            [InlineKeyboardButton("✅ Today's Tasks", callback_data="manage_tasks")],
            [InlineKeyboardButton("🧪 Test Log", callback_data="test_log")],
            [InlineKeyboardButton("👥 Set Report Group", callback_data="menu_set_group")],
            [InlineKeyboardButton("❌ Delete Plan", callback_data="delete_plan")],
            [InlineKeyboardButton("🌐 تغییر زبان / Change Language", callback_data="change_lang")],
        ]
    return InlineKeyboardMarkup(keyboard)

def mood_keyboard(chat_id: str = None):
    lang = get_lang(chat_id) if chat_id else "fa"
    if lang == "fa":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("😞 بد", callback_data="mood_bad"),
             InlineKeyboardButton("😐 معمولی", callback_data="mood_ok")],
            [InlineKeyboardButton("😊 خوب", callback_data="mood_good"),
             InlineKeyboardButton("🤩 عالی", callback_data="mood_excellent")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("😞 Bad", callback_data="mood_bad"),
             InlineKeyboardButton("😐 Okay", callback_data="mood_ok")],
            [InlineKeyboardButton("😊 Good", callback_data="mood_good"),
             InlineKeyboardButton("🤩 Excellent", callback_data="mood_excellent")]
        ])

def energy_keyboard(chat_id: str = None):
    lang = get_lang(chat_id) if chat_id else "fa"
    if lang == "fa":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔋 کم", callback_data="energy_low"),
             InlineKeyboardButton("🔋 متوسط", callback_data="energy_medium")],
            [InlineKeyboardButton("🔋 زیاد", callback_data="energy_high")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔋 Low", callback_data="energy_low"),
             InlineKeyboardButton("🔋 Medium", callback_data="energy_medium")],
            [InlineKeyboardButton("🔋 High", callback_data="energy_high")]
        ])

def select_plan_keyboard(plans: List[Plan], action: str, chat_id: str = None):
    lang = get_lang(chat_id) if chat_id else "fa"
    keyboard = []
    for plan in plans:
        keyboard.append([InlineKeyboardButton(f"{plan.title} ({plan.start_date} - {plan.end_date})", callback_data=f"{action}_{plan.id}")])
    back_text = "🔙 بازگشت" if lang == "fa" else "🔙 Back"
    keyboard.append([InlineKeyboardButton(back_text, callback_data="menu_main")])
    return InlineKeyboardMarkup(keyboard)

def language_select_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ])

# ============================================================
# Handlers
# ============================================================

# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user = update.effective_user
    username = user.username
    first_name = user.first_name

    user_data = db.get_or_create_user(chat_id, username, first_name)
    lang = user_data.get("lang", "fa")

    if not user_data.get("lang"):
        await update.message.reply_text(
            "🌐 Please select your language:\nلطفاً زبان خود را انتخاب کنید:",
            reply_markup=language_select_keyboard()
        )
        return

    if user_data["role"] == "owner":
        await update.message.reply_text(
            get_text(chat_id, "start_owner"),
            reply_markup=main_menu(chat_id)
        )
    else:
        await update.message.reply_text(
            get_text(chat_id, "start_user"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(chat_id, "request_access"), callback_data="request_access")]
            ])
        )
        try:
            owner_chat = await context.bot.get_chat(f"@{OWNER_USERNAME}")
            owner_id = owner_chat.id
            await context.bot.send_message(
                chat_id=owner_id,
                text=get_text(chat_id, "notify_new_user",
                    id=chat_id,
                    name=first_name,
                    username=username if username else "None",
                    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    user=username if username else chat_id
                ),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            print(f"⚠️ Error notifying owner: {e}")

# ---------- Language Selection ----------
async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    lang = query.data.replace("lang_", "")
    
    db.set_user_lang(chat_id, lang)
    
    if lang == "fa":
        await query.edit_message_text("✅ زبان به فارسی تغییر یافت.", reply_markup=main_menu(chat_id))
    else:
        await query.edit_message_text("✅ Language changed to English.", reply_markup=main_menu(chat_id))

# ---------- Change Language (from menu) ----------
async def change_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    
    await query.edit_message_text(
        "🌐 Please select your language:\nلطفاً زبان خود را انتخاب کنید:",
        reply_markup=language_select_keyboard()
    )

# ---------- Menu Main ----------
async def menu_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)

    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "access_denied"))
        return

    await query.edit_message_text(get_text(chat_id, "main_menu"), reply_markup=main_menu(chat_id))

# ---------- Request Access ----------
async def request_access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    user = update.effective_user

    try:
        owner_chat = await context.bot.get_chat(f"@{OWNER_USERNAME}")
        owner_id = owner_chat.id
        await context.bot.send_message(
            chat_id=owner_id,
            text=get_text(chat_id, "notify_new_user",
                id=chat_id,
                name=user.first_name,
                username=user.username if user.username else "None",
                time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                user=user.username if user.username else chat_id
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        await query.edit_message_text(get_text(chat_id, "request_sent"), reply_markup=main_menu(chat_id))
    except Exception as e:
        await query.edit_message_text(get_text(chat_id, "request_error", error=str(e)))

# ---------- Claim Token ----------
async def claimtoken_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if not context.args:
        await update.message.reply_text(get_text(chat_id, "claim_usage"))
        return

    token = context.args[0].strip()
    if token == OWNER_TOKEN:
        db.set_user_role(chat_id, "owner")
        await update.message.reply_text(get_text(chat_id, "claim_success"))
    else:
        await update.message.reply_text(get_text(chat_id, "claim_failed"))

# ---------- Add User (Owner only) ----------
async def adduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if not db.is_owner(chat_id):
        await update.message.reply_text(get_text(chat_id, "owner_only"))
        return

    if not context.args:
        await update.message.reply_text(get_text(chat_id, "adduser_usage"))
        return

    target = context.args[0].strip()
    if target.startswith('@'):
        target = target[1:]

    try:
        if target.isdigit():
            target_chat_id = target
            user_data = db.get_user(target_chat_id)
        else:
            user_data = db.get_user_by_username(target)

        if not user_data:
            try:
                chat = await context.bot.get_chat(f"@{target}" if not target.isdigit() else int(target))
                target_chat_id = str(chat.id)
                username = chat.username
                first_name = chat.first_name
                user_data = db.get_or_create_user(target_chat_id, username, first_name)
            except Exception as e:
                await update.message.reply_text(get_text(chat_id, "user_not_found", error=str(e)))
                return

        db.set_user_role(user_data["chat_id"], "admin")
        await update.message.reply_text(
            get_text(chat_id, "user_added",
                name=user_data['first_name'],
                username=user_data['username'],
                id=user_data['chat_id']
            ),
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            await context.bot.send_message(
                chat_id=user_data["chat_id"],
                text=get_text(user_data["chat_id"], "access_granted")
            )
        except Exception as e:
            await update.message.reply_text(f"⚠️ Could not notify user: {e}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ---------- New Plan ----------
async def new_plan_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)

    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    db.set_state(chat_id, "plan_title", {})
    back_text = "🔙 انصراف" if get_lang(chat_id) == "fa" else "🔙 Cancel"
    await query.edit_message_text(
        get_text(chat_id, "plan_title"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(back_text, callback_data="menu_main")]])
    )

# ---------- Handle Plan Text ----------
async def handle_plan_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "no_access"))
        return

    state = db.get_state(chat_id)
    if not state or state["state"].startswith("daily_") or state["state"].startswith("test_"):
        return
    text = update.message.text.strip()
    data = state.get("data", {})
    state_name = state["state"]

    if state_name == "plan_title":
        data["title"] = text
        db.set_state(chat_id, "plan_start_date", data)
        await update.message.reply_text(get_text(chat_id, "plan_start_date"))

    elif state_name == "plan_start_date":
        if not validate_date(chat_id, text):
            await update.message.reply_text(get_text(chat_id, "invalid_date"))
            return
        data["start_date"] = text
        db.set_state(chat_id, "plan_end_date", data)
        await update.message.reply_text(get_text(chat_id, "plan_end_date"))

    elif state_name == "plan_end_date":
        if not validate_date(chat_id, text):
            await update.message.reply_text(get_text(chat_id, "invalid_date"))
            return
        data["end_date"] = text
        date_list = get_date_range(chat_id, data["start_date"], text)
        if not date_list:
            await update.message.reply_text(get_text(chat_id, "invalid_range"))
            return
        data["date_list"] = date_list
        data["days_tasks"] = {}
        data["current_date_index"] = 0
        first_date = date_list[0]
        db.set_state(chat_id, "plan_day_tasks", data)
        await update.message.reply_text(
            get_text(chat_id, "plan_tasks", date=first_date)
        )

    elif state_name == "plan_day_tasks":
        data = state.get("data", {})
        date_list = data.get("date_list", [])
        current_idx = data.get("current_date_index", 0)
        current_date = date_list[current_idx]
        days_tasks = data.get("days_tasks", {})
        if current_date not in days_tasks:
            days_tasks[current_date] = []

        end_day = "پایان روز" if get_lang(chat_id) == "fa" else "End Day"
        if text.lower() == end_day.lower():
            if not days_tasks[current_date]:
                await update.message.reply_text(get_text(chat_id, "min_one_task"))
                return
            next_idx = current_idx + 1
            if next_idx < len(date_list):
                data["current_date_index"] = next_idx
                data["days_tasks"] = days_tasks
                db.set_state(chat_id, "plan_day_tasks", data)
                await update.message.reply_text(
                    get_text(chat_id, "tasks_saved", date=current_date) + "\n\n" +
                    get_text(chat_id, "plan_tasks", date=date_list[next_idx])
                )
            else:
                days = []
                for date in date_list:
                    tasks = [Task(id=0, name=t) for t in days_tasks.get(date, [])]
                    days.append(DayTasks(date=date, tasks=tasks))
                plan = Plan(
                    id=0,
                    chat_id=chat_id,
                    title=data["title"],
                    start_date=data["start_date"],
                    end_date=data["end_date"],
                    days=days,
                    created_at=datetime.now().isoformat(),
                    status='active'
                )
                db.add_plan(chat_id, plan)
                db.clear_state(chat_id)
                await update.message.reply_text(
                    get_text(chat_id, "plan_saved", title=plan.title, days=len(days)),
                    reply_markup=main_menu(chat_id)
                )
            return

        days_tasks[current_date].append(text)
        data["days_tasks"] = days_tasks
        db.set_state(chat_id, "plan_day_tasks", data)
        await update.message.reply_text(get_text(chat_id, "task_added", task=text))

# ---------- Cancel Plan ----------
async def cancel_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return
    db.clear_state(chat_id)
    await query.edit_message_text(get_text(chat_id, "cancel"), reply_markup=main_menu(chat_id))

# ---------- List Plans ----------
async def list_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    plans = db.get_plans(chat_id)
    if not plans:
        await query.edit_message_text(get_text(chat_id, "no_plans"), reply_markup=main_menu(chat_id))
        return
    msg = get_text(chat_id, "plan_list")
    for p in plans:
        status = get_text(chat_id, "active") if p.status == 'active' else get_text(chat_id, "completed")
        total_tasks = sum(len(day.tasks) for day in p.days)
        msg += f"• *{p.title}* ({p.start_date} - {p.end_date}) - {status}\n"
        msg += f"  {get_text(chat_id, 'days_count', days=len(p.days), tasks=total_tasks)}\n\n"
    await query.edit_message_text(msg, reply_markup=main_menu(chat_id), parse_mode=ParseMode.MARKDOWN)

# ---------- Manage Tasks ----------
async def manage_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    today = get_today_date(chat_id)
    tasks = db.get_tasks_for_date(chat_id, today)
    if not tasks:
        await query.edit_message_text(
            get_text(chat_id, "no_tasks_today", date=today),
            reply_markup=main_menu(chat_id)
        )
        return
    log = db.get_today_log(chat_id)
    if not log:
        log = DailyLog(date=today)
        db.save_daily_log(chat_id, log)
    keyboard = []
    for task in tasks:
        status = log.task_status.get(task.id, False)
        status_text = get_text(chat_id, "task_done") if status else get_text(chat_id, "task_pending")
        keyboard.append([InlineKeyboardButton(f"{task.name} - {status_text}", callback_data=f"task_toggle_{task.id}")])
    keyboard.append([InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_main")])
    try:
        await query.edit_message_text(
            get_text(chat_id, "manage_today", date=today),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except tg_error.BadRequest as e:
        if "Message is not modified" in str(e):
            await query.answer(get_text(chat_id, "status_changed"))
        else:
            raise

async def task_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.answer(get_text(chat_id, "no_access"), show_alert=True)
        return

    task_id = int(query.data.replace("task_toggle_", ""))
    today = get_today_date(chat_id)
    log = db.get_today_log(chat_id)
    if not log:
        log = DailyLog(date=today)
        db.save_daily_log(chat_id, log)
    log.task_status[task_id] = not log.task_status.get(task_id, False)
    db.save_daily_log(chat_id, log)
    await query.answer(get_text(chat_id, "status_changed"))
    await manage_tasks(update, context)

# ---------- Today Schedule (AI) ----------
async def today_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    today = get_today_date(chat_id)
    log = db.get_today_log(chat_id)
    if not log or not log.wake_time or not log.sleep_time:
        await query.edit_message_text(
            get_text(chat_id, "schedule_need_log"),
            reply_markup=main_menu(chat_id)
        )
        return
    tasks = db.get_tasks_for_date(chat_id, today)
    if not tasks:
        await query.edit_message_text(
            get_text(chat_id, "no_tasks_today", date=today),
            reply_markup=main_menu(chat_id)
        )
        return
    
    await query.edit_message_text(get_text(chat_id, "in_progress"))
    try:
        lang = get_lang(chat_id)
        schedule_text = await ai_handler.generate_schedule(
            tasks=[task.name for task in tasks],
            wake_time=log.wake_time,
            sleep_time=log.sleep_time,
            date=today,
            lang=lang
        )
        msg = get_text(chat_id, "schedule_today",
            date=today,
            wake=log.wake_time,
            sleep=log.sleep_time,
            provider=ai_handler.current_provider
        )
        msg += schedule_text
        await query.edit_message_text(msg, reply_markup=main_menu(chat_id), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await query.edit_message_text(
            get_text(chat_id, "schedule_error", error=str(e)),
            reply_markup=main_menu(chat_id)
        )

# ---------- Test Log ----------
async def test_log_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    db.set_state(chat_id, "test_total", {})
    await query.edit_message_text(
        get_text(chat_id, "test_total"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data="menu_main")]])
    )

async def handle_test_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "no_access"))
        return

    state = db.get_state(chat_id)
    if not state or not state["state"].startswith("test_"):
        return
    text = update.message.text.strip()
    data = state.get("data", {})
    state_name = state["state"]

    if state_name == "test_total":
        try:
            total = int(text)
            if total <= 0:
                raise ValueError
            data["total"] = total
            db.set_state(chat_id, "test_wrong", data)
            await update.message.reply_text(get_text(chat_id, "test_wrong"))
        except:
            await update.message.reply_text(get_text(chat_id, "invalid_number"))

    elif state_name == "test_wrong":
        try:
            wrong = int(text)
            if wrong < 0:
                raise ValueError
        except:
            await update.message.reply_text(get_text(chat_id, "invalid_number"))
            return
        total = data.get("total", 0)
        if wrong > total:
            await update.message.reply_text(f"❌ Wrong can't exceed total ({total}). Try again:")
            return
        today = get_today_date(chat_id)
        log = db.get_today_log(chat_id)
        if not log:
            log = DailyLog(date=today)
        log.total_tests = total
        log.wrong_tests = wrong
        log.correct_tests = total - wrong
        log.test_accuracy = round((total - wrong) / total * 100) if total > 0 else 0
        db.save_daily_log(chat_id, log)
        db.clear_state(chat_id)
        await update.message.reply_text(
            get_text(chat_id, "test_saved",
                total=total,
                wrong=wrong,
                correct=total - wrong,
                accuracy=log.test_accuracy
            ),
            reply_markup=main_menu(chat_id)
        )

# ---------- Daily Report ----------
async def daily_report_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    db.set_state(chat_id, "daily_wake", {})
    await query.edit_message_text(
        get_text(chat_id, "daily_wake"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data="menu_main")]])
    )

async def handle_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "no_access"))
        return

    state = db.get_state(chat_id)
    if not state or not state["state"].startswith("daily_"):
        return
    text = update.message.text.strip()
    data = state.get("data", {})
    state_name = state["state"]

    if state_name == "daily_wake":
        if not validate_time(text):
            await update.message.reply_text(get_text(chat_id, "invalid_time"))
            return
        normalized = persian_to_english_digits(text)
        data["wake"] = normalized
        db.set_state(chat_id, "daily_sleep", data)
        await update.message.reply_text(get_text(chat_id, "daily_sleep"))

    elif state_name == "daily_sleep":
        if not validate_time(text):
            await update.message.reply_text(get_text(chat_id, "invalid_time"))
            return
        normalized = persian_to_english_digits(text)
        data["sleep"] = normalized
        db.set_state(chat_id, "daily_mood", data)
        await update.message.reply_text(get_text(chat_id, "daily_mood"), reply_markup=mood_keyboard(chat_id))

    elif state_name == "daily_mood":
        await update.message.reply_text(get_text(chat_id, "daily_mood"), reply_markup=mood_keyboard(chat_id))

    elif state_name == "daily_energy":
        await update.message.reply_text(get_text(chat_id, "daily_energy"), reply_markup=energy_keyboard(chat_id))

    elif state_name == "daily_questions":
        end = "پایان" if get_lang(chat_id) == "fa" else "End"
        if text.lower() == end.lower():
            today = get_today_date(chat_id)
            log = db.get_today_log(chat_id)
            if not log:
                log = DailyLog(date=today)
            log.wake_time = data.get("wake", "")
            log.sleep_time = data.get("sleep", "")
            log.mood = data.get("mood", "")
            log.energy = data.get("energy", "")
            log.answers = data.get("answers", {})
            db.save_daily_log(chat_id, log)
            db.clear_state(chat_id)
            await update.message.reply_text(get_text(chat_id, "daily_saved"), reply_markup=main_menu(chat_id))
        else:
            if ":" not in text:
                await update.message.reply_text(get_text(chat_id, "qa_format"))
                return
            q, a = text.split(":", 1)
            q, a = q.strip(), a.strip()
            if "answers" not in data:
                data["answers"] = {}
            data["answers"][q] = a
            db.set_state(chat_id, "daily_questions", data)
            await update.message.reply_text(get_text(chat_id, "qa_saved"))

# ---------- Mood & Energy Callbacks ----------
async def mood_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    state = db.get_state(chat_id)
    if not state or state["state"] != "daily_mood":
        await query.edit_message_text("❌ Invalid state.", reply_markup=main_menu(chat_id))
        return
    mood = query.data.replace("mood_", "")
    data = state.get("data", {})
    data["mood"] = mood
    db.set_state(chat_id, "daily_energy", data)
    await query.edit_message_text(get_text(chat_id, "daily_energy"), reply_markup=energy_keyboard(chat_id))

async def energy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    state = db.get_state(chat_id)
    if not state or state["state"] != "daily_energy":
        await query.edit_message_text("❌ Invalid state.", reply_markup=main_menu(chat_id))
        return
    energy = query.data.replace("energy_", "")
    data = state.get("data", {})
    data["energy"] = energy
    db.set_state(chat_id, "daily_questions", data)
    await query.edit_message_text(get_text(chat_id, "daily_questions"))

# ---------- Set Group ----------
async def menu_set_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    await query.edit_message_text(
        get_text(chat_id, "set_group_info"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_main")]])
    )

async def setgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ This command only works in groups.")
        return
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    if not db.is_authorized(user_id):
        await update.message.reply_text(get_text(user_id, "no_access"))
        return
    db.set_report_group(user_id, chat_id)
    await update.message.reply_text(
        get_text(user_id, "group_set", group=update.effective_chat.title)
    )

async def cleargroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "no_access"))
        return
    db.set_report_group(chat_id, None)
    await update.message.reply_text(get_text(chat_id, "group_cleared"))

# ---------- Delete Plan ----------
async def delete_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.edit_message_text(get_text(chat_id, "no_access"))
        return

    plans = db.get_plans(chat_id)
    if not plans:
        await query.edit_message_text(get_text(chat_id, "no_plans_delete"), reply_markup=main_menu(chat_id))
        return
    await query.edit_message_text(
        get_text(chat_id, "delete_select"),
        reply_markup=select_plan_keyboard(plans, "delete", chat_id)
    )

async def delete_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await query.answer(get_text(chat_id, "no_access"), show_alert=True)
        return

    plan_id = int(query.data.replace("delete_", ""))
    plan = db.get_plan_by_id(chat_id, plan_id)
    if not plan:
        await query.answer("Plan not found!", show_alert=True)
        return
    db.delete_plan(chat_id, plan_id)
    await query.edit_message_text(
        get_text(chat_id, "deleted", title=plan.title),
        reply_markup=main_menu(chat_id)
    )

# ---------- FT Command (Instant Report) ----------
async def ft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "no_access"))
        return

    today = get_today_date(chat_id)
    log = db.get_today_log(chat_id)
    if not log:
        await update.message.reply_text(get_text(chat_id, "ft_no_report"))
        return
    tasks = db.get_tasks_for_date(chat_id, today)
    report = generate_daily_report(chat_id, today, log, tasks)
    group_id = db.get_report_group(chat_id)
    if group_id:
        await context.bot.send_message(chat_id=group_id, text=report, parse_mode=ParseMode.MARKDOWN)
        await update.message.reply_text(get_text(chat_id, "ft_sent"))
    else:
        await update.message.reply_text(get_text(chat_id, "ft_no_group"))

# ---------- Debug & State ----------
async def state_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "no_access"))
        return

    state = db.get_state(chat_id)
    if state:
        await update.message.reply_text(
            get_text(chat_id, "state_info", state=json.dumps(state, indent=2, ensure_ascii=False))
        )
    else:
        await update.message.reply_text(get_text(chat_id, "no_state"))

async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "no_access"))
        return

    today_jalali = get_today_jalali()
    today_gregorian = get_today_gregorian()
    lang = get_lang(chat_id)
    day = get_day_of_week(chat_id)
    state = db.get_state(chat_id)
    state_str = json.dumps(state, indent=2, ensure_ascii=False) if state else "None"
    log = db.get_today_log(chat_id)
    if log:
        log_str = f"Wake: {log.wake_time}\nSleep: {log.sleep_time}\nMood: {log.mood}\nEnergy: {log.energy}\nTests: {log.total_tests} total, {log.wrong_tests} wrong, {log.test_accuracy}% accuracy"
    else:
        log_str = get_text(chat_id, "no_log")
    await update.message.reply_text(
        get_text(chat_id, "debug_title",
            today_jalali=today_jalali,
            today_gregorian=today_gregorian,
            day=day,
            state=state_str,
            log=log_str
        ),
        parse_mode=ParseMode.MARKDOWN
    )

# ============================================================
# All Text Handler
# ============================================================

async def handle_all_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if not db.is_authorized(chat_id):
        await update.message.reply_text(get_text(chat_id, "access_denied"))
        return

    state = db.get_state(chat_id)
    if state and state["state"].startswith("daily_"):
        await handle_daily_report(update, context)
    elif state and state["state"].startswith("test_"):
        await handle_test_input(update, context)
    else:
        await handle_plan_text(update, context)

# ============================================================
# Auto Reports (Cron)
# ============================================================

async def send_daily_reports(app: Application):
    try:
        users = db.get_all_chat_ids()
        for chat_id in users:
            if not db.is_authorized(chat_id):
                continue
            today = get_today_date(chat_id)
            log = db.get_today_log(chat_id)
            if not log or log.submitted_to_consultant:
                continue
            tasks = db.get_tasks_for_date(chat_id, today)
            report = generate_daily_report(chat_id, today, log, tasks)
            group_id = db.get_report_group(chat_id)
            if group_id:
                await app.bot.send_message(chat_id=group_id, text=report, parse_mode=ParseMode.MARKDOWN)
                db.mark_log_submitted(chat_id, today)
                print(f"✅ Auto report sent for {chat_id}")
            else:
                print(f"⚠️ User {chat_id} has no report group set.")
    except Exception as e:
        print(f"❌ Auto report error: {e}")

async def schedule_reports(app: Application):
    while True:
        now = datetime.now()
        tehran = now + timedelta(hours=3, minutes=30)
        if tehran.hour == 23 and tehran.minute == 0:
            await send_daily_reports(app)
            await asyncio.sleep(60)
        await asyncio.sleep(60)

# ============================================================
# Reset Webhook
# ============================================================

def reset_webhook_sync():
    try:
        response = httpx.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url=")
        if response.status_code == 200:
            print("✅ Webhook cleared.")
        else:
            print(f"⚠️ Webhook clear error: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Webhook clear error: {e}")

# ============================================================
# Main
# ============================================================

def main():
    reset_webhook_sync()

    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("claimtoken", claimtoken_command))
    app.add_handler(CommandHandler("adduser", adduser_command))
    app.add_handler(CommandHandler("setgroup", setgroup_command))
    app.add_handler(CommandHandler("cleargroup", cleargroup_command))
    app.add_handler(CommandHandler("ft", ft_command))
    app.add_handler(CommandHandler("state", state_command))
    app.add_handler(CommandHandler("debug", debug_command))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(menu_main, pattern="^menu_main$"))
    app.add_handler(CallbackQueryHandler(new_plan_start, pattern="^new_plan$"))
    app.add_handler(CallbackQueryHandler(list_plans, pattern="^list_plans$"))
    app.add_handler(CallbackQueryHandler(daily_report_start, pattern="^daily_report$"))
    app.add_handler(CallbackQueryHandler(today_schedule, pattern="^today_schedule$"))
    app.add_handler(CallbackQueryHandler(manage_tasks, pattern="^manage_tasks$"))
    app.add_handler(CallbackQueryHandler(task_toggle_callback, pattern="^task_toggle_"))
    app.add_handler(CallbackQueryHandler(delete_plan, pattern="^delete_plan$"))
    app.add_handler(CallbackQueryHandler(delete_plan_callback, pattern="^delete_"))
    app.add_handler(CallbackQueryHandler(cancel_plan, pattern="^cancel_plan$"))
    app.add_handler(CallbackQueryHandler(mood_callback, pattern="^mood_"))
    app.add_handler(CallbackQueryHandler(energy_callback, pattern="^energy_"))
    app.add_handler(CallbackQueryHandler(test_log_start, pattern="^test_log$"))
    app.add_handler(CallbackQueryHandler(menu_set_group, pattern="^menu_set_group$"))
    app.add_handler(CallbackQueryHandler(request_access_callback, pattern="^request_access$"))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(change_lang_callback, pattern="^change_lang$"))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_text))

    # Schedule
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(schedule_reports(app))

    print("🤖 Multi-Language Bot started successfully!")
    print(f"🧠 AI Provider: {ai_handler.current_provider}")
    print(f"👑 Owner: @{OWNER_USERNAME}")
    print("🌐 Languages: Persian (Jalali Calendar) / English (Gregorian Calendar)")
    print("📅 Both calendars supported based on user language preference")
    print("🔹 Change Language button is bilingual for clarity.")

    app.run_polling()

if __name__ == "__main__":
    main()
