import sys
from gmail_loader import load_emails
from vector_store import create_vector_db, load_vector_db
from gemini_service import GeminiService
from config import Config

def main():
    if not Config.GOOGLE_API_KEY or not Config.GMAIL_ID or not Config.GMAIL_APP_PASSWORD:
        print("Error: .env 파일에 필요한 API 키나 계정 정보가 설정되지 않았습니다.")
        return

    print("--- Gmail RAG Chatbot ---")
    
    # 1. 벡터 데이터베이스 로드 또는 생성
    vector_db = load_vector_db()
    
    if not vector_db:
        print("MX 라벨의 메일 데이터를 수집하여 인덱싱을 시작합니다. (잠시만 기다려주세요...)")
        emails = load_emails(mailbox="MX", num_emails=50) # MX 라벨 메일 수집
        if not emails:
            print("'MX' 라벨에서 수집된 메일이 없습니다. Gmail 라벨 이름을 확인하세요.")
            return
        vector_db = create_vector_db(emails)
        print("인덱싱 완료!")
    else:
        print("기존 벡터 데이터베이스를 로드했습니다.")
        refresh = input("메일을 새로 수집할까요? (y/n): ").lower()
        if refresh == 'y':
            print("MX 라벨에서 새로 수집 중...")
            emails = load_emails(mailbox="MX", num_emails=50)
            vector_db = create_vector_db(emails)
            print("인덱싱 완료!")

    # 2. Gemini 서비스 초기화
    gemini = GeminiService()

    # 3. 채팅 루프
    print("\n챗봇이 준비되었습니다. 질문을 입력하세요 (종료: exit, q)")
    while True:
        query = input("\n나: ")
        if query.lower() in ['exit', 'q']:
            break
        
        # 관련 문서 검색 (상위 3개)
        print("검색 중...", end="\r")
        docs = vector_db.similarity_search(query, k=3)
        
        # 답변 생성
        response = gemini.generate_response(query, docs)
        print(f"Gemini: {response}")

if __name__ == "__main__":
    main()
