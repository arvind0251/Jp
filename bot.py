from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from pymongo import MongoClient
from buy import buy, buy_callback  # <-- Import buy feature

# Configuration
BOT_TOKEN = "7751080418:AAHML4fdAFjUoR6VDhLKUkDI_YrTL7dJxHY"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "otp_bot_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"Hello, {update.effective_user.first_name}! Welcome to OTP Service Bot.")

    user = db.users.find_one({"telegram_id": user_id})
    if not user:
        db.users.insert_one({
            "telegram_id": user_id,
            "username": update.effective_user.username,
            "first_name": update.effective_user.first_name,
            "balance": 0,
            "created_at": update.message.date
        })

# /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.users.find_one({"telegram_id": user_id})
    if user:
        balance = user.get("balance", 0)
        await update.message.reply_text(f"Your current balance is: ₹{balance}")
    else:
        await update.message.reply_text("User not found, please use /start first.")

# Start the bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("buy", buy))  # <-- Buy command
    app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))  # <-- Callback for buy

    print("Bot is running...")
    app.run_polling()
