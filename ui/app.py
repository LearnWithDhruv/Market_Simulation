import dash
from dash import dcc, html, Input, Output
from cryptofeed import FeedHandler
from cryptofeed.exchanges.okx import OKX
from models import AlmgrenChriss, SlippageModel

app = dash.Dash(__name__)

# Initialize models
ac_model = AlmgrenChriss()
slip_model = SlippageModel()

app.layout = html.Div([
    html.H1("OKX Trade Simulator"),
    dcc.Interval(id='update', interval=1000),
    html.Div(id='metrics-output'),
    dcc.Graph(id='order-book')
])

@app.callback(
    Output('metrics-output', 'children'),
    Input('update', 'n_intervals')
)
def update_metrics(n):
    """Callback for updating metrics"""
    # Get current book data from cryptofeed
    current_book = get_current_book()  
    
    # Calculate metrics
    impact = ac_model.calculate_impact(100, current_book)
    slippage = slip_model.predict(current_book, 100)
    
    return html.Div([
        html.H3("Execution Metrics"),
        html.P(f"Market Impact: {impact['total']:.4f}"),
        html.P(f"Expected Slippage: {slippage:.4f}")
    ])

def start_feed():
    """Start cryptofeed in background"""
    def book_update(book):
        global current_book
        current_book = book
        
    fh = FeedHandler()
    fh.add_feed(OKX(symbols=['BTC-USDT'], callbacks={'book': book_update}))
    fh.run()