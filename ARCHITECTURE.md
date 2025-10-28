# TrafficLaw Chatbot Architecture

## Monorepo Structure

```
trafficlaw_chatbot/
├── apps/
│   ├── web/                 # Next.js Frontend (port 3000)
│   │   ├── src/app/page.tsx
│   │   └── package.json
│   └── api/                 # Next.js API Gateway (port 3001)
│       ├── src/app/api/
│       │   ├── chat/route.ts
│       │   ├── sessions/[sessionId]/route.ts
│       │   └── health/route.ts
│       └── package.json
├── main.py                  # Python Backend (port 8000)
├── rag_pipeline.py
├── data_preprocessing.py
├── models/
├── schemas/
├── utils/
└── data/
    └── raw/                 # PDF corpus
```

## Data Flow

```
User Query
    ↓
Next.js Frontend (port 3000)
    ↓ HTTP POST /api/chat
Next.js API Gateway (port 3001)
    ↓ HTTP POST /chat
Python Backend (port 8000)
    ↓ SQL Query
PostgreSQL + pgvector
    ↓ Vector Search + LLM
Response
    ↓
Next.js API Gateway
    ↓
Next.js Frontend
    ↓
User Interface
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Next.js Frontend | 3000 | React UI, user interface |
| Next.js API | 3001 | API gateway, request routing |
| Python Backend | 8000 | RAG pipeline, ML models |
| PostgreSQL | 5432 | Vector database, embeddings |

## Benefits

1. **Clean Separation**: Frontend, API, and ML services are isolated
2. **Scalability**: Each service can be scaled independently
3. **Development**: Use the right tool for each job
4. **Maintenance**: Easier to debug and modify individual components
5. **Deployment**: Can deploy services separately if needed
