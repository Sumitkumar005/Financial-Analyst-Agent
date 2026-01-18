# Uploaded Files RAG Pipeline

## ✅ What Was Implemented

### 1. **HTML File Download**
- Uploaded files now save both HTML and Markdown versions
- Frontend displays "Download HTML" button alongside "Download MD"
- HTML files are saved as `{TICKER}_uploaded.html` in `processed_data/`

### 2. **Automatic RAG Indexing**
- When a file is uploaded, it's **automatically indexed in Qdrant**
- Same pipeline as the original 89 companies:
  - Extracts summary (first 2000 chars + key sections)
  - Generates embeddings using `all-MiniLM-L6-v2`
  - Stores in Qdrant with metadata
- **Tagged with `"source": "uploaded"`** to separate from original 89

### 3. **Ready for QnA Indicator**
- Frontend shows a beautiful "Ready for QnA & Agentic Analysis!" badge
- Appears when file is successfully indexed
- Indicates the file is ready to use in the Analyze tab

### 4. **Smart File Selection**
- `/analyze` endpoint now **prefers uploaded files** over original 89
- If both exist for the same ticker, uploaded version is used
- Falls back to original if uploaded version doesn't exist

### 5. **Separate Collections (Optional)**
- Uploaded files are tagged with `"source": "uploaded"` in payload
- Can be filtered separately if needed
- Original 89 companies have no `source` tag (or `"source": "original"`)

## 📁 File Structure

```
processed_data/
├── AAPL_2024.md          # Original 89 companies
├── MSFT_2024.md
├── ...
├── D_uploaded.md         # Uploaded files
├── D_uploaded.html       # HTML version
├── XYZ_uploaded.md
└── XYZ_uploaded.html
```

## 🔄 Workflow

### Upload Process:
1. User uploads `full-submission.txt` via frontend
2. Backend extracts HTML → Converts to Markdown
3. Extracts ticker symbol
4. **Saves both HTML and Markdown files**
5. **Automatically indexes in Qdrant** (same as original 89)
6. Returns success with `ready_for_qa: true`

### Query Process:
1. User asks query in Analyze tab (e.g., "Tell me about Company D")
2. System extracts ticker "D"
3. Searches Qdrant for ticker "D"
4. **Prefers uploaded file** if available
5. Loads full Markdown file from disk
6. Sends to Gemini for analysis

## 🎯 Key Features

### Separation of Uploaded vs Original
- **Uploaded files**: Tagged with `"source": "uploaded"` in Qdrant
- **Original 89**: No source tag (or `"source": "original"`)
- Both stored in same collection but can be filtered separately

### Automatic Indexing
- No manual step required
- Happens automatically during upload
- Same quality embeddings as original 89

### Frontend Integration
- Beautiful "Ready for QnA" badge
- HTML download option
- Clear indication when file is indexed

## 🛠️ Manual Re-indexing (Optional)

If you need to re-index uploaded files manually:

```bash
python index_uploaded_files.py
```

This script:
- Finds all `*_uploaded.md` files
- Indexes them in Qdrant
- Useful if indexing failed during upload

## 📊 Qdrant Payload Structure

### Uploaded Files:
```json
{
  "ticker": "D",
  "year": "2024",
  "file_path": "processed_data/D_uploaded.md",
  "summary": "...",
  "tables_count": 1234,
  "size_mb": 0.75,
  "lines": 5000,
  "source": "uploaded",        // ← Key identifier
  "uploaded_at": "uuid..."
}
```

### Original 89:
```json
{
  "ticker": "AAPL",
  "year": "2024",
  "file_path": "processed_data/AAPL_2024.md",
  "summary": "...",
  "tables_count": 5678,
  "size_mb": 1.2,
  "lines": 8000
  // No "source" field (or "source": "original")
}
```

## ✅ Testing

1. **Upload a file** via frontend
2. **Check the "Ready for QnA" badge** appears
3. **Download both HTML and MD** files
4. **Go to Analyze tab** and query about the uploaded company
5. **Verify** it uses the uploaded file (check server logs)

## 🚀 Benefits

1. **Seamless Integration**: Uploaded files work exactly like original 89
2. **Automatic**: No manual indexing required
3. **Separate but Unified**: Can distinguish uploaded vs original, but both work in queries
4. **Full RAG Pipeline**: Same embeddings, same search, same analysis quality
5. **User-Friendly**: Clear indicators when files are ready

## 📝 Notes

- Uploaded files are **automatically indexed** during upload
- If indexing fails, file is still saved but `ready_for_qa` will be `false`
- You can manually re-index using `index_uploaded_files.py`
- Original 89 companies remain unchanged and continue to work
