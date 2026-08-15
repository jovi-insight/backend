"""
Script de autorização OAuth2 para o Google Drive.
Rode UMA VEZ para gerar o token.json que o backend usará.

Pré-requisitos:
1. Baixe o oauth-credentials.json do Google Cloud Console
   (APIs & Services > Credentials > OAuth 2.0 Client IDs > Desktop App)
2. Coloque na raiz do projeto como 'oauth-credentials.json'
3. Rode: python3 auth_drive.py
4. Autorize no navegador
5. O token.json será gerado automaticamente
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "oauth-credentials.json"
TOKEN_FILE = "token.json"


def main():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Arquivo '{CREDENTIALS_FILE}' não encontrado.")
        print("   Baixe do Google Cloud Console (OAuth 2.0 Client ID - Desktop App)")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print(f"✅ Token salvo em '{TOKEN_FILE}'")
    print("   O backend agora pode fazer uploads pro seu Google Drive.")


if __name__ == "__main__":
    main()
