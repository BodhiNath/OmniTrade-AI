"""
Alpaca Broker Integration for Stock Trading
Supports both paper and live trading
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
import logging

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from app.core.config import settings

logger = logging.getLogger(__name__)


class AlpacaBroker:
    """Alpaca broker interface for stock trading"""
    
    def __init__(self):
        if not settings.ALPACA_API_KEY or not settings.ALPACA_SECRET_KEY:
            raise ValueError("Alpaca API credentials not configured")
            
        self.trading_client = TradingClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY,
            paper=not settings.ALPACA_LIVE_MODE
        )
        
        self.data_client = StockHistoricalDataClient(
            api_key=settings.ALPACA_API_KEY,
            secret_key=settings.ALPACA_SECRET_KEY
        )
        
        self.is_live = settings.ALPACA_LIVE_MODE
        logger.info(f"Alpaca broker initialized ({'LIVE' if self.is_live else 'PAPER'} mode)")
        
    def get_account(self) -> Dict:
        """Get account information"""
        try:
            account = self.trading_client.get_account()
            return {
                'account_id': account.id,
                'cash': Decimal(account.cash),
                'portfolio_value': Decimal(account.portfolio_value),
                'buying_power': Decimal(account.buying_power),
                'equity': Decimal(account.equity),
                'last_equity': Decimal(account.last_equity),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'account_blocked': account.account_blocked,
                'status': account.status
            }
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise
            
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            positions = self.trading_client.get_all_positions()
            return [{
                'symbol': pos.symbol,
                'quantity': Decimal(pos.qty),
                'side': 'long' if Decimal(pos.qty) > 0 else 'short',
                'entry_price': Decimal(pos.avg_entry_price),
                'current_price': Decimal(pos.current_price),
                'market_value': Decimal(pos.market_value),
                'cost_basis': Decimal(pos.cost_basis),
                'unrealized_pl': Decimal(pos.unrealized_pl),
                'unrealized_plpc': Decimal(pos.unrealized_plpc),
                'change_today': Decimal(pos.change_today)
            } for pos in positions]
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
            
    def get_current_price(self, symbol: str) -> Decimal:
        """Get current price for symbol"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.data_client.get_stock_latest_quote(request)
            
            if symbol in quote:
                bid = Decimal(str(quote[symbol].bid_price))
                ask = Decimal(str(quote[symbol].ask_price))
                return (bid + ask) / 2
            else:
                raise ValueError(f"No quote data for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise
            
    def place_market_order(
        self,
        symbol: str,
        quantity: Decimal,
        side: str,
        stop_loss_price: Optional[Decimal] = None
    ) -> Dict:
        """
        Place a market order
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            side: 'buy' or 'sell'
            stop_loss_price: Optional stop loss price
            
        Returns:
            Order details
        """
        try:
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            
            # Create order request
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=float(quantity),
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            # Add stop loss if provided
            if stop_loss_price:
                order_data.stop_loss = StopLossRequest(
                    stop_price=float(stop_loss_price)
                )
            
            # Submit order
            order = self.trading_client.submit_order(order_data)
            
            logger.info(f"Market order placed: {side.upper()} {quantity} {symbol} @ market")
            
            return {
                'order_id': order.id,
                'symbol': order.symbol,
                'quantity': Decimal(order.qty),
                'side': order.side.value,
                'type': order.type.value,
                'status': order.status.value,
                'filled_qty': Decimal(order.filled_qty or 0),
                'filled_avg_price': Decimal(order.filled_avg_price) if order.filled_avg_price else None,
                'submitted_at': order.submitted_at,
                'stop_loss': float(stop_loss_price) if stop_loss_price else None
            }
            
        except Exception as e:
            logger.error(f"Error placing market order for {symbol}: {e}")
            raise
            
    def place_limit_order(
        self,
        symbol: str,
        quantity: Decimal,
        side: str,
        limit_price: Decimal,
        stop_loss_price: Optional[Decimal] = None
    ) -> Dict:
        """Place a limit order"""
        try:
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=float(quantity),
                side=order_side,
                time_in_force=TimeInForce.DAY,
                limit_price=float(limit_price)
            )
            
            if stop_loss_price:
                order_data.stop_loss = StopLossRequest(
                    stop_price=float(stop_loss_price)
                )
            
            order = self.trading_client.submit_order(order_data)
            
            logger.info(f"Limit order placed: {side.upper()} {quantity} {symbol} @ ${limit_price}")
            
            return {
                'order_id': order.id,
                'symbol': order.symbol,
                'quantity': Decimal(order.qty),
                'side': order.side.value,
                'type': order.type.value,
                'limit_price': Decimal(order.limit_price),
                'status': order.status.value,
                'submitted_at': order.submitted_at,
                'stop_loss': float(stop_loss_price) if stop_loss_price else None
            }
            
        except Exception as e:
            logger.error(f"Error placing limit order for {symbol}: {e}")
            raise
            
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
            
    def close_position(self, symbol: str, quantity: Optional[Decimal] = None) -> Dict:
        """Close a position (partial or full)"""
        try:
            if quantity:
                # Close partial position
                position = self.trading_client.get_open_position(symbol)
                current_qty = Decimal(position.qty)
                side = 'sell' if current_qty > 0 else 'buy'
                return self.place_market_order(symbol, quantity, side)
            else:
                # Close entire position
                order = self.trading_client.close_position(symbol)
                logger.info(f"Position closed: {symbol}")
                return {
                    'order_id': order.id,
                    'symbol': order.symbol,
                    'status': order.status.value
                }
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
            raise
            
    def close_all_positions(self) -> List[Dict]:
        """Close all open positions"""
        try:
            orders = self.trading_client.close_all_positions(cancel_orders=True)
            logger.info(f"All positions closed: {len(orders)} orders")
            return [{
                'order_id': order.id,
                'symbol': order.symbol,
                'status': order.status.value
            } for order in orders]
        except Exception as e:
            logger.error(f"Error closing all positions: {e}")
            raise
            
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        try:
            order = self.trading_client.get_order_by_id(order_id)
            return {
                'order_id': order.id,
                'symbol': order.symbol,
                'status': order.status.value,
                'filled_qty': Decimal(order.filled_qty or 0),
                'filled_avg_price': Decimal(order.filled_avg_price) if order.filled_avg_price else None
            }
        except Exception as e:
            logger.error(f"Error fetching order status {order_id}: {e}")
            raise
            
    def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = '1Day',
        limit: int = 100
    ) -> List[Dict]:
        """Get historical price bars"""
        try:
            timeframe_map = {
                '1Min': TimeFrame.Minute,
                '5Min': TimeFrame(5, 'Min'),
                '15Min': TimeFrame(15, 'Min'),
                '1Hour': TimeFrame.Hour,
                '1Day': TimeFrame.Day
            }
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe_map.get(timeframe, TimeFrame.Day),
                limit=limit
            )
            
            bars = self.data_client.get_stock_bars(request)
            
            if symbol in bars:
                return [{
                    'timestamp': bar.timestamp,
                    'open': Decimal(str(bar.open)),
                    'high': Decimal(str(bar.high)),
                    'low': Decimal(str(bar.low)),
                    'close': Decimal(str(bar.close)),
                    'volume': bar.volume
                } for bar in bars[symbol]]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching historical bars for {symbol}: {e}")
            raise
            
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        try:
            clock = self.trading_client.get_clock()
            return clock.is_open
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False

