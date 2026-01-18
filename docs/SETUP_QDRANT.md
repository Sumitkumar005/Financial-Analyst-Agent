# Qdrant Setup Guide

## Option 1: Docker (Recommended - Easiest)

### Step 1: Start Qdrant Container
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

This will:
- Start Qdrant on `http://localhost:6333`
- Web UI available at `http://localhost:6333/dashboard`
- Persist data in Docker volume (data survives container restarts)

### Step 2: Verify Connection
Open browser: `http://localhost:6333/dashboard`

You should see the Qdrant dashboard.

### Step 3: Run Indexing
```bash
python index.py
```

## Option 2: Local Installation

### Step 1: Install Qdrant
```bash
# On Windows (using PowerShell)
# Download from: https://github.com/qdrant/qdrant/releases
# Or use WSL and follow Linux instructions
```

### Step 2: Start Qdrant Server
```bash
qdrant
```

### Step 3: Run Indexing
```bash
python index.py
```

## Option 3: Cloud Qdrant (Production)

1. Sign up at https://cloud.qdrant.io
2. Create a cluster
3. Get API key and endpoint
4. Set environment variables:
   ```bash
   export QDRANT_HOST=your-cluster.qdrant.io
   export QDRANT_PORT=443
   export QDRANT_API_KEY=your-api-key
   ```

## Environment Variables

Create a `.env` file (optional):
```env
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# OpenAI API (for embeddings)
OPENAI_API_KEY=your-api-key-here

# Alternative: Use Jina embeddings (free, no API key needed)
# Just install: pip install jina
```

## Testing Qdrant Connection

Run this quick test:
```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
collections = client.get_collections()
print(f"Connected! Collections: {[c.name for c in collections.collections]}")
```

## Troubleshooting

### "Connection refused"
- Make sure Qdrant is running: `docker ps` (for Docker)
- Check port 6333 is not blocked by firewall

### "Collection already exists"
- The script will ask if you want to recreate it
- Or manually delete: `client.delete_collection("financial_reports")`

### "OpenAI API key not found"
- The script will use dummy embeddings (for testing only)
- For production, set `OPENAI_API_KEY` environment variable
- Or use Jina embeddings (free alternative)
