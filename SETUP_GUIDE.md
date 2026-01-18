# Complete Setup Guide

Step-by-step guide to set up and run the Financial Analyst Agent.

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Git
- Qdrant Cloud account (or local Qdrant instance)
- Google Gemini API key

## Step 1: Clone Repository

```bash
git clone https://github.com/Sumitkumar005/Financial-Analyst-Agent.git
cd Financial-Analyst-Agent
```

## Step 2: Set Up Python Backend

### 2.1 Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2.3 Configure Environment Variables

Create a `.env` file in the project root:

```env
# Qdrant Cloud Configuration
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Important**: Replace the placeholder values with your actual API keys.

## Step 3: Set Up Frontend

### 3.1 Install Dependencies

```bash
cd frontend
npm install
cd ..
```

## Step 4: Verify Setup

### 4.1 Test Qdrant Connection

```bash
python -m backend.tests.test_qdrant_connection
```

Expected output: `[SUCCESS] Connected successfully!`

### 4.2 Check Python Imports

```bash
python -c "from backend.app.config import BASE_DIR; print('Config OK')"
```

## Step 5: Run the Application

### 5.1 Start Backend Server

**Option 1: Using Python module (Recommended)**
```bash
python -m backend.app.main
```

**Option 2: Using uvicorn**
```bash
uvicorn backend.app.main:app --reload
```

**Option 3: Using batch file (Windows)**
```bash
start_server.bat
```

The server will start at: **http://localhost:8000**

### 5.2 Start Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

The frontend will start at: **http://localhost:5173**

## Step 6: Verify Everything Works

1. **Backend Health Check**
   - Open browser: http://localhost:8000/health
   - Should show: `{"status": "healthy", ...}`

2. **API Documentation**
   - Open browser: http://localhost:8000/docs
   - Should show Swagger UI

3. **Frontend**
   - Open browser: http://localhost:5173
   - Should show the application interface

## Troubleshooting

### Issue: "QDRANT_URL environment variable is required"

**Solution**: Make sure you created `.env` file in the project root with your Qdrant credentials.

### Issue: "ModuleNotFoundError"

**Solution**: 
```bash
pip install -r backend/requirements.txt
```

### Issue: Frontend won't start

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json  # Linux/Mac
# OR
rmdir /s node_modules & del package-lock.json  # Windows

npm install
```

### Issue: Port already in use

**Solution**: 
- Backend: Change port in `backend/app/main.py` (line 41)
- Frontend: Vite will automatically use next available port

## Next Steps

1. **Index Companies** (if you have data):
   ```bash
   python -m backend.scripts.index
   ```

2. **Test the API**:
   ```bash
   python -m backend.tests.test_api
   ```

3. **Upload a File**:
   - Use the frontend upload feature
   - Or POST to http://localhost:8000/upload

## Ready for Demo! 🎬

Once all steps are complete and you see:
- ✅ Backend running on port 8000
- ✅ Frontend running on port 5173
- ✅ Health check returns "healthy"
- ✅ No errors in console

You're ready to record your demo video!
