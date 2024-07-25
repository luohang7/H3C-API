import os
from flask import Flask, request, jsonify
import subprocess
import logging
import sys
from flask_socketio import SocketIO, emit

app = Flask(__name__)
process = None  # 用于跟踪当前运行的进程

# 设置日志
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/run_script', methods=['POST'])
def run_script():
    global process
    script = request.json.get('script')
    app.logger.debug(f'Received script request: {script}')
    python_interpreter = sys.executable
    app.logger.debug(f'Using Python interpreter: {python_interpreter}')
    try:
        if script == 'check_version':
            process = subprocess.Popen([python_interpreter, 'check_version.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        elif script == 'upgrade_device':
            process = subprocess.Popen([python_interpreter, 'upgrade_device_new.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        else:
            return jsonify({"error": "错误的脚本名称"}), 400

        app.logger.info(f'Started script with PID: {process.pid}')
        stdout, stderr = process.communicate()
        process = None
        return jsonify({"output": stdout, "error": stderr})
    except Exception as e:
        app.logger.error(f'Error running script: {e}')
        process = None
        return jsonify({"错误": str(e)}), 500

@app.route('/stop_script', methods=['POST'])
def stop_script():
    global process  # 声明为全局变量
    app.logger.info('Received stop script request')
    if process:
        app.logger.info('Stopping the script...')
        process.terminate()  # 终止进程
        process.wait()
        process = None
        app.logger.info('Script stopped successfully')
        return jsonify({"message": "脚本已停止"}), 200
    else:
        app.logger.error('No script is running')
        return jsonify({"error": "脚本未运行"}), 400

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "未找到文件部分"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    if file:
        filename = os.path.join('uploads', file.filename)
        file.save(filename)

        return jsonify({"message": "文件上传成功"}), 200


if __name__ == '__main__':
    app.run(debug=True)

