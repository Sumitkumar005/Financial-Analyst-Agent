"""
Markdown conversion utilities
"""

import re
import markdownify


def convert_html_to_markdown(html_content: str) -> str:
    """Convert HTML to Markdown using markdownify, then fix table formatting"""
    md = markdownify.markdownify(html_content, heading_style="ATX")
    
    # Post-process: Fix tab-separated tables to markdown format
    # This ensures all tables are properly formatted
    lines = md.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line looks like a tab-separated table row
        if '\t' in line and line.count('\t') >= 2 and bool(re.search(r'[\d$%]', line)):
            # Collect consecutive table lines
            table_lines = [line]
            i += 1
            
            while i < len(lines):
                next_line = lines[i]
                if '\t' in next_line and next_line.count('\t') >= 2 and bool(re.search(r'[\d$%]', next_line)):
                    table_lines.append(next_line)
                    i += 1
                elif not next_line.strip():  # Empty line might be separator
                    i += 1
                    break
                else:
                    break
            
            # Convert to markdown table
            if len(table_lines) >= 2:
                rows = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.split('\t') if c.strip() or len(c) > 0]
                    if len(cells) >= 2:
                        rows.append(cells)
                
                if rows:
                    max_cols = max(len(r) for r in rows)
                    for r in rows:
                        while len(r) < max_cols:
                            r.append('')
                    
                    # Build markdown table
                    fixed_lines.append('| ' + ' | '.join(rows[0]) + ' |')
                    fixed_lines.append('| ' + ' | '.join(['---'] * len(rows[0])) + ' |')
                    for row in rows[1:]:
                        fixed_lines.append('| ' + ' | '.join(row) + ' |')
                    continue
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)
