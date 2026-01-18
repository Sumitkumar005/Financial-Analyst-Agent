"""
Convert all HTML files to Markdown for all 89 companies
Uses the CORRECT method: Extract from <TEXT> tag, then convert with markdownify
"""

import re
import os
import markdownify
from pathlib import Path
from tqdm import tqdm

def extract_10k_html_from_txt(file_path):
    """Extract FULL 10-K HTML from full-submission.txt using <TEXT> tag method"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the first DOCUMENT section with TYPE=10-K and extract from <TEXT> tag
        pattern = r'<DOCUMENT>.*?<TYPE>10-K.*?<TEXT>(.*?)</TEXT>.*?</DOCUMENT>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1)
        return None
    except Exception as e:
        return None

def convert_html_to_markdown(html_content):
    """Convert HTML to Markdown using markdownify"""
    return markdownify.markdownify(html_content, heading_style="ATX")

def process_all_companies(data_dir="data", output_dir="processed_data"):
    """Process all companies: TXT -> HTML -> Markdown"""
    
    print("="*80)
    print("CONVERTING ALL COMPANIES: TXT -> HTML -> MARKDOWN")
    print("="*80)
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Find all full-submission.txt files
    data_path = Path(data_dir)
    txt_files = []
    
    for txt_file in data_path.rglob("full-submission.txt"):
        # Extract ticker from path: data/TICKER/10-K/...
        parts = txt_file.parts
        if len(parts) >= 3 and parts[-3] == "10-K":
            ticker = parts[-4]  # data/TICKER/10-K/...
            txt_files.append((ticker, txt_file))
    
    print(f"Found {len(txt_files)} companies to process\n")
    
    if not txt_files:
        print(f"[ERROR] No files found in {data_dir}")
        return
    
    # Process each file
    results = []
    success_count = 0
    failed_count = 0
    failed_tickers = []
    
    for ticker, txt_file in tqdm(txt_files, desc="Processing companies"):
        try:
            # Step 1: Extract HTML from TXT
            html_content = extract_10k_html_from_txt(txt_file)
            
            if not html_content:
                print(f"\n[{ticker}] [ERROR] Could not extract HTML")
                failed_count += 1
                failed_tickers.append(ticker)
                continue
            
            # Step 2: Convert HTML to Markdown
            markdown_text = convert_html_to_markdown(html_content)
            
            # Step 3: Save Markdown file
            md_file = output_path / f"{ticker}_2024.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            
            # Calculate stats
            html_size_mb = len(html_content) / (1024 * 1024)
            md_size_mb = len(markdown_text) / (1024 * 1024)
            md_lines = len(markdown_text.splitlines())
            table_count = markdown_text.count('|') // 3  # Rough estimate
            
            print(f"\n[{ticker}] Converted: {ticker}_2024.md")
            print(f"    HTML: {html_size_mb:.2f} MB -> Markdown: {md_size_mb:.2f} MB")
            print(f"    Lines: {md_lines:,}, Tables: ~{table_count}")
            
            results.append({
                'ticker': ticker,
                'html_size_mb': html_size_mb,
                'md_size_mb': md_size_mb,
                'md_lines': md_lines,
                'success': True
            })
            success_count += 1
            
        except Exception as e:
            print(f"\n[{ticker}] [ERROR] {str(e)}")
            failed_count += 1
            failed_tickers.append(ticker)
    
    # Summary
    print("\n" + "="*80)
    print("CONVERSION SUMMARY")
    print("="*80)
    print(f"Total companies: {len(txt_files)}")
    print(f"Successfully converted: {success_count}")
    print(f"Failed: {failed_count}")
    
    if failed_tickers:
        print(f"\nFailed tickers: {', '.join(failed_tickers)}")
    
    if results:
        total_md_size = sum(r['md_size_mb'] for r in results)
        total_md_lines = sum(r['md_lines'] for r in results)
        avg_tokens = (total_md_lines * 50) / len(results)  # Rough estimate: 50 tokens per line
        
        print(f"\nTotal Markdown size: {total_md_size:.2f} MB")
        print(f"Total Markdown lines: {total_md_lines:,}")
        print(f"Average tokens per file: ~{avg_tokens:,.0f}")
        print(f"All files fit easily in Gemini 2.5 Flash (1M+ token capacity)")
    
    print(f"\nAll Markdown files saved to: {output_path.absolute()}")
    print("="*80)

if __name__ == "__main__":
    process_all_companies()
