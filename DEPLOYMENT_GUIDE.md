# OmniTrade AI - Production Deployment Guide

## ⚠️ CRITICAL SAFETY NOTICE

**THIS IS A REAL TRADING SYSTEM THAT WILL EXECUTE ACTUAL TRADES WITH REAL MONEY.**

Before enabling live trading:
1. Test thoroughly with paper trading accounts
2. Start with small position sizes
3. Monitor system closely for at least 1 week
4. Understand all risk parameters
5. Have emergency stop procedures in place

**NEVER enable live trading without extensive testing.**

---

## Prerequisites

### Required Accounts

1. **Alpaca Account** (for stock trading)
   - Sign up at: https://alpaca.markets/
   - Get API keys from dashboard
   - Start with paper trading account

2. **Binance Account** (for crypto trading)
   - Sign up at: https://www.binance.com/
   - Enable API access with trading permissions
   - Start with testnet: https://testnet.binance.vision/

3. **Telegram Bot** (for notifications - optional)
   - Create bot via @BotFather on Telegram
   - Get bot token and your chat ID

### System Requirements

- Linux server (Ubuntu 20.04+ recommended)
- Docker and Docker Compose installed
- Minimum 2GB RAM, 20GB disk space
- Stable internet connection
- PostgreSQL, Redis, InfluxDB (via Docker)

---

## Installation Steps

### 1. Clone/Upload Project

```bash
# Upload the omnitrade-ai directory to your server
cd /home/ubuntu/omnitrade-ai
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Configuration:**

```bash
# Security
SECRET_KEY=your-random-secret-key-here  # Generate with: openssl rand -hex 32

# Database (Docker will create these)
DATABASE_URL=postgresql://omnitrade:omnitrade_password@postgres:5432/omnitrade
REDIS_URL=redis://redis:6379/0
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=omnitrade-token-change-this

# Alpaca (Stock Trading)
ALPACA_API_KEY=your-alpaca-api-key
ALPACA_SECRET_KEY=your-alpaca-secret-key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
ALPACA_LIVE_MODE=false  # KEEP FALSE FOR TESTING

# Binance (Crypto Trading)
BINANCE_API_KEY=your-binance-api-key
BINANCE_SECRET_KEY=your-binance-secret-key
BINANCE_TESTNET=true  # KEEP TRUE FOR TESTING

# Trading Controls
ENABLE_TRADING=false  # MUST BE MANUALLY ENABLED AFTER TESTING

# Notifications (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

### 3. Start Services with Docker

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","trading_engine":false,"trading_enabled":false}
```

---

## API Usage

### Start Trading Engine

```bash
curl -X POST http://localhost:8000/api/v1/system/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### Execute Strategy on Symbol

```bash
# Analyze and potentially trade AAPL stock
curl -X POST http://localhost:8000/api/v1/trade/execute \
  -H "Content-Type: application/json" \
  -d '{
    "broker": "alpaca",
    "symbol": "AAPL",
    "strategy": "technical",
    "indicators": ["rsi", "macd", "bollinger"]
  }'
```

### Get Account Information

```bash
# Alpaca account
curl http://localhost:8000/api/v1/account/alpaca

# Binance account
curl http://localhost:8000/api/v1/account/binance
```

### Get Open Positions

```bash
curl http://localhost:8000/api/v1/positions/alpaca
```

### Close Position

```bash
curl -X POST http://localhost:8000/api/v1/trade/close \
  -H "Content-Type: application/json" \
  -d '{
    "broker": "alpaca",
    "symbol": "AAPL",
    "reason": "manual_exit"
  }'
```

### Get Risk Metrics

```bash
curl http://localhost:8000/api/v1/risk/metrics
```

### Get Current Price

```bash
curl http://localhost:8000/api/v1/market/price/alpaca/AAPL
```

---

## Risk Management Configuration

### Position Sizing

Edit in `.env`:

```bash
MAX_POSITION_SIZE_PCT=5.0        # Max 5% of portfolio per trade
MAX_PORTFOLIO_EXPOSURE_PCT=80.0  # Max 80% total exposure
DEFAULT_STOP_LOSS_PCT=2.0        # 2% stop loss per trade
```

### Circuit Breakers

```bash
DAILY_LOSS_LIMIT_PCT=10.0        # Halt trading after 10% daily loss
MAX_CONSECUTIVE_LOSSES=5         # Pause after 5 consecutive losses
```

### Trading Controls

```bash
ENABLE_TRADING=false             # Master trading switch
TRADING_HOURS_ONLY=true          # Only trade during market hours
MIN_ORDER_SIZE_USD=10.0          # Minimum order size
MAX_OPEN_POSITIONS=20            # Maximum concurrent positions
```

---

## Monitoring & Logs

### View Logs

