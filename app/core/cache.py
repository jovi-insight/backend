# ============================================================
# Cache Temporário de Imagens
# Armazena imagens em memória com TTL de 5 minutos.
# Evita reenvio de imagem entre análise e confirmação.
# ============================================================
# Conceitos aplicados:
# - Manipulação de variáveis
# - Estruturas de decisão (if/else)
# - Estruturas de repetição (for)
# - Armazenamento com dicionário (similar a lista associativa)
# - Listas (list comprehension para filtrar expirados)
# ============================================================

import time
import threading
from dataclasses import dataclass

# [VARIÁVEL] Tempo de vida do cache em segundos (5 minutos)
_TTL_SECONDS: int = 300


@dataclass
class CacheEntry:
    """Estrutura que armazena uma imagem no cache."""
    file_bytes: bytes
    content_type: str
    created_at: float


# [ARMAZENAMENTO] Dicionário que funciona como lista associativa
_store: dict[str, CacheEntry] = {}
_lock = threading.Lock()


def salvar(cache_id: str, file_bytes: bytes, content_type: str) -> None:
    """Salva imagem no cache com timestamp de criação."""
    with _lock:
        _store[cache_id] = CacheEntry(
            file_bytes=file_bytes,
            content_type=content_type,
            created_at=time.time(),
        )


def obter(cache_id: str) -> CacheEntry | None:
    """Obtém imagem do cache se ainda não expirou."""
    with _lock:
        entry = _store.get(cache_id)

        # [DECISÃO - if] Verifica se existe
        if entry is None:
            return None

        # [DECISÃO - if] Verifica se expirou
        tempo_decorrido: float = time.time() - entry.created_at
        if tempo_decorrido > _TTL_SECONDS:
            del _store[cache_id]
            return None

        return entry


def remover(cache_id: str) -> None:
    """Remove imagem do cache após uso."""
    with _lock:
        _store.pop(cache_id, None)


def limpar_expirados() -> None:
    """Remove todas as entradas expiradas do cache."""
    agora: float = time.time()
    with _lock:
        # [LISTA - list comprehension] Filtra chaves expiradas
        expirados: list[str] = [
            chave for chave, entrada in _store.items()
            if agora - entrada.created_at > _TTL_SECONDS
        ]

        # [REPETIÇÃO - for] Remove cada entrada expirada
        for chave in expirados:
            del _store[chave]
