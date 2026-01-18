# Backend Structure

This directory contains the backend application for the Financial Analyst Agent.

## Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── qdrant_service.py      # Qdrant client service
│   │   ├── embedding_service.py   # Embedding model service
│   │   ├── llm_service.py        # Gemini LLM service
│   │   └── file_service.py        # File retrieval service
│   └── utils/
│       ├── __init__.py
│       ├── html_extractor.py      # HTML extraction utilities
│       ├── markdown_converter.py   # Markdown conversion utilities
│       └── ticker_extractor.py     # Ticker extraction utilities
├── scripts/
│   ├── __init__.py
│   ├── index.py                    # Index all companies in Qdrant
│   ├── chunk_markdown_files.py     # Chunk files for smart retrieval
│   ├── create_ticker_index.py      # Create ticker index in Qdrant
│   ├── index_uploaded_files.py    # Index uploaded files
│   ├── convert_all_to_markdown.py  # Convert all HTML to Markdown
│   ├── extract_all_html.py         # Extract HTML from all TXT files
│   └── convert_html_to_markdown.py  # HTML to Markdown conversion utility
└── tests/
    ├── __init__.py
    ├── test_api.py                 # API endpoint tests
    └── test_qdrant_connection.py   # Qdrant connection test
```

## Running the Server

From the project root:

```bash
python -m backend.app.main
```

Or using uvicorn directly:

```bash
uvicorn backend.app.main:app --reload
```

## Running Scripts

From the project root:

```bash
# Index all companies
python -m backend.scripts.index

# Chunk markdown files
python -m backend.scripts.chunk_markdown_files

# Create ticker index
python -m backend.scripts.create_ticker_index
```

## Installation

Install dependencies from the project root:

```bash
pip install -r backend/requirements.txt
```

## Configuration

All configuration is in `app/config.py` and uses environment variables from `.env` file in the project root.
