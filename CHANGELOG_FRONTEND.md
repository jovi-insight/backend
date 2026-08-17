# Changelog Backend — Para o Front-end

## Novos Endpoints

### 1. Narrar texto (Text-to-Speech)

```
POST /ia/narrar
```

**Body (JSON):**
```json
{
  "texto": "O Egito Antigo foi uma civilização...",
  "idioma": "pt"
}
```

**Response:** Retorna áudio MP3 direto (content-type: `audio/mpeg`). Não é JSON — é o arquivo de áudio binário. No front, trata como blob/download ou toca direto.

**Idiomas suportados:** `pt`, `en`, `es`, `fr`, `de`, `it`, `ja`, `ko`, `zh`

---

### 2. Gerar Quiz

```
POST /ia/quiz
```

**Body (JSON):**
```json
{
  "conteudo_id": "uuid-do-conteudo",
  "num_perguntas": 5
}
```

**Response (JSON):**
```json
{
  "conteudo_id": "uuid",
  "perguntas": [
    {
      "id": "uuid",
      "id_conteudo": "uuid",
      "pergunta": "Qual era a base da economia do Egito Antigo?",
      "alternativa_a": "Comércio marítimo",
      "alternativa_b": "Agricultura e criação de animais",
      "alternativa_c": "Mineração de ouro",
      "alternativa_d": "Pesca",
      "resposta_correta": "b",
      "explicacao": "A economia egípcia era baseada na agricultura...",
      "criado_em": "2026-08-17T10:00:00Z"
    }
  ]
}
```

---

### 3. Buscar Quiz existente

```
GET /ia/quiz/{conteudo_id}
```

**Response:** Mesmo formato acima. Retorna 404 se não existir quiz pro conteúdo.

---

## Endpoints Alterados

### POST /conteudo/confirmar

**Mudanças:**
- Agora faz upload automático pro Google Drive (best-effort, não falha se Drive tiver problema)
- Agora retorna vídeos recomendados do YouTube junto com o conteúdo

**Response atualizado — novos campos:**
```json
{
  "id": "uuid",
  "user_id": "test_user_123",
  "pasta_id": "uuid",
  "extracao_original": "texto...",
  "resumo_ia": null,
  "ultima_atualizacao": "2026-08-17T10:00:00Z",
  "imagens": [
    {
      "id": "uuid",
      "id_conteudo": "uuid",
      "url_storage": "https://...supabase.co/storage/..."
    }
  ],
  "videos": [
    {
      "id": "uuid",
      "url": "https://www.youtube.com/results?search_query=...",
      "titulo": "Egito Antigo - Me Salva"
    }
  ]
}
```

---

### POST /ia/resumo

**Mudança:** Agora atualiza automaticamente o arquivo `.txt` no Google Drive com o resumo gerado. Nenhuma mudança na interface — response continua igual.

---

### GET /conteudo/{conteudo_id}

**Novo endpoint** que retorna um conteúdo específico com imagens e vídeos recomendados.

**Response:** Mesmo formato do `/conteudo/confirmar` acima.
