import google.generativeai as genai
import os
import vertexai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from newspaper import Article
import time

# Google Cloud 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keyfile.json"
location = "asia-northeast3"
project_id = "uhdidge"
vertexai.init(project=project_id, location=location)

# Vertex AI 모델 초기화
model = genai.GenerativeModel("gemini-pro")


# Google Cloud 인증 설정
def setup_google_credentials():
    credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if credentials_json:
        with open("keyfile.json", "w") as f:
            f.write(credentials_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keyfile.json"


setup_google_credentials()


# URL에서 주요 본문 텍스트 추출 (newspaper3k + Selenium)
def fetch_main_content(url):
    try:
        # 1. Newspaper3k 사용
        article = Article(url)
        article.download()
        article.parse()
        if article.text.strip():
            return article.text
        else:
            raise Exception("No content extracted with Newspaper3k.")
    except Exception as e:
        print(f"Error extracting content with Newspaper3k: {e}")
        print("Falling back to Selenium for content extraction.")
        return fetch_content_with_selenium(url)


# Selenium을 사용한 동적 콘텐츠 추출
def fetch_content_with_selenium(url):
    try:
        # Render 환경에 맞게 Chromedriver 설치
        os.system("apt-get update && apt-get install -y chromium-driver")

        # Selenium Chrome 옵션 설정
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )

        service = Service("/usr/bin/chromedriver")  # Render 환경의 Chromedriver 경로
        driver = webdriver.Chrome(service=service, options=options)

        # URL 접속 및 대기
        driver.get(url)
        time.sleep(3)

        # 동적 콘텐츠 추출
        try:
            content = driver.find_element(
                By.XPATH, "//meta[@property='og:description']"
            ).get_attribute("content")
        except Exception:
            content = driver.find_element(By.TAG_NAME, "body").text

        driver.quit()
        return content if content.strip() else "본문 텍스트를 찾을 수 없습니다."
    except Exception as e:
        return f"Error extracting content with Selenium: {e}"


# Vertex AI를 사용한 텍스트 생성 함수
def generate_text(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Error generating text with Vertex AI: {e}")


# 요약 생성 함수
def summarize_content(content):
    prompt = f"""
    아래 내용을 간단히 요약해 주세요:
    {content}
    """
    return generate_text(prompt)


# 제목 생성 함수
def generate_title(content):
    prompt = f"""
    아래 내용을 바탕으로 기억하기 쉬운 제목을 생성해 주세요:
    {content}
    """
    return generate_text(prompt)


# 전체 프로세스
def process_url(url):
    try:
        print(f"Fetching main content from URL: {url}")
        content = fetch_main_content(url)

        print("Generating summary...")
        summary = summarize_content(content[:3000])  # Vertex AI 입력 길이 제한 적용

        print("Generating title...")
        title = generate_title(content[:3000])

        return {"summary": summary, "title": title}
    except Exception as e:
        print(f"Error processing URL: {e}")
        return None
