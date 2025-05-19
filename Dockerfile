# 베이스 이미지
FROM python:3.10-slim

# Chrome 설치를 위한 기본 패키지
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip fonts-liberation \
    libnss3 libgconf-2-4 libxss1 libasound2 libx11-xcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxi6 \
    libatk-bridge2.0-0 libgtk-3-0 xvfb \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치 (버전 자동 일치)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) && \
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# 작업 디렉토리 및 복사
WORKDIR /app
COPY . /app

# 의존성 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 실행
CMD ["python", "cloudtype_restart.py"]
