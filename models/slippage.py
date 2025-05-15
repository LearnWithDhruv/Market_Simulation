from sklearn.linear_model import LinearRegression
from cryptofeed.exchanges.okx import OKX

class SlippageModel:
    def __init__(self):
        self.model = LinearRegression()
        self.okx = OKX()
        
    def train(self, historical_data):
        """Train model with historical data"""
        X = [[d['quantity'], d['spread'], d['imbalance']] for d in historical_data]
        y = [d['slippage'] for d in historical_data]
        self.model.fit(X, y)
    
    def predict(self, current_book, quantity):
        """Predict slippage for given quantity"""
        features = [
            quantity,
            current_book['spread'],
            self._calculate_imbalance(current_book)
        ]
        return self.model.predict([features])[0]
    
    def _calculate_imbalance(self, book):
        """Calculate order book imbalance"""
        total_bid = sum(amount for price, amount in book['bids'])
        total_ask = sum(amount for price, amount in book['asks'])
        return (total_bid - total_ask) / (total_bid + total_ask)