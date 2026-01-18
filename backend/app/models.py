"""
Pydantic models for API requests and responses
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """Request model for financial analysis"""
    query: str
    max_companies: Optional[int] = 5


class AnalyzeResponse(BaseModel):
    """Response model for financial analysis"""
    query: str
    companies_found: List[str]
    file_paths: List[str]
    analysis: str
    metadata: Dict[str, Any]


class CompanyInfo(BaseModel):
    """Company information model"""
    ticker: str
    year: str
    file_path: str
    tables_count: int
    size_mb: float
    lines: int


class ProcessFileResponse(BaseModel):
    """Response model for file upload and processing"""
    success: bool
    steps: Dict[str, Any]
    ticker: Optional[str]
    html_size: int
    markdown_size: int
    markdown_preview: str
    file_path: Optional[str]
    html_file_path: Optional[str] = None
    indexed: bool = False
    ready_for_qa: bool = False
    error: Optional[str] = None
