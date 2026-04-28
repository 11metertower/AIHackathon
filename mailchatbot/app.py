import http.server
import socketserver
import json
import os
from main import ChatbotService

PORT = 8000

class ChatbotHandler(http.server.SimpleHTTPRequestHandler):
    chatbot_service = None

    def __init__(self, *args, **kwargs):
        if ChatbotHandler.chatbot_service is None:
            print("Chatbot Service 초기화 중...")
            ChatbotHandler.chatbot_service = ChatbotService()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
            return super().do_GET()
        elif self.path == '/categories':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            categories = ChatbotHandler.chatbot_service.get_categories()
            self.wfile.write(json.dumps(categories).encode())
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            query = data.get('query')
            category = data.get('category')
            
            print(f"질문 수신: [{category}] {query}")
            response = ChatbotHandler.chatbot_service.answer_question(query, category)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode())
        else:
            self.send_error(404)

if __name__ == "__main__":
    # mailchatbot 디렉토리로 작업 디렉토리 변경 (index.html 등을 찾기 위해)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), ChatbotHandler) as httpd:
        print(f"Chatbot 서비스가 http://localhost:{PORT} 에서 실행 중입니다.")
        httpd.serve_forever()
