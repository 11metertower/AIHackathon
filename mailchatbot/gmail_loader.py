import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from config import Config

def decode_mime_words(s):
    if not s: return ""
    decoded_string = ""
    for word, encoding in decode_header(s):
        if isinstance(word, bytes):
            try:
                decoded_string += word.decode(encoding if encoding else "utf-8", errors="ignore")
            except:
                decoded_string += word.decode("utf-8", errors="ignore")
        else:
            decoded_string += str(word)
    return decoded_string

def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode(errors="ignore")
            elif content_type == "text/html" and "attachment" not in content_disposition:
                html = part.get_payload(decode=True).decode(errors="ignore")
                return BeautifulSoup(html, "html.parser").get_text()
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

def load_emails(mailbox="INBOX", num_emails=50):
    emails = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(Config.GMAIL_ID, Config.GMAIL_APP_PASSWORD)
        mail.select(mailbox)

        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()
        recent_ids = mail_ids[-num_emails:]

        for i in reversed(recent_ids):
            res, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_mime_words(msg.get("Subject", ""))
                    sender = decode_mime_words(msg.get("From", ""))
                    body = get_email_body(msg)
                    
                    content = f"Subject: {subject}\nFrom: {sender}\nBody: {body}"
                    emails.append(content)
        
        mail.logout()
    except Exception as e:
        print(f"Error loading emails: {e}")
    
    return emails