```bash
# Application logs
tail -f logs/omnitrade.log

# Trade logs
tail -f logs/trades.log

# Risk events
tail -f logs/risk.log

# Errors only
tail -f logs/errors.log
```

### Docker Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database
docker-compose logs -f postgres
```

---

## Enabling Live Trading

### ⚠️ CRITICAL STEPS - READ CAREFULLY

1. **Complete Paper Trading Testing**
   - Run for minimum 1 week with paper trading
   - Verify all strategies work as expected
   - Confirm risk management triggers correctly
   - Review all logs for errors

2. **Switch to Live Broker Accounts**

```bash
# Edit .env
ALPACA_BASE_URL=https://api.alpaca.markets  # Live API
ALPACA_LIVE_MODE=true

BINANCE_TESTNET=false  # Live Binance
```

3. **Start with Small Capital**
   - Fund account with small amount first
   - Test with minimum position sizes
   - Gradually increase as confidence grows

4. **Enable Trading**

```bash
# Edit .env
ENABLE_TRADING=true
```

5. **Restart Services**

```bash
docker-compose restart backend
```

6. **Monitor Closely**
   - Watch logs continuously for first 24 hours
   - Set up Telegram notifications
   - Have emergency stop procedure ready

---

## Emergency Procedures

### Stop All Trading Immediately

```bash
# Method 1: API
curl -X POST http://localhost:8000/api/v1/system/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'

# Method 2: Disable in config
# Edit .env: ENABLE_TRADING=false
docker-compose restart backend

# Method 3: Stop container
docker-compose stop backend
```

### Close All Positions

Access broker directly:
- Alpaca: https://app.alpaca.markets/
- Binance: https://www.binance.com/

Or use API:
```python
# Emergency close script
import requests

# Close all Alpaca positions
response = requests.get('http://localhost:8000/api/v1/positions/alpaca')
positions = response.json()['positions']

for pos in positions:
    requests.post('http://localhost:8000/api/v1/trade/close', json={
        'broker': 'alpaca',
        'symbol': pos['symbol'],
        'reason': 'emergency_stop'
    })
```

---

## Backup & Recovery

### Backup Database

```bash
# Backup PostgreSQL
docker exec omnitrade-postgres pg_dump -U omnitrade omnitrade > backup.sql

# Backup InfluxDB
docker exec omnitrade-influxdb influx backup /backup
docker cp omnitrade-influxdb:/backup ./influx_backup
```

### Restore Database

```bash
# Restore PostgreSQL
docker exec -i omnitrade-postgres psql -U omnitrade omnitrade < backup.sql

# Restore InfluxDB
docker cp ./influx_backup omnitrade-influxdb:/backup
docker exec omnitrade-influxdb influx restore /backup
```

---

## Performance Optimization

### Increase Resources

Edit `docker-compose.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

### Database Tuning

```bash
# PostgreSQL connection pooling
DATABASE_URL=postgresql://omnitrade:password@postgres:5432/omnitrade?pool_size=20&max_overflow=10
```

---

## Security Best Practices

1. **API Keys**
   - Never commit `.env` to version control
   - Use environment-specific keys
   - Rotate keys regularly
   - Use IP whitelisting on broker accounts

2. **Server Security**
   - Use firewall (UFW)
   - Enable SSH key authentication only
   - Keep system updated
   - Use HTTPS for API access

3. **Access Control**
   - Restrict API access to trusted IPs
   - Use strong SECRET_KEY
   - Enable 2FA on broker accounts

---

## Troubleshooting

### Trading Not Executing

1. Check `ENABLE_TRADING=true` in `.env`
2. Verify broker API keys are correct
3. Check circuit breakers haven't triggered
4. Review logs for errors

### Connection Errors

```bash
# Check broker connectivity
curl http://localhost:8000/api/v1/account/alpaca

# Check Docker services
docker-compose ps

# Restart services
docker-compose restart
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

---

## Maintenance

### Daily Tasks

- Review trade logs
- Check risk metrics
- Monitor system performance
- Verify notifications working

### Weekly Tasks

- Analyze strategy performance
- Review and adjust risk parameters
- Update market data
- Backup databases

### Monthly Tasks

- Rotate API keys
- Update dependencies
- Review and optimize strategies
- Audit system logs

---

## Support & Resources

### Documentation

- Alpaca API: https://alpaca.markets/docs/
- Binance API: https://binance-docs.github.io/
- ccxt Library: https://docs.ccxt.com/

### Community

- Discord: [Your Discord]
- GitHub Issues: [Your Repo]
- Email: [Your Email]

---

## Legal Disclaimer

This software is provided "as is" without warranty of any kind. Trading involves substantial risk of loss. Past performance is not indicative of future results. The developers are not responsible for any financial losses incurred through use of this system.

**USE AT YOUR OWN RISK.**

---

## License

[Your License Here]

---

**Remember: Start with paper trading, test extensively, and never risk more than you can afford to lose.**

