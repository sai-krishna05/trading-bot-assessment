"""
Binance Futures (USDT-M) API client wrapper using requests.
Supports MARKET, LIMIT and STOP-LIMIT (mapped to Binance STOP type with stopPrice).
Signs requests with HMAC-SHA256 (signature as query param).
"""
import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests
from typing import Dict, Any, Optional
from bot.logging_config import setup_logging

logger = setup_logging()

class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://testnet.binancefuture.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

    def _sign(self, params: Dict[str, Any]) -> str:
        """
        Create signature for given params dict. Returns hex digest.
        """
        # Note: urlencode must be deterministic; ensure booleans, floats, etc. are stringified consistently
        query = urlencode(params, doseq=True)
        signature = hmac.new(self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
        return signature

    def _request(self, method: str, path: str, params: Dict[str, Any], signed: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """
        Internal request helper. Logs request/response. If dry_run=True then returns simulated response and does not send HTTP call.
        """
        url = f"{self.base_url}{path}"
        params = params or {}
        params_to_sign = params.copy()

        # Add timestamp for signed endpoints
        if signed:
            params_to_sign["timestamp"] = int(time.time() * 1000)
            signature = self._sign(params_to_sign)
            params_with_sig = params_to_sign.copy()
            params_with_sig["signature"] = signature
        else:
            params_with_sig = params_to_sign

        headers = {"X-MBX-APIKEY": self.api_key}

        # Log request without exposing secret
        logger.debug(f"Request URL: {url}")
        logger.debug(f"Request params (pre-sign): {params_to_sign}")
        logger.debug(f"Request params (signed): { {k:v for k,v in params_with_sig.items() if k != 'signature' } }")

        if dry_run:
            # Return a simulated response for local testing; do not transmit secrets
            logger.info("Dry-run enabled: request prepared but not sent.")
            return {
                "simulated": True,
                "method": method,
                "url": url,
                "params": params_with_sig,
                "headers": {"X-MBX-APIKEY": self.api_key},
            }

        try:
            if method.upper() == "GET":
                resp = requests.get(url, params=params_with_sig, headers=headers, timeout=10)
            elif method.upper() == "POST":
                # Binance expects params in query string for order endpoint
                resp = requests.post(url, params=params_with_sig, headers=headers, timeout=10)
            else:
                raise ValueError("Unsupported HTTP method")
        except requests.RequestException as e:
            logger.exception(f"Network error when calling {url}: {e}")
            raise

        # Parse and log response
        try:
            data = resp.json()
        except ValueError:
            logger.error(f"Non-JSON response: {resp.text}")
            resp.raise_for_status()
            raise ValueError("Non-JSON response from API")

        logger.debug(f"Response status: {resp.status_code}, body: {data}")

        if resp.status_code >= 400:
            err_msg = data.get("msg") or data
            logger.error(f"API error: status {resp.status_code}, msg: {err_msg}")
            raise Exception(f"API error: {err_msg}")

        return data

    def new_order(
        self,
        symbol: str,
        side: str,
        ord_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        timeInForce: str = "GTC",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Place a new futures order.
        ord_type: expected values: "MARKET", "LIMIT", "STOP_LIMIT"
        STOP_LIMIT is mapped to Binance type "STOP" with stopPrice + price.
        """
        path = "/fapi/v1/order"
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            # Binance expects 'type' to be one of their recognized types; we'll map below
        }

        if ord_type == "MARKET":
            params["type"] = "MARKET"
            params["quantity"] = quantity
        elif ord_type == "LIMIT":
            params["type"] = "LIMIT"
            params["quantity"] = quantity
            params["price"] = price
            params["timeInForce"] = timeInForce
        elif ord_type == "STOP_LIMIT":
            # Map to Binance STOP (stopPrice + price). Note: ensure both provided by caller
            params["type"] = "STOP"
            params["quantity"] = quantity
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = timeInForce
        else:
            raise ValueError("Unsupported order type")

        return self._request("POST", path, params, signed=True, dry_run=dry_run)
