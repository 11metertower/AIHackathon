import os
import time
import re
from bs4 import BeautifulSoup
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config
from langchain_core.documents import Document

def clean_html(html_content):
    if not html_content:
        return ""
    # HTML 태그 제거
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=' ')
    # 연속된 공백 및 줄바꿈 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_vector_db(emails):
    # 텍스트 분할 (청크 생성)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    docs = []
    print("메일 본문 정리 중...")
    for email in emails:
        raw_body = email.get('Body', '')
        # HTML 태그 제거하여 토큰 사용량 최적화
        clean_body = clean_html(raw_body)
        
        # 내용이 너무 길 경우 토큰 제한 대비 절단
        if len(clean_body) > 5000:
            clean_body = clean_body[:5000]

        content = f"Title: {email.get('Title', 'No Title')}\nSender: {email.get('Sender', 'Unknown')}\nDate: {email.get('Date', '')}\nContent: {clean_body}"
        metadata = {"category": email.get("Category", "Uncategorized")}
        
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            docs.append(Document(page_content=chunk, metadata=metadata))
    
    # 임베딩 모델 설정
    embeddings = GoogleGenerativeAIEmbeddings(
        model=Config.EMBEDDING_MODEL,
        google_api_key=Config.GOOGLE_API_KEY
    )
    
    # 벡터 저장소 생성 (Rate Limit 및 Quota 대응을 위해 보수적인 배치 처리)
    print(f"총 {len(docs)}개의 문서 청크를 인덱싱합니다. (지연 시간이 발생할 수 있습니다)")
    batch_size = 5 
    vector_db = None
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        
        retry_count = 0
        max_retries = 5
        base_delay = 10 # 초 단위
        
        while retry_count < max_retries:
            try:
                if vector_db is None:
                    vector_db = FAISS.from_documents(batch, embeddings)
                else:
                    vector_db.add_documents(batch)
                break # 성공 시 루프 탈출
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    retry_count += 1
                    wait_time = base_delay * (2 ** (retry_count - 1))
                    print(f"\n[Quota Error] {wait_time}초 후 재시도 중... ({retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e # 다른 에러는 즉시 발생
        else:
            print("최대 재시도 횟수를 초과했습니다. 일부 데이터가 누락될 수 있습니다.")
        
        print(f"진행 상황: {min(i + batch_size, len(docs))}/{len(docs)} 완료...", end="\r")
        time.sleep(5) # 기본 배치 간 지연
        
    print("\n인덱싱이 완료되었습니다.")
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
