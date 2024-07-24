import os
from flask import Flask, request, jsonify
import subprocess
import logging
import sys

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/run_script', methods=['POST'])
def run_script():
    script = request.json.get('script')
    app.logger.debug(f'Received script request: {script}')

    python_interpreter = sys.executable
    app.logger.debug(f'Using Python interpreter: {python_interpreter}')

    try:
        if script == 'check_version':
            result = subprocess.run([python_interpreter, 'check_version.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        elif script == 'upgrade_device':
            result = subprocess.run([python_interpreter, 'upgrade_device_new.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        elif script == 'extract_device_ip':
            result = subprocess.run([python_interpreter, 'extract_device_ip.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        else:
            return jsonify({"error": "Invalid script name"}), 400

        app.logger.debug(f'Script output: {result.stdout}')
        app.logger.debug(f'Script error: {result.stderr}')

        return jsonify({"output": result.stdout, "error": result.stderr})
    except Exception as e:
        app.logger.error(f'Error running script: {e}')
        return jsonify({"error": str(e)}), 500


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = os.path.join('uploads', file.filename)
        file.save(filename)

        return jsonify({"message": "File uploaded successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)

