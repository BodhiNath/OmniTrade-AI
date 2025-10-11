"""
OmniTrade AI - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.core.config import settings
from app.core.trading_engine import trading_engine
from app.core.risk_manager import risk_manager
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sovereign-grade AI-powered trading system"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class TradeRequest(BaseModel):
    broker: str  # 'alpaca' or 'binance'
    symbol: str
    strategy: str = 'technical'
    indicators: Optional[List[str]] = None


class ClosePositionRequest(BaseModel):
    broker: str
    symbol: str
    reason: str = 'manual'


class SystemControlRequest(BaseModel):
    action: str  # 'start' or 'stop'


# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "trading_engine": trading_engine.is_running,
        "trading_enabled": settings.ENABLE_TRADING
    }


# System Control
@app.post("/api/v1/system/control")
async def control_system(request: SystemControlRequest):
    """Start or stop the trading engine"""
    try:
        if request.action == 'start':
            await trading_engine.start()
            return {"message": "Trading engine started", "status": "running"}
        elif request.action == 'stop':
            await trading_engine.stop()
            return {"message": "Trading engine stopped", "status": "stopped"}
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
    except Exception as e:
        logger.error(f"Error controlling system: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/system/status")
async def get_system_status():
    """Get system status"""
    try:
        status = trading_engine.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Trading Operations
@app.post("/api/v1/trade/execute")
async def execute_trade(request: TradeRequest):
    """Execute a trading strategy"""
    try:
        result = await trading_engine.execute_strategy(
            broker_name=request.broker,
            symbol=request.symbol,
            strategy_name=request.strategy,
            indicators=request.indicators
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/trade/close")
async def close_position(request: ClosePositionRequest):
    """Close an open position"""
    try:
        result = await trading_engine.close_position(
            broker_name=request.broker,
            symbol=request.symbol,
            reason=request.reason
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Account & Portfolio
@app.get("/api/v1/account/{broker}")
async def get_account(broker: str):
    """Get account information"""
    try:
        if broker not in trading_engine.brokers:
            raise HTTPException(status_code=404, detail=f"Broker {broker} not found")
            
        account = trading_engine.brokers[broker].get_account()
        return account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/positions/{broker}")
async def get_positions(broker: str):
    """Get open positions"""
    try:
        if broker not in trading_engine.brokers:
            raise HTTPException(status_code=404, detail=f"Broker {broker} not found")
            
        positions = trading_engine.brokers[broker].get_positions()
        return {"positions": positions}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Risk Management
@app.get("/api/v1/risk/metrics")
async def get_risk_metrics():
    """Get current risk metrics"""
    try:
        # Get portfolio value from first available broker
        portfolio_value = 10000  # Default
        for broker in trading_engine.brokers.values():
            try:
                account = broker.get_account()
                portfolio_value = account['portfolio_value']
                break
            except:
                continue
                
        metrics = risk_manager.get_risk_metrics(portfolio_value)
        return metrics
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/risk/reset")
async def reset_risk_stats():
    """Reset daily risk statistics"""
    try:
        risk_manager.reset_daily_stats()
        return {"message": "Risk statistics reset"}
    except Exception as e:
        logger.error(f"Error resetting risk stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Market Data
@app.get("/api/v1/market/price/{broker}/{symbol}")
async def get_price(broker: str, symbol: str):
    """Get current price for symbol"""
    try:
        if broker not in trading_engine.brokers:
            raise HTTPException(status_code=404, detail=f"Broker {broker} not found")
            
        price = trading_engine.brokers[broker].get_current_price(symbol)
        return {"symbol": symbol, "price": float(price)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/market/bars/{broker}/{symbol}")
async def get_historical_bars(
    broker: str,
    symbol: str,
    timeframe: str = '1Day',
    limit: int = 100
):
    """Get historical price bars"""
    try:
        if broker not in trading_engine.brokers:
            raise HTTPException(status_code=404, detail=f"Broker {broker} not found")
            
        bars = trading_engine.brokers[broker].get_historical_bars(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        return {"symbol": symbol, "bars": bars}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical bars: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

