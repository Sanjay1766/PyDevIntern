import argparse
import os
from bot.client import BinanceFuturesClient
from bot.orders import submit_order
from bot.validators import (
    validate_symbol, validate_side, validate_order_type, validate_quantity, validate_price
)
from bot.logging_config import setup_logging

import logging

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description='Binance Futures Testnet Trading Bot')
    parser.add_argument('--api-key', required=True, help='Binance API Key')
    parser.add_argument('--api-secret', required=True, help='Binance API Secret')
    parser.add_argument('--symbol', required=True, help='Trading symbol, e.g., BTCUSDT')
    parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('--order-type', required=True, choices=['MARKET', 'LIMIT'], help='Order type')
    parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    parser.add_argument('--price', type=float, help='Order price (required for LIMIT)')
    args = parser.parse_args()

    # Validate inputs
    if not validate_symbol(args.symbol):
        print('Invalid symbol. Must be uppercase and alphanumeric.')
        return
    if not validate_side(args.side):
        print('Invalid side. Must be BUY or SELL.')
        return
    if not validate_order_type(args.order_type):
        print('Invalid order type. Must be MARKET or LIMIT.')
        return
    if not validate_quantity(args.quantity):
        print('Invalid quantity. Must be positive.')
        return
    if args.order_type == 'LIMIT':
        if args.price is None or not validate_price(args.price):
            print('Price is required and must be positive for LIMIT orders.')
            return

    base_url = 'https://testnet.binancefuture.com'
    client = BinanceFuturesClient(args.api_key, args.api_secret, base_url)

    print(f"Placing {args.order_type} order: {args.side} {args.quantity} {args.symbol} at {args.price if args.price else 'MARKET'}")
    order = submit_order(client, args.symbol, args.side, args.order_type, args.quantity, args.price)
    if order:
        print(f"Order placed! Order ID: {order.get('orderId')}, Status: {order.get('status')}, Executed Qty: {order.get('executedQty')}, Avg Price: {order.get('avgPrice', 'N/A')}")
    else:
        print('Order placement failed. Check logs for details.')

if __name__ == '__main__':
    main()
