"""
Currency Exchange Tool - Get currency conversion rates.

Uses the free ExchangeRate-API (no key required for basic usage)
and falls back to Frankfurter API (European Central Bank data).
"""

import logging

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)

# API endpoints (both free, no key required)
FRANKFURTER_API = "https://api.frankfurter.app/latest"
EXCHANGERATE_API = "https://open.er-api.com/v6/latest"

# Common currency names for display
CURRENCY_NAMES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "INR": "Indian Rupee",
    "CNY": "Chinese Yuan",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "KRW": "South Korean Won",
    "SGD": "Singapore Dollar",
    "HKD": "Hong Kong Dollar",
    "NZD": "New Zealand Dollar",
    "BRL": "Brazilian Real",
    "MXN": "Mexican Peso",
    "RUB": "Russian Ruble",
    "ZAR": "South African Rand",
    "AED": "UAE Dirham",
    "SAR": "Saudi Riyal",
    "THB": "Thai Baht",
}


def get_currency_name(code: str) -> str:
    """Get full currency name from code."""
    return CURRENCY_NAMES.get(code, code)


async def get_rate_frankfurter(from_curr: str, to_curr: str) -> float | None:
    """Get exchange rate from Frankfurter API."""
    url = f"{FRANKFURTER_API}?from={from_curr}&to={to_curr}"
    data = await fetch_json(url)
    
    if data and "rates" in data and to_curr in data["rates"]:
        return data["rates"][to_curr]
    return None


async def get_rate_exchangerate(from_curr: str, to_curr: str) -> float | None:
    """Get exchange rate from ExchangeRate API."""
    url = f"{EXCHANGERATE_API}/{from_curr}"
    data = await fetch_json(url)
    
    if data and "rates" in data and to_curr in data["rates"]:
        # Calculate rate (API returns rates relative to base)
        return data["rates"][to_curr]
    return None


async def get_currency_rate(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0,
) -> str:
    """
    Get currency exchange rate and convert amount.
    
    Args:
        from_currency: Source currency code (e.g., USD, EUR)
        to_currency: Target currency code
        amount: Amount to convert (default: 1.0)
        
    Returns:
        Exchange rate and converted amount
    """
    from_curr = from_currency.upper().strip()
    to_curr = to_currency.upper().strip()
    
    if not from_curr or not to_curr:
        return "❌ Error: Please provide both source and target currency codes."
    
    if len(from_curr) != 3 or len(to_curr) != 3:
        return "❌ Error: Currency codes should be 3 letters (e.g., USD, EUR, GBP)."
    
    if from_curr == to_curr:
        return f"💱 {amount:,.2f} {from_curr} = {amount:,.2f} {to_curr} (same currency)"
    
    # Try primary API
    rate = await get_rate_frankfurter(from_curr, to_curr)
    api_source = "European Central Bank"
    
    # Fallback to secondary API
    if rate is None:
        rate = await get_rate_exchangerate(from_curr, to_curr)
        api_source = "ExchangeRate-API"
    
    if rate is None:
        return f"""❌ Unable to get exchange rate for {from_curr} → {to_curr}

This could mean:
• One or both currency codes are invalid
• The currency is not supported by free APIs
• Temporary API unavailability

Common currency codes: USD, EUR, GBP, JPY, INR, CNY, AUD, CAD, CHF
"""
    
    converted = amount * rate
    
    from_name = get_currency_name(from_curr)
    to_name = get_currency_name(to_curr)
    
    return f"""💱 **Currency Conversion**
{'=' * 40}

**{amount:,.2f} {from_curr}** ({from_name})
      ⬇️
**{converted:,.2f} {to_curr}** ({to_name})

📊 Exchange Rate: 1 {from_curr} = {rate:,.6f} {to_curr}
📅 Source: {api_source} (live rates)
"""
