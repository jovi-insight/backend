# ============================================================
# Service: Narração (ElevenLabs Text-to-Speech)
# Converte texto em áudio MP3 no idioma pedido.
# ============================================================

import logging

import httpx

from app.core.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

logger = logging.getLogger(__name__)

_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# turbo_v2_5 aceita language_code e custa metade dos créditos do multilingual_v2.
MODEL = "eleven_turbo_v2_5"

# Voz de reserva: "premade" com português verificado, que o plano free pode
# usar. As vozes com sotaque brasileiro são todas "professional" e a API as
# recusa com 402 fora de plano pago — sem esta reserva, uma ELEVENLABS_VOICE_ID
# assim deixa a narração inteira muda, no quiz e no resumo.
FALLBACK_VOICE_ID = "SAz9YHcvj6GT2YYXdXww"  # River

# Teto de caracteres por narração — protege a cota da conta (o plano free tem
# 10 mil créditos/mês). ponytail: corte seco no limite; se precisar narrar
# textos longos, quebrar em partes e concatenar os MP3s no cliente.
MAX_CHARS = 2500


async def narrar(texto: str, idioma: str = "pt") -> bytes:
    """Gera o MP3 do texto no idioma indicado (código ISO: pt, en, es...)."""

    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY não configurada no ambiente.")

    async def pedir(client: httpx.AsyncClient, voice_id: str) -> httpx.Response:
        return await client.post(
            _URL.format(voice_id=voice_id),
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            json={
                "text": texto[:MAX_CHARS],
                "model_id": MODEL,
                "language_code": idioma,
            },
        )

    async with httpx.AsyncClient(timeout=60) as client:
        resposta = await pedir(client, ELEVENLABS_VOICE_ID)

        # 402/403 = a voz configurada exige plano pago. Repetir com a reserva
        # entrega uma narração pior em vez de nenhuma. 401 fica de fora: chave
        # inválida não melhora ao trocar de voz.
        if resposta.status_code in (402, 403) and ELEVENLABS_VOICE_ID != FALLBACK_VOICE_ID:
            logger.warning(
                "Voz %s recusada (%s); repetindo com a voz de reserva %s.",
                ELEVENLABS_VOICE_ID,
                resposta.status_code,
                FALLBACK_VOICE_ID,
            )
            resposta = await pedir(client, FALLBACK_VOICE_ID)

    if resposta.status_code != 200:
        raise RuntimeError(f"ElevenLabs {resposta.status_code}: {resposta.text[:200]}")

    return resposta.content
