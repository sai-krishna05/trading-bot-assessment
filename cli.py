#!/usr/bin/env python3
"""
CLI entry point for the trading bot.
Examples:
  python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 42000
  python cli.py order --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --stop-price 41500 --price 41450
  python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
"""
from typing import Optional
import os
import typer
from dotenv import load_dotenv

from bot.logging_config import setup_logging
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)
from bot.orders import place_order

load_dotenv()
app = typer.Typer()
logger = setup_logging()

@app.command()
def order(
    symbol: str = typer.Option(..., help="Trading symbol, e.g., BTCUSDT"),
    side: str = typer.Option(..., help="BUY or SELL"),
    type: str = typer.Option(..., help="MARKET / LIMIT / STOP_LIMIT"),
    quantity: float = typer.Option(..., help="Order quantity (contracts/lot size)"),
    price: Optional[float] = typer.Option(None, help="Price (required for LIMIT and STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", help="Stop price (required for STOP_LIMIT)"),
    dry_run: bool = typer.Option(False, help="Prepare & log request but do not send it"),
):
    """
    Place an order on Binance Futures Testnet (USDT-M).
    """
    # Normalize inputs
    symbol = symbol.upper()
    side = side.upper()
    type = type.upper()

    try:
        validate_symbol(symbol)
        validate_side(side)
        validate_order_type(type)
        validate_quantity(quantity)
        if type == "LIMIT":
            validate_price(price)
        if type == "STOP_LIMIT":
            validate_stop_price(stop_price)
            validate_price(price)
    except ValueError as e:
        typer.secho(f"Input validation error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Get API keys and base URL
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    base_url = os.getenv("BINANCE_BASE_URL", "https://testnet.binancefuture.com")

    if not api_key or not api_secret:
        typer.secho("Missing BINANCE_API_KEY or BINANCE_API_SECRET in environment (.env).", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Summarize request
    typer.secho("Order Request Summary", fg=typer.colors.GREEN, bold=True)
    typer.echo(f"  symbol:      {symbol}")
    typer.echo(f"  side:        {side}")
    typer.echo(f"  type:        {type}")
    typer.echo(f"  quantity:    {quantity}")
    if type in ("LIMIT", "STOP_LIMIT"):
        typer.echo(f"  price:       {price}")
    if type == "STOP_LIMIT":
        typer.echo(f"  stop_price:  {stop_price}")
    typer.echo(f"  dry_run:     {dry_run}")

    # Place order
    try:
        response = place_order(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
            symbol=symbol,
            side=side,
            ord_type=type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            dry_run=dry_run,
        )
    except Exception as e:
        typer.secho(f"Error placing order: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Print response details
    typer.secho("\nOrder Response", fg=typer.colors.BLUE, bold=True)
    import json
    typer.echo(json.dumps(response, indent=2))

if __name__ == "__main__":
    app()
