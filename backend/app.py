import os
from flask import Flask, request, jsonify
import subprocess
import logging
import sys
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
process = None  # 用于跟踪当前运行的进程
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 设置日志
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/run_script', methods=['POST'])
def run_script():
    global process
    if process is not None:
        return jsonify({"error": "已经有一个脚本在运行"}), 400
    script = request.json.get('script')
    python_interpreter = sys.executable

    try:
        if script == 'check_version':
            process = subprocess.Popen([python_interpreter, 'check_version.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        elif script == 'upgrade_device':
            process = subprocess.Popen([python_interpreter, 'upgrade_device_new.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        else:
            return jsonify({"error": "错误的脚本名称"}), 400

        socketio.start_background_task(target=stream_output, process=process)
        return jsonify({"message": "脚本启动成功"})
    except Exception as e:
        process = None
        return jsonify({"错误": str(e)}), 500

def background_emit(event, data):
    with app.app_context():
        socketio.emit(event, data)

def stream_output(process):
    for line in process.stdout:
        socketio.start_background_task(background_emit, '脚本输出', {'output': line})
    process.stdout.close()
    process.wait()
    socketio.start_background_task(background_emit, '脚本输出', {'output': '运行完毕'})

@app.route('/stop_script', methods=['POST'])
def stop_script():
    global process  # 声明为全局变量
    if process:
        process.terminate()  # 终止进程
        process.wait()
        process = None
        return jsonify({"message": "脚本已停止"}), 200
    else:
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
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

