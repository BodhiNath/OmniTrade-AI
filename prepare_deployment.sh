#!/bin/bash

# OmniTrade AI - Deployment Preparation Script
# This script prepares the system for deployment

set -e

echo "================================================"
echo "OmniTrade AI - Deployment Preparation"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: Must run from omnitrade-ai directory${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Running from correct directory"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file not found, creating from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠${NC} Please edit .env and add your API keys before deployment!"
    echo ""
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs data backend/app/api backend/app/models
echo -e "${GREEN}✓${NC} Directories created"

# Create __init__.py files for Python modules
echo "Creating Python module files..."
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/core/__init__.py
touch backend/app/brokers/__init__.py
touch backend/app/strategies/__init__.py
touch backend/app/models/__init__.py
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py
echo -e "${GREEN}✓${NC} Python modules initialized"

# Check Docker installation
echo ""
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker not found. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker is installed"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗${NC} Docker Compose not found. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker Compose is installed"

# Validate .env file
echo ""
echo "Validating configuration..."
if grep -q "your-alpaca-api-key" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Warning: Alpaca API keys not configured"
fi

if grep -q "your-binance-api-key" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Warning: Binance API keys not configured"
fi

if grep -q "ENABLE_TRADING=true" .env 2>/dev/null; then
    echo -e "${RED}⚠ WARNING: TRADING IS ENABLED!${NC}"
    echo "Make sure you've tested thoroughly before enabling live trading!"
fi

# Check if trading is disabled (safety check)
if grep -q "ENABLE_TRADING=false" .env 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Trading is disabled (safe mode)"
fi

# Create deployment package
echo ""
echo "Creating deployment package..."
DEPLOY_DIR="deployment"
mkdir -p $DEPLOY_DIR

# Create tarball
tar -czf $DEPLOY_DIR/omnitrade-ai-$(date +%Y%m%d-%H%M%S).tar.gz \
    --exclude='deployment' \
    --exclude='logs/*' \
    --exclude='data/*' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    .

echo -e "${GREEN}✓${NC} Deployment package created in $DEPLOY_DIR/"

# Generate deployment checklist
cat > $DEPLOY_DIR/DEPLOYMENT_CHECKLIST.md << 'EOF'
# OmniTrade AI - Deployment Checklist

## Pre-Deployment

- [ ] Obtained Alpaca API keys (paper trading)
- [ ] Obtained Binance API keys (testnet)
- [ ] Created Telegram bot (optional)
- [ ] Configured .env file with all keys
- [ ] Verified ENABLE_TRADING=false
- [ ] Verified ALPACA_LIVE_MODE=false
- [ ] Verified BINANCE_TESTNET=true

## Initial Deployment

- [ ] Uploaded project to server
- [ ] Installed Docker and Docker Compose
- [ ] Configured .env file
- [ ] Started services: `docker-compose up -d`
- [ ] Verified health endpoint: `curl http://localhost:8000/health`
- [ ] Checked logs: `docker-compose logs -f`

## Paper Trading Testing (Minimum 1 Week)

- [ ] Started trading engine via API
- [ ] Executed test trades on multiple symbols
- [ ] Verified risk management triggers
- [ ] Monitored stop-loss execution
- [ ] Checked circuit breakers activate correctly
- [ ] Reviewed all logs for errors
- [ ] Confirmed notifications working
- [ ] Tested emergency stop procedures

## Performance Validation

- [ ] Reviewed trade logs for accuracy
- [ ] Analyzed P&L calculations
- [ ] Verified position sizing correct
- [ ] Confirmed stop-loss placement
- [ ] Checked exposure limits enforced
- [ ] Validated strategy signals

## Live Trading Preparation (Only After Extensive Testing)

- [ ] Completed minimum 1 week paper trading
- [ ] Reviewed and understood all risks
- [ ] Funded live account with small amount
- [ ] Updated .env: ALPACA_LIVE_MODE=true
- [ ] Updated .env: BINANCE_TESTNET=false
- [ ] Reduced position sizes for initial live trading
- [ ] Set up monitoring alerts
- [ ] Prepared emergency stop procedure

## Go Live (PROCEED WITH EXTREME CAUTION)

- [ ] Updated .env: ENABLE_TRADING=true
- [ ] Restarted services: `docker-compose restart`
- [ ] Started trading engine
- [ ] Monitoring logs continuously
- [ ] Telegram notifications active
- [ ] Emergency stop procedure ready

## Post-Deployment Monitoring

- [ ] Check logs every 4 hours (first 24h)
- [ ] Review all trades daily
- [ ] Monitor risk metrics
- [ ] Verify notifications
- [ ] Backup databases weekly
- [ ] Review and adjust parameters monthly

## Emergency Procedures

### Stop Trading Immediately
```bash
# Method 1: API
curl -X POST http://localhost:8000/api/v1/system/control \
  -d '{"action": "stop"}'

# Method 2: Disable in config
# Edit .env: ENABLE_TRADING=false
docker-compose restart backend

# Method 3: Stop container
docker-compose stop backend
```

### Close All Positions
- Access broker dashboard directly
- Or use API close endpoints

## Important Reminders

⚠️ **NEVER enable live trading without extensive paper trading**
⚠️ **START WITH SMALL CAPITAL**
⚠️ **MONITOR CONTINUOUSLY**
⚠️ **UNDERSTAND ALL RISKS**
⚠️ **HAVE EMERGENCY PROCEDURES READY**

Trading involves substantial risk of loss. Use at your own risk.
EOF

echo -e "${GREEN}✓${NC} Deployment checklist created"

# Print summary
echo ""
echo "================================================"
echo -e "${GREEN}Deployment preparation complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Review DEPLOYMENT_GUIDE.md"
echo "3. Review deployment/$DEPLOY_DIR/DEPLOYMENT_CHECKLIST.md"
echo "4. Start with: docker-compose up -d"
echo "5. Test thoroughly with paper trading"
echo ""
echo -e "${RED}⚠ IMPORTANT: Never enable live trading without extensive testing!${NC}"
echo ""

