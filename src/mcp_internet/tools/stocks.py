"""
Stock and Cryptocurrency Price Tools.

Uses free APIs for real-time market data:
- Stocks: Yahoo Finance (no API key required)
- Crypto: CoinGecko API (no API key required)
"""

import logging
import re
from urllib.parse import quote_plus

from ..utils.http_client import fetch_url, fetch_json

logger = logging.getLogger(__name__)


async def get_stock_price(symbol: str) -> str:
    """
    Get the current stock price and market data.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
        
    Returns:
        Current stock price, change, and market data
    """
    if not symbol.strip():
        return "❌ Error: Please provide a stock symbol."
    
    symbol = symbol.upper().strip()
    
    # Use Yahoo Finance
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    
    data = await fetch_json(url)
    
    if not data or "chart" not in data:
        return f"❌ Error: Unable to fetch stock data for '{symbol}'."
    
    result = data.get("chart", {}).get("result")
    if not result or len(result) == 0:
        return f"❌ Error: Stock symbol '{symbol}' not found."
    
    try:
        meta = result[0].get("meta", {})
        quote = result[0].get("indicators", {}).get("quote", [{}])[0]
        
        current_price = meta.get("regularMarketPrice", 0)
        previous_close = meta.get("previousClose", 0)
        currency = meta.get("currency", "USD")
        exchange = meta.get("exchangeName", "Unknown")
        short_name = meta.get("shortName", symbol)
        
        # Calculate change
        if previous_close and current_price:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
            change_emoji = "📈" if change >= 0 else "📉"
            change_sign = "+" if change >= 0 else ""
        else:
            change = 0
            change_percent = 0
            change_emoji = "➖"
            change_sign = ""
        
        # Get high/low from the day
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        day_high = max(h for h in highs if h is not None) if highs else None
        day_low = min(l for l in lows if l is not None) if lows else None
        
        output = f"""📊 **{short_name}** ({symbol})
{'=' * 40}

💰 Current Price: {currency} {current_price:,.2f}
{change_emoji} Change: {change_sign}{change:,.2f} ({change_sign}{change_percent:.2f}%)

📈 Day High: {currency} {day_high:,.2f}
📉 Day Low: {currency} {day_low:,.2f}
📊 Previous Close: {currency} {previous_close:,.2f}

🏛️ Exchange: {exchange}
"""
        return output
        
    except Exception as e:
        logger.error(f"Error parsing stock data: {e}")
        return f"❌ Error: Unable to parse stock data for '{symbol}'."


async def get_crypto_price(coin: str, currency: str = "usd") -> str:
    """
    Get the current cryptocurrency price.
    
    Args:
        coin: Cryptocurrency name or ID (e.g., 'bitcoin', 'ethereum', 'dogecoin')
        currency: Fiat currency for price (default: 'usd')
        
    Returns:
        Current crypto price and market data
    """
    if not coin.strip():
        return "❌ Error: Please provide a cryptocurrency name."
    
    coin = coin.lower().strip()
    currency = currency.lower().strip()
    
    # Common name mappings
    coin_mappings = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "doge": "dogecoin",
        "xrp": "ripple",
        "sol": "solana",
        "ada": "cardano",
        "bnb": "binancecoin",
        "usdt": "tether",
        "usdc": "usd-coin",
        "matic": "matic-network",
        "dot": "polkadot",
        "shib": "shiba-inu",
        "avax": "avalanche-2",
        "link": "chainlink",
        "ltc": "litecoin",
    }
    
    coin_id = coin_mappings.get(coin, coin)
    
    # Use CoinGecko API
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false"
    
    data = await fetch_json(url)
    
    if not data or "error" in data:
        # Try searching for the coin
        search_url = f"https://api.coingecko.com/api/v3/search?query={coin}"
        search_data = await fetch_json(search_url)
        
        if search_data and "coins" in search_data and search_data["coins"]:
            coin_id = search_data["coins"][0]["id"]
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false"
            data = await fetch_json(url)
        
        if not data or "error" in data:
            return f"❌ Error: Cryptocurrency '{coin}' not found."
    
    try:
        name = data.get("name", coin)
        symbol = data.get("symbol", "").upper()
        market_data = data.get("market_data", {})
        
        current_price = market_data.get("current_price", {}).get(currency, 0)
        price_change_24h = market_data.get("price_change_percentage_24h", 0)
        high_24h = market_data.get("high_24h", {}).get(currency, 0)
        low_24h = market_data.get("low_24h", {}).get(currency, 0)
        market_cap = market_data.get("market_cap", {}).get(currency, 0)
        total_volume = market_data.get("total_volume", {}).get(currency, 0)
        ath = market_data.get("ath", {}).get(currency, 0)
        ath_change = market_data.get("ath_change_percentage", {}).get(currency, 0)
        
        change_emoji = "📈" if price_change_24h >= 0 else "📉"
        change_sign = "+" if price_change_24h >= 0 else ""
        
        # Format large numbers
        def format_large(n):
            if n >= 1e12:
                return f"{n/1e12:.2f}T"
            elif n >= 1e9:
                return f"{n/1e9:.2f}B"
            elif n >= 1e6:
                return f"{n/1e6:.2f}M"
            else:
                return f"{n:,.2f}"
        
        output = f"""🪙 **{name}** ({symbol})
{'=' * 40}

💰 Current Price: {currency.upper()} {current_price:,.4f}
{change_emoji} 24h Change: {change_sign}{price_change_24h:.2f}%

📈 24h High: {currency.upper()} {high_24h:,.4f}
📉 24h Low: {currency.upper()} {low_24h:,.4f}

💎 All-Time High: {currency.upper()} {ath:,.4f} ({ath_change:.1f}% from ATH)
📊 Market Cap: {currency.upper()} {format_large(market_cap)}
📈 24h Volume: {currency.upper()} {format_large(total_volume)}
"""
        return output
        
    except Exception as e:
        logger.error(f"Error parsing crypto data: {e}")
        return f"❌ Error: Unable to parse cryptocurrency data for '{coin}'."
