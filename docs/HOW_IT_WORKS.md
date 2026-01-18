# How the System Works: Query to Analysis

## 🔄 Complete Workflow

### Step 1: User Query
```
"Compare AWS and Azure revenue"
```

### Step 2: Router Node (Extract Tickers)
- Simple keyword matching finds: `AWS` → `AMZN`, `Azure` → `MSFT`
- Returns: `['AMZN', 'MSFT']`

### Step 3: Retriever Node (Query Qdrant)
- Searches Qdrant for companies with tickers `AMZN` and `MSFT`
- Returns file paths:
  - `processed_data/AMZN_2024.md`
  - `processed_data/MSFT_2024.md`

### Step 4: Loader Node (Load Full Files)
- Reads complete Markdown files from disk
- **NO CHUNKING** - Full files loaded
- Example sizes:
  - AMZN: ~0.5 MB, ~4,000 lines
  - MSFT: ~0.7 MB, ~5,000 lines

### Step 5: Smart Content Handling

#### Option A: Direct Full File (Default - 95% of cases)
- Files fit in Gemini's 1M token window
- Send full content directly
- **Total tokens**: ~200k-400k (well within limit)

#### Option B: Smart Section Extraction (If too large)
- Query: "Compare AWS and Azure revenue"
- Extract only:
  - "Segment Information" sections
  - Revenue tables
  - Skip: Risk Factors, Legal, etc.
- **Tables stay intact** - never split!

#### Option C: Two-Pass Analysis (Complex queries)
1. First pass: LLM identifies relevant sections
2. Extract those sections
3. Second pass: Analyze extracted content

### Step 6: Generator Node (Gemini Analysis)
- Sends to Gemini 2.5 Flash:
  ```
  System Prompt: "You are a financial analyst..."
  User Query: "Compare AWS and Azure revenue"
  Documents: [Full AMZN content] [Full MSFT content]
  ```
- Gemini analyzes with full context
- Returns structured analysis

### Step 7: Response
```json
{
  "query": "Compare AWS and Azure revenue",
  "companies_found": ["AMZN", "MSFT"],
  "file_paths": ["processed_data/AMZN_2024.md", "processed_data/MSFT_2024.md"],
  "analysis": "Based on the 2024 10-K filings...\n\nAWS Revenue: $90.8B\nAzure Revenue: $...",
  "metadata": {...}
}
```

## 🎯 Key Points

1. **Qdrant stores**: Summaries + metadata (for fast search)
2. **Disk stores**: Full MD files (for complete analysis)
3. **Gemini receives**: Full files (or smart-extracted sections)
4. **Tables preserved**: Never chunked, always intact

## 💡 Why This Works

- **Fast Search**: Qdrant finds companies instantly
- **Complete Data**: Full files preserve all tables
- **Large Context**: Gemini handles 1M+ tokens
- **Smart Extraction**: Only when needed
- **No Data Loss**: Tables never split

This is the optimal approach! 🚀
