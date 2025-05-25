import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Anon/public key
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")  # JWT secret from Supabase

# Log configuration (without sensitive values)
logger.info(f"Supabase URL configured: {bool(SUPABASE_URL)}")
logger.info(f"Supabase Key configured: {bool(SUPABASE_KEY)}")
logger.info(f"Supabase JWT Secret configured: {bool(SUPABASE_JWT_SECRET)}")
