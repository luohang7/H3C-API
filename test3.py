from ncclient import manager
from ncclient.xml_ import to_ele
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

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

def send_rpc(m, rpc, description):
    try:
        response = m.dispatch(to_ele(rpc))
        print(f"{description} RPC 回复: {response.xml}")
    except Exception as e:
        print(f"{description} 操作期间出错: {e}")

def main():
    with manager.connect(
            host="192.168.253.97",
            port=830,
            username="lpssy",
            password="Lpssy123",
            hostkey_verify=False,
            timeout=150  # 设置更长的超时时间
    ) as m:
        print(f"此会话 ID 是 {m.session_id}.")

        # 删除旧系统文件
        print("删除旧系统文件...")
        send_rpc(m, delete_system_rpc, "删除旧系统文件")

        # 删除旧引导文件
        print("删除旧引导文件...")
        send_rpc(m, delete_boot_rpc, "删除旧引导文件")

        # 发送安装特性包命令
        print("发送安装特性包命令...")
        send_rpc(m, install_feature_rpc, "安装特性包")

if __name__ == "__main__":
    main()
