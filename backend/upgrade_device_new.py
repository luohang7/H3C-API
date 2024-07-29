from ncclient import manager
import logging
import time
from ncclient.operations.errors import TimeoutExpiredError
from concurrent.futures import ThreadPoolExecutor, as_completed
from netconf_utils import send_rpc
from read_file import process_file
from custom_logging import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

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
        logger.debug(f"尝试重新连接... 尝试次数 {attempt + 1}")
        try:
            m = manager.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                hostkey_verify=False
            )
            logger.debug("重新连接成功.")
            return m
        except Exception as e:
            logger.error(f"重新连接失败: {e}")
            for remaining in range(wait_time, 0, -1):
                logger.info(f"等待 {remaining} 秒后再尝试重新连接...")
                time.sleep(1)
    raise Exception("无法重新连接到设备.")

def main(device_info):

    name, host, port, username, password = device_info

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

            logger.info(f"{name} ({host})发送固件升级命令...")
            send_rpc(m, firmware_upgrade_rpc, "固件升级")

            logger.info(f"{name} ({host})发送保存配置命令...")
            send_rpc(m, save_config_rpc, "保存配置")

            logger.info(f"{name} ({host})发送重启命令...")
            send_rpc(m, reboot_rpc, "重启")

            # 直接关闭会话
            try:
                m._session.close()
                logger.info(f'{name} ({host})会话关闭成功')
            except Exception as e:
                logger.error(f"{name} ({host})会话关闭期间出错: {e}")

    except Exception as e:
        logger.error(f"{name} ({host})处理设备期间出错: {e}")


    try:
        # 等待设备重启完成
        time.sleep(120)
        logger.info(f"{name} ({host})等待设备重启完成...")

        # 重新连接设备并执行删除旧文件和安装特性包命令
        m = reconnect(host, port, username, password)
        with m:

            # 删除旧系统文件
            logger.info(f"{name} ({host})删除旧系统文件...")
            send_rpc(m, delete_system_rpc, "删除旧系统文件")

            # 删除旧引导文件
            logger.info(f"{name} ({host})删除旧引导文件...")
            send_rpc(m, delete_boot_rpc, "删除旧引导文件")

            # 发送安装特性包命令
            logger.info(f"{name} ({host})发送安装特性包命令...")
            send_rpc(m, install_feature_rpc, "安装特性包")

    except TimeoutExpiredError as e:
        logger.error(f"{name} ({host})重连设备时出错: {e}，继续执行剩余操作。")
    except Exception as e:
        logger.error(f"{name} ({host})重连设备时出错: {e}")


if __name__ == "__main__":
    devices_info = process_file('devices_upgrade.csv')
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(main, device_info) for device_info in devices_info]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"执行设备处理期间出错: {e}")
