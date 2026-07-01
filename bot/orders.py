from typing import Optional, Dict, Any
from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging

logger = setup_logging()

def place_order(
    api_key: str,
    api_secret: str,
    base_url: str,
    symbol: str,
    side: str,
    ord_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Places an order via the BinanceFuturesClient and returns the parsed response dict.
    Raises exceptions on error.
    """
    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret, base_url=base_url)
    try:
        resp = client.new_order(
            symbol=symbol,
            side=side,
            ord_type=ord_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            dry_run=dry_run,
        )
    except Exception as e:
        logger.exception(f"Failed to place order: {e}")
        raise

    # Log the important result fields or the simulated request
    if isinstance(resp, dict) and resp.get("simulated"):
        logger.info(f"Dry-run prepared: method={resp.get('method')}, url={resp.get('url')}")
        logger.debug(f"Prepared params: {resp.get('params')}")
    else:
        logger.info(f"Order placed: symbol={symbol}, side={side}, type={ord_type}, quantity={quantity}, price={price}, stop_price={stop_price}")
        logger.debug(f"Order response: {resp}")
    return resp
