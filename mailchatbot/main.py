import sys
import json
import os
from vector_store import load_vector_db
from gemini_service import GeminiService
from config import Config

class ChatbotService:
    def __init__(self):
        self.vector_db = load_vector_db()
        if not self.vector_db:
            raise Exception("Vector database not found. Please run indexing first.")
        self.gemini = GeminiService()
        
        # 카테고리 로드
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        category_file = os.path.join(base_dir, "jsonData", "category.json")
        
        if not os.path.exists(category_file):
             # Fallback to local if jsonData not found (though according to structure it should be there)
             category_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "category.json")
        
        with open(category_file, 'r', encoding='utf-8') as f:
            self.categories = json.load(f)

    def get_categories(self):
        return self.categories

    def answer_question(self, query, category):
        # 관련 문서 검색 (카테고리 필터 적용)
        docs = self.vector_db.similarity_search(query, k=3, filter={"category": category})
        
        if not docs:
            return "선택한 카테고리에서 관련 정보를 찾을 수 없습니다."

        # 답변 생성
        response = self.gemini.generate_response(query, docs)
        return response

def main():
    try:
        service = ChatbotService()
    except Exception as e:
        print(f"Error: {e}")
        return

    print("--- Gmail RAG Chatbot (Service Mode) ---")
    categories = service.get_categories()
    
    print("\n[사용 가능한 카테고리]")
    for i, cat in enumerate(categories):
        print(f"{i+1}. {cat}")
    
    try:
        cat_idx = int(input("\n조회할 카테고리 번호를 선택하세요: ")) - 1
        if 0 <= cat_idx < len(categories):
            selected_category = categories[cat_idx]
            print(f"'{selected_category}' 카테고리에 대해 질문을 받습니다.")
        else:
            print("잘못된 선택입니다. 종료합니다.")
            return
    except ValueError:
        print("숫자를 입력해야 합니다.")
        return

    print("\n챗봇이 준비되었습니다. 질문을 입력하세요 (종료: exit, q)")
    while True:
        query = input("\n나: ")
        if query.lower() in ['exit', 'q']:
            break
        
        response = service.answer_question(query, selected_category)
        print(f"Gemini: {response}")

if __name__ == "__main__":
    main()
