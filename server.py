from flask import Flask, request, jsonify, send_from_directory, send_file
import json
import os
import zipfile
import io
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

@app.route("/files", methods=["GET"])
def list_uploaded_files():
    files = os.listdir(SAVE_DIR)
    return jsonify(sorted(files))

@app.route("/files/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(SAVE_DIR, filename, as_attachment=True)

@app.route("/files.zip", methods=["GET"])
def download_all_as_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for filename in os.listdir(SAVE_DIR):
            if filename.endswith(".json") and not filename.startswith("."):
                zipf.write(os.path.join(SAVE_DIR, filename), arcname=filename)
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="uploaded_jsons.zip"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)

@app.route("/files.zip", methods=["GET"])
def download_all_as_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        for fname in os.listdir(SAVE_DIR):
            if fname.endswith(".json") and not fname.startswith("."):
                z.write(os.path.join(SAVE_DIR, fname), arcname=fname)
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="uploaded_jsons.zip")
