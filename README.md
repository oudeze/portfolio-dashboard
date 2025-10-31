# Market Data Dashboard

Personal trading dashboard built with FastAPI and Next.js.

## Setup

### Backend

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run server:
```bash
uvicorn main:app --reload --port 8000
```


### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run dev server:
```bash
npm run dev
```

Front-end run on local 

## Current Features

- Health check endpoint
- Market data provider abstraction (mock + Binance providers)
- Symbols endpoint (`GET /api/symbols`)
- Latest quotes endpoint (`GET /api/quotes/latest?symbol=SYMBOL`)
- WebSocket endpoint (`/api/ws/quotes`) for real-time quotes
- Watchlist page with WebSocket support for live crypto prices
- Alert system with price triggers (price_above, price_below, pct_move)
- Slack webhook notifications for triggered alerts
- Alerts management UI (create, enable/disable, delete, test)
- Trade journal with buy/sell entries
- Position tracking with FIFO average price
- P&L calculation (realized and unrealized)
- Journal and P&L UI
- SQLite database persistence
- Configuration management via environment variables

### Providers

- **Mock Provider**: Random walk prices (default)
- **Binance Provider**: Live crypto prices via WebSocket (no API key required)
  - Set `DATA_PROVIDER=binance` in `.env` to enable

### Alerts

- **Alert Types**: Price above, price below, percentage move
- **Notifications**: Slack webhook integration (optional)
  - Set `SLACK_WEBHOOK_URL` in `.env` to enable
  - Alerts are evaluated on incoming quotes from WebSocket stream

