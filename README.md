# Trading Bot — Binance Futures Testnet (USDT-M)

Simple Python trading bot that can place MARKET, LIMIT, and STOP-LIMIT orders on Binance Futures Testnet (USDT‑M). Built for clarity, reuse, and safe testing.

Features
- Place MARKET, LIMIT, and STOP-LIMIT orders
- BUY and SELL sides
- CLI entrypoint (Typer) with a --dry-run flag
- Structured client layer for Binance Futures REST API (signed requests)
- Input validation and helpful error messages
- Logging of API requests, responses, and errors to a log file

Testnet Base URL
https://testnet.binancefuture.com

Security
- Use environment variables (see .env.example)
- Never commit your API secret to version control

Requirements
- Python 3.9+
- See `requirements.txt` for dependencies

Quickstart
1. Clone or copy the repo
2. Create a virtual environment and install:
   python -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   pip install -r requirements.txt

3. Create a `.env` file (copy `.env.example`) and set:
   BINANCE_API_KEY=your_testnet_api_key
   BINANCE_API_SECRET=your_testnet_api_secret
   BINANCE_BASE_URL=https://testnet.binancefuture.com

4. Examples
- Place a MARKET buy:
  python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

- Place a LIMIT sell:
  python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 42000

- Place a STOP-LIMIT buy (stopPrice triggers the limit order):
  python cli.py order --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --stop-price 41500 --price 41450

- Dry-run (prepare & log request but do not send):
  python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run

5. Logs
- Requests/responses and errors are written to logs/trading_bot.log
- Example sample logs included under logs/ (market_order.log, limit_order.log, stop_limit_order.log)

Notes & Assumptions
- Quantity must follow the exchange's lot/contract rules — this CLI performs basic validation only and does not query exchange filters automatically.
- For STOP-LIMIT orders, both `--stop-price` (trigger) and `--price` (limit order price) are required.
- Dry-run shows the full prepared request (method, url, params including signature) but does not transmit the request to Binance.
- This project uses Binance Futures testnet endpoints. Use testnet keys only for testing.

If you want:
- I can add a real exchange filter check to ensure quantities/prices conform to symbol rules.
- I can produce a downloadable ZIP file on request (I can provide a direct bundle if you need).
