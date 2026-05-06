import json
import base64
import re
from groq import Groq

from app.core.config import GROQ_API_KEY

_client = Groq(api_key=GROQ_API_KEY)

TEXT_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def _parse_json(text: str) -> dict:
    """
    Faz parse de JSON retornado pela IA, tratando caracteres de controle.
    [VALIDAÇÃO + DECISÃO] Tenta múltiplas estratégias de parsing.
    """
    # Remove blocos markdown se existirem
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    # Tenta parse direto primeiro
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Remove caracteres de controle (exceto \n e \t) e tenta novamente
    text_limpo = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f]', '', text)

    try:
        return json.loads(text_limpo)
    except json.JSONDecodeError:
        pass

    # Última tentativa: usa strict=False
    try:
        return json.loads(text_limpo, strict=False)
    except json.JSONDecodeError:
        # Se nada funcionar, retorna o texto cru como valor
        return {"raw": text}


async def analisar_imagem(image_bytes: bytes, mime_type: str) -> dict:
    """Envia imagem ao Groq Vision para extração de texto e sugestão de matéria."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = _client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analise a imagem a seguir. Extraia todo o texto visível e identifique "
                            "a qual matéria escolar/universitária o conteúdo pertence. "
                            "Responda APENAS com JSON válido no formato: "
                            '{"texto_extraido": "...", "materia_sugerida": "..."}'
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    },
                ],
            }
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return _parse_json(text)


async def traduzir_imagem(image_bytes: bytes, mime_type: str) -> str:
    """Envia imagem ao Groq Vision para tradução do conteúdo."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = _client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analise a imagem a seguir. Extraia todo o texto visível e traduza "
                            "para português brasileiro. Responda APENAS com JSON válido no formato: "
                            '{"traducao": "..."}'
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    },
                ],
            }
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    text = response.choices[0].message.content.strip()
    data = _parse_json(text)
    return data.get("traducao", text)


async def traduzir_texto(texto: str, idioma_destino: str = "português brasileiro") -> str:
    """Recebe um texto e retorna a tradução via Groq."""
    response = _client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Traduza o texto a seguir para {idioma_destino}. "
                    "Responda APENAS com JSON válido no formato: "
                    '{"traducao": "..."}\n\n'
                    f"Texto: {texto}"
                ),
            }
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    text = response.choices[0].message.content.strip()
    data = _parse_json(text)
    return data.get("traducao", text)


async def gerar_resumo(texto: str) -> str:
    """Recebe um texto e retorna um resumo estruturado via Groq."""
    response = _client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a study assistant. You MUST reply in the SAME language as the input text. "
                    "If the text is in English, reply in English. If in Portuguese, reply in Portuguese. "
                    "Never translate the content to another language."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Generate a clear and structured summary of the content below, "
                    "highlighting the main points as bullet items. "
                    "Reply ONLY with valid JSON in the format: "
                    '{"resumo": "..."}\n\n'
                    f"Content: {texto}"
                ),
            }
        ],
        temperature=0.3,
        max_tokens=2048,
    )
    text = response.choices[0].message.content.strip()
    data = _parse_json(text)
    return data.get("resumo", text)
