from ncclient import manager
from lxml import etree

# 连接设备的参数
device_params = {
    'host': '192.168.253.99',  # 设备IP地址
    'port': 830,               # NETCONF端口
    'username': 'lpssy',       # 登录用户名
    'password': 'Lpssy123',    # 登录密码
    'hostkey_verify': False    # 关闭主机密钥验证
}

try:
    with manager.connect(**device_params) as m:
        # 构造获取schemas列表的请求
        filter_xml = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" type="subtree">
            <netconf-state xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
                <schemas/>
            </netconf-state>
        </filter>
        '''
        # 发送获取schemas列表的请求
        response = m.get(filter=etree.fromstring(filter_xml))
        print(response.xml)
except Exception as e:
    print(f"获取schemas列表时出错: {e}")
