# OmniTrade AI 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://github.com/yourusername/omnitrade-ai/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yourusername/omnitrade-ai/actions)
[![codecov](https://codecov.io/gh/yourusername/omnitrade-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/omnitrade-ai)

**Sovereign-Grade AI-Powered Trading System**

A production-ready, automated trading platform that connects to real broker accounts, analyzes markets using AI and technical analysis, and executes trades automatically with comprehensive risk management.

📚 **[Quick Start](QUICKSTART.md)** | 📖 **[Documentation](ARCHITECTURE.md)** | 🔒 **[Security](SECURITY.md)** | 🤝 **[Contributing](CONTRIBUTING.md)**

---

## ⚠️ WARNING: REAL TRADING SYSTEM

**This system executes REAL trades with REAL money. Losses can and will occur.**

- Start with paper trading accounts
- Test extensively before going live
- Understand all risk parameters
- Never risk more than you can afford to lose
- Monitor the system continuously

**Trading involves substantial risk. Use at your own risk.**

---

## Features

### 🎯 Core Capabilities

- **Multi-Broker Support**: Alpaca (stocks), Binance (crypto)
- **AI-Driven Strategies**: Technical analysis with ML optimization
- **Real-Time Execution**: Automated order placement and management
- **Risk Management**: Position sizing, stop-loss, circuit breakers
- **Portfolio Tracking**: Real-time P&L and performance metrics
- **Notifications**: Telegram, SMS, email alerts

### 📊 Technical Analysis

- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Average Crossovers
- Momentum Indicators
- Combined Multi-Indicator Analysis

### 🛡️ Risk Management

- **Position Sizing**: Automatic calculation based on risk parameters
- **Stop Loss**: Hard stops and trailing stops
- **Circuit Breakers**: Daily loss limits, consecutive loss protection
- **Exposure Limits**: Maximum position size and portfolio exposure
- **Real-Time Monitoring**: Continuous position and risk tracking

### 📈 Monitoring & Logging

- Comprehensive trade logging
- Risk event tracking
- Performance metrics
- System health monitoring
- Real-time notifications

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      OmniTrade AI                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   FastAPI    │  │   Trading    │  │     Risk     │    │
│  │   Backend    │──│    Engine    │──│   Manager    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         │                  │                  │            │
│  ┌──────┴──────┐    ┌─────┴─────┐    ┌──────┴──────┐    │
│  │  Strategies │    │  Brokers  │    │ Notifications│    │
│  │  Technical  │    │  Alpaca   │    │   Telegram   │    │
│  │  Sentiment  │    │  Binance  │    │     SMS      │    │
│  └─────────────┘    └───────────┘    └──────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  PostgreSQL  │  │   InfluxDB   │  │    Redis     │    │
│  │   (Trades)   │  │ (Time Series)│  │   (Cache)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

**New to OmniTrade AI?** Check out our [Quick Start Guide](QUICKSTART.md) for a 10-minute setup!

### 1. Prerequisites

- Docker and Docker Compose
- Broker accounts (Alpaca, Binance)
- Linux server (Ubuntu 20.04+ recommended) or macOS

### 2. Installation

```bash
# Clone/upload project
cd omnitrade-ai

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Verify Installation

```bash
curl http://localhost:8000/health
```

### 4. Start Trading Engine

```bash
curl -X POST http://localhost:8000/api/v1/system/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### 5. Execute Strategy

```bash
curl -X POST http://localhost:8000/api/v1/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "broker": "alpaca",
    "symbol": "AAPL",
    "strategy": "technical"
  }'
```

---

## Configuration

### Environment Variables

Key configuration in `.env`:

```bash
# Trading Controls
ENABLE_TRADING=false              # Master switch
ALPACA_LIVE_MODE=false            # Paper trading
BINANCE_TESTNET=true              # Testnet

# Risk Parameters
MAX_POSITION_SIZE_PCT=5.0         # Max 5% per trade
DEFAULT_STOP_LOSS_PCT=2.0         # 2% stop loss
DAILY_LOSS_LIMIT_PCT=10.0         # 10% daily limit
MAX_CONSECUTIVE_LOSSES=5          # Circuit breaker

# Broker API Keys
ALPACA_API_KEY=your-key
ALPACA_SECRET_KEY=your-secret
BINANCE_API_KEY=your-key
BINANCE_SECRET_KEY=your-secret
```

---

## API Endpoints

### System Control

- `POST /api/v1/system/control` - Start/stop trading engine
- `GET /api/v1/system/status` - Get system status

### Trading

- `POST /api/v1/trade/execute` - Execute strategy
- `POST /api/v1/trade/close` - Close position

### Account & Portfolio

- `GET /api/v1/account/{broker}` - Get account info
- `GET /api/v1/positions/{broker}` - Get open positions

### Risk Management

- `GET /api/v1/risk/metrics` - Get risk metrics
- `POST /api/v1/risk/reset` - Reset daily stats

### Market Data

- `GET /api/v1/market/price/{broker}/{symbol}` - Get current price
- `GET /api/v1/market/bars/{broker}/{symbol}` - Get historical data

---

## Project Structure

```
omnitrade-ai/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core engine & config
│   │   │   ├── config.py
│   │   │   ├── risk_manager.py
│   │   │   └── trading_engine.py
│   │   ├── brokers/          # Broker integrations
│   │   │   ├── alpaca_broker.py
│   │   │   └── binance_broker.py
│   │   ├── strategies/       # Trading strategies
│   │   │   └── technical_strategy.py
│   │   ├── models/           # Data models
│   │   ├── utils/            # Utilities
│   │   │   ├── logger.py
│   │   │   └── notifications.py
│   │   └── main.py           # FastAPI app
│   ├── tests/                # Test suite
│   └── requirements.txt      # Dependencies
├── frontend/                 # Web dashboard (optional)
├── docker/                   # Docker configs
├── logs/                     # Application logs
├── data/                     # Data storage
├── docker-compose.yml        # Services orchestration
├── .env.example              # Config template
├── ARCHITECTURE.md           # Architecture docs
├── DEPLOYMENT_GUIDE.md       # Deployment guide
└── README.md                 # This file
```

---

## Testing

### Run Test Suite

```bash
cd backend
python3.11 -m pytest tests/ -v
```

### Test Coverage

- Risk management: Position sizing, stop-loss, circuit breakers
- Technical analysis: RSI, MACD, Bollinger Bands, MA crossovers
- Trade validation: Size limits, exposure checks
- Strategy signals: Buy/sell signal generation

---

## Monitoring

### View Logs

```bash
# All logs
tail -f logs/omnitrade.log

# Trades only
tail -f logs/trades.log

# Risk events
tail -f logs/risk.log

# Errors
tail -f logs/errors.log
```

### Metrics

- Daily P&L and percentage
- Win rate and profit factor
- Open positions and exposure
- Circuit breaker status
- Consecutive losses

---

## Safety Features

### Circuit Breakers

1. **Daily Loss Limit**: Halts trading after X% daily loss
2. **Consecutive Losses**: Pauses after N losing trades
3. **Max Exposure**: Limits total portfolio exposure
4. **Position Size**: Enforces maximum position size

### Risk Controls

- Automatic position sizing based on risk
- Hard stop-loss on every trade
- Trailing stops for profit protection
- Real-time risk monitoring
- Emergency stop procedures

### Notifications

- Trade execution alerts
- Stop-loss triggers
- Risk event warnings
- Daily performance summary
- System status updates

---

## Roadmap

### Phase 1: MVP ✅
- Single broker integration
- Core technical strategies
- Basic risk management
- API and logging

### Phase 2: Enhancement (In Progress)
- Multi-broker support
- Advanced AI strategies
- Backtesting framework
- Web dashboard

### Phase 3: Advanced (Planned)
- Reinforcement learning
- Sentiment analysis
- News integration
- Portfolio optimization
- Multi-asset strategies

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

---

## License

[Your License]

---

## Disclaimer

**IMPORTANT LEGAL NOTICE**

This software is provided "as is" without warranty of any kind, express or implied. Trading stocks, cryptocurrencies, and other financial instruments involves substantial risk of loss. Past performance is not indicative of future results.

The developers and contributors of this software:
- Are NOT financial advisors
- Do NOT guarantee profits or returns
- Are NOT responsible for any financial losses
- Do NOT provide investment advice

**You are solely responsible for:**
- Understanding the risks involved
- Testing the system thoroughly
- Monitoring your trades
- Managing your capital
- Complying with local regulations

**USE THIS SOFTWARE AT YOUR OWN RISK.**

By using this software, you acknowledge that you understand these risks and accept full responsibility for any outcomes.

---

## Support

- **Documentation**: See `DEPLOYMENT_GUIDE.md`
- **Issues**: GitHub Issues
- **Email**: [Your Email]
- **Discord**: [Your Discord]

---

## Acknowledgments

Built with:
- FastAPI - Modern Python web framework
- Alpaca API - Stock trading
- Binance/ccxt - Crypto trading
- TA-Lib - Technical analysis
- PostgreSQL, Redis, InfluxDB - Data storage

---

**Remember: Start with paper trading. Test extensively. Never risk more than you can afford to lose.**

---

*Made with ⚡ for serious traders*

