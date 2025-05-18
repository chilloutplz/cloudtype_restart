import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("CLOUDTYPE_ID")
USER_PW = os.getenv("CLOUDTYPE_PW")

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")  # GitHub Actions 권장 옵션
    chrome_options.add_argument("--disable-dev-shm-usage")  # 리소스 부족 방지
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
    time.sleep(3)

    # 로그인 방법 선택: GitHub 로그인 버튼 클릭
    try:
        element = driver.find_element(By.XPATH, "//*[contains(text(), 'GitHub 계정으로 로그인')]")
        element.click()
    except Exception as e:
        print(f"로그인 방법 선택 오류 발생: {e}")
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[-1])

    # GitHub 로그인
    try:
        id_field = driver.find_element(By.ID, "login_field")
        id_field.clear()
        id_field.send_keys(USER_ID)
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(USER_PW)
        commit_button = driver.find_element(By.NAME, "commit")
        commit_button.click()
    except Exception as e:
        print(f"로그인 오류: {e}")
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[-1])

    is_restarted = False

    while True:
        try:
            elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")
            print(f"{datetime.now()}: 서비스 버튼 개수 - {len(elements)}")
            for element in elements:
                class_attr = element.get_attribute("class")
                if 'text-muted' in class_attr:
                    print(f"{datetime.now()} - 서비스가 실행중입니다.")
                else:
                    parent_element = element.find_element(By.XPATH, "..")
                    if 'duration-300' in parent_element.get_attribute("class"):
                        print(f"{datetime.now()} - 서비스가 중단되어 재시작합니다.")
                        parent_element.click()
                        is_restarted = True

            if is_restarted:
                time.sleep(2)
                driver.close()
                break
        except Exception as e:
            print(f"요소 찾기 오류 발생: {e}")

        print(f"{datetime.now()} - 5분 후에 다시 확인합니다.")
        time.sleep(300)  # 5분 대기

    # GitHub Actions 환경에선 input() 사용 불가 → 바로 종료 처리
    print(f"{datetime.now()} - 자동 종료 처리 (GitHub Actions 환경에서는 사용자 입력 불가).")

    # 프로세스 종료
    driver.quit()

if __name__ == "__main__":
    main()
