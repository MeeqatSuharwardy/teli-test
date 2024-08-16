from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

load_dotenv()

templates = Jinja2Templates(directory="templates")
supabase_url: str = os.getenv("SUPABASE_URL")  
supabase_key: str = os.getenv("SUPABASE_KEY")  
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
