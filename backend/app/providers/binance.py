"""
Binance WebSocket data provider.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncIterator, List

import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed

from app.models import Quote, Symbol
from app.providers.base import IDataProvider


class BinanceProvider(IDataProvider):
    """
    Binance WebSocket provider for real-time crypto prices.
    No API key required.
    """
    
    BASE_WS_URL = "wss://stream.binance.com:9443/stream"
    
    def __init__(self):
        """Initialize Binance provider."""
        # Available crypto symbols (Binance format)
        self._symbols = [
            Symbol(symbol="BTCUSDT", name="Bitcoin", asset_type="crypto"),
            Symbol(symbol="ETHUSDT", name="Ethereum", asset_type="crypto"),
            Symbol(symbol="SOLUSDT", name="Solana", asset_type="crypto"),
            Symbol(symbol="BNBUSDT", name="BNB", asset_type="crypto"),
            Symbol(symbol="ADAUSDT", name="Cardano", asset_type="crypto"),
            Symbol(symbol="XRPUSDT", name="Ripple", asset_type="crypto"),
        ]
        
        # Latest prices cache
        self._latest_prices: dict[str, float] = {}
    
    async def list_symbols(self) -> List[Symbol]:
        """List available symbols."""
        return self._symbols.copy()
    
    async def get_quote(self, symbol: str) -> Quote:
        """
        Get latest quote for a symbol using Binance REST API.
        Uses cached price if available, otherwise fetches from API.
        """
        # If we have a cached price, return it
        if symbol in self._latest_prices:
            return Quote(
                symbol=symbol,
                price=self._latest_prices[symbol],
                ts=datetime.now(timezone.utc).isoformat()
            )
        
        # Otherwise, fetch from Binance REST API
        async with aiohttp.ClientSession() as session:
            url = f"https://api.binance.com/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    price = float(data["price"])
                    ts = datetime.now(timezone.utc).isoformat()
                    
                    # Cache the price
                    self._latest_prices[symbol] = price
                    
                    return Quote(
                        symbol=symbol,
                        price=round(price, 2),
                        ts=ts
                    )
                else:
                    raise ValueError(f"Failed to fetch quote for {symbol}")
    
    async def stream(self, subscriptions: List[str]) -> AsyncIterator[Quote]:
        """
        Stream real-time quotes from Binance WebSocket.
        
        Binance stream format: <symbol>@trade (lowercase)
        Example: btcusdt@trade
        """
        if not subscriptions:
            return
        
        # Convert symbols to Binance stream format (lowercase)
        binance_streams = [f"{symbol.lower()}@trade" for symbol in subscriptions]
        
        # Build WebSocket URL with multiple streams
        streams_param = "/".join(binance_streams)
        ws_url = f"{self.BASE_WS_URL}?streams={streams_param}"
        
        reconnect_delay = 1
        max_reconnect_delay = 60
        
        while True:
            try:
                async with websockets.connect(ws_url) as websocket:
                    reconnect_delay = 1  # Reset on successful connection
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            
                            # Binance stream response format:
                            # {"stream": "btcusdt@trade", "data": {"e": "trade", "s": "BTCUSDT", "p": "43250.50", "T": 1234567890, ...}}
                            if "data" in data:
                                trade_data = data["data"]
                                
                                # Extract symbol and price
                                symbol = trade_data.get("s")  # Symbol (e.g., BTCUSDT)
                                price_str = trade_data.get("p")  # Price as string
                                trade_time = trade_data.get("T")  # Trade timestamp (ms)
                                
                                if symbol and price_str:
                                    try:
                                        price = float(price_str)
                                        
                                        # Convert timestamp (ms) to ISO string
                                        ts = datetime.fromtimestamp(
                                            trade_time / 1000, 
                                            tz=timezone.utc
                                        ).isoformat()
                                        
                                        # Cache the price
                                        self._latest_prices[symbol] = price
                                        
                                        # Yield quote
                                        yield Quote(
                                            symbol=symbol,
                                            price=round(price, 2),
                                            ts=ts
                                        )
                                    except (ValueError, TypeError) as e:
                                        # Skip invalid data
                                        continue
                        
                        except json.JSONDecodeError:
                            # Skip invalid JSON
                            continue
                        except Exception as e:
                            # Log error but continue
                            print(f"Error processing message: {e}")
                            continue
            
            except ConnectionClosed:
                # Normal closure, try to reconnect
                print(f"WebSocket closed, reconnecting in {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
            
            except Exception as e:
                # Other errors, reconnect with exponential backoff
                print(f"WebSocket error: {e}, reconnecting in {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)

