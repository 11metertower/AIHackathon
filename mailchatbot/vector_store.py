import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config

def create_vector_db(texts):
    # 텍스트 분할 (청크 생성)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    docs = text_splitter.create_documents(texts)
    
    # 임베딩 모델 설정
    embeddings = GoogleGenerativeAIEmbeddings(
        model=Config.EMBEDDING_MODEL,
        google_api_key=Config.GOOGLE_API_KEY
    )
    
    # 벡터 저장소 생성 및 저장
    vector_db = FAISS.from_documents(docs, embeddings)
    vector_db.save_local(Config.VECTOR_DB_PATH)
    return vector_db

def load_vector_db():
    embeddings = GoogleGenerativeAIEmbeddings(
        model=Config.EMBEDDING_MODEL,
        google_api_key=Config.GOOGLE_API_KEY
    )
    if os.path.exists(Config.VECTOR_DB_PATH):
        return FAISS.load_local(Config.VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    return None
