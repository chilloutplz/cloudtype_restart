FROM python:3.10-slim

# 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg xvfb libnss3 libgconf-2-4 libxss1 libasound2 libatk1.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y ./google-chrome-stable_current_amd64.deb || apt --fix-broken install -y

# ChromeDriver 설치
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip chromedriver.zip && \
    mv chromedriver /usr/local/bin/ && chmod +x /usr/local/bin/chromedriver

# 파이썬 패키지 설치
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 스크립트 복사
COPY cloudtype_restart.py .

# 실행
ENTRYPOINT ["python", "cloudtype_restart.py"]
