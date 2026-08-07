import os
from dotenv import load_dotenv

load_dotenv()

# Monitor credentials
TG_API_ID = int(os.getenv("TG_API_ID", "0"))
TG_API_HASH = os.getenv("TG_API_HASH", "")
TG_PHONE = os.getenv("TG_PHONE", "")
TARGET_BOT_USERNAME = os.getenv("TARGET_BOT_USERNAME", "")

# Admin Bot credentials
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# Caller credentials
CALLER_API_ID = int(os.getenv("CALLER_API_ID", os.getenv("TG_API_ID", "0")))
CALLER_API_HASH = os.getenv("CALLER_API_HASH", os.getenv("TG_API_HASH", ""))
CALLER_PHONE = os.getenv("CALLER_PHONE", "")
CALLER_SESSION_NAME = os.getenv("CALLER_SESSION_NAME", "caller_session")

# Twilio Optional Backup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER", "")

# App Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE_PATH = os.path.join(BASE_DIR, "state.json")
