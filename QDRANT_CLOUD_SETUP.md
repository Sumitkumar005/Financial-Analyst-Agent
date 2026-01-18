# Qdrant Cloud Setup Guide

## Your Cluster Details
- **Cluster ID**: 273f28aa-76da-48ae-a13e-c55ed05fa841
- **Endpoint**: https://273f28aa-76da-48ae-a13e-c55ed05fa841.us-east4-0.gcp.cloud.qdrant.io
- **Region**: us-east4 (GCP)
- **Version**: v1.16.3

## Configuration

### Step 1: Create `.env` file
Create a `.env` file in the project root:

```env
# Qdrant Cloud Configuration
QDRANT_URL=https://273f28aa-76da-48ae-a13e-c55ed05fa841.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ZY9xJOuFt7X8hlaSxyonJD4PJo-wQ3qCg-9atesbUD8
```

**Note**: You can find your API key in the Qdrant Cloud dashboard. If your cluster doesn't require an API key, leave `QDRANT_API_KEY` empty.

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `qdrant-client` - For Qdrant connection
- `sentence-transformers` - For free embeddings (no API key needed!)

### Step 3: Test Connection
```bash
python test_qdrant_connection.py
```

### Step 4: Run Indexing
```bash
python index.py
```

## Embedding Model

We're using **sentence-transformers** with the model `all-MiniLM-L6-v2`:
- ✅ **Free** - No API key needed
- ✅ **Fast** - Runs locally
- ✅ **Good Quality** - 384 dimensions, optimized for semantic search
- ✅ **Lightweight** - ~80MB download

## Troubleshooting

### "Connection failed"
1. Check your `.env` file has the correct `QDRANT_URL`
2. Verify your cluster is running in Qdrant Cloud dashboard
3. If required, set `QDRANT_API_KEY` in `.env`

### "API key required"
- Get your API key from: https://cloud.qdrant.io
- Add it to `.env` file as `QDRANT_API_KEY=your-key`

### "Model download failed"
- Check internet connection (first run downloads the model)
- Model will be cached locally after first download
    