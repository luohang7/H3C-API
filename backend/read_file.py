import os
import pandas as pd

def process_device(row):
    name = row['name']
    host = row['host']
    port = int(row['port'])
    username = row['username']
    password = row['password']

    return name, host, port, username, password


def process_file(filename):
    # 构建完整文件路径
    filepath = os.path.join('uploads', filename)
    # 读取并解析CSV文件
    config = pd.read_csv(filepath)
    for idx, row in config.iterrows():
        process_device(row)
