"""
Extract HTML from all 10-K filings in the dataset
Processes all companies and saves HTML files to output folder
"""

import re
from pathlib import Path
from tqdm import tqdm

def extract_10k_html(file_path):
    """Extract the main 10-K HTML content from a full-submission.txt file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the first DOCUMENT section with TYPE=10-K
        pattern = r'<DOCUMENT>.*?<TYPE>10-K.*?<TEXT>(.*?)</TEXT>.*?</DOCUMENT>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            html_content = match.group(1)
            return html_content
        else:
            return None
    except Exception as e:
        print(f"    [ERROR] Failed to read file: {e}")
        return None

def get_all_10k_files(data_dir):
    """Find all full-submission.txt files in the data directory"""
    data_path = Path(data_dir)
    files = []
    
    # Find all full-submission.txt files
    for txt_file in data_path.rglob("full-submission.txt"):
        # Extract ticker from path: data/TICKER/10-K/...
        parts = txt_file.parts
        if len(parts) >= 3 and parts[-3] == "10-K":
            ticker = parts[-4]  # data/TICKER/10-K/...
            files.append((ticker, txt_file))
    
    return files

def process_all_companies(data_dir="data", output_dir="output"):
    """Process all companies and extract their 10-K HTML"""
    
    print("="*80)
    print("EXTRACTING HTML FROM ALL 10-K FILINGS")
    print("="*80)
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get all files
    print("Scanning for 10-K filings...")
    all_files = get_all_10k_files(data_dir)
    print(f"Found {len(all_files)} companies to process\n")
    
    # Process each file
    success_count = 0
    failed_count = 0
    failed_tickers = []
    
    for ticker, file_path in tqdm(all_files, desc="Processing companies"):
        print(f"\n[{ticker}] Processing {file_path.name}...")
        
        html_content = extract_10k_html(file_path)
        
        if html_content:
            # Save HTML file
            output_file = output_path / f"{ticker}_10K_HTML.html"
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                html_size_mb = len(html_content) / (1024 * 1024)
                table_count = len(re.findall(r'<table[^>]*>', html_content, re.IGNORECASE))
                
                print(f"    [OK] Saved: {output_file.name}")
                print(f"    [OK] Size: {html_size_mb:.2f} MB, Tables: {table_count}")
                success_count += 1
            except Exception as e:
                print(f"    [ERROR] Failed to save: {e}")
                failed_count += 1
                failed_tickers.append(ticker)
        else:
            print(f"    [WARNING] Could not extract HTML content")
            failed_count += 1
            failed_tickers.append(ticker)
    
    # Summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total companies: {len(all_files)}")
    print(f"Successfully extracted: {success_count}")
    print(f"Failed: {failed_count}")
    
    if failed_tickers:
        print(f"\nFailed tickers: {', '.join(failed_tickers)}")
    
    print(f"\nAll HTML files saved to: {output_path.absolute()}")
    print("="*80)

if __name__ == "__main__":
    process_all_companies()
