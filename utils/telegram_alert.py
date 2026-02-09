import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """
    Sends a message via Telegram Bot. 100% Free.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram Bot Token or Chat ID missing. Skipping Telegram alert.")
        return False, "Telegram Config Missing"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()
        if result.get("ok"):
            logger.info("Telegram notification sent successfully.")
            return True, "Telegram Alert Sent"
        else:
            logger.error(f"Telegram API Error: {result.get('description')}")
            return False, f"Telegram Error: {result.get('description')}"
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False, f"Connection Error: {str(e)}"

if __name__ == "__main__":
    # Test call
    send_telegram_message("🔥 *Wildfire Alert Test*\nThis is a test notification from your AI Prediction System.")
