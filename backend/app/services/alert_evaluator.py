"""
Alert rule evaluator.
"""

from typing import List

from app.models import AlertRule, Quote


class AlertEvaluator:
    """
    Evaluates alert rules against price quotes.
    """
    
    def __init__(self):
        """Initialize evaluator."""
        # Track previous prices for pct_move alerts
        self._previous_prices: dict[str, float] = {}
    
    def evaluate(self, quote: Quote, rules: List[AlertRule]) -> List[AlertRule]:
        """
        Evaluate alert rules against a quote.
        
        Args:
            quote: Current quote
            rules: List of alert rules to evaluate
            
        Returns:
            List of triggered alert rules
        """
        triggered = []
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            if rule.symbol != quote.symbol:
                continue
            
            # Evaluate based on alert kind
            if rule.kind == "price_above":
                if quote.price >= rule.threshold:
                    triggered.append(rule)
            
            elif rule.kind == "price_below":
                if quote.price <= rule.threshold:
                    triggered.append(rule)
            
            elif rule.kind == "pct_move":
                # Calculate percentage change from previous price
                if quote.symbol in self._previous_prices:
                    prev_price = self._previous_prices[quote.symbol]
                    if prev_price > 0:
                        pct_change = abs((quote.price - prev_price) / prev_price) * 100
                        if pct_change >= rule.threshold:
                            triggered.append(rule)
                
                # Update previous price
                self._previous_prices[quote.symbol] = quote.price
            
            else:
                # Unknown alert kind, skip
                continue
        
        return triggered

