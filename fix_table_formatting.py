"""
Post-process Gemini responses to fix table formatting
Converts tab-separated or space-separated tables to proper markdown format
"""

import re
from typing import List, Tuple


def detect_table_lines(text: str) -> List[Tuple[int, str]]:
    """
    Detect lines that look like table rows (contain multiple numbers/values separated by tabs or spaces)
    Returns list of (line_number, line_content) tuples
    """
    lines = text.split('\n')
    table_lines = []
    
    for i, line in enumerate(lines):
        # Check if line looks like a table row:
        # - Contains multiple numbers or dollar signs
        # - Has multiple separators (tabs or multiple spaces)
        # - Not too short (at least 20 chars)
        if len(line) < 20:
            continue
        
        # Count tabs
        tab_count = line.count('\t')
        
        # Count multiple spaces (2+ consecutive spaces)
        space_separators = len(re.findall(r'\s{2,}', line))
        
        # Check for financial indicators
        has_numbers = bool(re.search(r'\d+', line))
        has_dollar = '$' in line
        has_percent = '%' in line
        
        # If it has multiple separators and financial data, it's likely a table row
        if (tab_count >= 2 or space_separators >= 2) and (has_numbers or has_dollar or has_percent):
            table_lines.append((i, line))
    
    return table_lines


def convert_to_markdown_table(lines: List[str]) -> str:
    """
    Convert a list of table lines to proper markdown format
    """
    if not lines:
        return ''
    
    # Split each line by tabs or multiple spaces
    rows = []
    for line in lines:
        # Try tabs first
        if '\t' in line:
            cells = [cell.strip() for cell in line.split('\t')]
        else:
            # Try multiple spaces
            cells = [cell.strip() for cell in re.split(r'\s{2,}', line) if cell.strip()]
        
        if len(cells) >= 2:  # At least 2 columns
            rows.append(cells)
    
    if not rows:
        return ''
    
    # Find max columns
    max_cols = max(len(row) for row in rows)
    
    # Pad rows to same length
    for row in rows:
        while len(row) < max_cols:
            row.append('')
    
    # Build markdown table
    markdown_lines = []
    
    # Header row
    if rows:
        header = rows[0]
        markdown_lines.append('| ' + ' | '.join(header) + ' |')
        
        # Separator row
        markdown_lines.append('| ' + ' | '.join(['---'] * len(header)) + ' |')
        
        # Data rows
        for row in rows[1:]:
            markdown_lines.append('| ' + ' | '.join(row) + ' |')
    
    return '\n'.join(markdown_lines)


def fix_table_formatting(text: str) -> str:
    """
    Main function to fix table formatting in Gemini responses
    """
    lines = text.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line looks like a table row
        tab_count = line.count('\t')
        space_separators = len(re.findall(r'\s{2,}', line))
        has_financial_data = bool(re.search(r'[\d$%]', line))
        
        # If it looks like a table, collect consecutive table lines
        if (tab_count >= 2 or space_separators >= 2) and has_financial_data and len(line) >= 20:
            table_lines = [line]
            i += 1
            
            # Collect consecutive table lines
            while i < len(lines):
                next_line = lines[i]
                next_tabs = next_line.count('\t')
                next_spaces = len(re.findall(r'\s{2,}', next_line))
                next_has_data = bool(re.search(r'[\d$%]', next_line))
                
                # If next line is also a table row, add it
                if (next_tabs >= 2 or next_spaces >= 2) and next_has_data and len(next_line) >= 20:
                    table_lines.append(next_line)
                    i += 1
                # If next line is empty or a header, might be part of table
                elif (not next_line.strip() or 
                      (next_line.strip() and not next_line.strip().startswith('#'))):
                    # Check if it's a continuation (like a multi-line header)
                    if len(next_line.strip()) > 0:
                        table_lines.append(next_line)
                        i += 1
                    else:
                        break
                else:
                    break
            
            # Convert to markdown table
            markdown_table = convert_to_markdown_table(table_lines)
            if markdown_table:
                fixed_lines.append(markdown_table)
            else:
                # If conversion failed, keep original
                fixed_lines.extend(table_lines)
        else:
            # Not a table line, keep as is
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)


# Example usage
if __name__ == "__main__":
    # Test with example broken table
    broken_table = """Year Ended December 31,		
2022	2023	2024
CASH, CASH EQUIVALENTS...	$ 36,477	$ 54,253	$ 73,890
OPERATING ACTIVITIES:			
Net income (loss)	(2,722)	30,425	59,248"""
    
    fixed = fix_table_formatting(broken_table)
    print("BROKEN:")
    print(broken_table)
    print("\nFIXED:")
    print(fixed)
