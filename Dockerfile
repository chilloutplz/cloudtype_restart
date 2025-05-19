FROM python:3.10-slim

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg gnupg2 fonts-liberation libu2f-udev \
    chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# ChromeDriver 링크 설정
RUN ln -sf /usr/bin/chromium /usr/bin/google-chrome && \
    ln -sf /usr/lib/chromium/chromedriver /usr/local/bin/chromedriver

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY cloudtype_restart.py .

# 실행
CMD ["python", "cloudtype_restart.py"]
