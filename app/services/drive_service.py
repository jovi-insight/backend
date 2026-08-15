# ============================================================
# Service: Google Drive (OAuth2 com refresh token)
# Faz upload de imagens e resumos para o Google Drive do
# usuário usando credenciais OAuth2 pessoais.
# ============================================================

import io
import os
import json
import uuid
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.core.config import GOOGLE_DRIVE_FOLDER_ID

_service = None

SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../../token.json")
TOKEN_PATH = os.path.abspath(TOKEN_PATH)

# Variável de ambiente alternativa (pro Render e outros deploys)
GOOGLE_DRIVE_TOKEN_JSON = os.getenv("GOOGLE_DRIVE_TOKEN_JSON", "")


def _get_service():
    """Inicializa o cliente do Google Drive usando OAuth2 token."""
    global _service
    if _service is not None:
        return _service

    creds = None

    # Prioridade 1: variável de ambiente (produção/Render)
    if GOOGLE_DRIVE_TOKEN_JSON:
        token_data = json.loads(GOOGLE_DRIVE_TOKEN_JSON)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    # Prioridade 2: arquivo local (desenvolvimento)
    elif os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds:
        return None

    # Renova o token se expirou
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Salva atualização no arquivo local (se existir)
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())

    if not creds.valid:
        return None

    _service = build("drive", "v3", credentials=creds)
    return _service


def _buscar_ou_criar_pasta(nome: str, parent_id: str) -> str:
    """Busca ou cria pasta pelo nome dentro do parent."""
    service = _get_service()
    if not service:
        return ""

    query = (
        f"name='{nome}' and "
        f"'{parent_id}' in parents and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"trashed=false"
    )
    resultado = service.files().list(q=query, fields="files(id)").execute()
    arquivos = resultado.get("files", [])

    if arquivos:
        return arquivos[0]["id"]

    metadata = {
        "name": nome,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    pasta = service.files().create(body=metadata, fields="id").execute()
    return pasta["id"]


async def upload_para_drive(
    nome_materia: str,
    image_bytes: bytes,
    content_type: str,
    texto_extraido: str,
    resumo: str | None = None,
) -> dict[str, str]:
    """
    Faz upload da imagem e do resumo para o Google Drive.
    Organiza em: JOVI_FOLDER / matéria / imagem + resumo.txt
    """
    service = _get_service()
    if not service or not GOOGLE_DRIVE_FOLDER_ID:
        return {}

    pasta_materia_id: str = _buscar_ou_criar_pasta(nome_materia, GOOGLE_DRIVE_FOLDER_ID)
    urls: dict[str, str] = {}

    # Upload da imagem
    extensao_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    ext = extensao_map.get(content_type, ".jpg")
    nome_imagem = f"conteudo_{uuid.uuid4().hex[:8]}{ext}"

    if image_bytes:
        media_imagem = MediaIoBaseUpload(
            io.BytesIO(image_bytes), mimetype=content_type, resumable=True
        )
        metadata_imagem = {
            "name": nome_imagem,
            "parents": [pasta_materia_id],
        }
        arquivo_imagem = (
            service.files()
            .create(body=metadata_imagem, media_body=media_imagem, fields="id, webViewLink")
            .execute()
        )
        urls["imagem_drive_url"] = arquivo_imagem.get("webViewLink", "")

    # Upload do resumo como .txt
    conteudo_texto = f"TEXTO EXTRAÍDO:\n{texto_extraido}\n"
    if resumo:
        conteudo_texto += f"\nRESUMO:\n{resumo}\n"

    media_texto = MediaIoBaseUpload(
        io.BytesIO(conteudo_texto.encode("utf-8")),
        mimetype="text/plain",
        resumable=True,
    )
    metadata_texto = {
        "name": f"resumo_{uuid.uuid4().hex[:8]}.txt",
        "parents": [pasta_materia_id],
    }
    arquivo_texto = (
        service.files()
        .create(body=metadata_texto, media_body=media_texto, fields="id, webViewLink")
        .execute()
    )
    urls["resumo_drive_url"] = arquivo_texto.get("webViewLink", "")

    return urls


def is_configured() -> bool:
    """Verifica se o Google Drive está configurado (token existe e válido)."""
    return os.path.exists(TOKEN_PATH) and bool(GOOGLE_DRIVE_FOLDER_ID)


async def atualizar_resumo_drive(
    nome_materia: str,
    texto_extraido: str,
    resumo: str,
) -> None:
    """
    Busca o arquivo resumo mais recente na pasta da matéria e atualiza.
    Se não encontrar, cria um novo.
    """
    service = _get_service()
    if not service or not GOOGLE_DRIVE_FOLDER_ID:
        return

    pasta_materia_id: str = _buscar_ou_criar_pasta(nome_materia, GOOGLE_DRIVE_FOLDER_ID)

    # Busca o resumo mais recente na pasta
    query = (
        f"'{pasta_materia_id}' in parents and "
        f"name contains 'resumo_' and "
        f"mimeType='text/plain' and "
        f"trashed=false"
    )
    resultado = (
        service.files()
        .list(q=query, fields="files(id, name)", orderBy="createdTime desc", pageSize=1)
        .execute()
    )
    arquivos = resultado.get("files", [])

    conteudo_texto = f"TEXTO EXTRAÍDO:\n{texto_extraido}\n\nRESUMO:\n{resumo}\n"
    media = MediaIoBaseUpload(
        io.BytesIO(conteudo_texto.encode("utf-8")),
        mimetype="text/plain",
        resumable=True,
    )

    if arquivos:
        # Atualiza o arquivo existente
        file_id = arquivos[0]["id"]
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # Cria novo se não existir
        metadata = {
            "name": f"resumo_{uuid.uuid4().hex[:8]}.txt",
            "parents": [pasta_materia_id],
        }
        service.files().create(body=metadata, media_body=media, fields="id").execute()
