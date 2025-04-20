from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests

# Country & Service options
COUNTRIES = {
    "India": "india",
    "Russia": "russia"
}

SERVICES = {
    "WhatsApp": "whatsapp",
    "Telegram": "telegram",
    "OLX": "olx"
}

OPERATOR = "any"  # You can let user select this too, if needed

API_KEY = "a4ac091e88004e00ba43894f854a789d"  # Replace with your 5sim key
API_URL_TEMPLATE = "https://5sim.net/v1/user/buy/activation/{country}/{operator}/{service}"

# Step 1: Choose Country
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(c, callback_data=f"buy_country|{v}")] for c, v in COUNTRIES.items()]
    await update.message.reply_text("Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))

# Step 2: Choose Service → Buy number from 5sim
async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("|")

    if data[0] == "buy_country":
        context.user_data["country"] = data[1]
        keyboard = [[InlineKeyboardButton(s, callback_data=f"buy_service|{v}")] for s, v in SERVICES.items()]
        await query.edit_message_text("Select a service:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data[0] == "buy_service":
        service_code = data[1]
        country_code = context.user_data.get("country")
        operator = OPERATOR

        url = API_URL_TEMPLATE.format(country=country_code, operator=operator, service=service_code)

        response = requests.get(url, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        })

        if response.status_code == 200:
            result = response.json()
            number = result.get("phone")
            order_id = result.get("id")
            await query.edit_message_text(f"Number purchased: {number}\nOrder ID: {order_id}")
        else:
            await query.edit_message_text(f"Failed to buy number: {response.json().get('message', 'Try again')}")
