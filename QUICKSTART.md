# OmniTrade AI - Quick Start Guide

Get OmniTrade AI up and running in 10 minutes!

## ⚠️ Before You Start

**CRITICAL SAFETY NOTICE**:
- This system executes REAL trades with REAL money
- ALWAYS start with paper trading/testnet accounts
- Test thoroughly before using live trading
- Never risk more than you can afford to lose

---

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended) or macOS
- Docker and Docker Compose installed
- Broker accounts (Alpaca and/or Binance)
- Basic command line knowledge

## Installation Steps

### 1. Get the Code

```bash
# Clone the repository
git clone https://github.com/yourusername/omnitrade-ai.git
cd omnitrade-ai
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

**Minimum Required Configuration**:

```bash
# Generate a secret key
SECRET_KEY=$(openssl rand -hex 32)

# Alpaca (Paper Trading)
ALPACA_API_KEY=your-alpaca-api-key
ALPACA_SECRET_KEY=your-alpaca-secret-key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
ALPACA_LIVE_MODE=false

# Binance (Testnet)
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key
BINANCE_TESTNET=true

# Safety Settings
ENABLE_TRADING=false  # KEEP FALSE UNTIL TESTED!
```

**Getting API Keys**:

- **Alpaca**: Sign up at https://alpaca.markets/ → Dashboard → API Keys
- **Binance Testnet**: https://testnet.binance.vision/ → Login → API Management

### 3. Validate Configuration

```bash
# Run validation script
./scripts/validate_deployment.sh
```

This checks:
- ✓ Environment variables are set
- ✓ File permissions are correct
- ✓ Docker is installed
- ✓ Safety settings are configured

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "trading_engine": false,
#   "trading_enabled": false
# }
```

---

## Basic Usage

### Start Trading Engine

```bash
curl -X POST http://localhost:8000/api/v1/system/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### Execute a Strategy

```bash
# Analyze AAPL stock
curl -X POST http://localhost:8000/api/v1/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "broker": "alpaca",
    "symbol": "AAPL",
    "strategy": "technical",
    "indicators": ["rsi", "macd", "bollinger"]
  }'
```

### Check Account Status

```bash
# Get account info
curl http://localhost:8000/api/v1/account/alpaca

# Get open positions
curl http://localhost:8000/api/v1/positions/alpaca

# Get risk metrics
curl http://localhost:8000/api/v1/risk/metrics
```

### Stop Trading Engine

```bash
curl -X POST http://localhost:8000/api/v1/system/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

---

## Monitoring

### View Logs

```bash
# Application logs
tail -f logs/omnitrade.log

# Trade logs
tail -f logs/trades.log

# Risk events
tail -f logs/risk.log

# Docker logs
docker-compose logs -f backend
```

### Check System Status

```bash
# System status
curl http://localhost:8000/api/v1/system/status
```

---

## Common Tasks

### Close All Positions

```bash
# Close all Alpaca positions
POSITIONS=$(curl -s http://localhost:8000/api/v1/positions/alpaca)
# Parse and close each position (requires jq)
echo $POSITIONS | jq -r '.positions[].symbol' | while read symbol; do
    curl -X POST http://localhost:8000/api/v1/trade/close \
      -H "Content-Type: application/json" \
      -d "{\"broker\": \"alpaca\", \"symbol\": \"$symbol\", \"reason\": \"manual_close\"}"
done
```

### Reset Daily Risk Stats

```bash
curl -X POST http://localhost:8000/api/v1/risk/reset
```

### Get Current Price

```bash
curl http://localhost:8000/api/v1/market/price/alpaca/AAPL
```

---

## Testing Before Live Trading

### 1. Paper Trading Phase (1-2 weeks)

```bash
# In .env file:
ALPACA_LIVE_MODE=false  # Paper trading
BINANCE_TESTNET=true    # Testnet
ENABLE_TRADING=true     # Allow trades
```

**Daily Checklist**:
- [ ] Check trade logs for accuracy
- [ ] Verify risk management triggers
- [ ] Review position sizing
- [ ] Test stop-loss execution
- [ ] Monitor for errors

### 2. Small Capital Test (1 week)

```bash
# In .env file:
ALPACA_LIVE_MODE=true   # LIVE trading
BINANCE_TESTNET=false   # LIVE trading
ENABLE_TRADING=true

# Adjust risk parameters for small amounts:
MAX_POSITION_SIZE_PCT=1.0      # Only 1% per trade
DAILY_LOSS_LIMIT_PCT=2.0       # Stop after 2% loss
MAX_CONSECUTIVE_LOSSES=3       # Stop after 3 losses
```

Fund account with **small amount** you can afford to lose completely.

### 3. Gradual Scale-Up

After successful small capital test:
- Increase position sizes gradually
- Monitor performance continuously
- Adjust risk parameters based on results

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker daemon
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### API Returns Errors

```bash
# Check broker API keys are correct
# Check broker API status (may be down)
# Review backend logs for details
docker-compose logs backend
```

### Trading Not Executing

**Check**:
1. `ENABLE_TRADING=true` in .env
2. Broker API keys are valid
3. Trading engine is started
4. Circuit breakers haven't triggered
5. Account has sufficient funds

```bash
# Check system status
curl http://localhost:8000/api/v1/system/status

# Check risk metrics
curl http://localhost:8000/api/v1/risk/metrics
```

### Cannot Access Logs

```bash
# Check log directory permissions
ls -la logs/

# Fix permissions
chmod 755 logs
```

---

## Emergency Procedures

### 🚨 STOP ALL TRADING IMMEDIATELY

```bash
# Method 1: API
curl -X POST http://localhost:8000/api/v1/system/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'

# Method 2: Disable in config
# Edit .env: ENABLE_TRADING=false
docker-compose restart backend

# Method 3: Stop containers
docker-compose stop backend
```

### 🚨 CLOSE ALL POSITIONS

Access broker directly:
- **Alpaca**: https://app.alpaca.markets/ → Positions → Close All
- **Binance**: https://www.binance.com/ → Spot/Futures → Close All

---

## Next Steps

1. **Read Full Documentation**
   - `README.md` - Complete overview
   - `ARCHITECTURE.md` - System design
   - `DEPLOYMENT_GUIDE.md` - Production deployment
   - `SECURITY.md` - Security best practices

2. **Configure Notifications**
   - Set up Telegram bot for alerts
   - Configure SMS for critical events
   - See DEPLOYMENT_GUIDE.md for instructions

3. **Customize Strategies**
   - Review `backend/app/strategies/`
   - Adjust indicator parameters
   - Backtest before live use

4. **Set Up Monitoring**
   - Configure alerts
   - Set up performance tracking
   - Establish regular review schedule

---

## Support & Resources

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Security**: security@omnitrade.ai
- **Community**: Discord (link in README)

---

## Safety Checklist

Before enabling live trading:

- [ ] Tested with paper trading for at least 1 week
- [ ] All strategies perform as expected
- [ ] Risk management triggers correctly
- [ ] Stop-loss works properly
- [ ] Understand all configuration parameters
- [ ] Have emergency stop procedures ready
- [ ] Monitoring and alerts configured
- [ ] Using only funds you can afford to lose
- [ ] Reviewed all documentation
- [ ] Understand this is high-risk activity

---

**Remember**: Trading involves substantial risk of loss. Start small, test thoroughly, and never risk more than you can afford to lose!

---

*Last updated: January 2025*
