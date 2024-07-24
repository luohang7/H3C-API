from ncclient import manager
from ncclient.xml_ import to_ele
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import telnetlib
import time

# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("check_version.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 读取配置文件
config = pd.read_csv('devices.csv')

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

def configure_netconf_via_telnet(host, username, password):
    logger.info("开始 Telnet 连接以配置 NETCONF...")
    tn = telnetlib.Telnet(host)

    tn.read_until(b"Login:", timeout=10)
    tn.write(username.encode('ascii') + b"\n")
    tn.read_until(b"Password:", timeout=10)
    tn.write(password.encode('ascii') + b"\n")

    # 添加延迟，确保登录完成
    time.sleep(2)

    commands = [
        'system',
        'netconf ssh server enable',
        'local-user lpssy',
        'service-type terminal telnet ssh'
    ]

    for command in commands:
        logger.info(f"执行命令: {command}")
        tn.write(command.encode('ascii') + b"\n")

        if command == 'netconf ssh server enable':
            logger.info("等待命令执行完成...")
            time.sleep(20)  # 等待10秒以确保命令执行完成

        time.sleep(1)
        output = tn.read_very_eager().decode('ascii')
        logger.info(f"命令输出: {output}")

        if "% Unrecognized command found at '^' position." in output:
            logger.error(f"命令执行失败: {command}")
            break

    tn.close()
    logger.info("Telnet 配置 NETCONF 完成.")

def send_rpc(m, rpc, description):
    try:
        response = m.dispatch(to_ele(rpc))
        logger.info(f"{description} RPC 回复: {response.xml}")
        return response
    except Exception as e:
        logger.info(f"{description} 操作期间出错: {e}")
        return None

def check_version(m):
    logger.info("获取当前设备版本信息...")
    response = send_rpc(m, get_version_rpc, "获取版本信息")
    if response:
        root = to_ele(response.xml)
        namespaces = {'h3c': 'http://www.h3c.com/netconf/data:1.0'}
        version_elements = root.xpath('//h3c:BootList[h3c:BootType="0"]/h3c:ImageFiles/h3c:FileName', namespaces=namespaces)
        if version_elements:
            current_version_files = [elem.text for elem in version_elements]
            logger.info(f"当前设备版本文件: {current_version_files}")
            return current_version_files
    return None


def test(row):

    name = row['name']
    host = row['host']
    port = int(row['port'])
    username = row['username']
    password = row['password']

    logger.info(f"处理设备: {name} ({host})")

    target_version = [
        'flash:/s5130s_ei-cmw710-boot-r6357.bin',
        'flash:/s5130s_ei-cmw710-system-r6357.bin',
        'flash:/s5130s_ei-cmw710-freeradius-r6357.bin',
        'flash:/s5130s_ei-cmw710-grpcpkg-r6357.bin'
    ]

    # 配置 NETCONF
    'configure_netconf_via_telnet(host, username, password)'

    # 连接设备并检查版本
    with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
    ) as m:
        logger.info(f"This session id is {m.session_id}.")

        current_version_files = check_version(m)

        if current_version_files:
            if not all(file in current_version_files for file in target_version):
                logger.info(f"当前版本不匹配:{name} ({host})需要升级。")
            else:
                logger.info("当前版本已是最新，不需要升级。")
        else:
            logger.error("无法获取当前版本信息，检查失败。")


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(test, row) for idx, row in config.iterrows()]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")