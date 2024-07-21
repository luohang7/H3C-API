import os
import logging
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from ncclient import manager

log = logging.getLogger(__name__)


# 读取 XML 文件内容
def read_xml_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# 读取设备信息
def read_devices_from_csv(file_path):
    devices = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            devices.append({
                'host': row['host'],
                'port': int(row['port']),
                'username': row['username'],
                'password': row['password'],
                'hostkey_verify': False
            })
    return devices


# 建立与设备的连接
def h3c_connection(device):
    return manager.connect(
        host=device['host'],
        port=device['port'],
        username=device['username'],
        password=device['password'],
        hostkey_verify=device['hostkey_verify'],
        device_params={'name': "h3c"},
        allow_agent=False,
        look_for_keys=False
    )


# 检查 RPC 回复报文
def _check_response(rpc_obj, snippet_name, device):
    print(f"RPC reply for {snippet_name} on device {device['host']} is {rpc_obj.xml}")
    xml_str = rpc_obj.xml
    if "<ok/>" in xml_str:
        print(f"{snippet_name} successful on device {device['host']}")
    else:
        print(f"Cannot successfully execute: {snippet_name} on device {device['host']}")


# 执行操作
def execute_operation(device, xml_content, operation_name):
    try:
        with h3c_connection(device) as m:
            if operation_name == 'Reboot':
                response = m.dispatch(xml_content)
            else:
                response = m.edit_config(target='running', config=xml_content)
            _check_response(response, operation_name, device)
    except Exception as e:
        print(f"{operation_name}过程中在设备 {device['host']} 发生错误: {e}")


def main():
    devices = read_devices_from_csv('devices.csv')

    # 定义XML文件夹路径
    xml_folder = 'xml_files'

    # 读取 XML 文件
    tftp_download_xml = read_xml_file(os.path.join(xml_folder, 'tftp_download.xml'))
    system_boot_upgrade_xml = read_xml_file(os.path.join(xml_folder, 'system_boot_upgrade.xml'))
    reboot_xml = read_xml_file(os.path.join(xml_folder, 'reboot.xml'))

    # 定义要执行的操作
    operations = [
        ('TFTP_Download', tftp_download_xml),
        ('System_Boot_Upgrade', system_boot_upgrade_xml),
        ('Reboot', reboot_xml)
    ]

    # 使用 ThreadPoolExecutor 进行多线程操作
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        # 对于每个设备
        for device in devices:
            # 对于每个操作
            for operation_name, xml_content in operations:
                futures.append(executor.submit(execute_operation, device, xml_content, operation_name))

        # 等待所有任务完成
        for future in as_completed(futures):
            future.result()  # 等待任务完成并获取结果


if __name__ == "__main__":
    main()
