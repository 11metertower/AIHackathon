# Python 3.9 슬림 이미지를 기반으로 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 파일 복사
COPY . .

# 컨테이너 실행 시 main.py 실행
CMD ["python", "main.py"]