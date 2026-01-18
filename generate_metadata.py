"""
Generate metadata file with conversion statistics for all companies
Shows HTML size, Markdown size, lines, tables for easy reference
"""

import json
import csv
from pathlib import Path
import re

def extract_10k_html_from_txt(file_path):
    """Extract HTML size from full-submission.txt"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        pattern = r'<DOCUMENT>.*?<TYPE>10-K.*?<TEXT>(.*?)</TEXT>.*?</DOCUMENT>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            html_content = match.group(1)
            return len(html_content)
        return None
    except:
        return None

def analyze_markdown_file(md_file):
    """Analyze markdown file to get statistics"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = len(content.splitlines())
        chars = len(content)
        size_mb = chars / (1024 * 1024)
        table_count = content.count('|') // 3  # Rough estimate
        
        return {
            'size_mb': round(size_mb, 2),
            'lines': lines,
            'tables': table_count,
            'chars': chars
        }
    except:
        return None

def generate_metadata(data_dir="data", processed_dir="processed_data", output_file="conversion_metadata.json"):
    """Generate metadata for all converted files"""
    
    print("="*80)
    print("GENERATING CONVERSION METADATA")
    print("="*80)
    print()
    
    data_path = Path(data_dir)
    processed_path = Path(processed_dir)
    
    # Find all companies
    txt_files = []
    for txt_file in data_path.rglob("full-submission.txt"):
        parts = txt_file.parts
        if len(parts) >= 3 and parts[-3] == "10-K":
            ticker = parts[-4]
            txt_files.append((ticker, txt_file))
    
    print(f"Found {len(txt_files)} companies\n")
    
    metadata = []
    
    for ticker, txt_file in txt_files:
        md_file = processed_path / f"{ticker}_2024.md"
        
        if not md_file.exists():
            print(f"[{ticker}] Markdown file not found, skipping...")
            continue
        
        # Get HTML size from source
        html_size_chars = extract_10k_html_from_txt(txt_file)
        html_size_mb = html_size_chars / (1024 * 1024) if html_size_chars else 0
        
        # Analyze markdown
        md_stats = analyze_markdown_file(md_file)
        
        if md_stats:
            entry = {
                'ticker': ticker,
                'html_size_mb': round(html_size_mb, 2),
                'markdown_size_mb': md_stats['size_mb'],
                'markdown_lines': md_stats['lines'],
                'estimated_tables': md_stats['tables'],
                'markdown_file': str(md_file),
                'source_file': str(txt_file)
            }
            metadata.append(entry)
            
            print(f"[{ticker}] HTML: {entry['html_size_mb']:.2f} MB -> Markdown: {entry['markdown_size_mb']:.2f} MB, Lines: {entry['markdown_lines']:,}, Tables: ~{entry['estimated_tables']}")
    
    # Sort by ticker
    metadata.sort(key=lambda x: x['ticker'])
    
    # Save as JSON
    json_file = Path(output_file)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] JSON metadata saved to: {json_file}")
    
    # Save as CSV for easy viewing
    csv_file = Path(output_file.replace('.json', '.csv'))
    if metadata:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ticker', 'html_size_mb', 'markdown_size_mb', 'markdown_lines', 'estimated_tables'])
            writer.writeheader()
            for entry in metadata:
                writer.writerow({
                    'ticker': entry['ticker'],
                    'html_size_mb': entry['html_size_mb'],
                    'markdown_size_mb': entry['markdown_size_mb'],
                    'markdown_lines': entry['markdown_lines'],
                    'estimated_tables': entry['estimated_tables']
                })
    
    print(f"[OK] CSV metadata saved to: {csv_file}")
    
    # Calculate totals
    total_html = sum(e['html_size_mb'] for e in metadata)
    total_md = sum(e['markdown_size_mb'] for e in metadata)
    total_lines = sum(e['markdown_lines'] for e in metadata)
    total_tables = sum(e['estimated_tables'] for e in metadata)
    
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total companies: {len(metadata)}")
    print(f"Total HTML size: {total_html:.2f} MB")
    print(f"Total Markdown size: {total_md:.2f} MB")
    print(f"Total Markdown lines: {total_lines:,}")
    print(f"Total estimated tables: {total_tables:,}")
    print()
    print(f"Metadata files saved:")
    print(f"  JSON: {json_file.absolute()}")
    print(f"  CSV: {csv_file.absolute()}")
    print("="*80)

if __name__ == "__main__":
    generate_metadata()
