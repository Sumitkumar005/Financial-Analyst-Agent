"""
Time-Series Data Extractor
Extracts time-series data from financial tables and stores in structured format.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class TimeSeriesExtractor:
    """
    Extracts time-series data from financial tables.
    """
    
    def __init__(self):
        self.time_series_data = {}  # {ticker: {metric: {year: value}}}
    
    def extract_from_table(self, table_text: str, ticker: str) -> Dict[str, Any]:
        """
        Extract time-series data from a markdown table.
        
        Example table:
        | Year | Revenue | Net Income |
        |------|---------|------------|
        | 2022 | $100B   | $20B       |
        | 2023 | $120B   | $25B       |
        | 2024 | $150B   | $30B       |
        """
        lines = table_text.split('\n')
        
        # Find header row
        header_row = None
        header_index = -1
        for i, line in enumerate(lines):
            if '|' in line and ('Year' in line or '202' in line):
                header_row = line
                header_index = i
                break
        
        if not header_row:
            return {}
        
        # Parse header
        headers = [h.strip() for h in header_row.split('|') if h.strip()]
        
        # Find year column index
        year_col_index = None
        for i, header in enumerate(headers):
            if 'year' in header.lower() or header.isdigit():
                year_col_index = i
                break
        
        if year_col_index is None:
            return {}
        
        # Extract data rows
        extracted_data = {}
        
        for line in lines[header_index + 2:]:  # Skip header and separator
            if '|' not in line:
                continue
            
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) <= year_col_index:
                continue
            
            # Extract year
            year_str = cells[year_col_index]
            year_match = re.search(r'(\d{4})', year_str)
            if not year_match:
                continue
            
            year = int(year_match.group(1))
            
            # Extract metric values
            for i, header in enumerate(headers):
                if i == year_col_index or i >= len(cells):
                    continue
                
                value_str = cells[i]
                value = self._parse_value(value_str)
                
                if value is not None:
                    metric_name = self._normalize_metric_name(header)
                    if metric_name not in extracted_data:
                        extracted_data[metric_name] = {}
                    extracted_data[metric_name][year] = value
        
        # Store in time-series data
        if ticker not in self.time_series_data:
            self.time_series_data[ticker] = {}
        
        for metric, values in extracted_data.items():
            if metric not in self.time_series_data[ticker]:
                self.time_series_data[ticker][metric] = {}
            self.time_series_data[ticker][metric].update(values)
        
        return extracted_data
    
    def _parse_value(self, value_str: str) -> Optional[float]:
        """Parse a value string to float."""
        # Remove currency symbols, commas, etc.
        cleaned = re.sub(r'[$,()]', '', value_str)
        
        # Handle negative values in parentheses
        if '(' in value_str and ')' in value_str:
            cleaned = '-' + cleaned.replace('(', '').replace(')', '')
        
        # Handle multipliers (B=billion, M=million, K=thousand)
        multiplier = 1
        if 'B' in value_str.upper():
            multiplier = 1_000_000_000
        elif 'M' in value_str.upper():
            multiplier = 1_000_000
        elif 'K' in value_str.upper():
            multiplier = 1_000
        
        # Remove letters
        cleaned = re.sub(r'[A-Za-z]', '', cleaned)
        
        try:
            value = float(cleaned) * multiplier
            return value
        except ValueError:
            return None
    
    def _normalize_metric_name(self, name: str) -> str:
        """Normalize metric name."""
        name = name.strip()
        # Remove common prefixes/suffixes
        name = re.sub(r'^\(in\s+millions?\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\(USD\)', '', name, flags=re.IGNORECASE)
        return name.strip()
    
    def get_time_series(self, ticker: str, metric: str, years: Optional[List[int]] = None) -> Dict[int, float]:
        """Get time-series data for a ticker and metric."""
        if ticker not in self.time_series_data:
            return {}
        
        if metric not in self.time_series_data[ticker]:
            return {}
        
        data = self.time_series_data[ticker][metric]
        
        if years:
            return {year: data[year] for year in years if year in data}
        
        return data
    
    def calculate_growth_rate(self, ticker: str, metric: str, year1: int, year2: int) -> Optional[float]:
        """Calculate growth rate between two years."""
        data = self.get_time_series(ticker, metric)
        
        if year1 not in data or year2 not in data:
            return None
        
        value1 = data[year1]
        value2 = data[year2]
        
        if value1 == 0:
            return None
        
        growth_rate = ((value2 - value1) / value1) * 100
        return growth_rate
    
    def get_trend(self, ticker: str, metric: str, years: Optional[List[int]] = None) -> str:
        """Determine trend: increasing, decreasing, or stable."""
        data = self.get_time_series(ticker, metric, years)
        
        if len(data) < 2:
            return "insufficient_data"
        
        sorted_years = sorted(data.keys())
        values = [data[year] for year in sorted_years]
        
        # Calculate average change
        changes = [values[i+1] - values[i] for i in range(len(values)-1)]
        avg_change = sum(changes) / len(changes)
        
        # Calculate percentage change
        if values[0] != 0:
            pct_change = (avg_change / values[0]) * 100
        else:
            pct_change = 0
        
        if pct_change > 5:
            return "increasing"
        elif pct_change < -5:
            return "decreasing"
        else:
            return "stable"
    
    def compare_companies(self, tickers: List[str], metric: str, year: int) -> Dict[str, float]:
        """Compare multiple companies on a metric for a given year."""
        comparison = {}
        
        for ticker in tickers:
            data = self.get_time_series(ticker, metric, [year])
            if year in data:
                comparison[ticker] = data[year]
        
        return comparison
    
    def export_to_json(self, filepath: str):
        """Export time-series data to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.time_series_data, f, indent=2)
    
    def load_from_json(self, filepath: str):
        """Load time-series data from JSON."""
        with open(filepath, 'r') as f:
            self.time_series_data = json.load(f)


# Global instance
_time_series_extractor = None

def get_time_series_extractor() -> TimeSeriesExtractor:
    """Get or create time-series extractor instance."""
    global _time_series_extractor
    if _time_series_extractor is None:
        _time_series_extractor = TimeSeriesExtractor()
    return _time_series_extractor
