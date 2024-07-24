from ncclient.xml_ import to_ele
import logging
from ncclient.operations.errors import TimeoutExpiredError


# 配置日志级别和格式，包含时间戳，并将日志信息写入文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def send_rpc(m, rpc, description):
    try:
        response = m.dispatch(to_ele(rpc))
        logger.info(f"{description} RPC 回复: {response.xml}")
        return response
    except TimeoutExpiredError as e:
        logger.error(f"{description} 操作期间出错: {e}，继续执行剩余操作。")
        return None
    except Exception as e:
        logger.info(f"{description} 操作期间出错: {e}")
        return None