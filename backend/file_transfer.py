from ncclient import manager
import logging
from netconf_utils import send_rpc
import pandas as pd

# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 读取配置文件
config = pd.read_csv('devices.csv')

# 文件传输命令，使用临时 channel
file_transfer_rpc = """
<CLI xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <Configuration exec-use-channel="false">
    quit
    tftp 192.168.36.2 get S5130S_EI-CMW710-R6357.ipe 
    tftp 192.168.36.2 get s5130s_ei-cmw710-freeradius-r6357.bin 
    tftp 192.168.36.2 get s5130s_ei-cmw710-grpcpkg-r6357.bin
  </Configuration>
</CLI>
"""
def file_transfer(row):
    name = row['name']
    host = row['host']
    port = int(row['port'])
    username = row['username']
    password = row['password']

    with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
            timeout=600  # 设置更长的超时时间
    ) as m:
        logger.info("发送tftp获取文件命令...")
        send_rpc(m, file_transfer_rpc, "file transfer")