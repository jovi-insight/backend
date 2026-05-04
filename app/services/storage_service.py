import uuid
import unicodedata
from supabase import create_client

from app.core.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def _extensao(content_type: str) -> str:
    """Retorna extensão com base no content-type."""
    mapa = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return mapa.get(content_type, ".jpg")


def _normalizar(texto: str) -> str:
    """Remove acentos e caracteres especiais pra usar como nome de pasta."""
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.strip().replace(" ", "_").lower()


async def upload_image(file_bytes: bytes, content_type: str, nome_materia: str) -> str:
    """Faz upload de imagem organizada em pasta da matéria no Supabase Storage."""
    client = _get_client()
    ext = _extensao(content_type)
    pasta = _normalizar(nome_materia)
    filepath = f"{pasta}/{uuid.uuid4()}{ext}"

    client.storage.from_(SUPABASE_BUCKET).upload(
        path=filepath,
        file=file_bytes,
        file_options={"content-type": content_type},
    )
    return client.storage.from_(SUPABASE_BUCKET).get_public_url(filepath)


def _extrair_path(url: str) -> str | None:
    """Extrai o path do arquivo a partir da URL pública do Supabase."""
    marcador = f"/storage/v1/object/public/{SUPABASE_BUCKET}/"
    if marcador in url:
        path = url.split(marcador, 1)[1].split("?")[0]
        return path
    return None


async def delete_files(urls: list[str]) -> None:
    """Deleta múltiplos arquivos do Supabase Storage."""
    client = _get_client()
    paths = [_extrair_path(url) for url in urls]
    paths = [p for p in paths if p]
    if paths:
        client.storage.from_(SUPABASE_BUCKET).remove(paths)
