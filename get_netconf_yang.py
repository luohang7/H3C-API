from ncclient import manager

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
        # 获取特定YANG模型的定义
        schema = m.get_schema('H3C-syslog-data', '2017-01-29', 'yang')
        print(schema.xml)
except Exception as e:
    print(f"获取YANG模型时出错: {e}")
