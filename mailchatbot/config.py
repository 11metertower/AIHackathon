import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GMAIL_ID = os.getenv("GMAIL_ID")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # Gemini 모델 설정 (현재 최신 안정 버전인 1.5-pro 사용)
    GEMINI_MODEL = "models/gemini-flash-latest"
    EMBEDDING_MODEL = "models/gemini-embedding-001"
    
    # 벡터 저장소 경로
    VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_db")
