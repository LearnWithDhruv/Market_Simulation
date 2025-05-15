# CryptoFeed Market Simulation Pipeline

This project is a comprehensive market simulation framework designed around the OKX exchange. It features a custom data feed implementation, market microstructure modeling, and a UI dashboard for real-time insights.

---

## 📁 Project Structure

```
project-root/
├── cryptofeed/                  # Modified cryptofeed components
│   ├── exchanges/
│   │   ├── okx.py               # Core OKX implementation
│   │   └── mixins/okx.py        # Shared OKX functionality
│   └── connection.py            # WebSocket management
├── models/
│   ├── algren_chriss.py         # Market impact model
│   ├── slippage.py              # Slippage estimation
│   ├── fee_model.py             # Fee calculations
│   └── maker_taker.py           # Maker/taker prediction
├── ui/
│   ├── app.py                   # Main application
│   └── components/
│       ├── order_book.py        # Order book visualization
│       └── metrics_dashboard.py # Performance metrics
├── config/
│   ├── settings.yaml            # Configuration
│   └── okx_config.py            # OKX-specific settings
├── tests/
│   ├── test_slippage.py
│   ├── test_market_impact.py
│   └── test_fee_model.py
└── main.py                      # Entry point
```

---

## ⚙️ Pipeline Overview

### 1. **Exchange Connection** (`cryptofeed/`)
- `okx.py`: Implements OKX WebSocket feeds, subscribing to trades, order books, and funding rates.
- `mixins/okx.py`: Provides reusable methods for authentication and message parsing.
- `connection.py`: Manages asynchronous WebSocket connections.

### 2. **Market Microstructure Models** (`models/`)
- `algren_chriss.py`: Implements the Almgren-Chriss optimal execution model to simulate trade impact over time.
- `slippage.py`: Estimates slippage based on historical order book data.
- `fee_model.py`: Models exchange-specific fees, accounting for maker/taker structures.
- `maker_taker.py`: Predicts the probability of a trade being a maker or taker.

### 3. **UI Dashboard** (`ui/`)
- `app.py`: Initializes and launches the Streamlit-based dashboard.
- `components/order_book.py`: Displays real-time order book depth and market data.
- `metrics_dashboard.py`: Visualizes KPIs such as slippage, fees, and execution quality.

### 4. **Configuration** (`config/`)
- `settings.yaml`: Stores global settings such as exchange endpoints, tokens, and logging levels.
- `okx_config.py`: Contains detailed configurations for OKX, including endpoints and subscription parameters.

### 5. **Testing** (`tests/`)
- Unit tests for each model to ensure correctness and stability using historical and mock data.

### 6. **Entry Point** (`main.py`)
- Orchestrates the entire pipeline by initializing configurations, launching data feeds, loading models, and starting the UI.

---

## 🚀 How to Run

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Set your OKX API keys and config in `config/settings.yaml`

# Step 3: Run the main pipeline
python main.py
```

---

## 🧪 Running Tests

```bash
pytest tests/
```

---

## 📊 Output

- Real-time order book and trade feed from OKX
- Market impact simulations and KPIs
- Dashboard for monitoring execution metrics and slippage

---

## 📬 Contact

For inquiries, contact [Your Name] at [Your Email].
