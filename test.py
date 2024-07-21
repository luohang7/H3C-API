from ncclient import manager
from ncclient.xml_ import to_ele

# 设备连接参数
device_params = {
    'host': '192.168.253.99',  # 设备IP地址
    'port': 830,  # NETCONF端口，默认为830
    'username': 'lpssy',  # 登录用户名
    'password': 'Lpssy123',  # 登录密码
    'hostkey_verify': False,  # 不验证主机密钥
    'device_params': {'name': 'h3c'}  # 设备类型
}
def get_schema(identifier, version="2015-05-07", schema_format="yang"):
    try:
        with manager.connect(**device_params) as m:
            # 构造 get-schema 请求
            schema_request = f"""
            <get-schema xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring">
                <identifier>{identifier}</identifier>
                <version>{version}</version>
                <format>{schema_format}</format>
            </get-schema>
            """
            response = m.dispatch(to_ele(schema_request))
            print(response.xml)
    except Exception as e:
        print(f"获取YANG模型过程中发生错误: {e}")

if __name__ == "__main__":
    schema_names = ["H3C-fundamentals-config", "openconfig-vlan"]
    for schema_name in schema_names:
        print(f"Fetching schema for: {schema_name}")
        get_schema(schema_name)
