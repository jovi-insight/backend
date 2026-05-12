# JOVI API

API de produtividade estudantil construída com FastAPI, SQLAlchemy 2.0, PostgreSQL, Supabase Storage e Groq (IA).

## Estrutura do Projeto

```
├── cli.py                         # Interface de linha de comando (menu interativo)
├── Dockerfile                     # Container para deploy
├── requirements.txt               # Dependências Python
├── .env.example                   # Modelo de variáveis de ambiente
├── documentacao.md                # Documentação técnica do projeto
├── app/
│   ├── main.py                    # Ponto de entrada da API, CORS, Scalar
│   ├── core/
│   │   ├── config.py              # Variáveis de ambiente
│   │   ├── auth.py                # Mock de autenticação (get_current_user)
│   │   ├── database.py            # Engine, sessão e init_db()
│   │   ├── cache.py               # Cache temporário de imagens (TTL 5 min)
│   │   └── seed.py                # Seed de matérias base no startup
│   ├── models/
│   │   ├── materia.py             # Matéria (id, nome unique)
│   │   ├── pasta.py               # Pasta (user_id, id_materia FK, soft delete)
│   │   ├── conteudo.py            # Conteúdo (user_id, pasta_id FK, soft delete)
│   │   ├── imagens.py             # Imagem (id_conteudo FK, url_storage)
│   │   ├── audio.py               # Áudio (id_conteudo FK, url_storage)
│   │   └── termos_chave.py        # Termo-chave (id_conteudo FK, termo)
│   ├── schemas/
│   │   ├── materia.py             # MateriaCreate, MateriaOut
│   │   ├── pasta.py               # PastaOut, PastaDetailOut, PastaUpdate
│   │   ├── conteudo.py            # ConteudoConfirmarRequest, ConteudoOut
│   │   ├── imagem.py              # ImagemOut
│   │   ├── audio.py               # AudioOut
│   │   └── ia.py                  # AnalisarImagemResponse, Tradução, Resumo
│   ├── services/
│   │   ├── conteudo_service.py    # Criação de conteúdo e listagem de recentes
│   │   ├── pasta_service.py       # CRUD de pastas com soft delete
│   │   ├── storage_service.py     # Upload de imagens para Supabase Storage
│   │   └── gemini_service.py      # Integração com Groq (análise, tradução, resumo)
│   └── routers/
│       ├── ia.py                  # Endpoints de IA
│       ├── conteudo.py            # Confirmação de conteúdo
│       ├── dashboard.py           # Conteúdos recentes
│       ├── pastas.py              # CRUD de pastas
│       └── materias.py            # CRUD de matérias
```

## Pré-requisitos

- Python 3.12+
- PostgreSQL (local via Docker ou remoto via Aiven/Supabase)
- Conta no Supabase (Storage)
- API Key do Groq (gratuita — https://console.groq.com/keys)

## Instalação e Execução Local

### 1. Clone o repositório

```bash
git clone https://github.com/jovi-insight/backend.git
cd backend
```

### 2. Crie e ative o ambiente virtual

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

### 5. Inicie a API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

### 6. Execute o CLI (em outro terminal)

```bash
python3 cli.py
```

O CLI se conecta à API local por padrão. Para apontar para outro endereço:

```bash
JOVI_API_URL=https://sua-api.onrender.com python3 cli.py
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | Connection string do PostgreSQL (usar `postgresql://`) |
| `SUPABASE_URL` | URL do projeto Supabase (`https://xxx.supabase.co`) |
| `SUPABASE_KEY` | Chave `service_role` do Supabase |
| `SUPABASE_BUCKET` | Nome do bucket no Supabase Storage |
| `GROQ_API_KEY` | API Key do Groq |

## Documentação Interativa

- Swagger UI: `http://localhost:8000/docs`
- Scalar: `http://localhost:8000/scalar`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/ia/analisar-imagem` | Envia imagem → extrai texto + sugere matéria + retorna cache_id |
| POST | `/ia/traduzir-imagem` | Envia imagem → traduz conteúdo para pt-BR |
| POST | `/ia/traduzir-texto` | Envia texto → traduz para idioma destino |
| POST | `/ia/resumo` | Gera resumo por IA de um conteúdo salvo |
| POST | `/conteudo/confirmar` | Confirma conteúdo (usa cache_id, sem reenviar imagem) |
| GET | `/dashboard/recentes` | 4 conteúdos mais recentes do usuário |
| GET | `/materias` | Lista todas as matérias |
| POST | `/materias` | Cria nova matéria |
| PUT | `/materias/{id}` | Atualiza nome da matéria |
| DELETE | `/materias/{id}` | Remove matéria |
| GET | `/pastas` | Lista pastas do usuário (com contagem) |
| GET | `/pastas/{id}` | Detalhe da pasta com conteúdos |
| PUT | `/pastas/{id}` | Atualiza nome da pasta |
| DELETE | `/pastas/{id}` | Soft delete da pasta e conteúdos |

## CLI — Interface de Linha de Comando

O `cli.py` é um programa interativo que consome a API via terminal:

```
=== JOVI - Produtividade Estudantil ===
1. Analisar imagem (extrair texto e sugerir matéria)
2. Confirmar conteúdo (salvar no sistema)
3. Traduzir texto
4. Gerar resumo por IA
5. Listar matérias
6. Listar pastas do usuário
7. Ver conteúdos recentes
0. Sair
```

Cada opção solicita os dados necessários, chama a API e exibe o resultado formatado.

## Fluxo Principal

1. **Análise**: `POST /ia/analisar-imagem` com a foto do caderno
   - Retorna texto extraído, matéria sugerida e `cache_id`
   - Imagem fica em cache por 5 minutos
2. **Confirmação**: `POST /conteudo/confirmar` com `{cache_id, id_materia, texto_extraido}`
   - Sobe imagem do cache pro Supabase Storage (organizada por matéria)
   - Cria pasta (se necessário) e conteúdo no banco
3. **Resumo**: `POST /ia/resumo` com `{conteudo_id}`
   - Gera resumo estruturado e salva no banco

## Docker

```bash
# Build
docker build -t jovi-app .

# Run (local)
docker run -p 8000:8000 --env-file .env jovi-app
```

## Deploy no Render

1. Crie um Web Service no Render apontando pro repositório
2. Selecione "Docker" como ambiente
3. Configure as variáveis de ambiente
4. O Render detecta o `Dockerfile` e faz o build automaticamente

## Autenticação

Atualmente usa um mock que retorna `"test_user_123"` como user_id.
Para implementar autenticação real, substitua `get_current_user` em `app/core/auth.py`.
