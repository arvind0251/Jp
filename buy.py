from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
import requests

# Example country & service data
COUNTRIES = {
    "India": "in",
    "Russia": "ru"
}

SERVICES = {
    "WhatsApp": "wa",
    "Telegram": "tg",
    "OLX": "olx"
}

API_URL = "https://api.extrasim.net/v1/order"
API_KEY = "YOUR_API_KEY"

# Step 1 - Choose country
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(c, callback_data=f"buy_country|{v}")] for c, v in COUNTRIES.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a country:", reply_markup=reply_markup)

# Step 2 - Choose service
async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")
    
    if data[0] == "buy_country":
        country_code = data[1]
        context.user_data["country"] = country_code
        keyboard = [[InlineKeyboardButton(s, callback_data=f"buy_service|{v}")] for s, v in SERVICES.items()]
        await query.edit_message_text("Select a service:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data[0] == "buy_service":
        service_code = data[1]
        country_code = context.user_data.get("country")
        
        # Make API call to buy number
        response = requests.post(API_URL, headers={
            "Authorization": f"Bearer {API_KEY}"
        }, json={
            "country": country_code,
            "service": service_code
        })

        if response.status_code == 200:
            result = response.json()
            number = result.get("number")
            order_id = result.get("id")
            await query.edit_message_text(f"Number purchased: {number}\nOrder ID: {order_id}")
        else:
            await query.edit_message_text("Failed to buy number. Try again.")

# Register handlers in bot.py main section
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))
