# Python 기반 슬림 이미지
FROM python:3.10-slim

# Chrome 및 관련 패키지 설치
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    fonts-liberation libnss3 libxss1 libasound2 libatk-bridge2.0-0 \
    libgtk-3-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxi6 libgconf-2-4 xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Chrome 설치 (Stable)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# ChromeDriver 버전 고정 (Chrome 124 기준)
ENV CHROME_DRIVER_VERSION=124.0.6367.91

# ChromeDriver 설치
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# 작업 디렉토리 설정
WORKDIR /app
COPY . /app

# Python 패키지 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 스크립트 실행
CMD ["python", "cloudtype_restart.py"]
