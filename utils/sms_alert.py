import serial
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")
FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"


def send_online_sms_fast2sms(phone_number, message):
    if not FAST2SMS_API_KEY:
        return False, "Fast2SMS API key missing"

    payload = {
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": phone_number
    }

    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(FAST2SMS_URL, data=payload, headers=headers)
        result = response.json()

        if result.get("return"):
            logger.info("SMS sent via Fast2SMS")
            return True, "Online SMS sent"
        else:
            return False, result.get("message", "Fast2SMS error")

    except Exception as e:
        return False, str(e)


def send_offline_sms_gsm(phone_number, message, port="COM3", baudrate=9600):
    """
    REAL offline SMS requires GSM module (SIM800 / SIM900)
    """
    logger.info("Attempting GSM offline SMS...")

    # Uncomment ONLY when GSM hardware is connected
    """
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        ser.write(b'AT+CMGF=1\r')
        ser.write(f'AT+CMGS="{phone_number}"\r'.encode())
        ser.write((message + "\x1A").encode())
        ser.close()
        return True, "Offline SMS sent via GSM"
    except Exception as e:
        return False, str(e)
    """

    logger.info(f"[SIMULATED OFFLINE SMS] {phone_number}: {message}")
    return True, "Simulated GSM SMS"


def send_sms_alert(phone_number, message):
    success, msg = send_online_sms_fast2sms(phone_number, message)

    if success:
        return True, msg

    logger.warning("Online failed. Switching to GSM...")
    return send_offline_sms_gsm(phone_number, message)


if __name__ == "__main__":
    send_sms_alert("8591556205", "🔥 Wildfire Alert: High Risk Detected!")
