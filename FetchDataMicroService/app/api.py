from fastapi import APIRouter, Query
from app.coingecko import CoinGeckoAPI

router = APIRouter()
api = CoinGeckoAPI()

@router.get("/validate_coin/{coin_symbol}")
async def validate_coin(coin_symbol: str):
    """Validate a coin symbol and return the correct CoinGecko ID."""
    success, result = await api.validate_coin_symbol(coin_symbol)
    return {"success": success, "data": result}

@router.get("/coin_price/{coin_symbol}")
async def get_coin_price(coin_symbol: str):
    """Fetch the latest price of a coin."""
    success, result = await api.get_coin_price(coin_symbol)
    return {"success": success, "price": f"{result:.8f}"}

@router.get("/coin_icon/{coin_symbol}")
async def get_coin_icon(coin_symbol: str):
    """Fetch the coin icon, store in MinIO, and return its URL."""
    icon_url = await api.fetch_and_save_coin_icon(coin_symbol)
    return {"success": bool(icon_url), "icon_url": icon_url}

@router.get("/multiple_prices")
async def get_multiple_prices(coin_symbols: list[str] = Query(...)):
    """Fetch prices for multiple coins."""
    results = await api.get_multiple_prices(coin_symbols)
    return {"data": results}
