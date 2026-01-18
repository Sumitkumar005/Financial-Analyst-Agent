# Test the API

## ✅ Index Created Successfully!

The ticker index has been created in Qdrant. The API should now work properly!

## 🚀 Test Your Query

### Your Original Query:
```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "tell me about Business Company Background of Apple Inc",
  "max_companies": 2
}'
```

### Expected Flow:
1. **Router**: Extracts "Apple Inc" → Finds ticker "AAPL"
2. **Retriever**: Queries Qdrant with filter (now works with index!)
3. **Loader**: Loads `processed_data/AAPL_2024.md` from disk
4. **Generator**: Sends full content to Gemini 2.5 Flash
5. **Response**: Analysis about Apple's business background

## 📝 Other Test Queries

### Compare Companies:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare AWS and Azure revenue", "max_companies": 2}'
```

### Financial Analysis:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Microsoft's net income in 2024?", "max_companies": 1}'
```

### Semantic Search:
```bash
curl -X POST http://localhost:8000/search?query=cloud%20computing&limit=5
```

## 🔍 Check Server Status

Make sure server is running:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "collections": ["financial_reports"],
  "embedding_model": "all-MiniLM-L6-v2"
}
```

## 🎯 What to Expect

The `/analyze` endpoint will:
1. Find the company (AAPL for Apple)
2. Load the full Markdown file
3. Send to Gemini 2.5 Flash for analysis
4. Return structured response with:
   - Query
   - Companies found
   - File paths
   - **Full analysis from Gemini**
   - Metadata

The analysis will include accurate information from Apple's 10-K filing! 🚀
