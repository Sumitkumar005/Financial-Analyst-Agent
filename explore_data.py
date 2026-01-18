"""
Script to explore the structure of SEC EDGAR full-submission.txt files
This helps understand the data format before building the ingestion pipeline
"""

import re
import os
from pathlib import Path

def explore_submission_file(file_path):
    """Explore the structure of a full-submission.txt file"""
    print(f"\n{'='*80}")
    print(f"Exploring: {file_path}")
    print(f"{'='*80}\n")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # File size
    file_size_mb = len(content) / (1024 * 1024)
    print(f"File Size: {file_size_mb:.2f} MB")
    print(f"Total Characters: {len(content):,}")
    print(f"Total Lines: {len(content.splitlines()):,}\n")
    
    # Check for SEC document structure
    print("=== SEC Document Structure ===")
    sec_doc_match = re.search(r'<SEC-DOCUMENT>', content)
    sec_header_match = re.search(r'<SEC-HEADER>', content)
    print(f"<SEC-DOCUMENT> tag found: {sec_doc_match is not None}")
    print(f"<SEC-HEADER> tag found: {sec_header_match is not None}")
    
    # Find all DOCUMENT tags
    document_pattern = r'<DOCUMENT>\s*<TYPE>([^<]+)'
    documents = re.findall(document_pattern, content, re.IGNORECASE)
    print(f"\nNumber of <DOCUMENT> sections: {len(documents)}")
    print("Document types found:")
    for i, doc_type in enumerate(documents[:10], 1):
        print(f"  {i}. {doc_type.strip()}")
    if len(documents) > 10:
        print(f"  ... and {len(documents) - 10} more")
    
    # Find HTML sections
    print("\n=== HTML Content ===")
    html_pattern = r'<HTML>|</HTML>'
    html_matches = re.findall(html_pattern, content, re.IGNORECASE)
    print(f"HTML tags found: {len(html_matches)}")
    
    # Find table tags
    print("\n=== Table Content ===")
    # Look for <table> tags (case insensitive)
    table_pattern = r'<table[^>]*>'
    tables = re.findall(table_pattern, content, re.IGNORECASE)
    print(f"<table> tags found: {len(tables)}")
    
    # Find escaped table tags (like &lt;table)
    escaped_table_pattern = r'&lt;table[^&]*&gt;'
    escaped_tables = re.findall(escaped_table_pattern, content, re.IGNORECASE)
    print(f"Escaped &lt;table&gt; tags found: {len(escaped_tables)}")
    
    # Find the largest HTML document (10-K)
    print("\n=== Finding Main 10-K HTML Document ===")
    # Pattern to extract document sections
    doc_sections = re.split(r'<DOCUMENT>', content, flags=re.IGNORECASE)
    
    html_docs = []
    for i, section in enumerate(doc_sections[1:], 1):  # Skip first empty section
        # Check if this section contains HTML
        if re.search(r'<HTML>|&lt;HTML&gt;', section, re.IGNORECASE):
            # Try to find TYPE
            type_match = re.search(r'<TYPE>([^<\n]+)', section, re.IGNORECASE)
            doc_type = type_match.group(1).strip() if type_match else "UNKNOWN"
            html_docs.append({
                'index': i,
                'type': doc_type,
                'size': len(section),
                'has_html': True,
                'table_count': len(re.findall(r'<table[^>]*>|&lt;table', section, re.IGNORECASE))
            })
    
    if html_docs:
        print(f"Found {len(html_docs)} HTML document(s):")
        for doc in html_docs:
            print(f"  Document {doc['index']}: Type={doc['type']}, "
                  f"Size={doc['size']:,} chars, Tables={doc['table_count']}")
        
        # Find the largest one (likely the main 10-K)
        largest = max(html_docs, key=lambda x: x['size'])
        print(f"\nLargest HTML document: Document {largest['index']} "
              f"(Type: {largest['type']}, {largest['size']:,} chars)")
    
    # Sample content from different sections
    print("\n=== Sample Content ===")
    print("\nFirst 500 characters:")
    print(content[:500])
    print("\n" + "-"*80)
    
    # Look for a sample table
    table_sample = re.search(r'(&lt;table[^&]*&gt;.*?&lt;/table&gt;|<table[^>]*>.*?</table>)', 
                            content[:50000], re.IGNORECASE | re.DOTALL)
    if table_sample:
        sample = table_sample.group(0)
        print(f"\nSample table found (first 500 chars):")
        print(sample[:500] + "..." if len(sample) > 500 else sample)
    else:
        print("\nNo table samples found in first 50k characters")

if __name__ == "__main__":
    # Explore the AAPL file as an example
    sample_file = Path("data/AAPL/10-K/0000320193-25-000079/full-submission.txt")
    
    if sample_file.exists():
        explore_submission_file(sample_file)
    else:
        print(f"File not found: {sample_file}")
        print("\nAvailable data directories:")
        data_dir = Path("data")
        if data_dir.exists():
            for ticker_dir in sorted(data_dir.iterdir()):
                if ticker_dir.is_dir():
                    print(f"  {ticker_dir.name}")
