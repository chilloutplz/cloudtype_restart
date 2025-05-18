from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
from dotenv import load_dotenv
from datetime import datetime

print(f"{datetime.now()} - 스크립트 시작됨")

load_dotenv()

USER_ID = os.getenv("CLOUDTYPE_ID")
USER_PW = os.getenv("CLOUDTYPE_PW")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print(f"{datetime.now()} - Chrome 드라이버 초기화 중...")

driver = webdriver.Chrome(options=chrome_options)

try:
    print(f"{datetime.now()} - Cloudtype 서비스 페이지 접속 중...")
    driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
    time.sleep(3)

    wait = WebDriverWait(driver, 20)
    print(f"{datetime.now()} - 로그인 버튼 찾는 중...")
    element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page"]/div/div[1]/div/div[2]/div/div[2]/div[1]/a[1]')))
    print(f"{datetime.now()} - 로그인 버튼 텍스트: '{element.text}'")
    element.click()

    print(f"{datetime.now()} - GitHub 로그인 창으로 전환 중...")
    driver.switch_to.window(driver.window_handles[-1])
    print(f"{datetime.now()} - GitHub 로그인 시도 중...")
    driver.find_element(By.ID, "login_field").send_keys(USER_ID)
    driver.find_element(By.ID, "password").send_keys(USER_PW)
    driver.find_element(By.NAME, "commit").click()
    time.sleep(3)

    print(f"{datetime.now()} - Cloudtype 서비스 상태 확인 중...")
    driver.switch_to.window(driver.window_handles[-1])
    elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")

    found = False
    for element in elements:
        class_attr = element.get_attribute("class")
        if "text-muted" not in class_attr:
            print(f"{datetime.now()} - ❗서비스가 중단되어 재시작합니다.")
            parent = element.find_element(By.XPATH, "..")
            if "duration-300" in parent.get_attribute("class"):
                parent.click()
                print(f"{datetime.now()} - 🔁 재시작 클릭 완료")
                time.sleep(2)
                found = True
                break

    if not found:
        print(f"{datetime.now()} - ✅ 서비스는 실행 중입니다.")

except Exception as e:
    print(f"{datetime.now()} - ❌ 오류 발생: {e}")

finally:
    driver.quit()
    print(f"{datetime.now()} - 스크립트 종료됨")
