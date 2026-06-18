import json
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "توکن واقعی BotFather"
HF_TOKEN = "توکن واقعی HuggingFace"


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


# ---------- UI BUTTONS ----------
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🖼 ساخت عکس", callback_data="img")],
        [InlineKeyboardButton("🎵 ساخت موزیک", callback_data="music")]
    ]
    return InlineKeyboardMarkup(keyboard)


def agree_menu():
    keyboard = [
        [InlineKeyboardButton("✅ قبول قوانین", callback_data="agree")],
        [InlineKeyboardButton("❌ رد قوانین", callback_data="reject")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in db["users"]:
        db["users"][user_id] = {"accepted": False}
        save_db(db)

    await update.message.reply_text(
        "📜 قوانین ربات:\n"
        "1. استفاده مسئولیت خود کاربر است\n"
        "2. سازنده: امیر علی فروزان اصل\n\n"
        "آیا قبول می‌کنید؟",
        reply_markup=agree_menu()
    )


# ---------- BUTTON HANDLER ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)

    await query.answer()

    if query.data == "agree":
        db["users"][user_id]["accepted"] = True
        save_db(db)

        await query.message.edit_text(
            "✅ خوش آمدید!",
            reply_markup=main_menu()
        )

    elif query.data == "reject":
        await query.message.edit_text("⛔ بدون قبول قوانین نمی‌توانید استفاده کنید")

    elif query.data == "img":
        await query.message.reply_text("🖼 متن بده برای ساخت عکس:")

    elif query.data == "music":
        await query.message.reply_text("🎵 متن بده برای ساخت موزیک:")


# ---------- IMAGE ----------
def generate_image(prompt):
    url = f"https://api-inference.huggingface.co/models/{IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(url, headers=headers, json={"inputs": prompt})
    return r.content if r.status_code == 200 else None


# ---------- MUSIC ----------
def generate_music(prompt):
    url = f"https://api-inference.huggingface.co/models/{MUSIC_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    r = requests.post(url, headers=headers, json={"inputs": prompt})

    if r.status_code == 200:
        with open("music.mp3", "wb") as f:
            f.write(r.content)
        return "music.mp3"
    return None


# ---------- TEXT HANDLER ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in db["users"] or not db["users"][user_id]["accepted"]:
        await update.message.reply_text("اول قوانین را قبول کنید ❗")
        return

    if text.startswith("🖼"):
        prompt = text.replace("🖼", "").strip()
        await update.message.reply_text("⏳ در حال ساخت عکس...")

        img = generate_image(prompt)
        if img:
            await update.message.reply_photo(photo=img)
        else:
            await update.message.reply_text("❌ خطا در ساخت عکس")

    elif text.startswith("🎵"):
        prompt = text.replace("🎵", "").strip()
        await update.message.reply_text("⏳ در حال ساخت موزیک...")

        file = generate_music(prompt)
        if file:
            await update.message.reply_audio(audio=open(file, "rb"))
        else:
            await update.message.reply_text("❌ خطا در ساخت موزیک")


# ---------- MAIN ----------
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, handle_text))

print("Bot is running...")
app.run_polling()
