from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os, time
from datetime import datetime

# 환경변수 로드 (.env 대신 GitHub Actions에 설정된 Secrets 사용)
load_dotenv()
USER_ID = os.getenv("CLOUDTYPE_ID")
USER_PW = os.getenv("CLOUDTYPE_PW")

# Selenium 브라우저 옵션
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

try:
    print(f"[{datetime.now()}] Cloudtype 페이지 접속 중...")
    driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
    time.sleep(3)

    # GitHub 로그인 선택
    github_login_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'GitHub 계정으로 로그인')]")
    github_login_btn.click()
    time.sleep(3)

    # GitHub 로그인 창으로 전환
    driver.switch_to.window(driver.window_handles[-1])

    # GitHub 로그인
    driver.find_element(By.ID, "login_field").send_keys(USER_ID)
    driver.find_element(By.ID, "password").send_keys(USER_PW)
    driver.find_element(By.NAME, "commit").click()
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[-1])

    # 서비스 재시작 여부
    is_restarted = False

    # 서비스 상태 확인
    elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")
    print(f"[{datetime.now()}] 서비스 버튼 수: {len(elements)}")

    for element in elements:
        class_attr = element.get_attribute("class")
        if "text-muted" in class_attr:
            print(f"[{datetime.now()}] 서비스 실행 중입니다.")
        else:
            parent_element = element.find_element(By.XPATH, "..")
            if "duration-300" in parent_element.get_attribute("class"):
                print(f"[{datetime.now()}] 서비스가 중단되어 재시작합니다.")
                parent_element.click()
                is_restarted = True

    if is_restarted:
        time.sleep(2)
        print(f"[{datetime.now()}] 재시작 완료!")

except Exception as e:
    print(f"[{datetime.now()}] 에러 발생: {e}")

finally:
    driver.quit()
