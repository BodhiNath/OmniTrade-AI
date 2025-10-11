"""
Risk Management System for OmniTrade AI
Implements position sizing, stop-loss, circuit breakers, and portfolio risk controls
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self):
        self.daily_pnl: Decimal = Decimal('0')
        self.consecutive_losses: int = 0
        self.trading_halted: bool = False
        self.halt_reason: Optional[str] = None
        self.last_reset: datetime = datetime.utcnow()
        self.open_positions: Dict[str, Dict] = {}
        
    def reset_daily_stats(self):
        """Reset daily statistics (call at market open)"""
        self.daily_pnl = Decimal('0')
        self.consecutive_losses = 0
        self.trading_halted = False
        self.halt_reason = None
        self.last_reset = datetime.utcnow()
        logger.info("Daily risk statistics reset")
        
    def check_circuit_breakers(self, portfolio_value: Decimal) -> Tuple[bool, Optional[str]]:
        """
        Check if any circuit breakers should halt trading
        
        Returns:
            (can_trade, reason) - False if trading should be halted
        """
        # Check if already halted
        if self.trading_halted:
            return False, self.halt_reason
            
        # Check daily loss limit
        daily_loss_pct = (self.daily_pnl / portfolio_value * 100) if portfolio_value > 0 else 0
        if daily_loss_pct <= -settings.DAILY_LOSS_LIMIT_PCT:
            self.trading_halted = True
            self.halt_reason = f"Daily loss limit breached: {daily_loss_pct:.2f}%"
            logger.critical(self.halt_reason)
            return False, self.halt_reason
            
        # Check consecutive losses
        if self.consecutive_losses >= settings.MAX_CONSECUTIVE_LOSSES:
            self.trading_halted = True
            self.halt_reason = f"Max consecutive losses reached: {self.consecutive_losses}"
            logger.critical(self.halt_reason)
            return False, self.halt_reason
            
        # Check if trading is enabled globally
        if not settings.ENABLE_TRADING:
            return False, "Trading is disabled in configuration"
            
        return True, None
        
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: Decimal,
        stop_loss_price: Decimal,
        portfolio_value: Decimal,
        risk_per_trade_pct: Optional[float] = None
    ) -> Decimal:
        """
        Calculate position size based on risk parameters
        
        Args:
            symbol: Trading symbol
            entry_price: Planned entry price
            stop_loss_price: Stop loss price
            portfolio_value: Current portfolio value
            risk_per_trade_pct: Risk percentage per trade (default from config)
            
        Returns:
            Position size in base currency
        """
        if risk_per_trade_pct is None:
            risk_per_trade_pct = settings.DEFAULT_STOP_LOSS_PCT
            
        # Calculate risk amount
        risk_amount = portfolio_value * Decimal(risk_per_trade_pct / 100)
        
        # Calculate price risk per unit
        price_risk = abs(entry_price - stop_loss_price)
        if price_risk == 0:
            logger.warning(f"Zero price risk for {symbol}, using minimum position size")
            return Decimal(settings.MIN_ORDER_SIZE_USD)
            
        # Calculate position size
        position_size = risk_amount / price_risk
        
        # Apply maximum position size limit
        max_position_value = portfolio_value * Decimal(settings.MAX_POSITION_SIZE_PCT / 100)
        max_position_size = max_position_value / entry_price
        
        position_size = min(position_size, max_position_size)
        
        # Ensure minimum order size
        position_value = position_size * entry_price
        if position_value < Decimal(settings.MIN_ORDER_SIZE_USD):
            logger.warning(f"Position size too small for {symbol}, using minimum")
            position_size = Decimal(settings.MIN_ORDER_SIZE_USD) / entry_price
            
        logger.info(f"Calculated position size for {symbol}: {position_size} units (${position_value:.2f})")
        return position_size
        
    def validate_trade(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        price: Decimal,
        portfolio_value: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a trade meets risk requirements
        
        Returns:
            (is_valid, reason) - False if trade should be rejected
        """
        # Check circuit breakers
        can_trade, reason = self.check_circuit_breakers(portfolio_value)
        if not can_trade:
            return False, reason
            
        # Check position value
        position_value = quantity * price
        if position_value < Decimal(settings.MIN_ORDER_SIZE_USD):
            return False, f"Position value ${position_value:.2f} below minimum ${settings.MIN_ORDER_SIZE_USD}"
            
        # Check maximum position size
        max_position_value = portfolio_value * Decimal(settings.MAX_POSITION_SIZE_PCT / 100)
        if position_value > max_position_value:
            return False, f"Position value ${position_value:.2f} exceeds max ${max_position_value:.2f}"
            
        # Check total exposure
        total_exposure = sum(pos['value'] for pos in self.open_positions.values())
        total_exposure += position_value
        max_exposure = portfolio_value * Decimal(settings.MAX_PORTFOLIO_EXPOSURE_PCT / 100)
        
        if total_exposure > max_exposure:
            return False, f"Total exposure ${total_exposure:.2f} exceeds max ${max_exposure:.2f}"
            
        # Check max open positions
        if len(self.open_positions) >= settings.MAX_OPEN_POSITIONS:
            return False, f"Max open positions ({settings.MAX_OPEN_POSITIONS}) reached"
            
        return True, None
        
    def record_trade_result(self, symbol: str, pnl: Decimal):
        """Record trade result for risk tracking"""
        self.daily_pnl += pnl
        
        if pnl < 0:
            self.consecutive_losses += 1
            logger.warning(f"Loss recorded for {symbol}: ${pnl:.2f} (consecutive: {self.consecutive_losses})")
        else:
            self.consecutive_losses = 0
            logger.info(f"Profit recorded for {symbol}: ${pnl:.2f}")
            
        logger.info(f"Daily P&L: ${self.daily_pnl:.2f}")
        
    def add_position(self, symbol: str, quantity: Decimal, entry_price: Decimal, stop_loss: Decimal):
        """Track open position"""
        self.open_positions[symbol] = {
            'quantity': quantity,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'value': quantity * entry_price,
            'opened_at': datetime.utcnow()
        }
        logger.info(f"Position opened: {symbol} - {quantity} @ ${entry_price:.2f}")
        
    def remove_position(self, symbol: str):
        """Remove closed position"""
        if symbol in self.open_positions:
            del self.open_positions[symbol]
            logger.info(f"Position closed: {symbol}")
            
    def check_stop_loss(self, symbol: str, current_price: Decimal) -> bool:
        """Check if stop loss should be triggered"""
        if symbol not in self.open_positions:
            return False
            
        position = self.open_positions[symbol]
        stop_loss = position['stop_loss']
        
        # Check if price hit stop loss
        if current_price <= stop_loss:
            logger.warning(f"Stop loss triggered for {symbol}: ${current_price:.2f} <= ${stop_loss:.2f}")
            return True
            
        return False
        
    def update_trailing_stop(self, symbol: str, current_price: Decimal, trailing_pct: float = 2.0):
        """Update trailing stop loss"""
        if symbol not in self.open_positions:
            return
            
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        current_stop = position['stop_loss']
        
        # Only update if in profit
        if current_price > entry_price:
            new_stop = current_price * Decimal(1 - trailing_pct / 100)
            if new_stop > current_stop:
                position['stop_loss'] = new_stop
                logger.info(f"Trailing stop updated for {symbol}: ${new_stop:.2f}")
                
    def get_risk_metrics(self, portfolio_value: Decimal) -> Dict:
        """Get current risk metrics"""
        total_exposure = sum(pos['value'] for pos in self.open_positions.values())
        exposure_pct = (total_exposure / portfolio_value * 100) if portfolio_value > 0 else 0
        daily_pnl_pct = (self.daily_pnl / portfolio_value * 100) if portfolio_value > 0 else 0
        
        return {
            'daily_pnl': float(self.daily_pnl),
            'daily_pnl_pct': float(daily_pnl_pct),
            'consecutive_losses': self.consecutive_losses,
            'open_positions': len(self.open_positions),
            'total_exposure': float(total_exposure),
            'exposure_pct': float(exposure_pct),
            'trading_halted': self.trading_halted,
            'halt_reason': self.halt_reason,
            'can_trade': not self.trading_halted and settings.ENABLE_TRADING
        }


# Global risk manager instance
risk_manager = RiskManager()

