from ncclient import manager
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from netconf_utils import  send_rpc
from read_file import process_file
from custom_logging import setup_logging
import sys

setup_logging()
logger = logging.getLogger(__name__)

def generate_file_transfer_rpc(tftp_server, file_list):
    commands = [f"tftp {tftp_server} get {file.strip()}" for file in file_list]
    command_string = "\n    ".join(commands)
    return f"""
<CLI xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <Configuration exec-use-channel="false">
    quit
    {command_string}
  </Configuration>
</CLI>
"""

def main(device_info, tftp_server, file_list):

    name, host, port, username, password = device_info

    file_transfer_rpc = generate_file_transfer_rpc(tftp_server, file_list)

    with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
            timeout=600  # 设置更长的超时时间
    ) as m:
        logger.info(f"{name} ({host})发送tftp获取文件命令...")
        send_rpc(m, file_transfer_rpc, "file transfer")

if __name__ == '__main__':
    tftp_server = sys.argv[1]
    file_list = sys.argv[2:]
    devices_info = process_file('devices_upgrade.csv')
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(main, device_info, tftp_server, file_list) for device_info in devices_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")

    # 保存文件名到临时文件
    ipe_files = [file for file in file_list if file.endswith('.ipe')]
    bin_files = [file for file in file_list if file.endswith('.bin')]

    with open('temp_files.txt', 'w') as temp_file:
        if ipe_files:
            temp_file.write(f"ipe_file={ipe_files[0]}\n")
        for bin_file in bin_files:
            temp_file.write(f"bin_file={bin_file}\n")