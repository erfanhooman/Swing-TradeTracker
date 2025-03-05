import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from fastapi import HTTPException
from dotenv import load_dotenv

from .minio import MinioClient

load_dotenv()
API_KEY = os.getenv("API_KEY")
FETCH_SOURCE = os.getenv("COINGECKOAPI")

class CoinGeckoAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        }
        self.last_request_time = datetime.now()
        self.min_request_interval = timedelta(milliseconds=500)
        self.minio_client = MinioClient()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _wait_for_rate_limit(self):
        now = datetime.now()
        time_since_last_request = now - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            await asyncio.sleep((self.min_request_interval - time_since_last_request).total_seconds())
        self.last_request_time = datetime.now()

    async def fetch_and_save_coin_icon(self, coin:str) -> Optional[str]:
        """Fetch the coin icon, save in MinIO, and return its URL."""
        coin = coin.lower()

        # Check if icon exists in MinIO
        existing_icon_url = await self.minio_client.icon_exists(coin)
        if existing_icon_url:
            return existing_icon_url

        success, coin_id = await self.validate_coin_symbol(coin)
        if not success:
            return None

        await self._wait_for_rate_limit()

        url = f"{FETCH_SOURCE}api/v3/coins/{coin_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()

        icon_url = data.get("image", {}).get("large")
        if not icon_url:
            return None

        # Download the image
        await self._wait_for_rate_limit()

        async with aiohttp.ClientSession() as session:
            async with session.get(icon_url) as icon_response:
                icon_response.raise_for_status()
                image_data = await icon_response.read()

        # Upload to MinIO
        minio_url = await self.minio_client.upload_icon(coin, image_data)
        return minio_url


    async def validate_coin_symbol(self, coin_symbol: str):
        """Validate a coin symbol and return the correct CoinGecko ID."""
        try:
            await self._wait_for_rate_limit()
            url = f"{FETCH_SOURCE}api/v3/search?query={coin_symbol}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()

            coins = data.get("coins", [])
            if not coins:
                return False, f"Coin '{coin_symbol}' not found."

            for coin in coins:
                if coin["symbol"].lower() == coin_symbol.lower():
                    return True, coin["id"]

            return False, f"Did you mean {coins[0]['name']} ({coins[0]['symbol'].upper()})?"

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_coin_price(self, coin_symbol: str):
        """Get the current price of a coin."""
        try:
            success, coin_id = await self.validate_coin_symbol(coin_symbol)
            if not success:
                return False, coin_id

            await self._wait_for_rate_limit()
            url = f"{FETCH_SOURCE}api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()

            if coin_id in data:
                return True, data[coin_id]["usd"]
            return False, "Price data not available."

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_multiple_prices(self, coin_symbols: list[str]):
        """Fetch prices for multiple coins in parallel."""
        try:
            tasks = [self.get_coin_price(symbol) for symbol in coin_symbols]
            results = await asyncio.gather(*tasks)
            return dict(zip(coin_symbols, results))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
