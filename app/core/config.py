import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:mysecretpassword@localhost:5432/postgres",
)

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "imagens")

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# Google Gemini
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ElevenLabs (Text-to-Speech)
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

# Google Drive (OAuth2 - roda auth_drive.py uma vez pra gerar token.json)
GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")