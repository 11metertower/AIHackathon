import os
import csv
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# 현재 파일(classify.py)의 상위 디렉토리(root)에 있는 .env 파일을 로드
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("오류: .env 파일에 GEMINI_API_KEY를 찾을 수 없습니다.")
    exit()

INPUT_FILE = "gmail_list.csv"
OUTPUT_FILE = "classified_list.csv"

def main():
    print("1. CSV 파일 읽는 중...")
    try:
        with open(INPUT_FILE, mode="r", encoding="utf-8-sig") as infile:
            cleaned_lines = (line.replace('\0', '') for line in infile)
            reader = csv.reader(cleaned_lines)
            rows = list(reader)
    except FileNotFoundError:
        print("CSV 파일을 찾을 수 없습니다.")
        return

    header = rows[0]
    emails = [row for row in rows[1:] if len(row) >= 3]

    print(f"2. {len(emails)}개의 이메일을 Gemini Flash 모델로 전송 중... (약 3~5초 소요)")
    
    # AI에게 보낼 JSON 데이터 만들기
    email_data_for_ai = []
    for i, row in enumerate(emails):
        email_data_for_ai.append({"id": i, "subject": row[2]})

    prompt = f"""
    당신은 이메일 분류 전문가입니다. 아래 JSON 데이터를 보고 각 이메일의 제목(subject)을 분석하세요.
    반드시 다음 카테고리 중 하나로만 분류해야 합니다: ["광고/프로모션", "결제/영수증", "업무/알림", "뉴스레터", "기타"]
    
    분류 결과를 아래와 같은 JSON 배열(Array) 형식으로만 대답하세요. 다른 말은 절대 하지 마세요.
    예시: [{{"id": 0, "category": "광고/프로모션"}}, {{"id": 1, "category": "업무/알림"}}]
    
    분류할 데이터:
    {json.dumps(email_data_for_ai, ensure_ascii=False)}
    """

    # 구글 라이브러리 없이 직접 통신(REST API)하여 가장 빠른 모델 호출
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json" # 무조건 JSON으로만 답변하도록 강제
        }
    }

    try:
        # API 전송
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # 인터넷 연결 문제 등이 있으면 에러 발생
        
        # 구글 서버에서 온 답변 파싱
        result_data = response.json()
        text_response = result_data["candidates"][0]["content"]["parts"][0]["text"]
        
        # 텍스트를 파이썬 리스트로 변환
        classified_results = json.loads(text_response)
        
        print("3. 분류 완료! 결과를 새로운 CSV에 저장합니다...")
        
        # 기존 데이터에 'Category' 합치기
        header.append("Category")
        data_to_save = [header]
        
        for i, row in enumerate(emails):
            # AI가 답변한 결과에서 id가 일치하는 카테고리 찾기
            category = next((item["category"] for item in classified_results if item.get("id") == i), "분류 실패")
            row.append(category)
            data_to_save.append(row)

        # 새 파일로 저장
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8-sig") as outfile:
            writer = csv.writer(outfile)
            writer.writerows(data_to_save)
            
        print(f"\n✅ 성공! 100개의 메일이 눈 깜짝할 새에 분류되어 '{OUTPUT_FILE}'에 저장되었습니다.")

    except Exception as e:
        print(f"\n에러가 발생했습니다: {e}")
        if 'response' in locals():
            print("상세 에러 내용:", response.text)

if __name__ == "__main__":
    main()