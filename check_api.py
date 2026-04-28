import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("오류: .env 파일에 GOOGLE_API_KEY가 설정되지 않았습니다.")
else:
    genai.configure(api_key=api_key)
    print("\n--- 사용 가능한 모든 모델 목록 ---")
    try:
        for m in genai.list_models():
            print(f"이름: {m.name}, 지원메서드: {m.supported_generation_methods}")
    except Exception as e:
        print(f"오류 발생: {e}")
