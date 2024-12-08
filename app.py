from flask import Flask, request, jsonify
from search import process_url  # search.py의 process_url 함수 사용
import os

app = Flask(__name__)


# Google Cloud 인증 설정
def setup_google_credentials():
    credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if credentials_json:
        with open("keyfile.json", "w") as f:
            f.write(credentials_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keyfile.json"


setup_google_credentials()


@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.json
        url = data.get("url")
        userid = data.get("userid", "default_user")

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # URL 처리
        print(f"Processing URL: {url}")
        result = process_url(url)

        if result:
            return jsonify(
                {
                    "summary": result["summary"],
                    "title": result["title"],
                    "userid": userid,
                }
            )
        else:
            return jsonify({"error": "Failed to process the URL"}), 500
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
