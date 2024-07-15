from ncclient import manager

# 连接设备的参数
device_params = {
    'host': '192.168.254.99',  # 设备IP地址
    'port': 830,            # NETCONF端口
    'username': 'lpssy',    # 登录用户名
    'password': 'Lpssy123', # 登录密码
    'hostkey_verify': False # 关闭主机密钥验证
}

def get_device_capabilities(device_params):
    try:
        with manager.connect(**device_params) as m:
            # 获取设备支持的能力集
            capabilities = m.server_capabilities
            print("设备的NETCONF能力集：")
            for capability in capabilities:
                print(capability)
    except Exception as e:
        print(f"获取能力集时出错: {e}")

# 获取设备能力集
get_device_capabilities(device_params)