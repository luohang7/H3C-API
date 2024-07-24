from ncclient import manager
import logging
import telnetlib
import time
import pandas as pd
import sys
from ncclient.operations.errors import TimeoutExpiredError
from concurrent.futures import ThreadPoolExecutor, as_completed
from netconf_utils import send_rpc

# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 读取配置文件
config = pd.read_csv('devices.csv')

# 固件升级的 RPC
firmware_upgrade_rpc = """
<action xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <top xmlns="http://www.h3c.com/netconf/action:1.0">
    <Package>
      <SetBootImage>
        <DeviceNode>
          <Chassis>0</Chassis>
          <Slot>1</Slot>
          <CPUID>0</CPUID>
        </DeviceNode>
        <IPEFileName>flash:/S5130S_EI-CMW710-R6357.ipe</IPEFileName>
        <Type>1</Type>
        <OverwriteLocalFile>true</OverwriteLocalFile>
        <DeleteIPEFile>true</DeleteIPEFile>
      </SetBootImage>
    </Package>
  </top>
</action>
"""

# 保存配置的 RPC
save_config_rpc = """
<save xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <file>startup.cfg</file>
</save>
"""

# 重启设备的 RPC
reboot_rpc = """
<CLI xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <Configuration exec-use-channel="false">
    quit
    reboot force 
  </Configuration>
</CLI>
"""

# 删除旧文件的 RPC
delete_system_rpc = """
<action xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <top xmlns="http://www.h3c.com/netconf/action:1.0">
    <FileSystem>
      <Files>
        <File>
          <SrcName>flash:/s5130s_ei-cmw710-system-r6343p08.bin</SrcName>
          <Operations>
            <UnReservedDelete/>
          </Operations>
        </File>
      </Files>
    </FileSystem>
  </top>
</action>
"""

delete_boot_rpc = """
<action xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <top xmlns="http://www.h3c.com/netconf/action:1.0">
    <FileSystem>
      <Files>
        <File>
          <SrcName>flash:/s5130s_ei-cmw710-boot-r6343p08.bin</SrcName>
          <Operations>
            <UnReservedDelete/>
          </Operations>
        </File>
      </Files>
    </FileSystem>
  </top>
</action>
"""

# 安装特性包的 RPC
install_feature_rpc = """
<action xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <top xmlns="http://www.h3c.com/netconf/action:1.0">
    <Package>
      <InstallImage>
        <Action>1</Action>
        <ImageFiles>
          <Feature>flash:/s5130s_ei-cmw710-freeradius-r6357.bin</Feature>
          <Feature>flash:/s5130s_ei-cmw710-grpcpkg-r6357.bin</Feature>
        </ImageFiles>
        <OverwriteLocalFile>true</OverwriteLocalFile>
      </InstallImage>
    </Package>
  </top>
</action>
"""

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
def reconnect(host, port, username, password, max_retries=3, wait_time=60):
    for attempt in range(max_retries):
        logger.info(f"尝试重新连接... 尝试次数 {attempt + 1}")
        try:
            m = manager.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                hostkey_verify=False
            )
            logger.info("重新连接成功.")
            return m
        except Exception as e:
            logger.error(f"重新连接失败: {e}")
            for remaining in range(wait_time, 0, -1):
                logger.info(f"等待 {remaining} 秒后再尝试重新连接...")
                time.sleep(1)
    raise Exception("无法重新连接到设备.")


# Telnet 连接并配置 NETCONF
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

def process_device(row):
    name = row['name']
    host = row['host']
    port = int(row['port'])
    username = row['username']
    password = row['password']

    try:
        # 连接设备并执行文件传输命令
        with manager.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                hostkey_verify=False,
                timeout=600  # 设置更长的超时时间
        ) as m:

            if current_version_files:
                if set(target_version) != set(current_version_files):
                    logger.info("当前版本不匹配，需要升级。")


    
                    logger.info("发送固件升级命令...")
                    send_rpc(m, firmware_upgrade_rpc, "固件升级")
    
                    logger.info("发送保存配置命令...")
                    send_rpc(m, save_config_rpc, "保存配置")

                    logger.info("发送重启命令...")
                    send_rpc(m, reboot_rpc, "重启")

                    # 直接关闭会话
                    try:
                        m._session.close()
                        logger.info('会话关闭成功')
                    except Exception as e:
                        logger.error(f"会话关闭期间出错: {e}")
                else:
                    logger.info("当前版本已是最新，不需要升级。")
            else:
                logger.error("无法获取当前版本信息，检查失败。")
    except Exception as e:
        logger.error(f"处理设备期间出错: {e}")

    try:
        # 动态倒计时，等待设备重启完成
        wait_time = 120
        for remaining in range(wait_time, 0, -1):
            sys.stdout.write(f"\r等待设备重启完成，剩余时间: {remaining} 秒")
            sys.stdout.flush()
            time.sleep(1)
        print()  # 确保倒计时完成后换行
        logger.info("设备重启完成")

        # 重新连接设备并执行删除旧文件和安装特性包命令
        m = reconnect(host, port, username, password)
        with m:
            logger.info(f"This session id is {m.session_id}.")

            # 再次检查版本
            current_version_files = check_version(m)

            if current_version_files:
                if set(target_version) != set(current_version_files):
                    logger.info("当前版本不匹配，需要升级。")

                    # 删除旧系统文件
                    logger.info("删除旧系统文件...")
                    send_rpc(m, delete_system_rpc, "删除旧系统文件")

                    # 删除旧引导文件
                    logger.info("删除旧引导文件...")
                    send_rpc(m, delete_boot_rpc, "删除旧引导文件")

                    # 发送安装特性包命令
                    logger.info("发送安装特性包命令...")
                    send_rpc(m, install_feature_rpc, "安装特性包")

                else:
                    logger.info("当前版本已是最新，不需要升级。")
            else:
                logger.error("无法获取当前版本信息，检查失败。")

    except TimeoutExpiredError as e:
        logger.error(f"重连设备时出错: {e}，继续执行剩余操作。")
    except Exception as e:
        logger.error(f"重连设备时出错: {e}")

def main():
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_device, row) for idx, row in config.iterrows()]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")

if __name__ == "__main__":
    main()
