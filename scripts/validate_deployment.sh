#!/bin/bash

##############################################################################
# OmniTrade AI - Deployment Validation Script
# 
# This script validates that all required components are properly configured
# before starting the trading system.
#
# Usage: ./scripts/validate_deployment.sh
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
CHECKS=0

echo "======================================================================"
echo "          OmniTrade AI - Deployment Validation"
echo "======================================================================"
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2
    CHECKS=$((CHECKS + 1))
    
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
        WARNINGS=$((WARNINGS + 1))
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}✗${NC} $message"
        ERRORS=$((ERRORS + 1))
    fi
}

# Check if .env file exists
echo "📋 Checking configuration files..."
if [ -f ".env" ]; then
    print_status "OK" ".env file exists"
else
    print_status "ERROR" ".env file not found. Copy .env.example to .env"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check required environment variables
echo ""
echo "🔑 Checking required environment variables..."

check_env_var() {
    local var_name=$1
    local critical=$2
    
    if [ -z "${!var_name}" ]; then
        if [ "$critical" = "true" ]; then
            print_status "ERROR" "$var_name is not set"
        else
            print_status "WARNING" "$var_name is not set (optional)"
        fi
    else
        print_status "OK" "$var_name is set"
    fi
}

# Critical variables
check_env_var "SECRET_KEY" "true"
check_env_var "DATABASE_URL" "true"

# Trading configuration
if [ "$ENABLE_TRADING" = "true" ]; then
    print_status "WARNING" "ENABLE_TRADING is TRUE - Live trading is ENABLED!"
    echo "  ⚠️  Make sure you understand the risks!"
else
    print_status "OK" "ENABLE_TRADING is FALSE - Safe mode"
fi

# Broker API keys
echo ""
echo "🔌 Checking broker configurations..."

if [ -z "$ALPACA_API_KEY" ] && [ -z "$BINANCE_API_KEY" ]; then
    print_status "ERROR" "No broker API keys configured"
else
    [ -n "$ALPACA_API_KEY" ] && print_status "OK" "Alpaca API key configured"
    [ -n "$BINANCE_API_KEY" ] && print_status "OK" "Binance API key configured"
fi

# Check live vs paper trading
if [ -n "$ALPACA_API_KEY" ]; then
    if [ "$ALPACA_LIVE_MODE" = "true" ]; then
        print_status "WARNING" "Alpaca LIVE MODE enabled - using REAL money!"
    else
        print_status "OK" "Alpaca paper trading mode (safe)"
    fi
fi

if [ -n "$BINANCE_API_KEY" ]; then
    if [ "$BINANCE_TESTNET" = "false" ]; then
        print_status "WARNING" "Binance LIVE MODE enabled - using REAL money!"
    else
        print_status "OK" "Binance testnet mode (safe)"
    fi
fi

# Check risk management settings
echo ""
echo "🛡️ Checking risk management configuration..."

check_risk_param() {
    local param=$1
    local value=${!param}
    local recommended=$2
    
    if [ -z "$value" ]; then
        print_status "WARNING" "$param not set (will use default)"
    else
        print_status "OK" "$param = $value"
        if [ "$value" -gt "$recommended" ]; then
            print_status "WARNING" "  ⚠️  $param is higher than recommended ($recommended)"
        fi
    fi
}

check_risk_param "MAX_POSITION_SIZE_PCT" 5
check_risk_param "DAILY_LOSS_LIMIT_PCT" 10
check_risk_param "MAX_CONSECUTIVE_LOSSES" 5

# Check file permissions
echo ""
echo "📂 Checking file permissions..."

check_directory() {
    local dir=$1
    if [ -d "$dir" ]; then
        if [ -w "$dir" ]; then
            print_status "OK" "$dir is writable"
        else
            print_status "ERROR" "$dir is not writable"
        fi
    else
        mkdir -p "$dir" 2>/dev/null && print_status "OK" "$dir created" || print_status "ERROR" "Cannot create $dir"
    fi
}

check_directory "logs"
check_directory "data"

# Check Docker
echo ""
echo "🐳 Checking Docker environment..."

if command -v docker &> /dev/null; then
    print_status "OK" "Docker is installed"
    if docker ps &> /dev/null; then
        print_status "OK" "Docker daemon is running"
    else
        print_status "ERROR" "Docker daemon is not running"
    fi
else
    print_status "ERROR" "Docker is not installed"
fi

if command -v docker-compose &> /dev/null; then
    print_status "OK" "Docker Compose is installed"
else
    print_status "ERROR" "Docker Compose is not installed"
fi

# Check if services are running
echo ""
echo "🔍 Checking running services..."

if docker ps | grep -q "omnitrade-backend"; then
    print_status "OK" "Backend container is running"
else
    print_status "WARNING" "Backend container is not running"
fi

if docker ps | grep -q "omnitrade-postgres"; then
    print_status "OK" "PostgreSQL container is running"
else
    print_status "WARNING" "PostgreSQL container is not running"
fi

if docker ps | grep -q "omnitrade-redis"; then
    print_status "OK" "Redis container is running"
else
    print_status "WARNING" "Redis container is not running"
fi

# Check network connectivity
echo ""
echo "🌐 Checking network connectivity..."

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    print_status "OK" "Backend API is responding"
else
    print_status "WARNING" "Backend API is not responding (service may not be started)"
fi

# Security checks
echo ""
echo "🔒 Security checks..."

if [ -f ".env" ] && [ "$(stat -c %a .env)" != "600" ]; then
    print_status "WARNING" ".env file permissions should be 600 (run: chmod 600 .env)"
else
    print_status "OK" ".env file has secure permissions"
fi

if [ "$SECRET_KEY" = "your-secret-key-here-change-this" ] || [ "$SECRET_KEY" = "test-secret-key" ]; then
    print_status "ERROR" "SECRET_KEY is using default/test value - MUST be changed!"
fi

# Summary
echo ""
echo "======================================================================"
echo "                    Validation Summary"
echo "======================================================================"
echo ""
echo "Total checks: $CHECKS"
echo -e "Passed: ${GREEN}$((CHECKS - ERRORS - WARNINGS))${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo -e "Errors: ${RED}$ERRORS${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo "Please fix the errors above before starting the system."
    echo ""
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  VALIDATION PASSED WITH WARNINGS${NC}"
    echo "Review warnings above. System can start but issues should be addressed."
    echo ""
    echo "Continue? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
else
    echo -e "${GREEN}✓ VALIDATION PASSED${NC}"
    echo "All checks passed. System is ready to start."
    echo ""
fi

# Final warnings for live trading
if [ "$ENABLE_TRADING" = "true" ]; then
    echo ""
    echo "======================================================================"
    echo "                    ⚠️  LIVE TRADING WARNING ⚠️"
    echo "======================================================================"
    echo ""
    echo "ENABLE_TRADING is set to TRUE. This system will execute REAL trades"
    echo "with REAL money. Please ensure:"
    echo ""
    echo "  1. You have tested thoroughly with paper trading"
    echo "  2. You understand all risk parameters"
    echo "  3. You are monitoring the system continuously"
    echo "  4. You have emergency stop procedures in place"
    echo ""
    echo "Type 'I UNDERSTAND THE RISKS' to continue:"
    read -r confirmation
    if [ "$confirmation" != "I UNDERSTAND THE RISKS" ]; then
        echo "Deployment cancelled for safety."
        exit 1
    fi
fi

echo ""
echo "Validation complete. You can now start the system with:"
echo "  docker-compose up -d"
echo ""
echo "Monitor logs with:"
echo "  docker-compose logs -f backend"
echo ""
