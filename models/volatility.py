import numpy as np
from collections import deque
from typing import List

class VolatilityCalculator:
    def __init__(self, window_size: int = 100):
        self.price_history = deque(maxlen=window_size)
        self.returns_history = deque(maxlen=window_size-1)
        
    def update(self, price: float) -> float:
        """Update with new price and return current volatility"""
        if len(self.price_history) > 0:
            prev_price = self.price_history[-1]
            if prev_price > 0:
                ret = np.log(price/prev_price)
                self.returns_history.append(ret)
        
        self.price_history.append(price)
        return self.calculate()
    
    def calculate(self) -> float:
        """Calculate annualized volatility"""
        if len(self.returns_history) < 2:
            return 0.0
        return np.std(self.returns_history) * np.sqrt(365 * 24 * 60)  # Annualized minute volatility
    
    def get_historical_volatility(self, periods: int) -> List[float]:
        """Get rolling volatility for last N periods"""
        if len(self.returns_history) < periods:
            return []
        
        volatilities = []
        for i in range(len(self.returns_history) - periods + 1):
            window = list(self.returns_history)[i:i+periods]
            volatilities.append(np.std(window) * np.sqrt(365 * 24 * 60))
        
        return volatilities