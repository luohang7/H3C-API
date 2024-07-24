from ncclient import manager
from ncclient.xml_ import to_ele
import logging
import time


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

# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

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

def send_rpc(m, rpc, description):
    try:
        response = m.dispatch(to_ele(rpc))
        logger.info(f"{description} RPC 回复: {response.xml}")
    except Exception as e:
        logger.info(f"{description} 操作期间出错: {e}")

def check_version(m):
    logger.info("获取当前设备版本信息...")
    response = send_rpc(m, get_version_rpc, "获取版本信息")
    if response:
        # 在此处解析 response XML 以获取版本信息
        root = to_ele(response.xml)
        logger.debug(f"调试 XML 数据: {response.xml}")
        namespaces = {'h3c': 'http://www.h3c.com/netconf/data:1.0'}
        version_elements = root.xpath('//h3c:BootList[h3c:BootType="0"]/h3c:ImageFiles/h3c:FileName', namespaces=namespaces)
        if version_elements:
            current_version_files = [elem.text for elem in version_elements]
            logger.info(f"当前设备版本文件: {current_version_files}")
            return current_version_files
        else:
            logger.debug("未找到匹配的版本元素")
    return None


def main():
    host = '192.168.253.96'
    port = 830
    username = 'lpssy'
    password = 'Lpssy123'

    m = reconnect(host, port, username, password)
    with m:
        logger.info(f"This session id is {m.session_id}.")

        current_version_files = check_version(m)
        target_version = 'R6357'

        if current_version_files and current_version_files< target_version:
            logger.info(f"当前版本 {current_version_files} 小于目标版本 {target_version}，开始升级...")

            # 动态倒计时
            wait_time = 10
            for remaining in range(wait_time, 0, -1):
                logger.info(f"等待设备重启完成，剩余时间: {remaining} 秒", end='\r')
                time.sleep(1)

            # 重新连接设备并执行删除旧文件和安装特性包命令
            m = reconnect(host, port, username, password)
            with m:
                logger.info(f"This session id is {m.session_id}.")

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
            logger.info(f"当前版本 {current_version_files} 已是最新或无法获取版本信息，不需要升级。")

if __name__ == '__main__':
    main()