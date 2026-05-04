import json
import base64
from groq import Groq

from app.core.config import GROQ_API_KEY

_client = Groq(api_key=GROQ_API_KEY)

TEXT_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


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
    return json.loads(text)


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
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    data = json.loads(text)
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
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    data = json.loads(text)
    return data.get("traducao", text)


async def gerar_resumo(texto: str) -> str:
    """Recebe um texto e retorna um resumo estruturado via Groq."""
    response = _client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "Você é um assistente de estudos. Gere um resumo claro e estruturado "
                    "do conteúdo abaixo, destacando os pontos principais em tópicos. "
                    "Responda APENAS com JSON válido no formato: "
                    '{"resumo": "..."}\n\n'
                    f"Conteúdo: {texto}"
                ),
            }
        ],
        temperature=0.3,
        max_tokens=2048,
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    data = json.loads(text)
    return data.get("resumo", text)
