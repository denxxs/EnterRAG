# EnterRAG (modularized)

This refactor splits the monolithic app into a modular structure with env-based config, services, utilities, and Streamlit pages.

## Structure

- app/
  - config/settings.py — loads env vars
  - services/
    - openai_client.py — OpenAI chat/embeddings
    - chroma_store.py — ChromaDB wrapper
    - mongodb.py — MongoDB connection and CRUD
  - utils/
    - pdf.py — PDF text extraction and chunking
    - json_tools.py — dict flatten helper
  - pages/
    - chatbot.py — chatbot UI + collection manager
    - pdf_to_mongo.py — PDF -> MongoDB
    - mongo_audit.py — AI-assisted edit
    - mongo_viewer.py — view Mongo docs
- index.py — Streamlit entry wiring pages
- requirements.txt — dependencies
- .env.example — copy to .env and fill

## Setup

1. Create `.env` in project root (copy `.env.example`):

```
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb+srv://...
CHROMA_PERSIST_DIR=.chroma
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
```

2. Install dependencies:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run the app:

```
streamlit run index.py
```

## Notes
- Secrets are no longer hard-coded; everything reads from env.
- The original features are preserved: Chroma collections, chatbot, PDF->Mongo, Mongo viewer and audit, finance dashboard.
- If you used a persistent Chroma directory before, set `CHROMA_PERSIST_DIR` accordingly.
