import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CLOSERS_GROUP_ID = int(os.getenv("CLOSERS_GROUP_ID", 0))
VA_GROUP_ID = int(os.getenv("VA_GROUP_ID", 0))

# GoHighLevel Config
GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")
GHL_BASE_URL = "https://services.leadconnectorhq.com"

# GHL Webhook Security
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-token")

# Google Sheets Config
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Validation Config
VALID_PLATFORMS = [
    "Fanbasis", "Stripe", "Flexxbuy", "Wire Transfer", "Zelle", "Shoppay"
]

# Program Tag Mapping (Scalable for future programs)
PROGRAMS = {
    "default": {
        "tags": {
            "6 PIF": "#6mo-full-contract-send",
            "6 Payment Plan": "#6mo-full-pplan-contract-send"
        },
        "webhook_tags": {
            "course_access": ["#6mo-full-payment-april", "#6mo-payment-plan-april"],
            "contract_signed": "signed"
        }
    }
}
