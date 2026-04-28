import os
import json
import time
import sys
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# mailchatbot 폴더를 모듈 경로에 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIL_CHATBOT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'mailchatbot')
if MAIL_CHATBOT_DIR not in sys.path:
    sys.path.insert(0, MAIL_CHATBOT_DIR)

from main import ChatbotService

app = Flask(__name__)
app.secret_key = 'contextual_mail_tracker_secret'

# 데이터 파일 경로
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'jsonData')
CLASSIFIED_LIST_PATH = os.path.join(DATA_DIR, 'classified_list.json')
CATEGORY_PATH = os.path.join(DATA_DIR, 'category.json')

# ChatbotService 초기화 (지연 로딩 권장되지만 여기서는 전역으로 시도)
chatbot_service = None

def get_chatbot_service():
    global chatbot_service
    if chatbot_service is None:
        try:
            chatbot_service = ChatbotService()
        except Exception as e:
            print(f"Error initializing ChatbotService: {e}")
    return chatbot_service

def load_emails(limit=100):
    try:
        with open(CLASSIFIED_LIST_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data[:limit]
    except Exception as e:
        print(f"Error loading emails: {e}")
        return []

def load_categories():
    try:
        with open(CATEGORY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading categories: {e}")
        return []

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('inbox'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form.get('user_id')
    # 비밀번호는 실제로 검증하지 않고 아이디만 저장
    session['user_id'] = user_id
    return redirect(url_for('inbox'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    emails = load_emails()
    return render_template('inbox.html', emails=emails)

@app.route('/api/categories')
def get_categories():
    categories = load_categories()
    return jsonify(categories)

@app.route('/mailbox/<category>')
def mailbox(category):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    emails = [e for e in load_emails() if e.get('Category') == category]
    return render_template('mailbox.html', category=category, emails=emails)

@app.route('/mail/<int:mail_id>')
def mail_view(mail_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    emails = load_emails()
    if 0 <= mail_id < len(emails):
        mail = emails[mail_id]
        return render_template('mail_view.html', mail=mail, mail_id=mail_id)
    return "Mail not found", 404

@app.route('/api/chat', methods=['POST'])
def ai_chat():
    data = request.json
    user_message = data.get('message')
    category = data.get('category')
    
    service = get_chatbot_service()
    if service:
        try:
            # answer_question 내부에서 AI 요청 및 검색이 수행됨 (자연스러운 딜레이 발생)
            response = service.answer_question(user_message, category)
            return jsonify({"response": response})
        except Exception as e:
            print(f"Error in ai_chat: {e}")
            return jsonify({"response": f"오류가 발생했습니다: {str(e)}"}), 500
    
    return jsonify({"response": "Chatbot Service를 사용할 수 없습니다."}), 503

if __name__ == '__main__':
    app.run(debug=True, port=5000)
