import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'contextual_mail_tracker_secret'

# 데이터 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'jsonData')
CLASSIFIED_LIST_PATH = os.path.join(DATA_DIR, 'classified_list.json')
CATEGORY_PATH = os.path.join(DATA_DIR, 'category.json')

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
    
    # AI 요청을 기다리는 가상의 딜레이
    time.sleep(1.5)
    
    return jsonify({"response": "미구현되었습니다."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
