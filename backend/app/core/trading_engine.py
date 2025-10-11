"""
Core Trading Engine
Orchestrates strategy execution, order placement, and position management
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
import logging
import asyncio

from app.core.config import settings
from app.core.risk_manager import risk_manager
from app.brokers.alpaca_broker import AlpacaBroker
from app.brokers.binance_broker import BinanceBroker
from app.strategies.technical_strategy import TechnicalStrategy
from app.utils.logger import log_trade, log_risk_event
from app.utils.notifications import notification_manager

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading engine orchestrating all trading activities"""
    
    def __init__(self):
        self.is_running = False
        self.brokers = {}
        self.strategies = {}
        self.active_positions = {}
        self.pending_orders = {}
        
        # Initialize brokers
        try:
            if settings.ALPACA_API_KEY:
                self.brokers['alpaca'] = AlpacaBroker()
                logger.info("Alpaca broker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca: {e}")
            
        try:
            if settings.BINANCE_API_KEY:
                self.brokers['binance'] = BinanceBroker()
                logger.info("Binance broker initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Binance: {e}")
            
        # Initialize strategies
        self.strategies['technical'] = TechnicalStrategy()
        
        logger.info("Trading engine initialized")
        
    async def start(self):
        """Start the trading engine"""
        if self.is_running:
            logger.warning("Trading engine already running")
            return
            
        if not settings.ENABLE_TRADING:
            logger.warning("Trading is disabled in configuration")
            await notification_manager.notify_system_status(
                'warning',
                'Trading engine started but trading is DISABLED in configuration'
            )
            return
            
        self.is_running = True
        logger.info("Trading engine started")
        
        await notification_manager.notify_system_status(
            'started',
            'Trading engine is now active and monitoring markets'
        )
        
        # Reset daily risk statistics
        risk_manager.reset_daily_stats()
        
    async def stop(self):
        """Stop the trading engine"""
        if not self.is_running:
            logger.warning("Trading engine not running")
            return
            
        self.is_running = False
        logger.info("Trading engine stopped")
        
        await notification_manager.notify_system_status(
            'stopped',
            'Trading engine has been stopped'
        )
        
    async def execute_strategy(
        self,
        broker_name: str,
        symbol: str,
        strategy_name: str = 'technical',
        indicators: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute a trading strategy for a symbol
        
        Args:
            broker_name: 'alpaca' or 'binance'
            symbol: Trading symbol
            strategy_name: Strategy to use
            indicators: List of technical indicators
            
        Returns:
            Execution result
        """
        if not self.is_running:
            return {'error': 'Trading engine not running'}
            
        if broker_name not in self.brokers:
            return {'error': f'Broker {broker_name} not available'}
            
        broker = self.brokers[broker_name]
        strategy = self.strategies.get(strategy_name)
        
        if not strategy:
            return {'error': f'Strategy {strategy_name} not found'}
            
        try:
            # Get account info
            account = broker.get_account()
            portfolio_value = account['portfolio_value']
            
            # Check circuit breakers
            can_trade, reason = risk_manager.check_circuit_breakers(portfolio_value)
            if not can_trade:
                logger.warning(f"Trading halted: {reason}")
                await notification_manager.notify_risk_alert(
                    'Circuit Breaker',
                    'critical',
                    reason
                )
                return {'error': reason, 'trading_halted': True}
                
            # Get historical data
            bars = broker.get_historical_bars(symbol, limit=200)
            if not bars:
                return {'error': 'No historical data available'}
                
            prices = [bar['close'] for bar in bars]
            current_price = prices[-1]
            
            # Run strategy analysis
            signal, confidence, details = strategy.combined_analysis(prices, indicators)
            
            logger.info(f"Strategy signal for {symbol}: {signal.upper()} (confidence: {confidence:.2f})")
            
            # Execute trade if signal is strong enough
            if signal != 'hold' and confidence >= 0.6:
                return await self._execute_trade(
                    broker=broker,
                    broker_name=broker_name,
                    symbol=symbol,
                    signal=signal,
                    current_price=current_price,
                    portfolio_value=portfolio_value,
                    confidence=confidence,
                    analysis=details
                )
            else:
                return {
                    'action': 'hold',
                    'signal': signal,
                    'confidence': confidence,
                    'reason': 'Signal not strong enough' if signal != 'hold' else 'No clear signal',
                    'analysis': details
                }
                
        except Exception as e:
            logger.error(f"Error executing strategy for {symbol}: {e}")
            return {'error': str(e)}
            
    async def _execute_trade(
        self,
        broker,
        broker_name: str,
        symbol: str,
        signal: str,
        current_price: Decimal,
        portfolio_value: Decimal,
        confidence: float,
        analysis: Dict
    ) -> Dict:
        """Execute a trade based on strategy signal"""
        
        try:
            # Calculate stop loss
            stop_loss_pct = settings.DEFAULT_STOP_LOSS_PCT
            if signal == 'buy':
                stop_loss_price = current_price * Decimal(1 - stop_loss_pct / 100)
            else:
                stop_loss_price = current_price * Decimal(1 + stop_loss_pct / 100)
                
            # Calculate position size
            position_size = risk_manager.calculate_position_size(
                symbol=symbol,
                entry_price=current_price,
                stop_loss_price=stop_loss_price,
                portfolio_value=portfolio_value
            )
            
            # Validate trade
            is_valid, reason = risk_manager.validate_trade(
                symbol=symbol,
                side=signal,
                quantity=position_size,
                price=current_price,
                portfolio_value=portfolio_value
            )
            
            if not is_valid:
                logger.warning(f"Trade validation failed for {symbol}: {reason}")
                log_risk_event(
                    'trade_rejected',
                    'medium',
                    f"Trade rejected: {reason}",
                    symbol=symbol,
                    side=signal
                )
                return {'error': reason, 'trade_rejected': True}
                
            # Place order
            order = broker.place_market_order(
                symbol=symbol,
                quantity=position_size,
                side=signal,
                stop_loss_price=stop_loss_price
            )
            
            # Log trade
            log_trade(
                action='open',
                symbol=symbol,
                quantity=float(position_size),
                price=float(current_price),
                side=signal,
                order_id=order['order_id'],
                stop_loss=float(stop_loss_price),
                confidence=confidence
            )
            
            # Track position
            risk_manager.add_position(
                symbol=symbol,
                quantity=position_size,
                entry_price=current_price,
                stop_loss=stop_loss_price
            )
            
            # Send notification
            await notification_manager.notify_trade_executed(
                symbol=symbol,
                side=signal,
                quantity=float(position_size),
                price=float(current_price),
                order_id=order['order_id']
            )
            
            logger.info(f"Trade executed: {signal.upper()} {position_size} {symbol} @ ${current_price}")
            
            return {
                'success': True,
                'action': 'trade_executed',
                'order': order,
                'position_size': float(position_size),
                'entry_price': float(current_price),
                'stop_loss': float(stop_loss_price),
                'confidence': confidence,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            log_risk_event(
                'trade_error',
                'high',
                f"Trade execution failed: {str(e)}",
                symbol=symbol,
                side=signal
            )
            return {'error': str(e)}
            
    async def close_position(
        self,
        broker_name: str,
        symbol: str,
        reason: str = 'manual'
    ) -> Dict:
        """Close an open position"""
        
        if broker_name not in self.brokers:
            return {'error': f'Broker {broker_name} not available'}
            
        broker = self.brokers[broker_name]
        
        try:
            # Get position info
            if symbol not in risk_manager.open_positions:
                return {'error': f'No open position for {symbol}'}
                
            position = risk_manager.open_positions[symbol]
            entry_price = position['entry_price']
            quantity = position['quantity']
            
            # Get current price
            current_price = broker.get_current_price(symbol)
            
            # Close position
            order = broker.close_position(symbol)
            
            # Calculate P&L
            pnl = (current_price - entry_price) * quantity
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Log trade
            log_trade(
                action='close',
                symbol=symbol,
                quantity=float(quantity),
                price=float(current_price),
                side='sell',
                order_id=order['order_id'],
                pnl=float(pnl),
                pnl_pct=float(pnl_pct),
                reason=reason
            )
            
            # Update risk manager
            risk_manager.record_trade_result(symbol, pnl)
            risk_manager.remove_position(symbol)
            
            # Send notification
            await notification_manager.notify_position_closed(
                symbol=symbol,
                quantity=float(quantity),
                entry_price=float(entry_price),
                exit_price=float(current_price),
                pnl=float(pnl),
                pnl_pct=float(pnl_pct)
            )
            
            logger.info(f"Position closed: {symbol} | P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
            
            return {
                'success': True,
                'action': 'position_closed',
                'order': order,
                'pnl': float(pnl),
                'pnl_pct': float(pnl_pct),
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
            return {'error': str(e)}
            
    async def monitor_positions(self):
        """Monitor open positions for stop loss and trailing stop"""
        
        for symbol, position in list(risk_manager.open_positions.items()):
            try:
                # Determine broker
                broker_name = 'binance' if '/' in symbol else 'alpaca'
                if broker_name not in self.brokers:
                    continue
                    
                broker = self.brokers[broker_name]
                
                # Get current price
                current_price = broker.get_current_price(symbol)
                
                # Check stop loss
                if risk_manager.check_stop_loss(symbol, current_price):
                    logger.warning(f"Stop loss triggered for {symbol}")
                    
                    await notification_manager.notify_stop_loss_triggered(
                        symbol=symbol,
                        quantity=float(position['quantity']),
                        stop_price=float(position['stop_loss']),
                        current_price=float(current_price)
                    )
                    
                    await self.close_position(broker_name, symbol, reason='stop_loss')
                else:
                    # Update trailing stop
                    risk_manager.update_trailing_stop(symbol, current_price)
                    
            except Exception as e:
                logger.error(f"Error monitoring position {symbol}: {e}")
                
    def get_status(self) -> Dict:
        """Get trading engine status"""
        
        status = {
            'is_running': self.is_running,
            'trading_enabled': settings.ENABLE_TRADING,
            'brokers': list(self.brokers.keys()),
            'strategies': list(self.strategies.keys()),
            'risk_metrics': risk_manager.get_risk_metrics(Decimal('10000'))  # Placeholder
        }
        
        return status


# Global trading engine instance
trading_engine = TradingEngine()

