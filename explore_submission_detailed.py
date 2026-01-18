"""
Detailed exploration of SEC EDGAR full-submission.txt files
Specifically focuses on finding and understanding the main 10-K HTML document
"""

import re
import html
from pathlib import Path

def extract_main_10k_html(file_path):
    """Extract the main 10-K HTML document from a full-submission.txt file"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {file_path}")
    print(f"{'='*80}\n")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # File statistics
    file_size_mb = len(content) / (1024 * 1024)
    print(f"File Size: {file_size_mb:.2f} MB")
    print(f"Total Characters: {len(content):,}")
    print(f"Total Lines: {len(content.splitlines()):,}\n")
    
    # Find all DOCUMENT sections
    # Pattern: <DOCUMENT> followed by <TYPE>10-K
    document_pattern = r'<DOCUMENT>.*?(?=<DOCUMENT>|$)'
    documents = re.findall(document_pattern, content, re.DOTALL | re.IGNORECASE)
    
    print(f"Total DOCUMENT sections found: {len(documents)}\n")
    
    # Find the main 10-K HTML document
    main_10k = None
    main_10k_size = 0
    
    for i, doc in enumerate(documents, 1):
        # Check if this is a 10-K document
        type_match = re.search(r'<TYPE>([^<\n]+)', doc, re.IGNORECASE)
        doc_type = type_match.group(1).strip() if type_match else "UNKNOWN"
        
        # Check if it contains HTML
        has_html = bool(re.search(r'<HTML>|&lt;HTML&gt;', doc, re.IGNORECASE))
        
        if doc_type == "10-K" and has_html:
            doc_size = len(doc)
            if doc_size > main_10k_size:
                main_10k_size = doc_size
                main_10k = {
                    'index': i,
                    'type': doc_type,
                    'size': doc_size,
                    'content': doc
                }
    
    if main_10k:
        print(f"[OK] Found Main 10-K HTML Document (Document #{main_10k['index']})")
        print(f"  Size: {main_10k['size']:,} characters ({main_10k['size']/(1024*1024):.2f} MB)\n")
        
        # Extract HTML content
        html_match = re.search(r'<HTML>(.*?)</HTML>', main_10k['content'], re.DOTALL | re.IGNORECASE)
        if not html_match:
            # Try escaped HTML
            html_match = re.search(r'&lt;HTML&gt;(.*?)&lt;/HTML&gt;', main_10k['content'], re.DOTALL | re.IGNORECASE)
            if html_match:
                # Unescape HTML entities
                html_content = html.unescape(html_match.group(1))
            else:
                print("[WARNING] Could not find HTML boundaries")
                html_content = None
        else:
            html_content = html_match.group(1)
        
        if html_content:
            print(f"[OK] Extracted HTML content: {len(html_content):,} characters\n")
            
            # Count tables in HTML
            # Look for both <table> and escaped &lt;table&gt;
            table_tags = len(re.findall(r'<table[^>]*>|&lt;table[^&]*&gt;', html_content, re.IGNORECASE))
            print(f"[OK] Found {table_tags} table tags in HTML\n")
            
            # Show sample of HTML structure
            print("=== HTML Structure Sample (first 1000 chars) ===")
            print(html_content[:1000])
            print("...\n")
            
            # Find a sample table
            table_sample = re.search(
                r'(<table[^>]*>.*?</table>|&lt;table[^&]*&gt;.*?&lt;/table&gt;)',
                html_content[:50000],
                re.DOTALL | re.IGNORECASE
            )
            
            if table_sample:
                sample = table_sample.group(0)
                # Unescape if needed
                if '&lt;' in sample:
                    sample = html.unescape(sample)
                
                print("=== Sample Table (first 800 chars) ===")
                print(sample[:800])
                if len(sample) > 800:
                    print("...")
                print()
            
            return html_content
        else:
            print("[WARNING] Could not extract HTML content")
            return None
    else:
        print("[WARNING] No 10-K HTML document found")
        return None

def analyze_table_structure(html_content):
    """Analyze the structure of tables in the HTML"""
    if not html_content:
        return
    
    print("=== Table Structure Analysis ===")
    
    # Find all table tags
    tables = re.findall(r'<table[^>]*>.*?</table>', html_content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(tables)} complete table structures\n")
    
    if tables:
        # Analyze first few tables
        for i, table in enumerate(tables[:3], 1):
            # Count rows
            rows = re.findall(r'<tr[^>]*>', table, re.IGNORECASE)
            # Count cells
            cells = re.findall(r'<t[dh][^>]*>', table, re.IGNORECASE)
            
            print(f"Table {i}:")
            print(f"  Rows: {len(rows)}")
            print(f"  Cells: {len(cells)}")
            print(f"  Size: {len(table):,} characters")
            print()

if __name__ == "__main__":
    # Analyze the AAPL file
    sample_file = Path("data/AAPL/10-K/0000320193-25-000079/full-submission.txt")
    
    if sample_file.exists():
        html_content = extract_main_10k_html(sample_file)
        if html_content:
            analyze_table_structure(html_content)
    else:
        print(f"File not found: {sample_file}")
