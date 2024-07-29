from ncclient import manager
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from netconf_utils import  send_rpc
from read_file import process_file
from custom_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


# 文件传输命令，使用临时 channel
file_transfer_rpc = """
<CLI xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <Configuration exec-use-channel="false">
    quit
    tftp 192.168.36.2 get S5130S_EI-CMW710-R6357.ipe 
    tftp 192.168.36.2 get s5130s_ei-cmw710-freeradius-r6357.bin 
    tftp 192.168.36.2 get s5130s_ei-cmw710-grpcpkg-r6357.bin
  </Configuration>
</CLI>
"""
def main(device_info):

    name, host, port, username, password = device_info

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
    devices_info = process_file('devices.csv')
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(main, device_info) for device_info in devices_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")