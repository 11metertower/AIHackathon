import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# os.environ 또는 os.getenv를 사용하여 변수 값 가져오기
EMAIL_ADDRESS = os.getenv("GMAIL_ID")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def get_recent_gmail_subjects(username, app_password, num_emails=100):
    # 환경 변수가 제대로 불러와졌는지 확인
    if not username or not app_password:
        print("오류: .env 파일에서 아이디나 비밀번호를 찾을 수 없습니다.")
        return

    try:
        # 1. Gmail IMAP 서버에 SSL로 연결
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        
        # 2. 로그인
        mail.login(username, app_password)
        
        # 3. 받은 편지함(INBOX) 선택
        mail.select("inbox")
        
        # 4. 모든 메일 검색
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("메일을 불러오는 데 실패했습니다.")
            return

        # 메일 ID 목록 가져오기
        mail_ids = messages[0].split()
        
        # 최근 num_emails 개수만큼의 ID 추출
        recent_ids = mail_ids[-num_emails:]
        
        print(f"최근 {len(recent_ids)}개의 메일 제목을 가져옵니다...\n")

        # 5. 최신 메일부터 역순으로 제목 가져오기
        for i in reversed(recent_ids):
            # 메일 데이터 가져오기
            res, msg_data = mail.fetch(i, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # 이메일 객체로 파싱
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 제목 디코딩
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # 인코딩 정보가 있으면 해당 인코딩으로, 없으면 utf-8로 디코딩
                        # 간혹 인코딩 정보가 'unknown-8bit' 등으로 잘못 표기되는 경우를 대비해 에러 무시 처리 추가
                        try:
                            subject = subject.decode(encoding if encoding else "utf-8", errors='ignore')
                        except LookupError:
                            subject = subject.decode("utf-8", errors='ignore')
                    
                    print(f"- {subject}")

        # 6. 연결 종료
        mail.logout()

    except Exception as e:
        print(f"에러가 발생했습니다: {e}")

# 프로그램 실행
if __name__ == "__main__":
    get_recent_gmail_subjects(EMAIL_ADDRESS, APP_PASSWORD)