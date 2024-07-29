from read_file import process_file
import telnetlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from custom_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
def configure_netconf_via_telnet(name, host, username, password):
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
        logger.info(f"{name} ({host})执行命令: {command}")
        tn.write(command.encode('ascii') + b"\n")

        if command == 'netconf ssh server enable':
            logger.debug("等待命令执行完成...")
            time.sleep(20)  # 等待20秒以确保命令执行完成

        time.sleep(1)
        output = tn.read_very_eager().decode('ascii')
        logger.debug(f"{name} ({host})命令输出: {output}")

        if "% Unrecognized command found at '^' position." in output:
            logger.error(f"{name} ({host})命令执行失败: {command}")
            break

    tn.close()
    logger.info(f"{name} ({host})Telnet 配置 NETCONF 完成.")


def main(device_info):
    name, host, port, username, password = device_info
    #配置 NETCONF
    configure_netconf_via_telnet(name, host, username, password)

if __name__ == '__main__':
    devices_info = process_file('devices.csv')
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(main, device_info) for device_info in devices_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")
