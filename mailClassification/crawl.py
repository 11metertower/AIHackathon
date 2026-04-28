import os
import imaplib
import email
import json
from bs4 import BeautifulSoup
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv

# 현재 파일(crawl.py)의 상위 디렉토리(root)에 있는 .env 파일을 로드
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

EMAIL_ADDRESS = os.getenv("GMAIL_ID")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def decode_mime_words(s):
    """이메일 헤더의 인코딩된 문자열을 읽을 수 있는 문자열로 디코딩하는 헬퍼 함수"""
    if not s:
        return ""
    
    decoded_string = ""
    for word, encoding in decode_header(s):
        if isinstance(word, bytes):
            try:
                decoded_string += word.decode(encoding if encoding else "utf-8", errors="ignore")
            except LookupError:
                decoded_string += word.decode("utf-8", errors="ignore")
        else:
            decoded_string += str(word)
    return decoded_string

def get_email_body(msg):
    """이메일 메시지에서 본문 텍스트를 추출하는 함수 (Plain text 및 HTML 처리)"""
    body_text = ""
    if msg.is_multipart():
        html_part = None
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" in content_disposition:
                continue

            # 일반 텍스트(plain) 파트가 있으면 우선 선택
            if content_type == "text/plain" and "attachment" not in content_disposition:
                body_text = part.get_payload(decode=True).decode(errors="ignore")
                break
            elif content_type == "text/html" and "attachment" not in content_disposition:
                html_part = part.get_payload(decode=True).decode(errors="ignore")

        # plain 텍스트가 없고 HTML 파트만 있는 경우 BeautifulSoup으로 정제
        if not body_text and html_part:
            body_text = BeautifulSoup(html_part, "html.parser").get_text(separator=' ')
    else:
        body_text = msg.get_payload(decode=True).decode(errors="ignore")

    # 불필요한 공백 및 줄바꿈 정리 (용량 최적화 및 포맷 안정성)
    return " ".join(body_text.split())

def save_recent_gmails_to_json(username, app_password, num_emails=100, output_file="recent_emails.json"):
    if not username or not app_password:
        print("오류: .env 파일에서 아이디나 비밀번호를 찾을 수 없습니다.")
        return

    try:
        # 1. Gmail IMAP 서버에 SSL로 연결
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, app_password)
        mail.select("inbox")
        
        # 2. 모든 메일 검색
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("메일을 불러오는 데 실패했습니다.")
            return

        mail_ids = messages[0].split()
        recent_ids = mail_ids[-num_emails:]
        
        print(f"총 {len(recent_ids)}개의 메일을 '{output_file}'에 저장합니다...\n")

        # 3. 메일 데이터 수집
        email_list = []
        for i in reversed(recent_ids):
            res, msg_data = mail.fetch(i, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = decode_mime_words(msg.get("Subject", ""))
                    sender = decode_mime_words(msg.get("From", ""))
                    date = msg.get("Date", "")
                    body = get_email_body(msg)
                    
                    email_list.append({
                        "Date": date,
                        "Sender": sender,
                        "Title": subject,
                        "Body": body
                    })
                    print(f"수집 완료: {subject[:30]}...")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(email_list, f, ensure_ascii=False, indent=4)

        print(f"\n✅ 모든 데이터가 '{output_file}'에 성공적으로 저장되었습니다.")

        # 5. 연결 종료
        mail.logout()

    except Exception as e:
        print(f"에러가 발생했습니다: {e}")

# 프로그램 실행
if __name__ == "__main__":
    # 파일명과 가져올 메일 개수를 지정할 수 있습니다.
    save_recent_gmails_to_json(EMAIL_ADDRESS, APP_PASSWORD, num_emails=100, output_file="gmail_list.json")