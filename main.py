import asyncio
import threading
from cryptofeed import FeedHandler
from ui.app import app, start_feed_handler

def run_ui():
    """Run Dash application"""
    app.run_server(debug=True, host='0.0.0.0', port=8050)

def run_feed():
    """Run cryptofeed in background"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_feed_handler()

if __name__ == '__main__':
    # Start cryptofeed in background thread
    feed_thread = threading.Thread(target=run_feed, daemon=True)
    feed_thread.start()
    
    # Start UI in main thread
    run_ui()
