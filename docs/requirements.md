# Knowledge Assistant MVP Requirements

## Background

This project is a local knowledge assistant for Bilibili video resources. The user manually adds video links and their transcript text, then asks questions. The system answers only from the added video content and returns the referenced videos.

The first version focuses on a minimal but useful local FastAPI service. It does not include a web UI, user accounts, automatic Bilibili crawling, or automatic audio transcription.

## Goals

- Add Bilibili video resources through HTTP APIs.
- Use the Bilibili video URL as the unique resource key.
- Allow updating an existing video's title and transcript.
- Search resources semantically, not only by exact keywords.
- Generate answers based on relevant video transcript content.
- Return all referenced videos used by the answer.
- Return a clear "no relevant content found" response when the knowledge base does not contain enough related information.

## Non-Goals

- No web frontend in the first version.
- No login, permission, or multi-user support.
- No automatic Bilibili subtitle extraction.
- No automatic audio/video transcription.
- No timestamp-level citation.
- No vector database service dependency.
- No cloud database.

## User Workflow

### Add A Resource

1. The user gets the transcript from a third-party tool.
2. The user calls the local API with a Bilibili URL, title, and transcript.
3. The system rejects duplicate URLs for create requests.
4. The system stores the resource and prepares it for semantic search.

### Update A Resource

1. The user calls the update API with an existing Bilibili URL.
2. The user may update the title and transcript.
3. If the transcript changes, the system regenerates searchable chunks and embeddings.

### Search Resources

1. The user submits a natural-language question.
2. The system retrieves relevant transcript chunks from one or more videos.
3. If the retrieved content is not relevant enough, the system returns no result.
4. Otherwise, the system generates an answer grounded in the retrieved transcript chunks.
5. The response includes the referenced video titles and URLs.

## Third-Party Transcript Tools

The first version expects the user to manually provide transcript text. Recommended tools:

- Feishu Minutes: upload audio/video and generate transcripts.
- Tongyi Tingwu: audio/video transcription and meeting-style summaries.
- iFlyrec: audio transcription and speech-to-text.
- Jianying/CapCut: automatic subtitle recognition for videos.

## Functional Requirements

### Resource Creation

Endpoint:

```text
POST /resources
```

Request:

```json
{
  "url": "https://www.bilibili.com/video/...",
  "title": "Video title",
  "transcript": "Full transcript text"
}
```

Rules:

- `url` is required.
- `title` is required.
- `transcript` is required.
- `url` must be unique.
- Duplicate `url` returns a conflict error.
- After saving, the transcript is split into chunks and embeddings are generated.

### Resource Update

Endpoint:

```text
PUT /resources
```

Request:

```json
{
  "url": "https://www.bilibili.com/video/...",
  "title": "Updated video title",
  "transcript": "Updated transcript text"
}
```

Rules:

- `url` identifies the existing resource.
- Updating `title` is supported.
- Updating `transcript` is supported.
- If `transcript` changes, old chunks are deleted and new chunks plus embeddings are created.
- If the resource does not exist, return not found.

### Resource List

Endpoint:

```text
GET /resources
```

Response:

```json
[
  {
    "url": "https://www.bilibili.com/video/...",
    "title": "Video title",
    "created_at": "2026-06-21T12:00:00Z",
    "updated_at": "2026-06-21T12:00:00Z"
  }
]
```

Rules:

- Do not return full transcript text in list responses by default.
- Sort by latest update time descending.

### Search

Endpoint:

```text
POST /search
```

Request:

```json
{
  "question": "What is my question?"
}
```

Response when relevant content exists:

```json
{
  "answer": "Answer based on added video transcripts.",
  "sources": [
    {
      "url": "https://www.bilibili.com/video/...",
      "title": "Video title"
    }
  ]
}
```

Response when no relevant content exists:

```json
{
  "answer": "没有找到相关内容。",
  "sources": []
}
```

Rules:

- Search must support semantic matching through embeddings.
- A question may match multiple videos.
- The answer must only use retrieved transcript content.
- The source list must contain unique videos.
- Source order should follow relevance.
- If no retrieved chunk passes the relevance threshold, return the no-content response.

### Health Check

Endpoint:

```text
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Data Requirements

Resource fields:

- `id`
- `url`
- `title`
- `transcript`
- `created_at`
- `updated_at`

Chunk fields:

- `id`
- `resource_id`
- `chunk_index`
- `content`
- `embedding`
- `created_at`

## Quality Requirements

- Local-first: the app should run on a developer machine.
- Simple setup: install dependencies, set OpenAI API key, run FastAPI.
- Deterministic storage: SQLite is used for local persistence.
- Clear errors: duplicate resources, missing resources, invalid input, and OpenAI API failures should return understandable API errors.
- Grounded answers: generation should be constrained to retrieved transcript chunks.

## Acceptance Criteria

- A user can start the FastAPI service locally.
- A user can add a Bilibili video resource with a transcript by `curl`.
- Adding the same URL twice returns a conflict error.
- A user can update title and transcript for an existing URL.
- A user can list added resources.
- A user can ask a semantic question and get an answer with one or more video sources.
- A question with no relevant content returns `没有找到相关内容。` and an empty source list.
