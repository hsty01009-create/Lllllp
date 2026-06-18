import json
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "PUT_BOT_TOKEN"
HF_TOKEN = "PUT_HF_TOKEN"

IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
MUSIC_MODEL = "facebook/musicgen-small"

DB_FILE = "database.json"


def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


db = load_db()


def main_menu():
    return ReplyKeyboardMarkup(
        [["🖼 ساخت عکس", "🎵 ساخت موزیک"]],
        resize_keyboard=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in db["users"]:
        db["users"][user_id] = {"accepted": False, "warn": 0}
        save_db(db)

    keyboard = [["✅ قبول قوانین", "❌ رد قوانین"]]

    await update.message.reply_text(
        "📜 قوانین:\n"
        "1. استفاده مسئولیت خود کاربر است\n"
        "2. محتوای غیرقانونی ممنوع\n"
        "3. سازنده: امیر علی فروزان اصل\n\n"
        "آیا قبول می‌کنید؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in db["users"]:
        await start(update, context)
        return

    # قبول قوانین
    if text == "✅ قبول قوانین":
        db["users"][user_id]["accepted"] = True
        save_db(db)

        await update.message.reply_text(
            "✅ خوش آمدید!",
            reply_markup=main_menu()
        )
        return

    # رد قوانین
    if text == "❌ رد قوانین":
        await update.message.reply_text("⛔ بدون پذیرش قوانین نمی‌توانید استفاده کنید.")
        return

    # چک قوانین
    if not db["users"][user_id]["accepted"]:
        await update.message.reply_text("اول قوانین را قبول کنید ❗")
        return

    # ساخت عکس
    if text.startswith("🖼 ساخت عکس"):
        prompt = text.replace("🖼 ساخت عکس", "").strip()

        if not prompt:
            await update.message.reply_text("متن بده مثلا: 🖼 ساخت عکس یک ماشین در شب")
            return

        await update.message.reply_text("⏳ در حال ساخت عکس...")

        url = f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        response = requests.post(url, headers=headers, json={"inputs": prompt})

        if response.status_code == 200:
            await update.message.reply_photo(response.content)
        else:
            await update.message.reply_text("❌ خطا در ساخت عکس")
        return

    # ساخت موزیک (پاسخ ساده)
    if text.startswith("🎵 ساخت موزیک"):
        prompt = text.replace("🎵 ساخت موزیک", "").strip()

        if not prompt:
            await update.message.reply_text("مثلا: 🎵 ساخت موزیک آرام")
            return

        await update.message.reply_text("⏳ در حال ساخت موزیک...")

        url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        response = requests.post(url, headers=headers, json={"inputs": prompt})

        if response.status_code == 200:
            with open("music.wav", "wb") as f:
                f.write(response.content)

            await update.message.reply_audio(audio=open("music.wav", "rb"))
        else:
            await update.message.reply_text("❌ خطا در ساخت موزیک")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
