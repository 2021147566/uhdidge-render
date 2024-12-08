from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Google Apps Script URL
APPS_SCRIPT_URL = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"


@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.json
        url = data.get("url")
        userid = data.get("userid", "default_user")

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Google Apps Script로 데이터 전송
        payload = {
            "action": "saveData",  # Apps Script에서 처리할 액션 이름
            "userid": userid,
            "url": url,
        }

        response = requests.post(APPS_SCRIPT_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return jsonify({"message": "Data saved successfully", "userid": userid})
            else:
                return jsonify({"error": "Failed to save data in Apps Script"}), 500
        else:
            return jsonify({"error": f"Apps Script error: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
