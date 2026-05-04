"""Cache temporário de imagens com expiração de 5 minutos."""
import time
import threading
from dataclasses import dataclass

_TTL_SECONDS = 300  # 5 minutos


@dataclass
class CacheEntry:
    file_bytes: bytes
    content_type: str
    created_at: float


_store: dict[str, CacheEntry] = {}
_lock = threading.Lock()


def salvar(cache_id: str, file_bytes: bytes, content_type: str) -> None:
    """Salva imagem no cache."""
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
        if entry is None:
            return None
        if time.time() - entry.created_at > _TTL_SECONDS:
            del _store[cache_id]
            return None
        return entry


def remover(cache_id: str) -> None:
    """Remove imagem do cache."""
    with _lock:
        _store.pop(cache_id, None)


def limpar_expirados() -> None:
    """Remove todas as entradas expiradas."""
    agora = time.time()
    with _lock:
        expirados = [k for k, v in _store.items() if agora - v.created_at > _TTL_SECONDS]
        for k in expirados:
            del _store[k]
