# ============================================================
# Service: Narração (ElevenLabs Text-to-Speech)
# Converte texto em áudio MP3 no idioma pedido.
# ============================================================

import httpx

from app.core.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# turbo_v2_5 aceita language_code e custa metade dos créditos do multilingual_v2.
MODEL = "eleven_turbo_v2_5"

# Teto de caracteres por narração — protege a cota da conta (o plano free tem
# 10 mil créditos/mês). ponytail: corte seco no limite; se precisar narrar
# textos longos, quebrar em partes e concatenar os MP3s no cliente.
MAX_CHARS = 2500


async def narrar(texto: str, idioma: str = "pt") -> bytes:
    """Gera o MP3 do texto no idioma indicado (código ISO: pt, en, es...)."""

    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY não configurada no ambiente.")

    async with httpx.AsyncClient(timeout=60) as client:
        resposta = await client.post(
            _URL.format(voice_id=ELEVENLABS_VOICE_ID),
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            json={
                "text": texto[:MAX_CHARS],
                "model_id": MODEL,
                "language_code": idioma,
            },
        )

    if resposta.status_code != 200:
        raise RuntimeError(f"ElevenLabs {resposta.status_code}: {resposta.text[:200]}")

    return resposta.content
