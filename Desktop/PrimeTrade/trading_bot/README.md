# Binance Futures Testnet Trading Bot

## Overview

A simple Python CLI bot to place Market and Limit orders on Binance USDT-M Futures Testnet. Includes input validation, logging, and error handling.

## Features

- Place MARKET and LIMIT orders (BUY/SELL)
- CLI input with validation
- Logs API requests, responses, and errors
- Modular, reusable code structure

## Setup

1. Clone this repo or unzip the folder.
2. Register on [Binance Futures Testnet](https://testnet.binancefuture.com) and get API credentials.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run from the project root:

```bash
python -m trading_bot.cli --api-key <API_KEY> --api-secret <API_SECRET> --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

For LIMIT orders, add `--price`:

```bash
python -m trading_bot.cli --api-key <API_KEY> --api-secret <API_SECRET> --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 50000
```

## Log Files

- All API requests, responses, and errors are logged to `trading_bot.log`.
- Submit log files for at least one MARKET and one LIMIT order as part of your application.

## Assumptions

- Only USDT-M Futures are supported.
- User provides valid API credentials and symbol.

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies.
