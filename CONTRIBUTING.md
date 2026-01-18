# Contributing Guide

Thank you for your interest in contributing to Financial Analyst Agent!

## Development Setup

1. **Fork and clone the repository**
2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your API keys

## Code Structure

- **Backend**: `backend/app/` - FastAPI application
- **Frontend**: `frontend/src/` - React application
- **Scripts**: `backend/scripts/` - Data processing scripts
- **Tests**: `backend/tests/` - Test files
- **Docs**: `docs/` - Documentation

## Coding Standards

- Follow existing code patterns
- Use type hints in Python
- Use TypeScript in frontend
- Write clear commit messages
- Never commit API keys or secrets

## Running Tests

```bash
# Backend tests
python -m backend.tests.test_api
python -m backend.tests.test_qdrant_connection
```

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request with a clear description
