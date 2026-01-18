"""
Ticker extraction utilities
"""

import re
from typing import List, Optional


def extract_ticker_from_content(content: str) -> Optional[str]:
    """Extract ticker symbol from content (look for common patterns)"""
    # Try to find ticker in various patterns
    patterns = [
        r'<ticker>(\w+)</ticker>',
        r'CIK.*?(\d{10})',  # CIK number
        r'CENTRAL INDEX KEY:\s*(\d{10})',
        r'\(([A-Z]{1,5})\)',  # Ticker in parentheses
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            # If it's a CIK, we can't convert to ticker easily, so skip
            if pattern.startswith('CIK') or 'INDEX' in pattern:
                continue
            return match.group(1).upper()
    
    return None


def extract_tickers_simple(query: str) -> List[str]:
    """
    Simple ticker extraction using keyword matching.
    TODO: Replace with LLM-based extraction for better accuracy.
    """
    # Common company name to ticker mapping
    company_map = {
        "apple": "AAPL", "microsoft": "MSFT", "amazon": "AMZN", "google": "GOOGL",
        "alphabet": "GOOGL", "meta": "META", "facebook": "META", "tesla": "TSLA",
        "nvidia": "NVDA", "netflix": "NFLX", "disney": "DIS", "jpmorgan": "JPM",
        "jpm": "JPM", "bank of america": "BAC", "goldman sachs": "GS",
        "morgan stanley": "MS", "citigroup": "C", "wells fargo": "WFC",
        "aws": "AMZN", "azure": "MSFT", "gcp": "GOOGL"
    }
    
    query_lower = query.lower()
    found_tickers = []
    
    # Check for direct ticker mentions (uppercase 2-5 letter codes)
    ticker_pattern = r'\b([A-Z]{2,5})\b'
    direct_tickers = re.findall(ticker_pattern, query)
    found_tickers.extend(direct_tickers)
    
    # Check for company names
    for company, ticker in company_map.items():
        if company in query_lower and ticker not in found_tickers:
            found_tickers.append(ticker)
    
    return list(set(found_tickers))  # Remove duplicates
