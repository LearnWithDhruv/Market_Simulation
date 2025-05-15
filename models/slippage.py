import numpy as np
from sklearn.linear_model import QuantileRegressor
from cryptofeed.types import OrderBook
from cryptofeed.util.book import cumulative_depth, weighted_midpoint

class SlippageCalculator:
    def __init__(self, window_size=1000):
        self.window_size = window_size
        self.history = []
        self.linear_model = self._init_linear_model()
        self.quantile_model = QuantileRegressor(quantile=0.95)
        
    def update_model(self, book: OrderBook, executed_price: float, quantity: float):
        """Update models with new trade execution data"""
        features = self._extract_features(book, quantity)
        actual_slippage = (executed_price - weighted_midpoint(book)) / weighted_midpoint(book)
        
        # Maintain rolling window of samples
        self.history.append((features, actual_slippage))
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        # Retrain models periodically
        if len(self.history) % 100 == 0:
            self._retrain_models()

    def estimate(self, book: OrderBook, quantity: float) -> dict:
        """Estimate slippage for given quantity"""
        features = self._extract_features(book, quantity)
        
        return {
            'expected': float(self.linear_model.predict([features])[0]),
            'worst_case': float(self.quantile_model.predict([features])[0]),
            'liquidity_shortfall': self._calculate_shortfall(book, quantity),
            'features': features
        }

    def _extract_features(self, book: OrderBook, quantity: float) -> list:
        """Create feature vector for prediction"""
        return [
            quantity,
            book.spread(),
            book.imbalance(),
            cumulative_depth(book.bids, 0.05),  # Depth at 5% from mid
            cumulative_depth(book.asks, 0.05),
            np.log(quantity / book.total_volume())
        ]

    def _calculate_shortfall(self, book: OrderBook, quantity: float) -> float:
        """Calculate liquidity shortfall probability"""
        available = cumulative_depth(book.bids, 0.1) + cumulative_depth(book.asks, 0.1)
        return max(0, quantity - available) / quantity
