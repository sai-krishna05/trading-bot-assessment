def validate_symbol(symbol: str):
    if not symbol or not symbol.isalnum():
        raise ValueError("symbol must be an alphanumeric string, e.g., BTCUSDT")

def validate_side(side: str):
    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")

def validate_order_type(ord_type: str):
    if ord_type not in ("MARKET", "LIMIT", "STOP_LIMIT"):
        raise ValueError("type must be MARKET, LIMIT or STOP_LIMIT")

def validate_quantity(quantity: float):
    try:
        q = float(quantity)
    except Exception:
        raise ValueError("quantity must be a number")
    if q <= 0:
        raise ValueError("quantity must be positive")

def validate_price(price):
    if price is None:
        raise ValueError("price is required for LIMIT and STOP_LIMIT orders")
    try:
        p = float(price)
    except Exception:
        raise ValueError("price must be a numeric value")
    if p <= 0:
        raise ValueError("price must be positive")

def validate_stop_price(stop_price):
    if stop_price is None:
        raise ValueError("stop_price is required for STOP_LIMIT orders")
    try:
        sp = float(stop_price)
    except Exception:
        raise ValueError("stop_price must be a numeric value")
    if sp <= 0:
        raise ValueError("stop_price must be positive")
