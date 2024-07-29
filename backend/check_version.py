from ncclient import manager
from ncclient.xml_ import to_ele
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from netconf_utils import send_rpc
from read_file import process_file
from custom_logging import setup_logging
import sys

# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
setup_logging(log_file='check_version.log')

logger = logging.getLogger(__name__)

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

def extract_version(file_name):
    """提取文件名中的版本号，忽略大小写"""
    version = file_name.lower().replace('boot', '').replace('system', '').strip('-._ ')
    return version

def check_version(m, name, host, target_version):
    response = send_rpc(m, get_version_rpc, "获取版本信息")
    if response:
        root = to_ele(response.xml)
        namespaces = {'h3c': 'http://www.h3c.com/netconf/data:1.0'}
        version_elements = root.xpath('//h3c:BootList[h3c:BootType="0"]/h3c:ImageFiles/h3c:FileName', namespaces=namespaces)
        if version_elements:
            all_version_files = [elem.text for elem in version_elements]
            current_version_files = [file for file in all_version_files if
                                     'boot' in file.lower() or 'system' in file.lower()]
            current_versions = {extract_version(file) for file in current_version_files}

            # 记录当前设备版本文件列表
            logger.info(f"{name} ({host})当前设备版本文件: {all_version_files}")

            # 比较当前版本与目标版本
            target_version = target_version.lower()
            need_upgrade = False
            for current_version in current_versions:
                if current_version.split('-r')[-1] < target_version.split('-r')[-1]:
                    need_upgrade = True
                    break

            if need_upgrade:
                logger.info(f"{name} ({host})需要升级")
            else:
                logger.info(f"{name} ({host})不需要升级")
        else:
            logger.error(f"{name} ({host})无法获取当前版本信息")

def main(device_info, target_version):
    name, host, port, username, password = device_info

    # 连接设备并检查版本
    with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
    ) as m:

        check_version(m, name, host, target_version)

if __name__ == '__main__':
    devices_info = process_file('devices.csv')
    target_version = sys.argv[1]  # 从命令行参数中获取目标版本
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(main, device_info, target_version) for device_info in devices_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")