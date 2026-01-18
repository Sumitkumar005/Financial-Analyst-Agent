"""
LLM (Gemini) service
"""

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARNING] Google Generative AI not installed. Gemini features will be disabled.")
    print("   Install with: pip install google-generativeai")

from app.config import GEMINI_API_KEY, GEMINI_MODEL

# Global model instance (lazy loading)
_gemini_model = None


def get_gemini_model():
    """Get or create Gemini model."""
    global _gemini_model
    if not GEMINI_AVAILABLE:
        return None
    if _gemini_model is None:
        if not GEMINI_API_KEY:
            print("[WARNING] GOOGLE_API_KEY not set. Gemini features disabled.")
            return None
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            print(f"[SUCCESS] Gemini model '{GEMINI_MODEL}' loaded!")
            print(f"[INFO] API Key configured: {GEMINI_API_KEY[:20]}...{GEMINI_API_KEY[-4:]}")
        except Exception as e:
            print(f"[ERROR] Failed to load Gemini: {e}")
            return None
    return _gemini_model


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)."""
    return len(text) // 4
