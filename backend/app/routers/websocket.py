"""
WebSocket endpoints for real-time market data.
"""

import asyncio
import json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.providers.factory import create_provider
from app.services.alert_monitor import alert_monitor

router = APIRouter()

# Singleton provider instance
_provider = None


def get_provider():
    """Get or create provider instance."""
    global _provider
    if _provider is None:
        _provider = create_provider()
    return _provider


@router.websocket("/ws/quotes")
async def websocket_quotes(websocket: WebSocket):
    """
    WebSocket endpoint for real-time quotes.
    
    Client can send messages to subscribe/unsubscribe:
    - Subscribe: {"action": "subscribe", "symbols": ["BTCUSDT", "ETHUSDT"]}
    - Unsubscribe: {"action": "unsubscribe", "symbols": ["BTCUSDT"]}
    """
    await websocket.accept()
    
    provider = get_provider()
    active_subscriptions: Set[str] = set()
    stream_task = None
    stream_cancel = None
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                symbols = message.get("symbols", [])
                
                if action == "subscribe":
                    # Add symbols to subscriptions
                    for symbol in symbols:
                        active_subscriptions.add(symbol)
                    
                    await websocket.send_json({
                        "type": "subscribed",
                        "symbols": list(active_subscriptions)
                    })
                    
                    # Restart streaming with new subscriptions
                    if stream_task:
                        stream_cancel.set()
                        stream_task.cancel()
                        try:
                            await stream_task
                        except asyncio.CancelledError:
                            pass
                    
                    if active_subscriptions:
                        # Start new stream task with alert monitoring
                        stream_cancel = asyncio.Event()
                        stream_task = asyncio.create_task(
                            stream_quotes_with_alerts(websocket, provider, active_subscriptions, stream_cancel)
                        )
                
                elif action == "unsubscribe":
                    # Remove symbols from subscriptions
                    for symbol in symbols:
                        active_subscriptions.discard(symbol)
                    
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "symbols": list(active_subscriptions)
                    })
                    
                    # Restart streaming if subscriptions changed
                    if stream_task and active_subscriptions:
                        stream_cancel.set()
                        stream_task.cancel()
                        try:
                            await stream_task
                        except asyncio.CancelledError:
                            pass
                        
                        stream_cancel = asyncio.Event()
                        stream_task = asyncio.create_task(
                            stream_quotes_with_alerts(websocket, provider, active_subscriptions, stream_cancel)
                        )
                    elif not active_subscriptions and stream_task:
                        # Stop streaming if no subscriptions left
                        stream_cancel.set()
                        stream_task.cancel()
                        try:
                            await stream_task
                        except asyncio.CancelledError:
                            pass
                        stream_task = None
                        stream_cancel = None
                
                elif action == "ping":
                    # Keep-alive
                    await websocket.send_json({"type": "pong"})
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        # Client disconnected
        if stream_task:
            if stream_cancel:
                stream_cancel.set()
            stream_task.cancel()
        return


async def stream_quotes_with_alerts(websocket, provider, subscriptions: Set[str], cancel_event: asyncio.Event):
    """
    Background task that streams quotes to the WebSocket and evaluates alerts.
    """
    try:
        # Use alert monitor to wrap the stream
        async for quote in alert_monitor.monitor_quotes(
            provider,
            list(subscriptions)
        ):
            # Check if cancelled
            if cancel_event.is_set():
                break
            
            # Only send if still subscribed
            if quote.symbol in subscriptions:
                await websocket.send_json({
                    "type": "quote",
                    "data": {
                        "symbol": quote.symbol,
                        "price": quote.price,
                        "ts": quote.ts
                    }
                })
    except asyncio.CancelledError:
        # Task was cancelled, exit gracefully
        pass
    except Exception as e:
        # Send error to client
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Stream error: {str(e)}"
            })
        except:
            pass  # Client may have disconnected

