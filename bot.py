import asyncio
import logging
import sys
import random
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# اطلاعات و تنظیمات کلیدی جهان
BOT_TOKEN = "8807018385:AAH0BJOhINR_TqpU0i_3b29QGWOlL5QUL2M"
ADMIN_ID = 6937799221

import aiosqlite
DB_PATH = "world_war_master.db"

async def init_database():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS empires (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                country_name TEXT,
                treasury REAL DEFAULT 500000.0,
                uranium REAL DEFAULT 2000.0,
                nuclear_warheads INTEGER DEFAULT 5,
                military_troops INTEGER DEFAULT 50000,
                missile_defense INTEGER DEFAULT 10000,
                tech_level INTEGER DEFAULT 1,
                alliance TEXT DEFAULT 'بدون اتحاد',
                status TEXT DEFAULT 'فعال'
            )
        """)
        await db.commit()

async def fetch_empire(user_id: int, username: str = "فرمانده") -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM empires WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                default_country = f"جمهوری {username}"
                await db.execute(
                    "INSERT INTO empires (user_id, username, country_name, treasury, uranium, nuclear_warheads, military_troops, missile_defense, tech_level, alliance, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, username, default_country, 500000.0, 2000.0, 5, 50000, 10000, 1, "بدون اتحاد", "فعال")
                )
                await db.commit()
                return {
                    "user_id": user_id, "username": username, "country_name": default_country,
                    "treasury": 500000.0, "uranium": 2000.0, "nuclear_warheads": 5,
                    "military_troops": 50000, "missile_defense": 10000, "tech_level": 1,
                    "alliance": "بدون اتحاد", "status": "فعال"
                }
            return {
                "user_id": row[0], "username": row[1], "country_name": row[2],
                "treasury": row[3], "uranium": row[4], "nuclear_warheads": row[5],
                "military_troops": row[6], "missile_defense": row[7], "tech_level": row[8],
                "alliance": row[9], "status": row[10]
            }

async def modify_empire(user_id: int, column: str, value: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE empires SET {column} = {column} + ? WHERE user_id = ?", (value, user_id))
        await db.commit()

router = Router()

def get_main_game_menu(user_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📊 وضعیت امپراتوری و آمار", callback_data="menu_stats"),
         InlineKeyboardButton(text="🏦 وزارت اقتصاد و سود", callback_data="menu_economy")],
        [InlineKeyboardButton(text="🚀 سیلوی موشکی و اتمی", callback_data="menu_nuclear"),
         InlineKeyboardButton(text="🪖 وزارت دفاع و ارتش", callback_data="menu_military")],
        [InlineKeyboardButton(text="🌐 دیپلماسی و اتحادها", callback_data="menu_diplomacy"),
         InlineKeyboardButton(text="📰 اخبار جهانی جنگ", callback_data="menu_news")]
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton(text="👑 پنل خدای کل قوا (مدیریت مطلق جهان)", callback_data="god_control_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(F.text.in_({"/start", "استارت", "فرماندهی", "جنگ"}))
async def cmd_start_game(message: Message):
    user = message.from_user
    await fetch_empire(user.id, user.full_name)
    god_badge = " [👑 خدای مطلق جهان]" if user.id == ADMIN_ID else ""
    
    welcome_text = (
        f"☢️ **مرکز فرماندهی کل قوا (جنگ جهانی اتمی)**{god_badge}\n\n"
        "جهان در لبه پرتگاه نابودی قرار دارد. منابع استراتژیک را کنترل کنید، ارتش بسازید و کلاهک‌های هسته‌ای را آماده نگه دارید!\n\n"
        "لطفاً از دکمه‌های زیر برای مدیریت امپراتوری خود استفاده کنید:"
    )
    await message.reply(welcome_text, reply_markup=get_main_game_menu(user.id), parse_mode="Markdown")

@router.callback_query(F.data == "return_main")
async def return_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "☢️ **مرکز فرماندهی کل قوا (جنگ جهانی اتمی)**\n\nامپراتوری خود را از منوی زیر مدیریت کنید:",
        reply_markup=get_main_game_menu(callback.from_user.id), parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("menu_"))
async def handle_game_menus(callback: CallbackQuery):
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id
    empire = await fetch_empire(user_id, callback.from_user.full_name)

    if action == "stats":
        text = (
            f"🌐 **اطلاعات جامع امپراتوری ({empire['country_name']}):**\n\n"
            f"👤 رهبر: `{empire['username']}`\n"
            f"💰 خزانه ملی: `{empire['treasury']:,.0f} دلار`\n"
            f"☢️ اورانیوم غنی‌شده: `{empire['uranium']:,.1f} کیلوگرم`\n"
            f"🚀 کلاهک‌های اتمی آماده: `{empire['nuclear_warheads']} فروند`\n"
            f"🪖 نیروهای مسلح: `{empire['military_troops']:,} سرباز`\n"
            f"🛡 سیستم دفاع ضدموشکی: `{empire['missile_defense']:,}`\n"
            f"⭐ سطح تکنولوژی: `Level {empire['tech_level']}`\n"
            f"🤝 اتحاد: `{empire['alliance']}`"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="return_main")]])
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

    elif action == "economy":
        text = (
            f"🏦 **وزارت اقتصاد و صندوق سرمایه‌گذاری جهانی:**\n\n"
            f"با بهره‌برداری از منابع مالی، سود روزانه کلان دریافت کنید تا هزینه‌های تسلیحاتی تأمین شود."
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 دریافت سود اقتصادی (+200,000 دلار)", callback_data="action_claim_profit")],
            [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="return_main")]
        ])
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

    elif action == "nuclear":
        text = (
            f"🚀 **سیلوی موشکی و تسلیحات هسته‌ای استراتژیک:**\n\n"
            f"موجودی فعلی: `{empire['nuclear_warheads']} کلاهک اتمی`\n"
            f"هزینه ساخت هر کلاهک: `۳۰۰,۰۰۰ دلار و ۸۰۰ کیلو اورانیوم`\n\n"
            f"دستور شلیک در گروه: `#اتم [نام کشور هدف]`"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="☢️ تولید و غنی‌سازی کلاهک اتمی", callback_data="action_build_nuke")],
            [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="return_main")]
        ])
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

    elif action == "military":
        text = (
            f"🪖 **وزارت دفاع و ارتش زمین‌گیر:**\n\n"
            f"نیروی فعلی: `{empire['military_troops']:,} سرباز`\n"
            f"برای توسعه ارتش اقدام کنید تا در برابر حملات دیگران محافظت شوید."
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🪖 استخدام ۱۰,۰۰۰ سرباز جدید", callback_data="action_recruit_army")],
            [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="return_main")]
        ])
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

    elif action == "diplomacy":
        text = (
            f"🌐 **اتحادهای منطقه‌ای و جهانی:**\n\n"
            f"وضعیت فعلی شما: `{empire['alliance']}`\n"
            f"می‌توانید با سایر امپراتوری‌ها معاهده همکاری یا پیمان عدم تجاوز امضا کنید."
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="return_main")]])
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

    elif action == "news":
        headlines = [
            "🚨 خبر فوری: آژانس بین‌المللی انرژی اتمی نسبت به افزایش فعالیت‌های مشکوک هسته‌ای هشدار داد.",
            "💥 رویداد نظامی: پایگاه‌های مرزی دو قدرت بزرگ درگیر تنش مرزی سنگینی شدند.",
            "☢️ بازار سیاه جهانی: قیمت اورانیوم غنی‌شده به بالاترین رکورد تاریخی خود رسید.",
            "📈 تحولات اقتصادی: بانک‌های مرکزی نرخ سود سپرده‌های نظامی را افزایش دادند."
        ]
        text = f"📰 **خبرگزاری سراسری جنگ جهانی:**\n\n{random.choice(headlines)}"
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="return_main")]])
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

    await callback.answer()

@router.callback_query(F.data == "god_control_panel")
async def god_panel_handler(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ شما دسترسی به حکم خدا ندارید!", show_alert=True)
    
    text = (
        "👑 **پنل مدیریت مطلق جهان (حکم خدا):**\n\n"
        "به عنوان خالق کل این پلتفرم، شما اختیار تام بر روی تمام منابع، بودجه‌ها و تسلیحات هسته‌ای دارید."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 تزریق بودجه نامحدود خدایی (+10,000,000$)", callback_data="god_inject_money")],
        [InlineKeyboardButton(text="☢️ اعطای کلاهک‌های اتمی خدایی (+20 فروند)", callback_data="god_inject_nukes")],
        [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="return_main")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

@router.callback_query(F.data.startswith("god_"))
async def god_actions_handler(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("❌ دسترسی غیرمجاز!", show_alert=True)
    
    action = callback.data.split("_")[1]
    if action == "inject":
        target = callback.data.split("_")[2]
        if target == "money":
            await modify_empire(ADMIN_ID, "treasury", 10000000)
            await callback.answer("👑 ۱۰,۰۰۰,۰۰۰ دلار به خزانه خدا واریز شد!", show_alert=True)
        elif target == "nukes":
            await modify_empire(ADMIN_ID, "nuclear_warheads", 20)
            await callback.answer("👑 ۲۰ کلاهک اتمی به انبار خدایی اضافه شد!", show_alert=True)

@router.callback_query(F.data.startswith("action_"))
async def player_gameplay_actions(callback: CallbackQuery):
    act = callback.data.split("_")[1]
    user_id = callback.from_user.id
    empire = await fetch_empire(user_id)

    if act == "claim":
        await modify_empire(user_id, "treasury", 200000)
        await callback.answer("💰 سود اقتصادی ۲۰۰,۰۰۰ دلاری به حساب شما واریز شد!", show_alert=True)
    elif act == "build":
        if empire["treasury"] >= 300000 and empire["uranium"] >= 800:
            await modify_empire(user_id, "treasury", -300000)
            await modify_empire(user_id, "uranium", -800)
            await modify_empire(user_id, "nuclear_warheads", 1)
            await callback.answer("☢️ یک کلاهک هسته‌ای جدید با موفقیت ساخته شد!", show_alert=True)
        else:
            await callback.answer("❌ منابع کافی نیست! (نیاز به ۳۰۰,۰۰۰$ و ۸۰۰ کیلو اورانیوم)", show_alert=True)
    elif act == "recruit":
        if empire["treasury"] >= 50000:
            await modify_empire(user_id, "treasury", -50000)
            await modify_empire(user_id, "military_troops", 10000)
            await callback.answer("🪖 ۱۰,۰۰۰ سرباز جدید به ارتش ملحق شدند!", show_alert=True)
        else:
            await callback.answer("❌ بودجه کافی برای استخدام ارتش وجود ندارد!", show_alert=True)

@router.message(F.text.regexp(r"^#اتم\s+(.+)$"))
async def group_nuclear_strike_command(message: Message):
    if message.chat.type == "private":
        return await message.reply("❌ حملات اتمی باید حتماً در گروه‌های جنگی و دیپلماتیک انجام شود!")
    
    target_country = message.text.replace("#اتم", "").strip()
    user_id = message.from_user.id
    empire = await fetch_empire(user_id, message.from_user.full_name)

    if empire["nuclear_warheads"] < 1 and user_id != ADMIN_ID:
        return await message.reply("❌ شما هیچ کلاهک اتمی آماده‌ای برای شلیک در اختیار ندارید!")

    if user_id != ADMIN_ID:
        await modify_empire(user_id, "nuclear_warheads", -1)

    destruction_power = random.randint(500000, 2000000)
    strike_report = (
        f"🚨🚨 **هشدار بحران جهانی: شلیک موشک بالستیک اتمی!** 🚨🚨\n\n"
        f"🏴 کشور مهاجم: `{empire['country_name']}`\n"
        f"🎯 منطقه هدف: `{target_country}`\n\n"
        f"💥 **گزارش صدمات و خسارات:**\n"
        f"میزان انرژی اتمی آزاد شده: `{destruction_power:,.0f} تن تی‌ان‌تی`\n"
        f"☢️ منطقه مورد اصابت به کلی ویران و دچار آلودگی شدید رادیواکتیو شد!"
    )
    await message.reply(strike_report, parse_mode="Markdown")

async def main():
    await init_database()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    print("🌍 World War RP Master Engine is fully online and ready!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

