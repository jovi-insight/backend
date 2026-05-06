# ============================================================
# Service: Storage (Supabase)
# Upload de imagens para o Supabase Storage organizado
# em pastas por matéria.
# ============================================================
# Conceitos aplicados:
# - Manipulação de variáveis e strings
# - Estruturas de decisão (if/elif com match em dicionário)
# - Estruturas de repetição (for na deleção)
# - Listas (filtragem de paths)
# - f-strings na construção de caminhos
# ============================================================

import uuid
import unicodedata
from supabase import create_client

from app.core.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET

_client = None


def _get_client():
    """Inicializa o cliente Supabase (singleton)."""
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def _extensao(content_type: str) -> str:
    """
    Retorna extensão do arquivo com base no content-type.
    [ESTRUTURA DE DECISÃO] Usa dicionário como alternativa ao if/elif.
    """
    mapa: dict[str, str] = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    # [DECISÃO] Retorna extensão mapeada ou padrão
    return mapa.get(content_type, ".jpg")


def _normalizar(texto: str) -> str:
    """
    Remove acentos e caracteres especiais para uso como nome de pasta.
    [MANIPULAÇÃO DE STRINGS + REPETIÇÃO]
    """
    # [REPETIÇÃO IMPLÍCITA] normalize percorre cada caractere
    nfkd: str = unicodedata.normalize("NFKD", texto)

    # [LIST COMPREHENSION + DECISÃO] Filtra caracteres combinantes (acentos)
    sem_acento: str = "".join(c for c in nfkd if not unicodedata.combining(c))

    return sem_acento.strip().replace(" ", "_").lower()


async def upload_image(file_bytes: bytes, content_type: str, nome_materia: str) -> str:
    """
    Faz upload de imagem organizada em pasta da matéria no Supabase Storage.
    Retorna a URL pública do arquivo.
    """
    client = _get_client()

    # [MANIPULAÇÃO DE VARIÁVEIS] Monta o caminho do arquivo
    ext: str = _extensao(content_type)
    pasta: str = _normalizar(nome_materia)
    # [F-STRING] Constrói o filepath com pasta e nome único
    filepath: str = f"{pasta}/{uuid.uuid4()}{ext}"

    # Faz o upload para o Supabase Storage
    client.storage.from_(SUPABASE_BUCKET).upload(
        path=filepath,
        file=file_bytes,
        file_options={"content-type": content_type},
    )

    # [SAÍDA] Retorna URL pública
    return client.storage.from_(SUPABASE_BUCKET).get_public_url(filepath)


def _extrair_path(url: str) -> str | None:
    """Extrai o path do arquivo a partir da URL pública do Supabase."""
    # [F-STRING] Monta o marcador de busca
    marcador: str = f"/storage/v1/object/public/{SUPABASE_BUCKET}/"

    # [DECISÃO] Verifica se a URL contém o marcador esperado
    if marcador in url:
        path: str = url.split(marcador, 1)[1].split("?")[0]
        return path
    return None


async def delete_files(urls: list[str]) -> None:
    """Deleta múltiplos arquivos do Supabase Storage."""
    client = _get_client()

    # [LISTA + REPETIÇÃO] Extrai paths válidos das URLs
    paths: list[str] = [_extrair_path(url) for url in urls]

    # [LISTA - filtragem] Remove valores None
    paths_validos: list[str] = [p for p in paths if p is not None]

    # [DECISÃO] Só chama a API se houver paths para deletar
    if paths_validos:
        client.storage.from_(SUPABASE_BUCKET).remove(paths_validos)
