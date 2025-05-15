import dash_core_components as dcc
import plotly.graph_objs as go
from cryptofeed.types import OrderBook

class OrderBookVisualization:
    def __init__(self, depth_levels=20):
        self.depth_levels = depth_levels
        
    def create_figure(self, book: OrderBook) -> go.Figure:
        """Generate Plotly figure from order book"""
        bids = sorted(book.bids.items(), reverse=True)[:self.depth_levels]
        asks = sorted(book.asks.items())[:self.depth_levels]
        
        bid_prices, bid_sizes = zip(*bids) if bids else ([], [])
        ask_prices, ask_sizes = zip(*asks) if asks else ([], [])
        
        return go.Figure(
            data=[
                go.Bar(x=bid_sizes, y=bid_prices, 
                       orientation='h', name='Bids',
                       marker=dict(color='green')),
                go.Bar(x=ask_sizes, y=ask_prices,
                       orientation='h', name='Asks',
                       marker=dict(color='red'))
            ],
            layout=go.Layout(
                title='Order Book Depth',
                yaxis=dict(title='Price'),
                xaxis=dict(title='Size'),
                barmode='relative',
                hovermode='closest'
            )
        )
    
    def update_figure(self, fig: go.Figure, book: OrderBook) -> go.Figure:
        """Update existing figure with new data"""
        bids = sorted(book.bids.items(), reverse=True)[:self.depth_levels]
        asks = sorted(book.asks.items())[:self.depth_levels]
        
        with fig.batch_update():
            fig.data[0].x = [size for _, size in bids]
            fig.data[0].y = [price for price, _ in bids]
            fig.data[1].x = [size for _, size in asks]
            fig.data[1].y = [price for price, _ in asks]
        return fig
