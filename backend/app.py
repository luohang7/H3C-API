import os
from flask import Flask, request, jsonify, send_file, send_from_directory
import subprocess
import logging
import sys
from flask_socketio import SocketIO
from flask_cors import CORS
from queue import Queue
from threading import Thread

app = Flask(__name__, static_folder='dist')
process = None  # 用于跟踪当前运行的进程
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 设置日志
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class ScriptManager:
    def __init__(self):
        self.process = None
        self.log_queue = Queue()

    def start_process(self, script_name, args=[]):
        python_interpreter = sys.executable
        script_mapping = {
            'check_version': 'check_version.py',
            'upgrade_device': 'upgrade_device_new.py',
            'netconf_set': 'netconf_set.py',
            'file_transfer': 'file_transfer.py',
        }
        script_file = script_mapping.get(script_name)
        if not script_file:
            raise ValueError("错误的脚本名称")
        self.process = subprocess.Popen(
            [python_interpreter, '-u', script_file] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8'
        )
        return self.process

    def enqueue_output(self, proc):
        for line in iter(proc.stdout.readline, ''):
            self.log_queue.put(('stdout', line))
        for line in iter(proc.stderr.readline, ''):
            self.log_queue.put(('stderr', line))
        proc.stdout.close()
        proc.stderr.close()
        self.log_queue.put(('done', ''))  # 添加一个特殊标志，指示脚本已完成

    def stream_output(self):
        while True:
            source, line = self.log_queue.get()
            if source == 'stdout':
                logging.info(f"脚本输出: {line.strip()}")
                socketio.emit('脚本输出', {'output': line.strip()})
            elif source == 'stderr':
                logging.error(f"脚本错误输出: {line.strip()}")
                socketio.emit('脚本输出', {'output': line.strip()})
            elif source == 'done':  # 处理特殊标志
                logging.info("脚本运行完毕")
                socketio.emit('脚本输出', {'output': '运行完毕'})
                break  # 退出循环
            sys.stdout.flush()
            sys.stderr.flush()
            self.log_queue.task_done()


    def terminate_process(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            logging.info("脚本已终止")

script_manager = ScriptManager()

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/run_script', methods=['POST'])
def run_script():
    global process  # 声明为全局变量
    script = request.json.get('script')
    tftp_server = request.json.get('tftpServer')
    file_list = request.json.get('fileList')
    target_version = request.json.get('targetVersion')

    try:
        args = []
        if script == 'file_transfer':
            args = [tftp_server] + file_list.split(',')
        elif script == 'check_version':
            args = [target_version]

        process = script_manager.start_process(script, args)
        logging.info(f"启动脚本: {script}")

        # 启动新线程来处理进程的输出
        Thread(target=script_manager.enqueue_output, args=(process,)).start()

        socketio.start_background_task(target=script_manager.stream_output)
        return jsonify({"message": "脚本启动成功"})
    except Exception as e:
        return jsonify({"错误": str(e)}), 500

@app.route('/stop_script', methods=['POST'])
def stop_script():
    global process  # 声明为全局变量
    try:
        if process:
            script_manager.terminate_process()
            process = None  # 确保全局变量 process 被重置
            return jsonify({"message": "脚本已停止"}), 200
        else:
            return jsonify({"error": "脚本未运行"}), 400
    except Exception as e:
        return jsonify({"错误": str(e)}), 500

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

# 添加用于下载 CSV 文件的端点
@app.route('/download_csv', methods=['GET'])
def download_csv():
    try:
        return send_file('uploads/devices_upgrade.csv', as_attachment=True)
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
