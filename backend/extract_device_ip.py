import re

# 读取 .log 文件中的数据
with open('/check_version.log', 'r', encoding='gbk', errors='ignore') as file:
    log_data = file.read()

# 正则表达式模式，用于匹配设备名称和括号内的 IP 地址
pattern = r"当前版本不匹配:(.*?)\((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)"

# 使用 re.findall 提取所有匹配的设备名称和 IP 地址
matches = re.findall(pattern, log_data)

# 使用集合去重
unique_matches = set(matches)

# 输出提取的唯一设备名称和 IP 地址，并写入 CSV 文件
output_file_path = '/uploads/devices_upgrade.csv'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write("name,host,port,username,password\n")  # 写入CSV表头
    for device, ip in unique_matches:
        output_file.write(f"{device.strip()},{ip},830,lpssy,Lpssy123\n")
