# SEC EDGAR Full-Submission.txt Data Structure Analysis

## Overview
This document summarizes the structure and content of SEC EDGAR full-submission.txt files extracted from the dataset.

## File Structure

### Sample File Analyzed
- **Path**: `data/AAPL/10-K/0000320193-25-000079/full-submission.txt`
- **Size**: 8.96 MB
- **Total Characters**: 9,392,337
- **Total Lines**: 86,580

### Document Structure

The full-submission.txt file follows this hierarchical structure:

```
<SEC-DOCUMENT>
  <SEC-HEADER>
    [Metadata: Company info, filing dates, etc.]
  </SEC-HEADER>
  
  <DOCUMENT>
    <TYPE>10-K</TYPE>
    <SEQUENCE>1</SEQUENCE>
    <FILENAME>aapl-20250927.htm</FILENAME>
    <DESCRIPTION>10-K</DESCRIPTION>
    <TEXT>
      [HTML content with tables]
    </TEXT>
  </DOCUMENT>
  
  <DOCUMENT>
    <TYPE>EX-4.1</TYPE>
    ...
  </DOCUMENT>
  
  ... (90 total documents)
</SEC-DOCUMENT>
```

## Key Findings

### 1. Document Sections
- **Total Documents**: 90 sections
- **Main Document**: First document with `<TYPE>10-K</TYPE>`
- **Other Documents**: Exhibits (EX-4.1, EX-21.1, etc.), XML files, Graphics

### 2. HTML Content Location
- The main 10-K HTML content is inside the `<TEXT>` tag of the first `<DOCUMENT>` section
- HTML is **NOT escaped** (uses `<table>`, not `&lt;table&gt;`)
- HTML contains inline styles and complex table structures

### 3. Table Structure
- **Total `<table>` tags**: 1,390 found in the file
- **Escaped tables**: 55 instances of `&lt;table&gt;` (likely in XML sections)
- Tables use inline CSS styles for formatting
- Tables contain financial data with proper row/column alignment

### 4. HTML Table Format Example
Tables are structured as:
```html
<table style="border-collapse:collapse;display:inline-table;margin-bottom:5pt;vertical-align:text-bottom;width:100.000%">
  <tr>
    <td style="width:1.0%"/>
    <td style="width:59.280%"/>
    ...
  </tr>
  <tr>
    <td colspan="3" style="padding:2px 1pt;text-align:left;vertical-align:top">
      <span style="color:#000000;font-family:'Helvetica',sans-serif;font-size:9pt;...">
        [Cell content]
      </span>
    </td>
    ...
  </tr>
</table>
```

### 5. Content Characteristics
- **Text**: Regular HTML text with inline styles
- **Tables**: Complex HTML tables with:
  - Inline CSS styling
  - Nested `<span>` elements for text formatting
  - `colspan` and `rowspan` attributes
  - Proper alignment and spacing

## Data Extraction Strategy

### Recommended Approach

1. **Extract Main 10-K Document**:
   - Find first `<DOCUMENT>` section with `<TYPE>10-K</TYPE>`
   - Extract content from `<TEXT>...</TEXT>` tags
   - This contains the main HTML report

2. **Parse HTML Content**:
   - Use HTML parser (BeautifulSoup or similar)
   - Preserve table structure
   - Convert tables to Markdown using `markdownify` or custom converter

3. **Handle Tables**:
   - Keep tables as atomic units (don't chunk them)
   - Preserve column alignment
   - Maintain row structure

4. **Clean Content**:
   - Remove XML metadata
   - Keep only the main HTML document
   - Preserve table formatting

## Next Steps for Ingestion Pipeline

1. **Create extraction function** that:
   - Parses `<DOCUMENT>` sections
   - Identifies 10-K document by TYPE
   - Extracts `<TEXT>` content

2. **HTML to Markdown conversion**:
   - Use `markdownify` library
   - Ensure tables are properly converted
   - Preserve structure

3. **Storage**:
   - Save as `{TICKER}_{YEAR}.md` files
   - Store in `processed_data/` directory

## Notes

- The HTML content is well-structured and contains proper table markup
- Tables are the critical component for financial analysis
- The structure is consistent across SEC filings
- No need to handle escaped HTML in the main 10-K document (it's in plain HTML format)
