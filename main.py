import os
from dotenv import load_dotenv

load_dotenv()  # 모듈 임포트 전 환경 변수 로드
from mailClassification.crawl import save_recent_gmails_to_json, EMAIL_ADDRESS, APP_PASSWORD
from mailClassification.classify import main as classify_main

def run_pipeline():
    print("🚀 AI Email Classification Pipeline 시작")
    
    # 1. 크롤링 (crawl.py의 기능을 호출하여 gmail_list.json 생성)
    print("\n[Step 1] 이메일 데이터 수집 중...")
    save_recent_gmails_to_json(
        EMAIL_ADDRESS, 
        APP_PASSWORD, 
        num_emails=100, 
        output_file="gmail_list.json"
    )
    
    # 2. 분류 (classify.py의 기능을 호출하여 classified_list.json 생성)
    print("\n[Step 2] AI 카테고리 분류 중...")
    classify_main()
    
    print("\n✅ 모든 프로세스가 완료되었습니다. 결과 파일을 확인하세요.")

if __name__ == "__main__":
    run_pipeline()