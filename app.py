from flask import Flask, request, jsonify
from search import process_url
import requests

app = Flask(__name__)

# Google Apps Script URL
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzPNJCPkth5upiQO0WSzW1jlD3berUEAQXLX6UWdjnwfoGViP5K5RcooGNmCMijXCIZ/exec"

@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.json
        url = data.get("url")
        userid = data.get("userid", "default_user")

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # URL 처리 (요약 및 제목 생성)
        result = process_url(url)
        if not result:
            return jsonify({"error": "Failed to process the URL"}), 500

        summary = result["summary"]
        title = result["title"]

        # Google Apps Script로 데이터 전송
        payload = {
            "action": "saveData",
            "userid": userid,
            "url": url,
            "summary": summary,
            "title": title,
        }

        response = requests.post(APPS_SCRIPT_URL, json=payload)
        if response.status_code == 200:
            script_result = response.json()
            if script_result.get("success"):
                return jsonify({"message": "Data saved successfully", "userid": userid, "summary": summary, "title": title})
            else:
                return jsonify({"error": "Failed to save data in Apps Script"}), 500
        else:
            return jsonify({"error": f"Apps Script error: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
