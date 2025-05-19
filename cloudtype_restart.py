import imaplib, email, re, os, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from datetime import datetime

def log(msg): print(f"{datetime.now()} - {msg}")

log("스크립트 시작됨")
load_dotenv()

USER_ID = os.getenv("CLOUDTYPE_ID")
USER_PW = os.getenv("CLOUDTYPE_PW")
EMAIL = os.getenv("EMAIL_ADDRESS")
EMAIL_PW = os.getenv("EMAIL_PASSWORD")

# Chrome 설정
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless")  # 디버깅 시 주석 처리

log("Chrome 드라이버 초기화 중...")
driver = webdriver.Chrome(options=chrome_options)

def get_github_verification_code():
    log("인증코드 수신 대기 중...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, EMAIL_PW)
    mail.select("inbox")

    for _ in range(30):
        result, data = mail.search(None, '(FROM "noreply@github.com")')
        ids = data[0].split()
        if ids:
            latest_id = ids[-1]
            result, msg_data = mail.fetch(latest_id, "(RFC822)")
            if not msg_data or not msg_data[0]: time.sleep(1); continue

            try:
                raw = msg_data[0][1]
                if not raw: time.sleep(1); continue
                msg = email.message_from_bytes(raw)
                body = None

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            body = payload.decode() if payload else None
                            break
                else:
                    payload = msg.get_payload(decode=True)
                    body = payload.decode() if payload else None

                if body:
                    code = re.search(r'\b\d{6}\b', body)
                    if code:
                        log(f"인증 코드 감지됨: {code.group()}")
                        return code.group()
            except Exception as e:
                log(f"이메일 파싱 중 오류: {e}")
        else:
            log("아직 인증 메일이 도착하지 않았습니다.")
        time.sleep(1)

    log("30초 내 인증 코드 수신 실패")
    return None

try:
    log("Cloudtype 서비스 페이지 접속 중...")
    driver.get("https://app.cloudtype.io/@unclebob/unclebob:main")
    time.sleep(3)

    wait = WebDriverWait(driver, 20)
    log("로그인 버튼 찾는 중...")
    element = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//*[contains(text(), 'Continue with GitHub') or contains(text(), 'GitHub 계정으로 로그인')]"
    )))
    log(f"로그인 버튼 텍스트: '{element.text}'")
    element.click()

    log("GitHub 로그인 창으로 전환 중...")
    driver.switch_to.window(driver.window_handles[-1])
    log("GitHub 로그인 시도 중...")

    # 로그인 필드 입력
    driver.find_element(By.ID, "login_field").send_keys(USER_ID)
    log("✅ login_field 요소 찾음")

    driver.find_element(By.ID, "password").send_keys(USER_PW)
    log("✅ password 요소 찾음")

    driver.find_element(By.NAME, "commit").click()
    log("✅ 로그인 버튼(commit) 클릭 완료")
    time.sleep(3)

    # 디버깅용 현재 상태 저장
    driver.save_screenshot("login_failed.png")
    with open("login_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    current_url = driver.current_url
    log(f"로그인 후 현재 URL: {current_url}")

    if "github.com/session" in current_url or "github.com/login" in current_url:
        log("❌ 로그인 실패 또는 인증 미완료")
        try:
            error_box = driver.find_element(By.CLASS_NAME, "flash-error")
            log(f"🔍 에러 메시지: {error_box.text.strip()}")
        except:
            log("⚠️ 에러 메시지를 찾지 못함")
        driver.quit()
        exit()

    if "sessions/verified-device" in current_url:
        log("📧 GitHub 기기 인증 필요: 이메일에서 코드 입력 중...")
        code = get_github_verification_code()
        if code:
            log(f"🔐 인증 코드 수신: {code}")
            driver.find_element(By.ID, "otp").send_keys(code)
            driver.find_element(By.XPATH, "//button[contains(text(), 'Verify') or contains(text(), '확인')]").click()
            log("✅ 인증 코드 제출 완료")
        else:
            log("❌ 인증 코드 수신 실패: 종료")
            driver.quit()
            exit()

    log("Cloudtype 서비스 상태 확인 중...")
    driver.switch_to.window(driver.window_handles[-1])
    elements = driver.find_elements(By.CLASS_NAME, "bi-play-fill")

    if not elements:
        log("'bi-play-fill' 요소를 찾지 못했습니다.")
        log(driver.current_url)
    else:
        log(f"총 {len(elements)}개의 'bi-play-fill' 요소를 찾았습니다.")

    found = False
    for element in elements:
        class_attr = element.get_attribute("class")
        if "text-muted" not in class_attr:
            log("❗서비스가 중단되어 재시작합니다.")
            parent = element.find_element(By.XPATH, "..")
            if "duration-300" in parent.get_attribute("class"):
                parent.click()
                log("🔁 재시작 클릭 완료")
                time.sleep(2)
                found = True
                break

    if not found:
        log("✅ 서비스는 실행 중입니다.")

except Exception as e:
    log(f"❌ 오류 발생: {e}")

finally:
    driver.quit()
    log("스크립트 종료됨")
