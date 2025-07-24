from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Directory to save the uploaded JSON files
SAVE_DIR = "uploaded_jsons"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.get_json()
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        file_path = os.path.join(SAVE_DIR, f"{timestamp}.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "success", "file": file_path}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)