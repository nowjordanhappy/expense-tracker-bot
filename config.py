import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
CURRENCY = os.environ.get("CURRENCY", "$")
ADMIN_ID = int(os.environ["ADMIN_ID"])

CATEGORIES = [
    ("🛒 Food", "food"),
    ("🏠 Home", "home"),
    ("🚗 Transport", "transport"),
    ("💊 Health", "health"),
    ("🎉 Other", "other"),
]
