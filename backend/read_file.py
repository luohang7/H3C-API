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
    filepath = os.path.join('uploads', filename)
    config = pd.read_csv(filepath)
    devices = []
    for idx, row in config.iterrows():
        device_info = process_device(row)
        devices.append(device_info)
    return devices
