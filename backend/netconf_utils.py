from ncclient.xml_ import to_ele
import logging
from ncclient.operations.errors import TimeoutExpiredError

logger = logging.getLogger(__name__)

def send_rpc(m, rpc, description):
    try:
        response = m.dispatch(to_ele(rpc))
        logger.debug(f"{description} RPC 回复: {response.xml}")
        return response
    except TimeoutExpiredError as e:
        return None
    except Exception as e:
        return None