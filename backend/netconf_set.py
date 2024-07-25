from read_file import process_file
import telnetlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
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


def main(device_info):
    name, host, port, username, password = device_info
    #配置 NETCONF
    configure_netconf_via_telnet(host, username, password)

if __name__ == '__main__':
    devices_info = process_file('devices.csv')
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(main, device_info) for device_info in devices_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")
