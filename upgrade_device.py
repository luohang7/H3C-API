import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from ncclient import manager


# 读取设备列表的CSV文件
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


# 读取XML文件内容
def read_xml_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# 读取XML文件
system_boot_upgrade_xml = read_xml_file('system_boot_upgrade.xml')
feature_upgrade_xml = read_xml_file('feature_upgrade.xml')
reboot_xml = read_xml_file('reboot.xml')


# 升级设备的函数
def upgrade_device(device_params, upgrade_xmls):
    try:
        with manager.connect(**device_params) as m:
            # 传输系统和启动包并执行升级
            response = m.dispatch(upgrade_xmls['system_boot'])
            print(f"设备 {device_params['host']} 系统和启动包升级响应：{response}")

            # 重启设备
            response = m.dispatch(upgrade_xmls['reboot'])
            print(f"设备 {device_params['host']} 重启响应：{response}")

            # 等待设备重启完成 (假设等待300秒)
            import time
            time.sleep(300)

            # 重新连接设备
            with manager.connect(**device_params) as m:
                # 传输和升级特性包
                response = m.dispatch(upgrade_xmls['feature'])
                return f"设备 {device_params['host']} 特性包升级响应：{response}"
    except Exception as e:
        return f"设备 {device_params['host']} 升级失败：{e}"


# 主函数，读取设备列表并执行升级
def main():
    devices = read_devices_from_csv('devices.csv')
    upgrade_xmls = {
        'system_boot': system_boot_upgrade_xml,
        'feature': feature_upgrade_xml,
        'reboot': reboot_xml
    }

    # 使用多线程批量升级设备
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(upgrade_device, device, upgrade_xmls): device for device in devices}
        for future in as_completed(futures):
            device = futures[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"设备 {device['host']} 升级过程中出现异常：{e}")


if __name__ == "__main__":
    main()
