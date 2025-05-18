from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

USER_ID = os.getenv("CLOUDTYPE_ID")
USER_PW = os.getenv("CLOUDTYPE_PW")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
    time.sleep(3)

    element = driver.find_element(By.XPATH, "//*[contains(text(), 'GitHub 계정으로 로그인')]")
    element.click()
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[-1])
    driver.find_element(By.ID, "login_field").send_keys(USER_ID)
    driver.find_element(By.ID, "password").send_keys(USER_PW)
    driver.find_element(By.NAME, "commit").click()
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[-1])
    elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")

    for element in elements:
        class_attr = element.get_attribute("class")
        if "text-muted" not in class_attr:
            print(f"{datetime.now()} - 서비스가 중단되어 재시작합니다.")
            parent = element.find_element(By.XPATH, "..")
            if "duration-300" in parent.get_attribute("class"):
                parent.click()
                time.sleep(2)
                break
        else:
            print(f"{datetime.now()} - 서비스는 실행 중입니다.")

finally:
    driver.quit()
