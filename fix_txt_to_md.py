"""
FIXED: Complete pipeline TXT -> HTML -> Markdown
Uses the CORRECT method to extract FULL 10-K HTML from <TEXT> tag
Then converts to Markdown properly
"""

import re
import os
import markdownify
from pathlib import Path

# Test with AAPL file
file_path = "data/AAPL/10-K/0000320193-25-000079/full-submission.txt"
output_dir = "processed_data"
os.makedirs(output_dir, exist_ok=True)

print("="*80)
print("FIXED PIPELINE: TXT -> HTML -> MARKDOWN")
print("Using CORRECT extraction method (from <TEXT> tag)")
print("="*80)
print()

# STEP 1: Extract FULL 10-K HTML from <TEXT> tag (CORRECT METHOD)
print("STEP 1: Extracting FULL 10-K HTML from full-submission.txt...")
print(f"Reading: {file_path}")

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the first DOCUMENT section with TYPE=10-K and extract from <TEXT> tag
# This gets the FULL 10-K HTML (not just a small XBRL section)
pattern = r'<DOCUMENT>.*?<TYPE>10-K.*?<TEXT>(.*?)</TEXT>.*?</DOCUMENT>'
match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

if match:
    html_content = match.group(1)
    html_size_mb = len(html_content) / (1024 * 1024)
    
    print(f"[OK] Extracted FULL 10-K HTML: {len(html_content):,} characters ({html_size_mb:.2f} MB)")
    
    # Save intermediate HTML file
    html_save_path = f"{output_dir}/AAPL_2024_10K_FULL.html"
    with open(html_save_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"     Saved HTML to: {html_save_path}")
    print()
    
    # STEP 2: Convert HTML to Markdown (from htmltomdreference.txt)
    print("STEP 2: Converting HTML to Markdown...")
    print("Using: markdownify.markdownify(html_content, heading_style='ATX')")
    print()
    
    # Convert HTML Structure to Markdown
    # This keeps tables as | Column 1 | Column 2 | instead of mushy text
    markdown_text = markdownify.markdownify(html_content, heading_style="ATX")
    
    md_size_mb = len(markdown_text) / (1024 * 1024)
    print(f"[OK] Converted to Markdown: {len(markdown_text):,} characters ({md_size_mb:.2f} MB)")
    
    # Save the final Markdown file
    md_save_path = f"{output_dir}/AAPL_2024_Insights.md"
    with open(md_save_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    
    print(f"     Saved Markdown to: {md_save_path}")
    print()
    
    # Show statistics
    print("="*80)
    print("CONVERSION STATISTICS")
    print("="*80)
    table_count = markdown_text.count('|') // 3  # Rough estimate
    lines_count = len(markdown_text.splitlines())
    
    print(f"HTML size: {html_size_mb:.2f} MB")
    print(f"Markdown size: {md_size_mb:.2f} MB")
    print(f"Markdown lines: {lines_count:,}")
    print(f"Estimated tables: ~{table_count}")
    print()
    
    # Check for key content
    print("="*80)
    print("VERIFYING CONTENT:")
    print("="*80)
    
    checks = {
        "Revenue/Net sales": "Revenue" in markdown_text or "Net sales" in markdown_text,
        "Financial Statements": "Financial Statements" in markdown_text or "CONSOLIDATED" in markdown_text,
        "Years 2025/2024/2023": "2025" in markdown_text and "2024" in markdown_text and "2023" in markdown_text,
        "Table structure": "|" in markdown_text,
        "Apple Inc": "Apple Inc" in markdown_text or "AAPL" in markdown_text
    }
    
    for check, result in checks.items():
        status = "[OK]" if result else "[MISSING]"
        print(f"{status} {check}")
    
    print()
    
    # Show sample of markdown
    print("="*80)
    print("SAMPLE MARKDOWN (first 1500 characters):")
    print("="*80)
    print(markdown_text[:1500])
    print("...")
    print()
    
    # Show a financial table sample
    print("="*80)
    print("LOOKING FOR FINANCIAL TABLES:")
    print("="*80)
    
    # Find lines with financial data
    lines = markdown_text.split('\n')
    table_lines = [line for line in lines if '|' in line and ('$' in line or '2025' in line or '2024' in line)][:5]
    
    if table_lines:
        print("Found financial table lines:")
        for i, line in enumerate(table_lines, 1):
            print(f"  {i}. {line[:150]}...")
    else:
        print("[WARNING] No financial table lines found")
    
    print()
    print("="*80)
    print("COMPLETE! Files saved:")
    print(f"  HTML: {html_save_path}")
    print(f"  Markdown: {md_save_path}")
    print("="*80)
    
else:
    print("[ERROR] Could not find 10-K HTML content in <TEXT> tag")
