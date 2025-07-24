import os
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)

# بارگذاری توکن از فایل محیطی
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# دکمه‌ها
main_keyboard = [
    ["کانفیگ یک ماه", "تعرفه کانفیگ ها"],
    ["پشتیبانی", "بروزرسانی"]
]

volume_keyboard = [
    ["۱۰ گیگ", "۲۰ گیگ", "۵۰ گیگ", "۱۰۰ گیگ"],
    ["۲۰۰ گیگ", "نامحدود", "بازگشت"]
]

payment_keyboard = [
    ["💳 پرداخت از طریق کارت به کارت", "🔑 کد معرف دارید؟"],
    ["بازگشت"]
]

confirm_keyboard = [
    ["✅ پرداخت کردم"],
    ["بازگشت"]
]

# قیمت‌ها
prices = {
    "۱۰ گیگ": "۳۷ هزار تومان 💰",
    "۲۰ گیگ": "۵۷ هزار تومان 💰",
    "۵۰ گیگ": "۹۷ هزار تومان 💰",
    "۱۰۰ گیگ": "۱۴۷ هزار تومان 💰",
    "۲۰۰ گیگ": "۱۹۷ هزار تومان 💰",
    "نامحدود": "۶۷ هزار تومان 💰",
}

user_state = {}
selected_volume = {}
used_referral = {}
admin_id = 6621891772

# تابع محاسبه حجم هدیه
def calculate_bonus(volume_text):
    if volume_text == "نامحدود":
        return "نامحدود"
    try:
        base = int(volume_text.split()[0])
        bonus = int(base * 0.25)
        total = base + bonus
        return f"~~{base} گیگ~~ ➡️ {total} گیگ (+{bonus} گیگ 🎁)"
    except:
        return volume_text

# فرمان استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    used_referral[user_id] = False
    await update.message.reply_text(
        "👋 سلام! به ربات فروش VPN خوش آمدید.\nلطفا یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    )

# هندل پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if text == "بروزرسانی":
        return await start(update, context)

    # بررسی وضعیت کد معرف
    if user_state.get(user_id) == "awaiting_referral":
        if used_referral.get(user_id):
            await update.message.reply_text("⚠️ شما قبلاً از کد معرف استفاده کرده‌اید.")
        elif text.lower() == "panahide":
            used_referral[user_id] = True
            volume = selected_volume.get(user_id)
            updated_volume = calculate_bonus(volume)
            price = prices.get(volume, "نامشخص")
            await update.message.reply_text(
                f"✅ کد معرف معتبر بود!\n🎁 حجم شما افزایش یافت.\n\n"
                f"حجم انتخابی: {updated_volume}\n"
                f"💵 قیمت: {price}\n\n"
                "لطفاً روش پرداخت را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup(payment_keyboard, resize_keyboard=True),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ کد نامعتبر است.")
        user_state[user_id] = None
        return

    # منوها
    if text == "کانفیگ یک ماه":
        await update.message.reply_text("📦 لطفاً حجم مورد نظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(volume_keyboard, resize_keyboard=True)
        )

    elif text in prices:
        selected_volume[user_id] = text
        await update.message.reply_text(
            f"✅ شما حجم {text} را انتخاب کردید.\n"
            f"💵 قیمت: {prices[text]}\n\n"
            "لطفاً روش پرداخت را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(payment_keyboard, resize_keyboard=True)
        )

    elif text == "بازگشت":
        await update.message.reply_text("🔙 بازگشت به منوی اصلی:",
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        )

    elif text == "تعرفه کانفیگ ها":
        pricing_text = "\n".join([f"{k} - {v}" for k, v in prices.items()])
        await update.message.reply_text(f"📊 تعرفه کانفیگ‌ها:\n{pricing_text}")

    elif text == "پشتیبانی":
        await update.message.reply_text("📞 برای پشتیبانی لطفاً به @Alireza22H22 پیام دهید.")

    elif text == "💳 پرداخت از طریق کارت به کارت":
        await update.message.reply_text(
            "💳 لطفاً مبلغ مربوطه را به شماره کارت زیر واریز کنید:\n\n"
            "**۶۲۱۹-۸۶۱۸-۶۷۱۶-۵۷۸۸** 🏦 بانک سامان\n\n"
            "📸 سپس رسید را به آیدی زیر ارسال نمایید:\n"
            "🆔 @Alireza22H22\n\n"
            "در پایان روی دکمه «پرداخت کردم» بزنید.",
            reply_markup=ReplyKeyboardMarkup(confirm_keyboard, resize_keyboard=True),
            parse_mode="Markdown"
        )

    elif text == "🔑 کد معرف دارید؟":
        if not selected_volume.get(user_id):
            await update.message.reply_text("⚠️ ابتدا حجم مورد نظر را انتخاب کنید.")
        else:
            user_state[user_id] = "awaiting_referral"
            await update.message.reply_text("🔑 لطفاً کد معرف خود را وارد کنید:")

    elif text == "✅ پرداخت کردم":
        volume = selected_volume.get(user_id, "نامشخص")
        price = prices.get(volume, "نامشخص")
        referral_used = "✅ دارد" if used_referral.get(user_id) else "❌ ندارد"

        report = (
            f"🧾 گزارش سفارش جدید:\n"
            f"👤 آیدی عددی: {user_id}\n"
            f"📦 حجم انتخابی: {volume}\n"
            f"💰 قیمت: {price}\n"
            f"🎁 استفاده از کد معرف: {referral_used}"
        )

        await context.bot.send_message(chat_id=admin_id, text=report)
        await update.message.reply_text("✅ سفارش شما ثبت شد. لطفاً منتظر تایید پشتیبانی بمانید.")

    else:
        await update.message.reply_text("⚠️ لطفاً فقط از دکمه‌ها استفاده کنید.",
            reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        )

# هندل کمک
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای شروع از /start استفاده کنید.")

# اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 ربات در حال اجراست...")
    app.run_polling()
