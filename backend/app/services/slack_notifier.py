"""
Slack webhook notifier.
"""

import json
from typing import Optional

import aiohttp

from app.config import settings
from app.models import AlertRule


class SlackNotifier:
    """
    Sends notifications to Slack via webhook.
    """
    
    def __init__(self):
        """Initialize Slack notifier."""
        self.webhook_url = settings.SLACK_WEBHOOK_URL
    
    def is_configured(self) -> bool:
        """Check if Slack webhook is configured."""
        return bool(self.webhook_url)
    
    async def send_alert(self, alert: AlertRule, quote_price: float, quote_ts: str) -> bool:
        """
        Send alert notification to Slack.
        
        Args:
            alert: Triggered alert rule
            quote_price: Current price
            quote_ts: Quote timestamp
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            print(f"Slack webhook not configured, skipping alert: {alert.id}")
            return False
        
        # Format message
        message = self._format_message(alert, quote_price, quote_ts)
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": message,
                    "username": "Market Alert",
                    "icon_emoji": ":chart_with_upwards_trend:"
                }
                
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"Failed to send Slack notification: {response.status}")
                        return False
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False
    
    def _format_message(self, alert: AlertRule, price: float, ts: str) -> str:
        """
        Format alert message for Slack.
        
        Args:
            alert: Alert rule
            price: Current price
            ts: Timestamp
            
        Returns:
            Formatted message string
        """
        kind_labels = {
            "price_above": "Price Above",
            "price_below": "Price Below",
            "pct_move": "Percentage Move"
        }
        
        kind_label = kind_labels.get(alert.kind, alert.kind)
        
        message = f"🚨 *Alert Triggered*\n\n"
        message += f"*Symbol:* {alert.symbol}\n"
        message += f"*Alert Type:* {kind_label}\n"
        message += f"*Threshold:* ${alert.threshold:,.2f}\n"
        message += f"*Current Price:* ${price:,.2f}\n"
        message += f"*Time:* {ts}\n"
        
        return message
    
    async def send_test_alert(self) -> bool:
        """
        Send a test alert to verify Slack integration.
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": "🧪 *Test Alert*\n\nThis is a test notification from Market Data Dashboard.",
                    "username": "Market Alert",
                    "icon_emoji": ":test_tube:"
                }
                
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error sending test Slack notification: {e}")
            return False

