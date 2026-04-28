import os
import imaplib
import email
import csv
from email.header import decode_header
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

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

def save_recent_gmails_to_csv(username, app_password, num_emails=100, output_file="recent_emails.csv"):
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

        # 3. CSV 파일 열기 (utf-8-sig: 엑셀 한글 깨짐 방지)
        with open(output_file, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            # CSV 헤더(첫 줄) 작성
            writer.writerow(["Date", "Sender", "Title"])

            # 4. 최신 메일부터 역순으로 데이터 가져오기
            for i in reversed(recent_ids):
                res, msg_data = mail.fetch(i, "(RFC822)")
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # 메일 정보 디코딩
                        subject = decode_mime_words(msg.get("Subject", ""))
                        sender = decode_mime_words(msg.get("From", ""))
                        date = msg.get("Date", "")
                        
                        # CSV 파일에 한 줄씩 쓰기
                        writer.writerow([date, sender, subject])
                        print(f"저장 완료: {subject[:30]}...") # 진행 상황 출력 (제목이 길면 자름)

        print(f"\n✅ 모든 데이터가 '{output_file}'에 성공적으로 저장되었습니다.")

        # 5. 연결 종료
        mail.logout()

    except Exception as e:
        print(f"에러가 발생했습니다: {e}")

# 프로그램 실행
if __name__ == "__main__":
    # 파일명과 가져올 메일 개수를 지정할 수 있습니다.
    save_recent_gmails_to_csv(EMAIL_ADDRESS, APP_PASSWORD, num_emails=100, output_file="gmail_list.csv")