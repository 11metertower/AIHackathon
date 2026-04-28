import google.generativeai as genai
from config import Config

class GeminiService:
    def __init__(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    def generate_response(self, query, context_docs):
        # 검색된 문서들을 하나의 컨텍스트로 결합
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""
당신은 사용자의 이메일 데이터를 기반으로 답변하는 전문 비서입니다. 
제공된 이메일 내용(Context)을 바탕으로 사용자의 질문(Question)에 정확하고 친절하게 답변하세요.
만약 답변에 필요한 정보가 Context에 없다면, 모른다고 답변하거나 이메일 내용에 없음을 명시하세요.

[Context]
{context}

[Question]
{query}

[Answer]
"""
        response = self.model.generate_content(prompt)
        return response.text
