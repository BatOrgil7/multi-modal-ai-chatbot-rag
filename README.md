# Multi-Modal AI Chatbot RAG

A Streamlit-based chatbot powered by Google's Gemini API. This is a capstone project in progress — the current version implements a basic conversational chat interface, with multi-modal input and retrieval-augmented generation (RAG) planned as next steps.

## Current Features

- Chat interface built with [Streamlit](https://streamlit.io/)
- Conversation powered by the Gemini API (`gemini-3.6-flash`) via the `google-genai` SDK
- Responses are streamed token-by-token as they're generated, instead of waiting for the full reply
- Selectable chatbot persona (Travel Planner, Math Tutor, Chef, or a custom persona name) from the sidebar, or a fully custom system instruction
- Chat history persisted in Streamlit session state for the duration of a session
- Automatic conversation summarization every 10 user messages, keeping the context sent to the model small enough to avoid hitting context-length limits, without losing the full chat history shown on screen

## Planned

- Multi-modal input (images, documents, etc.)
- Retrieval-augmented generation (RAG) over a document/knowledge store

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
├── requirements.txt    # Python dependencies
├── Dockerfile           # Container build definition
├── .dockerignore
├── .gitignore
└── .env                 # Local secrets (not committed)
```
