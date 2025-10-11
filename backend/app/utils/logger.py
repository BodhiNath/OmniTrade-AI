"""
Comprehensive logging system for OmniTrade AI
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime

from app.core.config import settings


def setup_logging():
    """Configure logging for the application"""
    
    # Create logs directory
    log_dir = Path("/home/ubuntu/omnitrade-ai/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler - General application log
    app_log_file = log_dir / "omnitrade.log"
    app_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    app_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app_handler.setFormatter(file_formatter)
    root_logger.addHandler(app_handler)
    
    # Trade log - Separate log for all trading activity
    trade_logger = logging.getLogger('trading')
    trade_log_file = log_dir / "trades.log"
    trade_handler = TimedRotatingFileHandler(
        trade_log_file,
        when='midnight',
        interval=1,
        backupCount=90  # Keep 90 days
    )
    trade_handler.setLevel(logging.INFO)
    trade_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    trade_handler.setFormatter(trade_formatter)
    trade_logger.addHandler(trade_handler)
    trade_logger.propagate = False  # Don't propagate to root logger
    
    # Risk log - Separate log for risk events
    risk_logger = logging.getLogger('risk')
    risk_log_file = log_dir / "risk.log"
    risk_handler = TimedRotatingFileHandler(
        risk_log_file,
        when='midnight',
        interval=1,
        backupCount=90
    )
    risk_handler.setLevel(logging.WARNING)
    risk_handler.setFormatter(trade_formatter)
    risk_logger.addHandler(risk_handler)
    risk_logger.propagate = False
    
    # Error log - Critical errors only
    error_log_file = log_dir / "errors.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('alpaca').setLevel(logging.INFO)
    
    logging.info("Logging system initialized")
    logging.info(f"Log directory: {log_dir}")
    logging.info(f"Log level: {settings.LOG_LEVEL}")


def log_trade(
    action: str,
    symbol: str,
    quantity: float,
    price: float,
    side: str,
    order_id: str = None,
    **kwargs
):
    """Log trade execution"""
    trade_logger = logging.getLogger('trading')
    
    message = (
        f"TRADE {action.upper()} | "
        f"Symbol: {symbol} | "
        f"Side: {side.upper()} | "
        f"Quantity: {quantity} | "
        f"Price: ${price:.4f} | "
        f"Value: ${quantity * price:.2f}"
    )
    
    if order_id:
        message += f" | Order ID: {order_id}"
        
    for key, value in kwargs.items():
        message += f" | {key}: {value}"
        
    trade_logger.info(message)


def log_risk_event(
    event_type: str,
    severity: str,
    message: str,
    **kwargs
):
    """Log risk management events"""
    risk_logger = logging.getLogger('risk')
    
    log_message = (
        f"RISK {event_type.upper()} | "
        f"Severity: {severity.upper()} | "
        f"{message}"
    )
    
    for key, value in kwargs.items():
        log_message += f" | {key}: {value}"
    
    if severity.lower() == 'critical':
        risk_logger.critical(log_message)
    elif severity.lower() == 'high':
        risk_logger.error(log_message)
    elif severity.lower() == 'medium':
        risk_logger.warning(log_message)
    else:
        risk_logger.info(log_message)


def log_performance(
    period: str,
    pnl: float,
    win_rate: float,
    total_trades: int,
    **kwargs
):
    """Log performance metrics"""
    trade_logger = logging.getLogger('trading')
    
    message = (
        f"PERFORMANCE {period.upper()} | "
        f"P&L: ${pnl:.2f} | "
        f"Win Rate: {win_rate:.2f}% | "
        f"Total Trades: {total_trades}"
    )
    
    for key, value in kwargs.items():
        message += f" | {key}: {value}"
        
    trade_logger.info(message)

