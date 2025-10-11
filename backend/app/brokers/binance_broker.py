"""
Binance Broker Integration for Cryptocurrency Trading
Supports both testnet and live trading
"""
from typing import Dict, List, Optional
from decimal import Decimal
import logging

import ccxt

from app.core.config import settings

logger = logging.getLogger(__name__)


class BinanceBroker:
    """Binance broker interface for cryptocurrency trading"""
    
    def __init__(self):
        if not settings.BINANCE_API_KEY or not settings.BINANCE_SECRET_KEY:
            raise ValueError("Binance API credentials not configured")
            
        self.exchange = ccxt.binance({
            'apiKey': settings.BINANCE_API_KEY,
            'secret': settings.BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # spot, margin, future
                'adjustForTimeDifference': True
            }
        })
        
        # Use testnet if configured
        if settings.BINANCE_TESTNET:
            self.exchange.set_sandbox_mode(True)
            logger.info("Binance broker initialized (TESTNET mode)")
        else:
            logger.info("Binance broker initialized (LIVE mode)")
            
        self.is_live = not settings.BINANCE_TESTNET
        
    def get_account(self) -> Dict:
        """Get account information"""
        try:
            balance = self.exchange.fetch_balance()
            
            # Calculate total portfolio value in USDT
            total_value = Decimal('0')
            positions = []
            
            for currency, amounts in balance['total'].items():
                if amounts > 0:
                    amount = Decimal(str(amounts))
                    
                    # Get value in USDT
                    if currency == 'USDT':
                        value = amount
                    else:
                        try:
                            ticker = self.exchange.fetch_ticker(f"{currency}/USDT")
                            price = Decimal(str(ticker['last']))
                            value = amount * price
                        except:
                            value = Decimal('0')
                    
                    total_value += value
                    positions.append({
                        'currency': currency,
                        'amount': amount,
                        'value_usdt': value
                    })
            
            return {
                'account_id': 'binance',
                'portfolio_value': total_value,
                'cash': Decimal(str(balance['free'].get('USDT', 0))),
                'positions': positions
            }
            
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise
            
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            balance = self.exchange.fetch_balance()
            positions = []
            
            for currency, amounts in balance['total'].items():
                if amounts > 0 and currency != 'USDT':
                    amount = Decimal(str(amounts))
                    
                    try:
                        symbol = f"{currency}/USDT"
                        ticker = self.exchange.fetch_ticker(symbol)
                        current_price = Decimal(str(ticker['last']))
                        market_value = amount * current_price
                        
                        positions.append({
                            'symbol': symbol,
                            'currency': currency,
                            'quantity': amount,
                            'current_price': current_price,
                            'market_value': market_value
                        })
                    except Exception as e:
                        logger.warning(f"Could not fetch ticker for {currency}: {e}")
                        
            return positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
            
    def get_current_price(self, symbol: str) -> Decimal:
        """Get current price for symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return Decimal(str(ticker['last']))
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
            symbol: Trading pair (e.g., 'BTC/USDT')
            quantity: Amount to trade
            side: 'buy' or 'sell'
            stop_loss_price: Optional stop loss price
            
        Returns:
            Order details
        """
        try:
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side.lower(),
                amount=float(quantity)
            )
            
            logger.info(f"Market order placed: {side.upper()} {quantity} {symbol}")
            
            # Place stop loss order if provided
            stop_loss_order = None
            if stop_loss_price and order['status'] == 'closed':
                filled_qty = Decimal(str(order['filled']))
                opposite_side = 'sell' if side.lower() == 'buy' else 'buy'
                
                try:
                    stop_loss_order = self.exchange.create_order(
                        symbol=symbol,
                        type='stop_loss_limit',
                        side=opposite_side,
                        amount=float(filled_qty),
                        price=float(stop_loss_price),
                        params={'stopPrice': float(stop_loss_price)}
                    )
                    logger.info(f"Stop loss order placed: {stop_loss_price}")
                except Exception as e:
                    logger.error(f"Failed to place stop loss: {e}")
            
            return {
                'order_id': order['id'],
                'symbol': order['symbol'],
                'quantity': Decimal(str(order['amount'])),
                'side': order['side'],
                'type': order['type'],
                'status': order['status'],
                'filled_qty': Decimal(str(order['filled'])),
                'filled_avg_price': Decimal(str(order['average'])) if order['average'] else None,
                'timestamp': order['timestamp'],
                'stop_loss_order_id': stop_loss_order['id'] if stop_loss_order else None
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
            order = self.exchange.create_limit_order(
                symbol=symbol,
                side=side.lower(),
                amount=float(quantity),
                price=float(limit_price)
            )
            
            logger.info(f"Limit order placed: {side.upper()} {quantity} {symbol} @ ${limit_price}")
            
            return {
                'order_id': order['id'],
                'symbol': order['symbol'],
                'quantity': Decimal(str(order['amount'])),
                'side': order['side'],
                'type': order['type'],
                'limit_price': Decimal(str(order['price'])),
                'status': order['status'],
                'timestamp': order['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error placing limit order for {symbol}: {e}")
            raise
            
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
            
    def close_position(self, symbol: str, quantity: Optional[Decimal] = None) -> Dict:
        """Close a position"""
        try:
            # Get current position
            balance = self.exchange.fetch_balance()
            currency = symbol.split('/')[0]
            current_qty = Decimal(str(balance['total'].get(currency, 0)))
            
            if current_qty == 0:
                raise ValueError(f"No position to close for {symbol}")
                
            # Determine quantity to close
            qty_to_close = quantity if quantity else current_qty
            
            # Place market sell order
            return self.place_market_order(symbol, qty_to_close, 'sell')
            
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
            raise
            
    def close_all_positions(self) -> List[Dict]:
        """Close all open positions"""
        try:
            positions = self.get_positions()
            results = []
            
            for position in positions:
                try:
                    result = self.close_position(
                        position['symbol'],
                        position['quantity']
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to close {position['symbol']}: {e}")
                    
            logger.info(f"Closed {len(results)} positions")
            return results
            
        except Exception as e:
            logger.error(f"Error closing all positions: {e}")
            raise
            
    def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """Get order status"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return {
                'order_id': order['id'],
                'symbol': order['symbol'],
                'status': order['status'],
                'filled_qty': Decimal(str(order['filled'])),
                'filled_avg_price': Decimal(str(order['average'])) if order['average'] else None
            }
        except Exception as e:
            logger.error(f"Error fetching order status {order_id}: {e}")
            raise
            
    def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = '1d',
        limit: int = 100
    ) -> List[Dict]:
        """Get historical price bars"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            return [{
                'timestamp': bar[0],
                'open': Decimal(str(bar[1])),
                'high': Decimal(str(bar[2])),
                'low': Decimal(str(bar[3])),
                'close': Decimal(str(bar[4])),
                'volume': Decimal(str(bar[5]))
            } for bar in ohlcv]
            
        except Exception as e:
            logger.error(f"Error fetching historical bars for {symbol}: {e}")
            raise
            
    def is_market_open(self) -> bool:
        """Crypto markets are always open"""
        return True
        
    def get_trading_fees(self, symbol: str) -> Dict:
        """Get trading fees for symbol"""
        try:
            fees = self.exchange.fetch_trading_fees()
            if symbol in fees:
                return {
                    'maker': Decimal(str(fees[symbol]['maker'])),
                    'taker': Decimal(str(fees[symbol]['taker']))
                }
            return {'maker': Decimal('0.001'), 'taker': Decimal('0.001')}
        except Exception as e:
            logger.error(f"Error fetching fees: {e}")
            return {'maker': Decimal('0.001'), 'taker': Decimal('0.001')}

