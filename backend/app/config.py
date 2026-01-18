"""
Configuration settings for the Financial Analyst Agent
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# Collections
COLLECTION_NAME = "financial_reports"  # Original collection (company-level)
SECTIONS_COLLECTION = "financial_sections"  # New collection (section-level chunks)

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Directories
BASE_DIR = Path(__file__).parent.parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# Analysis Configuration
MAX_TOKENS_PER_FILE = 800000  # Leave room in 1M token window
USE_SMART_RETRIEVAL = True  # Toggle: True = smart retrieval, False = full file

# Validate required environment variables
if not QDRANT_URL:
    raise ValueError("QDRANT_URL environment variable is required. Please set it in .env file")
if not QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY environment variable is required. Please set it in .env file")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in .env file")
