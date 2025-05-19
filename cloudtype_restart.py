import imaplib, email, re, os, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from datetime import datetime

print(f"{datetime.now()} - 스크립트 시작됨")

load_dotenv()

USER_ID = os.getenv("CLOUDTYPE_ID")
USER_PW = os.getenv("CLOUDTYPE_PW")
EMAIL = os.getenv("EMAIL_ADDRESS")
EMAIL_PW = os.getenv("EMAIL_PASSWORD")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

print(f"{datetime.now()} - Chrome 드라이버 초기화 중...")

driver = webdriver.Chrome(options=chrome_options)

def get_github_verification_code():
    print(f"{datetime.now()} - 인증코드 수신 대기 중...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, EMAIL_PW)
    mail.select("inbox")

    for _ in range(30):
        result, data = mail.search(None, '(FROM "noreply@github.com")')
        ids = data[0].split()
        if ids:
            latest_id = ids[-1]
            result, msg_data = mail.fetch(latest_id, "(RFC822)")
            if not msg_data or not msg_data[0]:
                print(f"{datetime.now()} - 메일 본문 없음 (msg_data is None)")
                time.sleep(1)
                continue

            try:
                raw = msg_data[0][1]
                if not raw:
                    print(f"{datetime.now()} - 메시지 바디가 None입니다.")
                    time.sleep(1)
                    continue

                msg = email.message_from_bytes(raw)

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode()
                                code = re.search(r'\b\d{6}\b', body)
                                if code:
                                    print(f"{datetime.now()} - 인증 코드 감지됨: {code.group()}")
                                    return code.group()
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode()
                        code = re.search(r'\b\d{6}\b', body)
                        if code:
                            print(f"{datetime.now()} - 인증 코드 감지됨: {code.group()}")
                            return code.group()
            except Exception as e:
                print(f"{datetime.now()} - 이메일 파싱 중 오류: {e}")

        else:
            print(f"{datetime.now()} - 아직 인증 메일이 도착하지 않았습니다.")
        time.sleep(1)

    print(f"{datetime.now()} - 30초 내 인증 코드 수신 실패")
    return None

try:
    print(f"{datetime.now()} - Cloudtype 서비스 페이지 접속 중...")
    driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
    time.sleep(3)

    wait = WebDriverWait(driver, 20)
    print(f"{datetime.now()} - 로그인 버튼 찾는 중...")
    element = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//*[contains(text(), 'Continue with GitHub') or contains(text(), 'GitHub 계정으로 로그인')]"
    )))
    print(f"{datetime.now()} - 로그인 버튼 텍스트: '{element.text}'")
    element.click()

    print(f"{datetime.now()} - GitHub 로그인 창으로 전환 중...")
    driver.switch_to.window(driver.window_handles[-1])
    print(f"{datetime.now()} - GitHub 로그인 시도 중...")

    try:
        login_field = driver.find_element(By.ID, "login_field")
        print(f"{datetime.now()} - ✅ login_field 요소 찾음")
        login_field.send_keys(USER_ID)
    except Exception as e:
        print(f"{datetime.now()} - ❌ login_field 요소를 찾지 못함: {e}")
        driver.quit()
        exit()

    try:
        password_field = driver.find_element(By.ID, "password")
        print(f"{datetime.now()} - ✅ password 요소 찾음")
        password_field.send_keys(USER_PW)
    except Exception as e:
        print(f"{datetime.now()} - ❌ password 요소를 찾지 못함: {e}")
        driver.quit()
        exit()

    try:
        commit_button = driver.find_element(By.NAME, "commit")
        print(f"{datetime.now()} - ✅ 로그인 버튼(commit) 찾음")
        commit_button.click()
    except Exception as e:
        print(f"{datetime.now()} - ❌ 로그인 버튼(commit) 찾지 못함: {e}")
        driver.quit()
        exit()

    time.sleep(3)

    current_url = driver.current_url
    if "github.com/session" in current_url or "github.com/login" in current_url:
        print(f"{datetime.now()} - ❌ 로그인 실패 또는 인증 미완료. 현재 URL: {current_url}")
        driver.quit()
        exit()

    if "sessions/verified-device" in current_url:
        print(f"{datetime.now()} - 📧 GitHub 기기 인증 필요: 이메일에서 코드 입력 중...")
        code = get_github_verification_code()
        if code:
            print(f"{datetime.now()} - 🔐 인증 코드 수신: {code}")
            driver.find_element(By.ID, "otp").send_keys(code)
            driver.find_element(By.XPATH, "//button[contains(text(), 'Verify') or contains(text(), '확인')]").click()
            print(f"{datetime.now()} - ✅ 인증 코드 제출 완료")
        else:
            print(f"{datetime.now()} - ❌ 인증 코드 수신 실패: 종료")
            driver.quit()
            exit()

    print(f"{datetime.now()} - Cloudtype 서비스 상태 확인 중...")
    driver.switch_to.window(driver.window_handles[-1])
    elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")

    if not elements:
        print(f"{datetime.now()} - 'bi-play-fill' 요소를 찾지 못했습니다.")
        print(driver.current_url)
    else:
        print(f"{datetime.now()} - 총 {len(elements)}개의 'bi-play-fill' 요소를 찾았습니다.")

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
