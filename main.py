from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from cryptofeed import FeedHandler
from cryptofeed.exchanges import OKX
from cryptofeed.types import OrderBook, Trade
from models import SlippageCalculator, VolatilityEstimator
from ui.components.order_book import OrderBookVisualization

# Initialize components
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
slippage_model = SlippageCalculator()
volatility_model = VolatilityEstimator()
book_viz = OrderBookVisualization()

# Store current state
current_book = None
current_trade = None

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("OKX Trade Simulator POC"),
            dcc.Interval(id='update', interval=1000)
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Order Book"),
            dcc.Graph(id='order-book', figure=book_viz.create_figure(OrderBook('BTC-USDT')))
        ], width=6),
        dbc.Col([
            html.H3("Execution Metrics"),
            html.Div(id='slippage-metrics'),
            html.Div(id='volatility-metrics'),
            html.Div(id='latency-metrics')
        ], width=6)
    ])
])

# Callbacks
@app.callback(
    [Output('order-book', 'figure'),
     Output('slippage-metrics', 'children'),
     Output('volatility-metrics', 'children')],
    Input('update', 'n_intervals')
)
def update_ui(n):
    """Update all UI components"""
    global current_book, current_trade
    
    # Update order book visualization
    fig = book_viz.update_figure(book_viz.create_figure(OrderBook('BTC-USDT')), current_book)
    
    # Calculate slippage metrics
    slippage = slippage_model.estimate(current_book, 100) if current_book else {}
    
    # Get volatility metrics
    volatility = volatility_model.current_volatility() if current_trade else {}
    
    return (
        fig,
        html.Div([
            html.H4("Slippage Estimation"),
            html.P(f"Expected: {slippage.get('expected', 0):.4f}%"),
            html.P(f"Worst Case: {slippage.get('worst_case', 0):.4f}%"),
            html.P(f"Liquidity Shortfall: {slippage.get('liquidity_shortfall', 0):.2%}")
        ]),
        html.Div([
            html.H4("Volatility Metrics"),
            html.P(f"Instant: {volatility.get('instantaneous', 0):.4f}"),
            html.P(f"Short-Term: {volatility.get('short_term', 0):.4f}"),
            html.P(f"Long-Term: {volatility.get('long_term', 0):.4f}")
        ])
    )

def start_feed_handler():
    """Initialize and run cryptofeed"""
    def book_update(book: OrderBook, timestamp: float):
        global current_book
        current_book = book
        # Additional processing if needed
    
    def trade_update(trade: Trade, timestamp: float):
        global current_trade
        current_trade = trade
        volatility_model.update(trade)
        # Additional processing if needed
    
    fh = FeedHandler()
    fh.add_feed(OKX(
        symbols=['BTC-USDT'],
        channels=['book', 'trades'],
        callbacks={
            'book': book_update,
            'trades': trade_update
        }
    ))
    fh.run()
