# ============================================================
# Service: IA (Google Gemini)
# Responsável por todas as chamadas de inteligência artificial.
# Usa o Gemini 2.5 Flash para visão e texto.
# ============================================================

import json
import re
from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY

# Cliente Gemini
_client = genai.Client(api_key=GEMINI_API_KEY)

# Modelo único para tudo (visão + texto)
MODEL = "gemini-3.6-flash"


def _parse_json(text: str) -> dict:
    """
    Faz parse de JSON retornado pela IA, tratando caracteres de controle.
    """
    # Remove blocos markdown se existirem
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    text_limpo = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f]', '', text)

    try:
        return json.loads(text_limpo)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(text_limpo, strict=False)
    except json.JSONDecodeError:
        return {"raw": text}


# ============================================================
# FUNÇÕES DE VISÃO (imagem + texto)
# ============================================================

async def analisar_imagem(image_bytes: bytes, mime_type: str) -> dict:
    """Envia imagem ao Gemini para extração de texto e sugestão de matéria."""
    response = _client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_text(text=
                        "Analise a imagem a seguir. Extraia todo o texto visível e identifique "
                        "a qual matéria escolar/universitária o conteúdo pertence. "
                        "Responda APENAS com JSON válido no formato: "
                        '{"texto_extraido": "...", "materia_sugerida": "..."}'
                    ),
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2048,
        ),
    )
    text = response.text.strip()
    return _parse_json(text)


async def traduzir_imagem(image_bytes: bytes, mime_type: str) -> str:
    """Envia imagem ao Gemini para tradução do conteúdo visível."""
    response = _client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_text(text=
                        "Analise a imagem a seguir. Extraia todo o texto visível e traduza "
                        "para português brasileiro. Responda APENAS com JSON válido no formato: "
                        '{"traducao": "..."}'
                    ),
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2048,
        ),
    )
    text = response.text.strip()
    data = _parse_json(text)
    return data.get("traducao", text)


# ============================================================
# FUNÇÕES DE TEXTO
# ============================================================

async def traduzir_texto(texto: str, idioma_destino: str = "português brasileiro") -> str:
    """Recebe um texto e retorna a tradução via Gemini."""
    response = _client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_text(text=
                        f"Traduza o texto a seguir para {idioma_destino}. "
                        "Responda APENAS com JSON válido no formato: "
                        '{"traducao": "..."}\n\n'
                        f"Texto: {texto}"
                    ),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2048,
        ),
    )
    text = response.text.strip()
    data = _parse_json(text)
    return data.get("traducao", text)


async def gerar_resumo(texto: str) -> str:
    """Recebe um texto e retorna um resumo estruturado via Gemini."""
    response = _client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_text(text=
                        "Você é um assistente de estudos. Responda NO MESMO IDIOMA do texto de entrada. "
                        "Gere um resumo claro e estruturado do conteúdo abaixo, "
                        "destacando os pontos principais em tópicos. "
                        "Responda APENAS com JSON válido no formato: "
                        '{"resumo": "..."}\n\n'
                        f"Conteúdo: {texto}"
                    ),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=2048,
        ),
    )
    text = response.text.strip()
    data = _parse_json(text)
    return data.get("resumo", text)


async def recomendar_videos(texto: str, materia: str) -> list[dict]:
    """
    Recebe o texto extraído e a matéria, e retorna uma lista de
    links de busca do YouTube com termos relevantes para o conteúdo.
    Usa a IA para gerar termos de busca e monta URLs de pesquisa reais.
    """
    import urllib.parse

    response = _client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_text(text=
                        "Com base no conteúdo acadêmico abaixo, gere de 3 a 5 termos de busca "
                        "otimizados para encontrar vídeo-aulas no YouTube sobre esse assunto. "
                        "Os termos devem ser em português e incluir o nome de canais educativos "
                        "brasileiros quando possível (Me Salva, Descomplica, Professor Ferretto, "
                        "Débora Aladim, etc). Cada termo deve ser uma busca que um aluno faria.\n\n"
                        f"Matéria: {materia}\n"
                        f"Conteúdo: {texto[:1000]}"
                    ),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=1024,
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "termos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "busca": {"type": "string"},
                                "titulo": {"type": "string"},
                            },
                            "required": ["busca", "titulo"],
                        },
                    }
                },
                "required": ["termos"],
            },
        ),
    )
    raw_text = response.text.strip()
    data = _parse_json(raw_text)
    termos = data.get("termos", [])

    # Monta URLs de busca do YouTube a partir dos termos
    videos: list[dict] = []
    for termo in termos:
        query = urllib.parse.quote_plus(termo.get("busca", ""))
        url = f"https://www.youtube.com/results?search_query={query}"
        videos.append({
            "url": url,
            "titulo": termo.get("titulo", termo.get("busca", "")),
        })

    return videos
