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
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
    time.sleep(3)

    # GitHub 로그인 버튼 클릭
    try:
        element = driver.find_element(By.XPATH, "//*[contains(text(), 'GitHub 계정으로 로그인')]")
        element.click()
    except Exception as e:
        print(f"로그인 버튼 클릭 실패: {e}")
        driver.quit()
        return
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
        print(f"GitHub 로그인 실패: {e}")
        driver.quit()
        return
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[-1])

    # 서비스 상태 확인 및 재시작
    try:
        elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")
        print(f"{datetime.now()}: 서비스 버튼 개수 - {len(elements)}")

        for element in elements:
            class_attr = element.get_attribute("class")
            if 'text-muted' in class_attr:
                print(f"{datetime.now()} - 서비스가 실행중입니다. 종료합니다.")
            else:
                parent = element.find_element(By.XPATH, "..")
                if 'duration-300' in parent.get_attribute("class"):
                    print(f"{datetime.now()} - 서비스가 중단되어 재시작합니다.")
                    parent.click()
                    time.sleep(2)

    except Exception as e:
        print(f"서비스 상태 확인 중 오류: {e}")

    driver.quit()
    print(f"{datetime.now()} - 작업 완료 후 종료합니다.")

if __name__ == "__main__":
    main()
