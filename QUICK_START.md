# Quick Start Guide

## ✅ Configuration Complete!

Your server is now configured with:
- **Gemini API Key**: `AIzaSyB9jwQNFxk2k12RFAumXibX24hPHJVYqHk`
- **Model**: `gemini-2.5-flash`
- **Qdrant**: Connected to Cloud
- **89 Companies**: Indexed and ready

## 🚀 Start the Server

### Option 1: Using Batch File (Windows)
```bash
start_server.bat
```

### Option 2: Manual Start
```bash
.\venv\Scripts\activate
python server.py
```

The server will start at: **http://localhost:8000**

## 📝 Test the API

### 1. Health Check
Open browser: http://localhost:8000/health

### 2. List Companies
Open browser: http://localhost:8000/companies

### 3. Interactive API Docs
Open browser: http://localhost:8000/docs

### 4. Test Analysis (using curl or Postman)
```bash
curl -X POST http://localhost:8000/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"Compare AWS and Azure revenue\", \"max_companies\": 2}"
```

Or use Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={"query": "Compare AWS and Azure revenue", "max_companies": 2}
)
print(response.json())
```

## 🎯 How It Works

1. **Query**: "Compare AWS and Azure revenue"
2. **Router**: Extracts tickers → ['AMZN', 'MSFT']
3. **Retriever**: Finds files in Qdrant
4. **Loader**: Loads full MD files from disk
5. **Generator**: Sends to Gemini 2.5 Flash for analysis
6. **Response**: Structured analysis with accurate data

## 📊 What's Indexed

- **Qdrant**: Summaries + metadata (for fast search)
- **Disk**: Full MD files (for complete analysis)
- **Gemini**: Receives full files (or smart-extracted sections)

## 💡 Solution for Large Files

- Most files: **Direct full file** (fits in Gemini's 1M token window)
- Large files: **Smart section extraction** (tables stay intact)
- Complex queries: **Two-pass analysis**

**No chunking needed!** Tables are always preserved! 🚀
