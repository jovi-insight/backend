# JOVI API

API de produtividade estudantil construída com FastAPI, SQLAlchemy 2.0, PostgreSQL, Supabase Storage e Groq (IA).

## Estrutura do Projeto

```
app/
├── main.py                    # Ponto de entrada, lifespan, Scalar
├── core/
│   ├── config.py              # Variáveis de ambiente
│   ├── auth.py                # Mock de autenticação (get_current_user)
│   ├── database.py            # Engine, sessão e init_db()
│   ├── cache.py               # Cache temporário de imagens (TTL 5 min)
│   └── seed.py                # Seed de matérias base no startup
├── models/
│   ├── materia.py             # Matéria (id, nome unique)
│   ├── pasta.py               # Pasta (user_id, id_materia FK, soft delete)
│   ├── conteudo.py            # Conteúdo (user_id, pasta_id FK, soft delete)
│   ├── imagens.py             # Imagem (id_conteudo FK, url_storage)
│   ├── audio.py               # Áudio (id_conteudo FK, url_storage)
│   └── termos_chave.py        # Termo-chave (id_conteudo FK, termo)
├── schemas/
│   ├── materia.py             # MateriaCreate, MateriaOut
│   ├── pasta.py               # PastaOut, PastaDetailOut
│   ├── conteudo.py            # ConteudoConfirmarRequest, ConteudoOut
│   ├── imagem.py              # ImagemOut
│   ├── audio.py               # AudioOut
│   └── ia.py                  # AnalisarImagemResponse, Tradução, Resumo
├── services/
│   ├── conteudo_service.py    # Criação de conteúdo e listagem de recentes
│   ├── pasta_service.py       # CRUD de pastas com soft delete
│   ├── storage_service.py     # Upload de imagens para Supabase Storage
│   └── gemini_service.py      # Integração com Groq (análise, tradução, resumo)
└── routers/
    ├── ia.py                  # Endpoints de IA
    ├── conteudo.py            # Confirmação de conteúdo
    ├── dashboard.py           # Conteúdos recentes
    ├── pastas.py              # CRUD de pastas
    └── materias.py            # CRUD de matérias
```

## Pré-requisitos

- Python 3.12+
- PostgreSQL (local ou Docker)
- Conta no Supabase (Storage)
- API Key do Groq (gratuita)

## Instalação e Execução Local

```bash
# Cria e ativa ambiente virtual
python3.12 -m venv venv
source venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Configura variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Inicia a aplicação
uvicorn app.main:app --reload
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | Connection string do PostgreSQL |
| `SUPABASE_URL` | URL do projeto Supabase (`https://xxx.supabase.co`) |
| `SUPABASE_KEY` | Chave `anon public` ou `service_role` do Supabase |
| `SUPABASE_BUCKET` | Nome do bucket no Supabase Storage |
| `GROQ_API_KEY` | API Key do Groq (https://console.groq.com/keys) |

## Documentação da API

- Swagger UI: `http://localhost:8000/docs`
- Scalar: `http://localhost:8000/scalar`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Endpoints

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
| DELETE | `/materias/{id}` | Remove matéria |
| GET | `/pastas` | Lista pastas do usuário (com contagem) |
| GET | `/pastas/{id}` | Detalhe da pasta com conteúdos |
| DELETE | `/pastas/{id}` | Soft delete da pasta e conteúdos |

## Fluxo Principal

1. **Análise**: `POST /ia/analisar-imagem` com a foto do caderno
   - Retorna texto extraído, matéria sugerida e `cache_id`
   - Imagem fica em cache por 5 minutos
2. **Confirmação**: `POST /conteudo/confirmar` com `{cache_id, id_materia, texto_extraido}`
   - Sobe imagem do cache pro Supabase Storage (organizada por matéria)
   - Cria pasta (se necessário) e conteúdo no banco
3. **Resumo**: `POST /ia/resumo` com `{conteudo_id}`
   - Gera resumo estruturado e salva no banco

## Modelagem de Dados

```
Materia 1──N Pasta 1──N Conteudo 1──N Imagem
                                  1──N Audio
                                  1──N TermoChave
```

- IDs são UUID gerados automaticamente
- Tabelas criadas no startup via `init_db()`
- Soft delete em Pasta e Conteúdo (campos `deletado` e `deletado_em`)
- Matérias base são inseridas automaticamente no primeiro startup

## Deploy no Render

1. Crie um Web Service no Render apontando pro repositório
2. Selecione "Docker" como ambiente
3. Configure as variáveis de ambiente (mesmas do `.env`)
4. O Render detecta o `Dockerfile` e faz o build automaticamente

## Docker Local

```bash
docker build -t jovi-api .
docker run -p 8000:8000 --env-file .env jovi-api
```

## Autenticação

Atualmente usa um mock que retorna `"test_user_123"` como user_id.
Para implementar autenticação real, substitua `get_current_user` em `app/core/auth.py`.
