"""
HTML extraction utilities
"""

import re
from typing import Optional


def extract_10k_html_from_txt(content: str) -> Optional[str]:
    """Extract FULL 10-K HTML from full-submission.txt using <TEXT> tag method"""
    try:
        # Find the first DOCUMENT section with TYPE=10-K and extract from <TEXT> tag
        pattern = r'<DOCUMENT>.*?<TYPE>10-K.*?<TEXT>(.*?)</TEXT>.*?</DOCUMENT>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"[ERROR] HTML extraction failed: {e}")
        return None
