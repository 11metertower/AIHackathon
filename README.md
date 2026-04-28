# AI Email Classification Project

이 프로젝트는 Gmail의 최근 이메일 목록을 가져와 Google Gemini AI를 사용하여 자동으로 카테고리를 분류해주는 도구입니다.

## 주요 기능

1.  **이메일 크롤링 (`crawl.py`)**: IMAP을 통해 Gmail에 접속하여 최신 이메일 100개의 날짜, 발신자, 제목을 수집하여 CSV 파일로 저장합니다.
2.  **AI 분류 (`classfy.py`)**: Google Gemini 1.5 Flash (Lite) 모델을 사용하여 수집된 이메일 제목을 분석하고 5가지 카테고리(광고/프로모션, 결제/영수증, 업무/알림, 뉴스레터, 기타)로 분류합니다.

## 설치 및 설정

### 1. 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래 정보를 입력합니다.

```env
GMAIL_ID=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_app_password
GEMINI_API_KEY=your_gemini_api_key
```

*   **GMAIL_APP_PASSWORD**: Gmail 설정에서 '앱 비밀번호'를 생성하여 사용해야 합니다. (2단계 인증 필요)
*   **GEMINI_API_KEY**: Google AI Studio에서 발급받을 수 있습니다.

## 사용 방법

### 단계 1: 이메일 데이터 수집

먼저 Gmail에서 최신 메일 목록을 가져옵니다.

```bash
python crawl.py
```
이 명령을 실행하면 `gmail_list.csv` 파일이 생성됩니다.

### 단계 2: AI 카테고리 분류

수집된 데이터를 AI에게 전달하여 분류를 진행합니다.

```bash
python classfy.py
```
분류가 완료되면 최종 결과가 `classified_list.csv` 파일에 저장됩니다.

## 프로젝트 구조
*   `crawl.py`: Gmail IMAP 연동 및 데이터 추출 스크립트
*   `classfy.py`: Gemini API를 이용한 데이터 분류 및 결과 저장 스크립트