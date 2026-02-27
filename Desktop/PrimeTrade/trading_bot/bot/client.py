import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.logger = logging.getLogger(__name__)
        self.client = Client(api_key, api_secret, testnet=True)
        self.client.FUTURES_URL = base_url

    def place_order(self, symbol, side, order_type, quantity, price=None, **kwargs):
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
                **kwargs
            }
            if order_type == 'LIMIT':
                params['price'] = price
                params['timeInForce'] = 'GTC'
            self.logger.info(f"Placing order: {params}")
            order = self.client.futures_create_order(**params)
            self.logger.info(f"Order response: {order}")
            return order
        except (BinanceAPIException, BinanceRequestException) as e:
            self.logger.error(f"Binance API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
