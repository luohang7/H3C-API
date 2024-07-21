import sys
import logging
from ncclient import manager
from ncclient import operations

log = logging.getLogger(__name__)

# 用于创建 VLAN 的 RPC 报文。
VLAN_RPC = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
 <top xmlns="http://www.h3c.com/netconf/config:1.0">
 <VLAN xc:operation="create">
 <VLANs>
 <VLANID>
 <ID>3</ID>
 <Name>3</Name>
 <Description>2</Description>
 </VLANID>
 </VLANs>
 </VLAN>
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

# 检查 RPC 回复报文。
def _check_response(rpc_obj, snippet_name):
    print("RPC reply for %s is %s" % (snippet_name, rpc_obj.xml))
    xml_str = rpc_obj.xml
    if "<ok/>" in xml_str:
        print("%s successful" % snippet_name)
    else:
        print("Cannot successfully execute: %s" % snippet_name)

def create_vlan():
    try:
        with h3c_connection("192.168.253.99", 830, "lpssy", "Lpssy123") as m:
            # 执行创建 VLAN
            response = m.edit_config(target='running', config=VLAN_RPC)
            _check_response(response, 'VLAN_MERGE')
    except Exception as e:
        print(f"VLAN 创建过程中发生错误: {e}")

if __name__ == "__main__":
    create_vlan()
