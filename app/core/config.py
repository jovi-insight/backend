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
# River: voz "premade" com português verificado, liberada no plano free. A voz
# anterior (Sarah) não tem português verificado — lia PT com sotaque de inglês.
# Vozes com sotaque brasileiro (Jenifer, Giselli, Carla) são "professional" e
# devolvem 402 fora de plano pago; ver FALLBACK_VOICE_ID no elevenlabs_service.
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "SAz9YHcvj6GT2YYXdXww")

# Google Drive (OAuth2 - roda auth_drive.py uma vez pra gerar token.json)
GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")