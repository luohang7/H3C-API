from ncclient import manager
from ncclient.xml_ import to_ele
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

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

def send_rpc(m, rpc, description):
    try:
        response = m.dispatch(to_ele(rpc))
        print(f"{description} RPC 回复: {response.xml}")
    except Exception as e:
        print(f"{description} 操作期间出错: {e}")

def main():
    with manager.connect(
            host="192.168.253.98",
            port=830,
            username="lpssy",
            password="Lpssy123",
            hostkey_verify=False,
            timeout=300  # 设置更长的超时时间
    ) as m:
        print(f"此会话 ID 是 {m.session_id}.")

        # 发送固件升级命令
        print("发送固件升级命令...")
        send_rpc(m, firmware_upgrade_rpc, "固件升级")

        # 发送保存配置命令
        print("发送保存配置命令...")
        send_rpc(m, save_config_rpc, "保存配置")

        # 发送重启命令
        print("发送重启命令...")
        send_rpc(m, reboot_rpc, "重启")

if __name__ == "__main__":
    main()
