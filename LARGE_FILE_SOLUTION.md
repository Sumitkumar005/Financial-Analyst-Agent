# Solution for Large MD Files

## 🎯 The Problem
- MD files are large (some 1-2 MB, 10k+ lines)
- We can't chunk them (would break tables - the whole point!)
- Need to feed to LLM for analysis

## ✅ The Solution: Multi-Layered Approach

### Layer 1: Gemini 2.5 Flash's Large Context Window
**Gemini 2.5 Flash has 1M+ token context window!**

- Most files: 100k-200k tokens → **Fits easily!**
- Even largest files (C, JPM): ~300k tokens → **Still fits!**
- **Solution**: Load full file, send to Gemini directly

### Layer 2: Smart Section Extraction (If Needed)
For files that are too large or when query is specific:

1. **Query-Based Section Extraction**
   - User asks: "Compare AWS and Azure revenue"
   - Extract only relevant sections:
     - "Segment Information" tables
     - "Revenue" sections
     - Skip: "Risk Factors", "Legal Proceedings", etc.

2. **Table-Aware Extraction**
   - Keep tables intact (never split)
   - Extract sections around tables
   - Preserve context

### Layer 3: Recursive Analysis (RLM Approach)
For very complex queries:

1. **First Pass**: LLM identifies relevant sections
2. **Second Pass**: Extract those sections
3. **Third Pass**: Analyze extracted content

## 📊 File Size Analysis

From your metadata:
- **Average file**: ~0.7 MB, ~5,500 lines
- **Largest file** (C): 1.81 MB, 14,747 lines
- **Token estimate**: ~200k-400k tokens per file

**Conclusion**: Most files fit in Gemini 2.5 Flash's 1M token window!

## 🔄 Implementation Strategy

### Strategy 1: Direct Full File (Default)
```python
# For most queries
full_content = load_file(file_path)
response = gemini.analyze(query + full_content)
```

### Strategy 2: Smart Section Extraction
```python
# For specific queries
sections = extract_relevant_sections(query, full_content)
# sections = ["Segment Information", "Revenue", "Financial Statements"]
extracted = extract_sections(full_content, sections)
response = gemini.analyze(query + extracted)
```

### Strategy 3: Two-Pass Analysis
```python
# Pass 1: Identify relevant sections
sections = gemini.identify_sections(query, summary)
# Pass 2: Extract and analyze
extracted = extract_sections(full_content, sections)
response = gemini.analyze(query + extracted)
```

## 💡 Why This Works

1. **No Chunking**: Tables stay intact
2. **Efficient**: Only load what's needed
3. **Accurate**: Full context when needed
4. **Scalable**: Works for any file size

## 🚀 What We'll Implement

1. **Default**: Load full file → Send to Gemini (works for 95% of cases)
2. **Fallback**: Smart section extraction (for very large files or specific queries)
3. **Advanced**: Two-pass analysis (for complex multi-company comparisons)

This gives you the best of both worlds! 🎯
