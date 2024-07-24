from ncclient import manager
from ncclient.xml_ import to_ele
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

# 文件传输命令，使用临时 channel
file_transfer_rpc = """
<CLI xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <Configuration exec-use-channel="false">
    quit
    tftp 192.168.36.2 get S5130S_EI-CMW710-R6357.ipe 
    tftp 192.168.36.2 get s5130s_ei-cmw710-freeradius-r6357.bin 
    tftp 192.168.36.2 get s5130s_ei-cmw710-grpcpkg-r6357.bin
  </Configuration>
</CLI>
"""

def send_rpc(m, rpc, description):
    try:
        response = m.dispatch(to_ele(rpc))
        print(f"{description} RPC reply: {response.xml}")
    except Exception as e:
        print(f"Error during {description} operation: {e}")

def main():
    with manager.connect(
            host="192.168.253.98",
            port=830,
            username="lpssy",
            password="Lpssy123",
            hostkey_verify=False,
            timeout=700  # 设置更长的超时时间
    ) as m:
        print(f"This session id is {m.session_id}.")

        # 发送文件传输命令
        print("Sending file transfer command...")
        send_rpc(m, file_transfer_rpc, "file transfer")

if __name__ == "__main__":
    main()
