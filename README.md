# Multi-Modal AI Chatbot RAG

A Streamlit-based chatbot powered by Google's Gemini API. This is a capstone project in progress — the current version implements a basic conversational chat interface, with multi-modal input and retrieval-augmented generation (RAG) planned as next steps.

## Current Features

- Chat interface built with [Streamlit](https://streamlit.io/)
- Conversation powered by the Gemini API (`gemini-3.6-flash`) via the `google-genai` SDK
- Responses are streamed token-by-token as they're generated, instead of waiting for the full reply
- Selectable chatbot persona (Travel Planner, Math Tutor, Chef, or a custom persona name) from the sidebar, or a fully custom system instruction
- Chat history persisted in Streamlit session state for the duration of a session
- Automatic conversation summarization every 10 user messages, keeping the context sent to the model small enough to avoid hitting context-length limits, without losing the full chat history shown on screen
- Long-term memory: the chatbot extracts and remembers facts, preferences, and past events about the user across sessions, retrieves what's relevant to each new message, and exposes a sidebar dashboard to view, edit, or delete what it remembers (see [Long-Term Memory](#long-term-memory) below)

## Planned

- Multi-modal input (images, documents, etc.)
- Retrieval-augmented generation (RAG) over a document/knowledge store

## Long-Term Memory

The chatbot maintains a persistent memory store (`memories.db`, a local SQLite file) that survives across sessions — separate from the in-session chat history. It's implemented in [memory.py](memory.py).

**Memory types**

Every memory is classified as one of three types, following the standard cognitive-memory categories:
- **Semantic** — standalone facts (e.g. "The user's name is Alex", "The user is allergic to peanuts")
- **Procedural** — how the user wants things done (e.g. "Always answer in bullet points")
- **Episodic** — specific events tied to a time or occasion (e.g. "The user mentioned traveling to Japan in March 2026")

**How memories are created (extraction)**

A second, cheaper Gemini model (`gemini-3.1-flash-lite`) acts as a dedicated memory-management agent. Every 10 user messages — the same cadence as conversation summarization, and over the same batch of messages — it's given:
1. The entire current memory store (each memory's id, type, and content)
2. The recent conversation excerpt

Under a system prompt instructing it on the three memory types and the rules for managing them, it returns a structured JSON list of operations (`add`, `update`, or `delete`), enforced via Gemini's `response_json_schema` so the output is always well-formed. This is also how contradictions are resolved: if new information conflicts with an existing memory, the model is instructed to emit an `update` against that memory's id with the corrected content, rather than create a duplicate — the latest information always overwrites the old.

**How memories are used (retrieval)**

Before generating each reply, the user's latest message is embedded (`gemini-embedding-001`) and compared via cosine similarity against all stored memory embeddings, computed in plain Python (no vector database). The top 5 most relevant memories are injected into that turn's system instruction — never into the visible chat history, so the retrieval process stays invisible to the user.

**Memory dashboard**

The sidebar includes a "Long-Term Memory" section listing every stored memory grouped by type. Each memory can be edited in place (re-embedded automatically on save) or deleted individually, and a "Delete All Memories" button (behind a confirmation checkbox) wipes the store entirely.

## Prerequisites

- Python 3.12+
- A [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key)

## Setup

1. Clone the repository and move into the project directory.

2. (Recommended) Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   `.env` is already listed in `.gitignore`, so it won't be committed.

## Running the app

Streamlit apps must be started with the `streamlit run` command, not `python`:

```
streamlit run AI_Chatbot.py
```

This starts a local server (default `http://localhost:8501`) and opens the app in your browser.

## Running with Docker

Build the image:
```
docker build -t multi-modal-ai-chatbot-rag .
```

Run the container, passing your API key and mapping Streamlit's port:
```
docker run -p 8501:8501 --env-file .env multi-modal-ai-chatbot-rag
```

## Project Structure

```
.
├── AI_Chatbot.py       # Streamlit app entry point
├── memory.py            # Long-term memory: storage, extraction, retrieval
├── requirements.txt    # Python dependencies
├── Dockerfile           # Container build definition
├── .dockerignore
├── .gitignore
├── .env                 # Local secrets (not committed)
└── memories.db           # Long-term memory store, created at runtime (not committed)
```
