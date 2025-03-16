import logging
import time
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

    # First, try to get prices from cache
    cached_prices = cache.get("cached_price", {})
    symbols_to_fetch = [symbol for symbol in coin_symbols if symbol not in cached_prices]

    if not symbols_to_fetch:
        logger.debug(f"All prices found in cache for {coin_symbols}")
        return {symbol: cached_prices[symbol] for symbol in coin_symbols}

    # Constants for lock management
    lock_timeout = 30  # seconds
    check_interval = 0.1  # seconds between lock checks
    max_wait_time = 5  # seconds

    # Create a tracking dictionary for coins we need to fetch
    pending_coins = {symbol: False for symbol in symbols_to_fetch}

    # Step 1: Try to acquire locks for each coin
    for symbol in symbols_to_fetch:
        # Create a unique and consistent lock key for each coin
        lock_key = f"price_fetch_lock_{symbol}"
        # Try to acquire the lock
        if cache.add(lock_key, True, lock_timeout):
            # Successfully acquired lock
            pending_coins[symbol] = True
            logger.debug(f"Acquired lock for {symbol}")
        else:
            # Lock already exists, coin is being fetched by another process
            logger.debug(f"Lock already exists for {symbol}, will wait")

    # Step 2: Wait for other processes to complete if needed
    coins_to_wait_for = [s for s, has_lock in pending_coins.items() if not has_lock]
    if coins_to_wait_for:
        logger.debug(f"Waiting for other processes to fetch: {coins_to_wait_for}")
        start_time = time.time()

        while time.time() - start_time < max_wait_time and coins_to_wait_for:
            time.sleep(check_interval)

            # Check if the cache has been updated with any of the coins we're waiting for
            updated_cache = cache.get("cached_price", {})
            # Remove coins that are now in the cache from our wait list
            coins_to_wait_for = [s for s in coins_to_wait_for if s not in updated_cache]

            if not coins_to_wait_for:
                logger.debug("All waiting coins now in cache")
                break

        # After waiting, recheck the cache for all symbols
        cached_prices = cache.get("cached_price", {})

    # Step 3: Determine which coins we still need to fetch (we have locks for these)
    symbols_to_fetch = [s for s, has_lock in pending_coins.items() if has_lock]

    # Step 4: Fetch prices for coins we have locks for
    if symbols_to_fetch:
        logger.debug(f"Now fetching prices for: {symbols_to_fetch}")
        try:
            url = f"{settings.FETCH_PRICE_MICRO_SERVICE}/multiple_prices"
            response = requests.get(url, params={"coin_symbols": symbols_to_fetch})
            response.raise_for_status()
            data = response.json().get("data", {})

            # Process the fetched data
            fetched_prices = {}
            for symbol in symbols_to_fetch:
                if symbol in data and data[symbol][0]:
                    fetched_prices[symbol] = Decimal(data[symbol][1])
                else:
                    fetched_prices[symbol] = Decimal(0)
                    logger.warning(f"No price data received for {symbol}")

            # Update the cache with new prices
            cached_prices = cache.get("cached_price", {})  # Get latest version
            cached_prices.update(fetched_prices)
            cache.set("cached_price", cached_prices, timeout=60)
            logger.debug(f"Updated cache with new prices for {list(fetched_prices.keys())}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching multiple prices: {e}")
            # Set default values for coins we failed to fetch
            for symbol in symbols_to_fetch:
                cached_prices[symbol] = Decimal(0)
        finally:
            # Release all locks we acquired
            for symbol in symbols_to_fetch:
                lock_key = f"price_fetch_lock_{symbol}"
                cache.delete(lock_key)
                logger.debug(f"Released lock for {symbol}")

    # Step 5: Check if we have all the prices we need
    missing_symbols = [s for s in coin_symbols if s not in cached_prices]
    if missing_symbols:
        logger.warning(f"Missing prices for {missing_symbols}, returning zeros")
        for symbol in missing_symbols:
            cached_prices[symbol] = Decimal(0)

    # Return the prices for all requested coins
    return {symbol: cached_prices.get(symbol, Decimal(0)) for symbol in coin_symbols}


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
