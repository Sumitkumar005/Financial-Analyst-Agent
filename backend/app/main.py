"""
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

# Initialize FastAPI
app = FastAPI(
    title="Financial Analyst Agent API",
    description="Table-Aware RAG pipeline for financial document analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# Server startup
if __name__ == "__main__":
    import uvicorn
    print("="*80)
    print("🚀 Starting Financial Analyst Agent API Server")
    print("="*80)
    print(f"[INFO] Server will start at: http://localhost:8000")
    print(f"[INFO] API docs available at: http://localhost:8000/docs")
    print(f"[INFO] Health check: http://localhost:8000/health")
    print("="*80)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
