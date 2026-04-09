# Telegram Automation System (GHL & Google Sheets)

This production-ready system automates the sales pipeline by connecting Telegram sales reports, Google Sheets, and GoHighLevel.

## 🚀 Features
- **Telegram Bot**: Monitors group messages for "Status: Closed" and parses sales data.
- **Google Sheets**: Updates existing rows matched by Email or Name.
- **GoHighLevel**: Applies tags to contacts to trigger onboarding workflows.
- **Webhook Listener**: FastAPI server that updates Google Sheets based on GHL events (Contract Signed, Course Access).
- **VA Alerts**: Sends alerts to a dedicated VA group if errors occur or human intervention is needed.

## 🛠 Setup Instructions

### 1. Requirements
- Python 3.11+
- Google Cloud Service Account (JSON file) with access to the target Spreadsheet.
- Telegram Bot Token (from @BotFather).
- GoHighLevel API Key.

### 2. Local Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your secrets.
4. Place your Google Service Account JSON file in the root directory (rename to `service_account.json`).
5. Run the system:
   ```bash
   python bot.py
   ```

## 🚆 Railway Deployment

1. **New Project**: Create a new project on Railway.
2. **Connect Repo**: Link your GitHub repository.
3. **Variables**: Add all variables from `.env` to the Railway "Variables" tab.
4. **Service Account**: Since Railway doesn't easily store secret files, you can:
   - Option A: Add the JSON content as a variable `GOOGLE_AUTH_JSON` and modify `sheets_service.py` to use `Credentials.from_service_account_info`.
   - Option B: Use a private GiHub repo (standard).
5. **Start Command**: Railway will automatically detect the Python environment. Ensure the start command is:
   ```bash
   python bot.py
   ```
6. **Networking**: Railway will provide a public URL. Set this URL in GoHighLevel Webhooks (e.g., `https://your-app.up.railway.app/ghl-webhook`).

## 📊 Sheet Mapping
- **Column A**: Name
- **Column B**: Email
- **Column E**: Payment Plan (6PIF / 6PP)
- **Column F**: Platform
- **Column G**: Date
- **Column H**: 1st Payment
- **Column I**: Notes
- **Column R**: Mentorship Contract Signed (Checkbox)
- **Column S**: Mentorship Course Access (Checkbox)
