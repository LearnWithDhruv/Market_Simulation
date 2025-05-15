import numpy as np
from cryptofeed.exchanges.okx import OKX
from cryptofeed.connection import WebsocketConnection

class AlmgrenChriss:
    def __init__(self, volatility=0.02, risk_aversion=0.1):
        self.volatility = volatility
        self.risk_aversion = risk_aversion
        self.conn = WebsocketConnection(OKX)

    def calculate_impact(self, quantity: float, book_data: dict):
        """Calculate market impact using Almgren-Chriss model"""
        bids, asks = book_data['bids'], book_data['asks']
        spread = asks[0][0] - bids[0][0]
        mid_price = (asks[0][0] + bids[0][0]) / 2
        
        # Temporary impact (linear)
        temp_impact = (spread / mid_price) * quantity
        
        # Permanent impact (square root)
        perm_impact = self.volatility * np.sqrt(quantity)
        
        return {
            'temporary': temp_impact,
            'permanent': perm_impact,
            'total': temp_impact + perm_impact,
            'execution_price': mid_price * (1 + temp_impact + perm_impact)
        }