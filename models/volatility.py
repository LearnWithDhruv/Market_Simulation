import numpy as np
from collections import deque
from cryptofeed.types import Trade

class VolatilityEstimator:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.price_history = deque(maxlen=window_size)
        self.returns = deque(maxlen=window_size-1)
        
    def update(self, trade: Trade):
        """Update with new trade data"""
        if len(self.price_history) > 0:
            prev_price = self.price_history[-1]
            self.returns.append((trade.price - prev_price) / prev_price)
        self.price_history.append(trade.price)
    
    def current_volatility(self) -> dict:
        """Calculate current volatility metrics"""
        if len(self.returns) < 2:
            return {'instantaneous': 0, 'short_term': 0, 'long_term': 0}
        
        returns = np.array(self.returns)
        return {
            'instantaneous': abs(self.returns[-1]),
            'short_term': np.std(returns[-10:]) * np.sqrt(365*24),  # Annualized
            'long_term': np.std(returns) * np.sqrt(365*24),
            'current_price': self.price_history[-1]
        }
