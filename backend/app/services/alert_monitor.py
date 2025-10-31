"""
Alert monitoring service that evaluates alerts on incoming quotes.
"""

import asyncio
from typing import AsyncIterator

from app.models import Quote
from app.providers.base import IDataProvider
from app.services.alert_evaluator import AlertEvaluator
from app.services.alert_storage import alert_storage
from app.services.slack_notifier import SlackNotifier


class AlertMonitor:
    """
    Monitors quotes and evaluates alerts.
    """
    
    def __init__(self):
        """Initialize alert monitor."""
        self.evaluator = AlertEvaluator()
        self.notifier = SlackNotifier()
        self._active_tasks = set()
    
    async def monitor_quotes(
        self,
        provider: IDataProvider,
        subscriptions: list[str]
    ) -> AsyncIterator[Quote]:
        """
        Monitor quotes and evaluate alerts.
        This wraps the provider stream and evaluates alerts on each quote.
        
        Args:
            provider: Data provider
            subscriptions: List of symbols to monitor
            
        Yields:
            Quote objects as they arrive
        """
        async for quote in provider.stream(subscriptions):
            # Evaluate alerts for this quote
            await self._evaluate_quote(quote)
            
            # Yield the quote (pass-through)
            yield quote
    
    async def _evaluate_quote(self, quote: Quote):
        """
        Evaluate alerts for a quote.
        
        Args:
            quote: Current quote
        """
        # Get enabled alerts for this symbol
        alerts = alert_storage.get_by_symbol(quote.symbol)
        
        if not alerts:
            return
        
        # Evaluate alerts
        triggered = self.evaluator.evaluate(quote, alerts)
        
        # Send notifications for triggered alerts
        for alert in triggered:
            # Run notification in background
            task = asyncio.create_task(
                self._send_notification(alert, quote)
            )
            self._active_tasks.add(task)
            task.add_done_callback(self._active_tasks.discard)
    
    async def _send_notification(self, alert, quote: Quote):
        """
        Send notification for triggered alert.
        
        Args:
            alert: Triggered alert rule
            quote: Current quote
        """
        try:
            await self.notifier.send_alert(alert, quote.price, quote.ts)
        except Exception as e:
            print(f"Error sending alert notification: {e}")


# Global monitor instance
alert_monitor = AlertMonitor()

