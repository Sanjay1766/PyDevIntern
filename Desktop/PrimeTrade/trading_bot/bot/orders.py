import logging
from .client import BinanceFuturesClient

def submit_order(client: BinanceFuturesClient, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
    try:
        order = client.place_order(symbol, side, order_type, quantity, price)
        return order
    except Exception as e:
        logging.error(f"Order placement failed: {e}")
        return None
