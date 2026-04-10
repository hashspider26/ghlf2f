# GoHighLevel (GHL) Sales Automation Bot
A powerful automation system that bridges Telegram, GoHighLevel, and Google Sheets to streamline sales tracking and onboarding.

## 🚀 Core Functionalities

### 1. Telegram Sales Reporting
The bot monitors a specific Telegram group (Closers Group) for sales reports. When a closer posts a message containing **"Status: Closed"**, the bot:
- **Parses the Report**: Extracts Name, Email, Payment Plan, Platform, Amount, and Notes.
- **Updates Google Sheets**: Automatically finds the customer's row in your Master Spreadsheet and fills in the closer's name, payment details, and date.
- **Syncs with GHL**: 
    - Finds the contact in GoHighLevel by email.
    - Applies specific tags based on the payment plan (e.g., `#6mo-full-contract-send`).
- **VA Alerts**: If any error occurs (contact not found, invalid format), it sends an alert to a Virtual Assistant (VA) group for manual review.

### 2. Onboarding Automation (Webhooks)
The bot acts as a receiver for GoHighLevel webhooks to track the onboarding progress:
- **Contract Tracking**: When a contract is signed in GHL, the bot automatically checks the corresponding box in Google Sheets (Column R).
- **Course Access**: When course access tags are applied in GHL, the bot updates the Google Sheet (Column S) to confirm the student is set up.

---

## 🛠️ Setup Guide

### 1. Prerequisites
- **Python 3.10+** installed.
- **Telegram Bot Token**: Create one via [@BotFather](https://t.me/botfather).
- **Google Cloud Console**:
    - Enable Google Sheets and Google Drive APIs.
    - Create a Service Account and download the `service_account.json`.
    - **Share** your Google Sheet with the Service Account email.
- **GoHighLevel API Key**: Obtained from your GHL Agency/Sub-account settings.

### 2. Configuration (`.env`)
Create a `.env` file in the root directory and fill in the following:
```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
CLOSERS_GROUP_ID=-100xxxxxxxxxx
VA_GROUP_ID=-100xxxxxxxxxx

# GoHighLevel
GHL_API_KEY=your_ghl_api_key
GHL_LOCATION_ID=your_location_id
WEBHOOK_SECRET=your_custom_safe_token

# Google Sheets
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_JSON='{"type": "service_account", ...}' # For Railway
```

---

## 💻 Running the Bot

### Locally
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the System**:
   ```bash
   python bot.py
   ```
   *This starts both the Telegram listener and the Webhook server (default port 8000).*

---

## ☁️ Deployment on Railway

### 1. Prepare for Deployment
- Ensure `requirements.txt` includes `uvicorn`, `fastapi`, `python-telegram-bot`, `gspread`, `google-auth`, and `requests`.
- Ensure your project has a `Procfile` if needed, though Railway can run `python bot.py`.

### 2. Deploy to Railway
1. **Connect GitHub**: Connect your repository to Railway.
2. **Environment Variables**: Add all the variables from your `.env` to the Railway "Variables" tab.
    - **Note**: For `GOOGLE_CREDENTIALS_JSON`, paste the entire content of your `service_account.json` as a single line.
3. **Internal Port**: Railway will automatically detect the `PORT` environment variable. Ensure `bot.py` uses `os.environ.get("PORT", 8000)`.

### 3. Connect GHL to Railway
1. In GoHighLevel, go to **Automation (Workflows)**.
2. Create a workflow (e.g., "Contract Signed").
3. Add a **Webhook** action.
4. Set the URL to: `https://your-railway-app.up.railway.app/ghl-webhook?token=your_webhook_secret`.
5. Save and Publish.

---

## 📂 Project Structure
- `bot.py`: Main entry point (Runs Bot + FastAPI).
- `telegram_listener.py`: Logic for processing Telegram messages.
- `webhook_server.py`: FastAPI routes for GHL webhooks.
- `ghl_service.py`: GHL API wrappers.
- `sheets_service.py`: Google Sheets integration logic.
- `report_parser.py`: Regex-based parser for sales reports.
