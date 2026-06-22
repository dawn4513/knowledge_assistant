# Knowledge Assistant MVP Design

## Overview

The MVP is a local FastAPI application that implements a small RAG workflow for Bilibili video transcripts.

RAG means retrieval-augmented generation:

1. Indexing: split transcripts into chunks, generate embeddings, and store them.
2. Retrieval: embed the user's question and find semantically similar transcript chunks.
3. Generation: pass the relevant chunks to an OpenAI chat model and generate a grounded answer.

The first version uses SQLite for persistence and stores embeddings as JSON. Vector search is implemented in Python with cosine similarity. This keeps the system small and avoids introducing a vector database before it is needed.

## Architecture

```text
Client curl
  |
  v
FastAPI app
  |
  +-- Resource service
  |     +-- create/update resources
  |     +-- split transcript into chunks
  |     +-- call OpenAI embeddings API
  |
  +-- Search service
  |     +-- embed question
  |     +-- load chunk embeddings from SQLite
  |     +-- rank chunks by cosine similarity
  |     +-- call OpenAI chat completion API
  |
  v
SQLite
  +-- resources
  +-- chunks
```

## Suggested Project Structure

```text
knowledge_assistant/
  app/
    __init__.py
    main.py
    config.py
    database.py
    models.py
    schemas.py
    services/
      __init__.py
      chunking.py
      embeddings.py
      resources.py
      search.py
      generation.py
  data/
    knowledge.db
  docs/
    requirements.md
    design.md
  requirements.txt
```

## Dependencies

Suggested dependencies:

```text
fastapi
uvicorn
openai
python-dotenv
pydantic
```

SQLite can use Python's built-in `sqlite3` module for the first version. SQLAlchemy is optional, but not required for the MVP.

## Configuration

Environment variables:

```text
OPENAI_API_KEY=...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4.1-mini
DATABASE_PATH=data/knowledge.db
```

Defaults:

- `OPENAI_EMBEDDING_MODEL`: `text-embedding-3-small`
- `DATABASE_PATH`: `data/knowledge.db`

The chat model can be adjusted later based on cost and quality requirements.

## Database Schema

### resources

```sql
CREATE TABLE IF NOT EXISTS resources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  transcript TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

### chunks

```sql
CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  resource_id INTEGER NOT NULL,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
);
```

Indexes:

```sql
CREATE INDEX IF NOT EXISTS idx_resources_url ON resources(url);
CREATE INDEX IF NOT EXISTS idx_chunks_resource_id ON chunks(resource_id);
```

## Chunking Strategy

Input transcripts are expected to be around 3,000 to 6,000 Chinese characters for 5 to 10 minute videos.

Initial strategy:

- Chunk size: about 1,000 Chinese characters.
- Overlap: about 150 Chinese characters.
- Preserve original order with `chunk_index`.
- Remove leading/trailing whitespace.
- Skip empty chunks.

This is enough to keep retrieval focused while preserving local context.

## Embedding Strategy

On resource create or transcript update:

1. Split transcript into chunks.
2. Send chunk text to the OpenAI embeddings API.
3. Store each embedding as a JSON array in SQLite.

On search:

1. Generate an embedding for the user's question.
2. Load all chunk embeddings from SQLite.
3. Compute cosine similarity between the question embedding and each chunk embedding.
4. Keep the top matching chunks.

For MVP scale, scanning all chunks in Python is acceptable. If the number of resources grows substantially, the retrieval layer can be replaced with FAISS, Chroma, LanceDB, or pgvector.

## Retrieval Strategy

Suggested initial parameters:

```text
top_k_chunks = 6
max_sources = 5
similarity_threshold = 0.25
```

Flow:

1. Rank all chunks by cosine similarity.
2. Drop chunks below `similarity_threshold`.
3. Keep the top `top_k_chunks`.
4. Group source videos by first appearance in ranked chunks.
5. Return up to `max_sources` unique videos.

The threshold should be tuned with real examples. If the assistant answers too often when the knowledge base is unrelated, increase the threshold. If it says no content too often, lower the threshold.

## Answer Generation

The generation prompt should instruct the model to:

- Answer only with the provided transcript excerpts.
- Do not use outside knowledge.
- If the excerpts are insufficient, say `没有找到相关内容。`
- Keep the answer concise and practical.
- Do not invent video sources.

Prompt shape:

```text
You are a knowledge assistant. Answer the user's question only using the provided video transcript excerpts.
If the excerpts do not contain enough relevant information, answer exactly: 没有找到相关内容。

Question:
{question}

Transcript excerpts:
[{source_number}] Title: {title}
URL: {url}
Content:
{chunk_content}
```

The API response should use the retrieved source metadata, not model-generated source metadata. This prevents hallucinated citations.

## API Design

### GET /health

Returns service status.

### POST /resources

Creates a new resource.

Status codes:

- `201`: created.
- `409`: URL already exists.
- `422`: invalid request.
- `500`: embedding or storage failure.

### PUT /resources

Updates an existing resource identified by URL.

Status codes:

- `200`: updated.
- `404`: URL not found.
- `422`: invalid request.
- `500`: embedding or storage failure.

### GET /resources

Lists resources without full transcript text.

Status codes:

- `200`: success.

### POST /search

Searches resources and generates an answer.

Status codes:

- `200`: success, including no-content responses.
- `422`: invalid request.
- `500`: embedding, retrieval, or generation failure.

## Error Handling

Use clear JSON errors:

```json
{
  "detail": "Resource with this URL already exists."
}
```

Recommended cases:

- Duplicate URL on create.
- Missing resource on update.
- Empty title, URL, transcript, or question.
- OpenAI API request failure.
- Database failure.

## Implementation Order

1. Add FastAPI dependencies.
2. Create app structure.
3. Implement configuration loading.
4. Implement SQLite initialization.
5. Implement resource create, update, and list APIs.
6. Implement transcript chunking.
7. Implement OpenAI embedding service.
8. Store chunks and embeddings.
9. Implement cosine similarity retrieval.
10. Implement OpenAI answer generation.
11. Add curl examples to README.
12. Add focused tests or manual verification commands.

## Manual Verification Examples

Start server:

```bash
uvicorn app.main:app --reload
```

Add resource:

```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.bilibili.com/video/example",
    "title": "Example video",
    "transcript": "Transcript text here"
  }'
```

Search:

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does the video say about semantic search?"
  }'
```

Expected no-content response:

```json
{
  "answer": "没有找到相关内容。",
  "sources": []
}
```

## Future Extensions

- Add timestamp-level citations if transcripts include time ranges.
- Add automatic Bilibili subtitle extraction.
- Add audio transcription pipeline.
- Add web UI for resource management and search.
- Add tags, notes, and collections.
- Add vector database support when local scanning becomes slow.
- Add streaming answer responses.
- Add tests with mocked OpenAI clients.
