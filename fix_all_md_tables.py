"""
Fix all Markdown files: Convert tab-separated tables to proper markdown format
This fixes the source MD files so Gemini gets properly formatted tables
"""

import re
from pathlib import Path
from tqdm import tqdm


def detect_tab_table_block(lines: list, start_idx: int) -> tuple:
    """
    Detect a block of consecutive tab-separated table lines
    Returns (end_idx, table_lines) or (start_idx, []) if not a table
    """
    if start_idx >= len(lines):
        return start_idx, []
    
    # Check if this line looks like a table row
    line = lines[start_idx]
    if '\t' not in line or line.count('\t') < 2:
        return start_idx, []
    
    # Check if it has financial data
    has_numbers = bool(re.search(r'[\d$%]', line))
    if not has_numbers or len(line.strip()) < 10:
        return start_idx, []
    
    # Collect consecutive table lines
    table_lines = [line]
    i = start_idx + 1
    
    while i < len(lines):
        next_line = lines[i]
        
        # Stop if empty line (might be table separator)
        if not next_line.strip():
            # Check if next non-empty line is also a table
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            
            if j < len(lines):
                next_non_empty = lines[j]
                if '\t' in next_non_empty and next_non_empty.count('\t') >= 2:
                    # Continue table after empty line
                    i = j
                    continue
            
            break
        
        # Check if next line is also a table row
        if '\t' in next_line and next_line.count('\t') >= 2:
            has_data = bool(re.search(r'[\d$%]', next_line))
            if has_data and len(next_line.strip()) >= 10:
                table_lines.append(next_line)
                i += 1
                continue
        
        # Check if it's a continuation (like multi-line headers)
        if len(next_line.strip()) > 0 and not next_line.strip().startswith('#'):
            # Might be part of table (like a header continuation)
            table_lines.append(next_line)
            i += 1
        else:
            break
    
    return i, table_lines


def convert_tab_table_to_markdown(table_lines: list) -> str:
    """
    Convert tab-separated table lines to proper markdown format
    """
    if not table_lines:
        return ''
    
    # Split each line by tabs
    rows = []
    for line in table_lines:
        # Split by tabs and clean
        cells = [cell.strip() for cell in line.split('\t') if cell.strip() or len(cell) > 0]
        
        # Filter out completely empty cells at the end
        while cells and not cells[-1]:
            cells.pop()
        
        if len(cells) >= 2:  # At least 2 columns
            rows.append(cells)
    
    if not rows:
        return '\n'.join(table_lines)  # Return original if conversion fails
    
    # Find max columns
    max_cols = max(len(row) for row in rows) if rows else 0
    
    if max_cols < 2:
        return '\n'.join(table_lines)  # Return original if too few columns
    
    # Pad rows to same length
    for row in rows:
        while len(row) < max_cols:
            row.append('')
    
    # Build markdown table
    markdown_lines = []
    
    # First row as header
    if rows:
        header = rows[0]
        markdown_lines.append('| ' + ' | '.join(header) + ' |')
        
        # Separator row
        markdown_lines.append('| ' + ' | '.join(['---'] * len(header)) + ' |')
        
        # Data rows
        for row in rows[1:]:
            markdown_lines.append('| ' + ' | '.join(row) + ' |')
    
    return '\n'.join(markdown_lines)


def fix_markdown_file(md_file: Path) -> tuple:
    """
    Fix a single markdown file
    Returns (fixed_content, tables_fixed_count)
    """
    try:
        content = md_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        fixed_lines = []
        i = 0
        tables_fixed = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line looks like a tab-separated table row
            if '\t' in line and line.count('\t') >= 2:
                # Detect table block
                end_idx, table_lines = detect_tab_table_block(lines, i)
                
                if len(table_lines) >= 2:  # At least 2 rows to be a table
                    # Convert to markdown
                    markdown_table = convert_tab_table_to_markdown(table_lines)
                    fixed_lines.append(markdown_table)
                    tables_fixed += 1
                    i = end_idx
                    continue
            
            # Not a table line, keep as is
            fixed_lines.append(line)
            i += 1
        
        fixed_content = '\n'.join(fixed_lines)
        return fixed_content, tables_fixed
        
    except Exception as e:
        print(f"[ERROR] Failed to process {md_file.name}: {e}")
        return None, 0


def main():
    """Fix all MD files in processed_data directory"""
    processed_dir = Path("processed_data")
    
    if not processed_dir.exists():
        print(f"[ERROR] Directory {processed_dir} does not exist!")
        return
    
    # Find all MD files
    md_files = list(processed_dir.glob("*.md"))
    
    if not md_files:
        print(f"[ERROR] No MD files found in {processed_dir}")
        return
    
    print("="*80)
    print("FIXING TAB-SEPARATED TABLES IN MARKDOWN FILES")
    print("="*80)
    print(f"Found {len(md_files)} Markdown files to process\n")
    
    total_tables_fixed = 0
    files_fixed = 0
    files_failed = 0
    
    for md_file in tqdm(md_files, desc="Processing files"):
        fixed_content, tables_fixed = fix_markdown_file(md_file)
        
        if fixed_content is not None:
            # Backup original
            backup_file = md_file.with_suffix('.md.backup')
            if not backup_file.exists():
                md_file.rename(backup_file)
            
            # Write fixed content
            md_file.write_text(fixed_content, encoding='utf-8')
            
            total_tables_fixed += tables_fixed
            files_fixed += 1
            
            if tables_fixed > 0:
                print(f"\n[{md_file.name}] Fixed {tables_fixed} table(s)")
        else:
            files_failed += 1
    
    print("\n" + "="*80)
    print("FIXING COMPLETE")
    print("="*80)
    print(f"Files processed: {len(md_files)}")
    print(f"Files fixed: {files_fixed}")
    print(f"Files failed: {files_failed}")
    print(f"Total tables fixed: {total_tables_fixed}")
    print(f"\nBackups saved as: *.md.backup")
    print("="*80)


if __name__ == "__main__":
    main()
