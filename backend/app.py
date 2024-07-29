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
            process = subprocess.Popen([python_interpreter, '-u', 'check_version.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True, encoding='utf-8')
        elif script == 'upgrade_device':
            process = subprocess.Popen([python_interpreter, '-u', 'upgrade_device_new.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True, encoding='utf-8')
        else:
            return jsonify({"error": "错误的脚本名称"}), 400
        logging.info("启动脚本: " + script)  # 添加日志
        socketio.start_background_task(target=stream_output, proc=process)
        return jsonify({"message": "脚本启动成功"})
    except Exception as e:
        process = None
        return jsonify({"错误": str(e)}), 500

def background_emit(event, data):
    with app.app_context():
        socketio.emit(event, data)

def stream_output(proc):
    global process
    logging.info("开始读取脚本输出")  # 确保流输出开始
    while True:
        stdout_line = proc.stdout.readline()
        stderr_line = proc.stderr.readline()

        if stdout_line:
            logging.info(f"脚本输出: {stdout_line.strip()}")  # 确保在服务器端也能看到输出
            socketio.emit('脚本输出', {'output': stdout_line.strip()})
            sys.stdout.flush()  # 确保日志立即刷新

        if stderr_line:
            logging.error(f"脚本错误输出: {stderr_line.strip()}")  # 确保在服务器端也能看到错误输出
            socketio.emit('脚本输出', {'output': stderr_line.strip()})
            sys.stdout.flush()  # 确保日志立即刷新

        if not stdout_line and not stderr_line:
            logging.info("未读取到新行")
            break

    proc.stdout.close()
    proc.stderr.close()
    proc.wait()
    logging.info("脚本运行完毕")  # 添加日志
    socketio.emit('脚本输出', {'output': '运行完毕'})
    process = None  # 脚本运行结束后重置 process

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

