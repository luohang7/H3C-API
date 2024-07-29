import os
from ncclient import manager
from ncclient.xml_ import to_ele
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from netconf_utils import send_rpc
from read_file import process_file
from dotenv import load_dotenv
from custom_logging import setup_logging

# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
setup_logging(log_file='check_version.log')

logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 获取当前版本信息的 RPC
get_version_rpc = """
<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <filter>
    <Package xmlns="http://www.h3c.com/netconf/data:1.0">
      <BootLoaderList/>
    </Package>
  </filter>
</get>
"""

def check_version(m, name, host):
    response = send_rpc(m, get_version_rpc, "获取版本信息")
    if response:
        root = to_ele(response.xml)
        namespaces = {'h3c': 'http://www.h3c.com/netconf/data:1.0'}
        version_elements = root.xpath('//h3c:BootList[h3c:BootType="0"]/h3c:ImageFiles/h3c:FileName', namespaces=namespaces)
        if version_elements:
            current_version_files = [elem.text for elem in version_elements]
            logger.debug(f"{name} ({host})当前设备版本文件: {current_version_files}")
            return current_version_files
    return None


def main(device_info):
    name, host, port, username, password = device_info

    target_version = os.getenv("TARGET_VERSION")
    if target_version:
        target_version = target_version.split(',')

    # 连接设备并检查版本
    with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
    ) as m:

        current_version_files = check_version(m, name, host)

        if current_version_files:
            if not all(file in current_version_files for file in target_version):
                logger.info(f"{name} ({host})需要升级")
            else:
                logger.info(f"{name} ({host})不需要升级")
        else:
            logger.error(f"{name} ({host})无法获取当前版本信息")

if __name__ == '__main__':
    devices_info = process_file('devices.csv')
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(main, device_info) for device_info in devices_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")