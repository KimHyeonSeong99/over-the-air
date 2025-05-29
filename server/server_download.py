from flask import Flask, request, send_file
import os
import zipfile  # 추가된 모듈

app = Flask(__name__)

@app.route("/get_update", methods=["GET"])
def get_update():
    update_file_name = request.args.get("filename")
    
    # Check for missing parameters
    if not update_file_name:
        return "Missing required parameters", 400

    # Ensure paths are sanitized
    update_file_name = os.path.basename(update_file_name)

    os.makedirs(f"./updates", exist_ok=True)
    with open(f"./updates/{update_file_name}", "wb") as f:
        with open(f"firmware/{update_file_name}", "rb") as original_file:
            f.write(original_file.read())
    file_path = f"./updates/{update_file_name}"
    zip_path = f"./updates/update_package.zip"

    try:
        # ZIP 파일 생성
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(file_path, arcname=f"{update_file_name}")

        # ZIP 파일 전송
        return send_file(zip_path, as_attachment=True)
    except FileNotFoundError:
        # 파일이 없으면 404 응답
        return "Update file not found", 404
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
