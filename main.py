import asyncio
from decimal import Decimal
from typing import Dict, List, Tuple
from threading import Thread
from collections import deque
import logging
import numpy as np
from models.algren_chriss import AlmgrenChriss
from models.slippage import SlippageModel
from models.fee_model import FeeModel
from cryptofeed import FeedHandler
from cryptofeed.exchanges import OKX
from cryptofeed.defines import L2_BOOK, TRADES
from cryptofeed.types import OrderBook

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("trade_simulator")

class TradeAnalytics:
    def __init__(self, window_size=500):
        self.slippage_history = deque(maxlen=window_size)
        self.latency_history = deque(maxlen=window_size)
        self.trade_history = deque(maxlen=1000)
        
    def record_latency(self, timestamp: float, receipt_timestamp: float):
        self.latency_history.append((receipt_timestamp - timestamp) * 1000)
        
    def calculate_slippage(self, book: dict, quantity: float, is_buy: bool) -> float:
        levels = book['asks'] if is_buy else book['bids']
        filled, total_cost = 0.0, 0.0
        
        for price, size in levels:
            if filled >= quantity:
                break
            fill_amount = min(float(size), quantity - filled)
            total_cost += fill_amount * float(price)
            filled += fill_amount
            
        if filled == 0:
            return 0.0
            
        avg_price = total_cost / quantity
        slippage = (avg_price - float(levels[0][0])) / float(levels[0][0]) * 100
        self.slippage_history.append(slippage)
        return slippage

    def update_trades(self, trade: dict):
        self.trade_history.append(trade)
        
    def calculate_maker_taker_ratio(self) -> float:
        if not self.trade_history:
            return 0.5
        maker_trades = sum(1 for t in self.trade_history if t.get('maker'))
        return maker_trades / len(self.trade_history)

class VolatilityCalculator:
    def __init__(self, window=100):
        self.returns = deque(maxlen=window)
        self.last_price = None
        
    def update(self, price: float) -> float:
        if self.last_price:
            ret = np.log(price / self.last_price)
            self.returns.append(ret)
        self.last_price = price
        return np.std(self.returns) * np.sqrt(365) if self.returns else 0.03

class TradeSimulator:
    def __init__(self, config: dict):
        self.config = config
        self.analytics = TradeAnalytics()
        self.volatility = VolatilityCalculator()
        
        # Initialize models
        self.ac_model = AlmgrenChriss(
            volatility=config.get('volatility', 0.03),
            liquidity=config.get('liquidity', 1_000_000)
        )
        self.slippage_model = SlippageModel()
        self.fee_model = FeeModel()
        
        # Setup feed handler
        self.fh = FeedHandler()
        self.setup_feeds()

    def setup_feeds(self):
        """Configure WebSocket subscriptions"""
        self.fh.add_feed(
            OKX(
                symbols=[self.config['symbol']],
                channels=[L2_BOOK, TRADES],
                callbacks={
                    L2_BOOK: self.book_callback,
                    TRADES: self.trade_callback
                }
            )
        )

    async def book_callback(self, book: OrderBook, timestamp: float, receipt_timestamp: float):
        """Process order book updates"""
        try:
            # Update latency tracking
            self.analytics.record_latency(timestamp, receipt_timestamp)
            
            # Calculate current volatility
            current_price = float(book.book.asks.peekitem(0)[0])
            vol = self.volatility.update(current_price)
            self.ac_model.update_volatility(vol)
            
            # Calculate metrics
            metrics = self.calculate_metrics(book)
            self.log_metrics(metrics, timestamp)
            
            # Update UI through queue if running
            if hasattr(self, 'ui_queue'):
                self.ui_queue.put(metrics)
                
        except Exception as e:
            logger.error(f"Book callback error: {str(e)}", exc_info=True)

    def calculate_metrics(self, book: OrderBook) -> dict:
        """Calculate all required metrics"""
        quantity_btc = self.config['quantity'] / float(book.book.asks.peekitem(0)[0])
        
        return {
            'slippage': self.analytics.calculate_slippage(
                {'asks': list(book.book.asks.items())},
                quantity_btc,
                is_buy=True
            ),
            'fees': self.fee_model.calculate_fee(
                exchange='OKX',
                tier=self.config['fee_tier'],
                notional=self.config['quantity'],
                is_maker=False
            ),
            'market_impact': self.ac_model.optimal_execution(quantity_btc)[-1],
            'maker_taker': self.analytics.calculate_maker_taker_ratio(),
            'latency': self.analytics.latency_history[-1],
            'book_snapshot': {
                'bids': list(book.book.bids.items())[:15],
                'asks': list(book.book.asks.items())[:15]
            }
        }

    def log_metrics(self, metrics: dict, timestamp: float):
        """Log metrics to console"""
        logger.info(
            f"Metrics @ {timestamp:.2f}\n"
            f"• Slippage: {metrics['slippage']:.4f}%\n"
            f"• Fees: ${metrics['fees']:.4f}\n"
            f"• Market Impact: {metrics['market_impact']:.6f} BTC\n"
            f"• Maker/Taker: {metrics['maker_taker']:.2%}\n"
            f"• Latency: {metrics['latency']:.2f}ms\n"
            f"• Current Volatility: {self.volatility.last_volatility:.2%}"
        )

    async def trade_callback(self, trade: dict, timestamp: float, _):
        """Process trade updates"""
        self.analytics.update_trades(trade)

    def run(self, ui_mode=False):
        """Start the simulator"""
        try:
            logger.info(f"Starting simulator for {self.config['symbol']}")
            
            if ui_mode:
                from ui.app import start_ui
                self.ui_queue = start_ui(self)
                
            self.fh.run()
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            if hasattr(self, 'ui_queue'):
                self.ui_queue.put(None)  # Signal UI to shutdown

if __name__ == "__main__":
    config = {
        'symbol': 'BTC-USDT-SWAP',
        'quantity': 100,  # USD
        'fee_tier': 1,
        'volatility': 0.03,
        'liquidity': 1_000_000
    }
    
    simulator = TradeSimulator(config)
    
    # Run with UI (set ui_mode=False for console only)
    simulator.run(ui_mode=True)