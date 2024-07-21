import sys
import logging
from ncclient import manager
from ncclient import operations

log = logging.getLogger(__name__)

# 文件传输的RPC报文
FILE_TRANSFER_RPC = """<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <top xmlns="http://www.h3c.com/netconf/config:1.0">
        <file>
            <transfer>
                <source>
                    <tftp>
                        <server>43.229.153.28</server>
                        <file>S5130S_EI-CMW710-R6357/S5130S_EI-CMW710-R6357.ipe</file>
                    </tftp>
                </source>
                <destination>
                    <file>flash:/S5130S_EI-CMW710-R6357.ipe</file>
                </destination>
            </transfer>
        </file>
    </top>
</config>
"""

# 建立与设备的连接。
def h3c_connection(host, port, user, password):
    return manager.connect(
        host=host,
        port=port,
        username=user,
        password=password,
        hostkey_verify=False,
        device_params={'name': "h3c"},
        allow_agent=False,
        look_for_keys=False
    )

# 检查RPC回复报文。
def _check_response(rpc_obj, snippet_name):
    print("RPC reply for %s is %s" % (snippet_name, rpc_obj.xml))
    xml_str = rpc_obj.xml
    if "<ok/>" in xml_str:
        print("%s successful" % snippet_name)
    else:
        print("Cannot successfully execute: %s" % snippet_name)

def test_file_transfer(host, port, user, password):
    # 创建NETCONF会话。
    with h3c_connection(host, port=port, user=user, password=password) as m:
        # 发送RPC请求并检查RPC回复报文。
        rpc_obj = m.edit_config(target='running', config=FILE_TRANSFER_RPC)
        _check_response(rpc_obj, 'FILE_TRANSFER')

if __name__ == '__main__':
    test_file_transfer("192.168.253.99", 830, "lpssy", "Lpssy123")
