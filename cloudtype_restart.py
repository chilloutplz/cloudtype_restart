# 파일명: cloudtype_restart.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os, time
from datetime import datetime

# 환경변수 로드
load_dotenv()

USER_ID = os.getenv("CLOUDTYPE_ID")
USER_PW = os.getenv("CLOUDTYPE_PW")

# Chrome 설정 (headless + no-sandbox for GitHub Actions)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
time.sleep(3)

# 로그인
try:
    element = driver.find_element(By.XPATH, "//*[contains(text(), 'GitHub 계정으로 로그인')]")
    element.click()
except Exception as e:
    print(f"로그인 방법 선택 오류: {e}")
time.sleep(3)

driver.switch_to.window(driver.window_handles[-1])

try:
    driver.find_element(By.XPATH, '//*[@id="login_field"]').send_keys(USER_ID)
    driver.find_element(By.ID, "password").send_keys(USER_PW)
    driver.find_element(By.NAME, "commit").click()
except Exception as e:
    print(f"로그인 오류: {e}")
time.sleep(3)

driver.switch_to.window(driver.window_handles[-1])
is_restarted = False

try:
    elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")
    print(f"{datetime.now()}: element 개수 - {len(elements)}")
    for element in elements:
        if 'text-muted' in element.get_attribute("class"):
            print(f"{datetime.now()} - 서비스가 실행중입니다.")
        else:
            parent = element.find_element(By.XPATH, "..")
            if 'duration-300' in parent.get_attribute("class"):
                print(f"{datetime.now()} - 서비스가 중단되어 재시작합니다.")
                parent.click()
                is_restarted = True

    if is_restarted:
        time.sleep(2)
        print("✅ 서비스 재시작 완료")

except Exception as e:
    print(f"요소 찾기 오류: {e}")

driver.quit()
