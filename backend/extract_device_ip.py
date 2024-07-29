import os
import re
import pandas as pd

def extract_device_ip(log_file='check_version.log', output_dir='uploads', output_file='devices_upgrade.csv'):
    # 读取 .log 文件中的数据
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as file:
        log_data = file.read()

    # 正则表达式模式，用于匹配设备名称和括号内的 IP 地址
    pattern = r"INFO:(.*?)\((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)需要升级"

    # 使用 re.findall 提取所有匹配的设备名称和 IP 地址
    matches = re.findall(pattern, log_data)

    # 使用集合去重
    unique_matches = set(matches)

    # 检查 devices.csv 文件是否存在
    devices_file_path = os.path.join(output_dir, 'devices.csv')
    if not os.path.exists(devices_file_path):
        raise FileNotFoundError(f"{devices_file_path} 文件未找到，请确保文件存在并重试。")

    # 读取 devices.csv 文件
    devices_df = pd.read_csv(devices_file_path)

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 输出提取的唯一设备名称和 IP 地址，并写入 CSV 文件
    output_file_path = os.path.join(output_dir, output_file)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("name,host,port,username,password\n")  # 写入CSV表头
        for device, ip in unique_matches:
            device_info = devices_df[devices_df['host'] == ip].iloc[0]
            output_file.write(f"{device.strip()},{ip},{device_info['port']},{device_info['username']},{device_info['password']}\n")

    print(f"需升级设备列表已生成: {output_file_path}")
