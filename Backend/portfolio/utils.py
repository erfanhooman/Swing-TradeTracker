import logging
from decimal import Decimal

import requests
from django.core.cache import cache
from django.conf import settings

from Backend.messages import response_message as mt

logger = logging.getLogger("backend")


def fetch_coin_price(coin_symbol):
    """Fetch the latest price of a given coin from the API."""
    url = f"{settings.FETCH_PRICE_MICRO_SERVICE}/coin_price/{coin_symbol}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()

        if data.get("success"):
            return Decimal(data.get("price"))
        else:
            logger.error(f"Coin {coin_symbol} couldn't be fetched from api: {data}")
            raise Exception(mt[500])

    except requests.exceptions.RequestException as e:
        logger.error(f"Went wrong fetch price: {e}")
        raise Exception(mt[500])


def fetch_multiple_prices(coin_symbols):
    """Fetch the latest prices for multiple coins in a single request."""

    cached_prices = cache.get("cached_price", {})

    symbols_to_fetch = [symbol for symbol in coin_symbols if symbol not in cached_prices]

    if not symbols_to_fetch:
        return {symbol: cached_prices[symbol] for symbol in coin_symbols}


    url = f"{settings.FETCH_PRICE_MICRO_SERVICE}/multiple_prices"
    try:
        response = requests.get(url, params={"coin_symbols": symbols_to_fetch})
        response.raise_for_status()
        data = response.json().get("data", {})

        fetched_prices = {}
        for symbol in symbols_to_fetch:
            if symbol in data and data[symbol][0]:
                fetched_prices[symbol] = Decimal(data[symbol][1])

        cached_prices.update(fetched_prices)

        cache.set("cached_price", cached_prices, timeout=60)

        return {symbol: cached_prices[symbol] for symbol in coin_symbols}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching multiple prices: {e}")
        return {symbol: Decimal(0) for symbol in coin_symbols}

def fetch_coin_icon(coin_symbol: str):
    """
    Calls the microservice to fetch and store the coin icon.
    Returns the MinIO URL if successful.
    """
    url = f"{settings.FETCH_PRICE_MICRO_SERVICE}/coin_icon/{coin_symbol}"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    if data.get("success"):
        return data.get("icon_url")
    else:
        logger.error(f"Coin {coin_symbol} icon, couldn't be fetched from api: {data}")
        return None
