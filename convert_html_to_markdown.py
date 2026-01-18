"""
Convert all HTML 10-K files to Markdown format
Based on reference: htmltomdreference.txt
Simple conversion using markdownify with heading_style="ATX"
"""

import markdownify
from pathlib import Path
from tqdm import tqdm

def convert_html_to_markdown(html_file_path, output_dir):
    """Convert a single HTML file to Markdown - simple approach from reference"""
    try:
        # Read HTML
        with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # Extract ticker from filename (e.g., AAPL_10K_HTML.html -> AAPL)
        ticker = html_file_path.stem.replace('_10K_HTML', '').upper()
        
        # Convert HTML to Markdown - EXACTLY as in reference
        # This keeps tables as | Column 1 | Column 2 | instead of mushy text
        markdown_text = markdownify.markdownify(html_content, heading_style="ATX")
        
        # Save Markdown file - use format: TICKER_2024.md (or extract year if needed)
        # For now, using 2024 as default (most filings are 2024)
        output_file = output_dir / f"{ticker}_2024.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        # Calculate stats
        md_size_mb = len(markdown_text) / (1024 * 1024)
        table_count = markdown_text.count('|') // 3  # Rough estimate
        
        return {
            'ticker': ticker,
            'size_mb': md_size_mb,
            'tables': table_count,
            'success': True
        }
    except Exception as e:
        return {
            'ticker': ticker if 'ticker' in locals() else 'UNKNOWN',
            'error': str(e),
            'success': False
        }

def convert_all_html_files(html_dir="output", output_dir="processed_data"):
    """Convert all HTML files to Markdown"""
    
    print("="*80)
    print("CONVERTING HTML TO MARKDOWN")
    print("Using simple markdownify approach (from reference)")
    print("="*80)
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Find all HTML files
    html_path = Path(html_dir)
    html_files = list(html_path.glob("*_10K_HTML.html"))
    
    print(f"Found {len(html_files)} HTML files to convert\n")
    
    if not html_files:
        print(f"[ERROR] No HTML files found in {html_dir}")
        return
    
    # Process each file
    results = []
    success_count = 0
    failed_count = 0
    
    for html_file in tqdm(html_files, desc="Converting to Markdown"):
        result = convert_html_to_markdown(html_file, output_path)
        results.append(result)
        
        if result['success']:
            print(f"\n[{result['ticker']}] Converted: {result['ticker']}_2024.md")
            print(f"    Size: {result['size_mb']:.2f} MB, Tables: ~{result['tables']}")
            success_count += 1
        else:
            print(f"\n[{result['ticker']}] [ERROR] {result.get('error', 'Unknown error')}")
            failed_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("CONVERSION SUMMARY")
    print("="*80)
    print(f"Total HTML files: {len(html_files)}")
    print(f"Successfully converted: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"\nAll Markdown files saved to: {output_path.absolute()}")
    
    # Show sample of first successful conversion
    if results and results[0]['success']:
        sample_file = output_path / f"{results[0]['ticker']}_2024.md"
        if sample_file.exists():
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_content = f.read(2000)  # First 2000 chars
            
            print("\n" + "="*80)
            print(f"SAMPLE MARKDOWN ({results[0]['ticker']}_2024.md):")
            print("="*80)
            print(sample_content)
            print("...")
    
    print("="*80)

if __name__ == "__main__":
    convert_all_html_files()
