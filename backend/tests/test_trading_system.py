"""
Comprehensive test suite for OmniTrade AI
Tests risk management, trading logic, and safety mechanisms
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from app.core.risk_manager import RiskManager
from app.strategies.technical_strategy import TechnicalStrategy


class TestRiskManager:
    """Test risk management system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.risk_manager = RiskManager()
        self.portfolio_value = Decimal('10000')
        
    def test_circuit_breaker_daily_loss_limit(self):
        """Test daily loss limit circuit breaker"""
        # Simulate 10% loss
        self.risk_manager.daily_pnl = Decimal('-1000')
        
        can_trade, reason = self.risk_manager.check_circuit_breakers(self.portfolio_value)
        
        assert can_trade is False
        assert 'Daily loss limit' in reason
        assert self.risk_manager.trading_halted is True
        
    def test_circuit_breaker_consecutive_losses(self):
        """Test consecutive losses circuit breaker"""
        self.risk_manager.consecutive_losses = 5
        
        can_trade, reason = self.risk_manager.check_circuit_breakers(self.portfolio_value)
        
        assert can_trade is False
        assert 'consecutive losses' in reason
        assert self.risk_manager.trading_halted is True
        
    def test_position_size_calculation(self):
        """Test position size calculation"""
        symbol = 'AAPL'
        entry_price = Decimal('150')
        stop_loss_price = Decimal('147')  # 2% stop loss
        
        position_size = self.risk_manager.calculate_position_size(
            symbol=symbol,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            portfolio_value=self.portfolio_value,
            risk_per_trade_pct=2.0
        )
        
        # Should risk $200 (2% of $10,000)
        # Price risk is $3 per share
        # Position size should be ~66.67 shares
        expected_size = Decimal('200') / Decimal('3')
        
        assert abs(position_size - expected_size) < Decimal('1')
        
    def test_max_position_size_limit(self):
        """Test maximum position size enforcement"""
        symbol = 'AAPL'
        entry_price = Decimal('150')
        stop_loss_price = Decimal('149.5')  # Very tight stop
        
        position_size = self.risk_manager.calculate_position_size(
            symbol=symbol,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            portfolio_value=self.portfolio_value
        )
        
        position_value = position_size * entry_price
        max_position_value = self.portfolio_value * Decimal('0.05')  # 5% max
        
        assert position_value <= max_position_value
        
    def test_validate_trade_success(self):
        """Test successful trade validation"""
        symbol = 'AAPL'
        quantity = Decimal('10')
        price = Decimal('150')
        
        is_valid, reason = self.risk_manager.validate_trade(
            symbol=symbol,
            side='buy',
            quantity=quantity,
            price=price,
            portfolio_value=self.portfolio_value
        )
        
        assert is_valid is True
        assert reason is None
        
    def test_validate_trade_position_too_large(self):
        """Test trade rejection for oversized position"""
        symbol = 'AAPL'
        quantity = Decimal('100')  # $15,000 position on $10k portfolio
        price = Decimal('150')
        
        is_valid, reason = self.risk_manager.validate_trade(
            symbol=symbol,
            side='buy',
            quantity=quantity,
            price=price,
            portfolio_value=self.portfolio_value
        )
        
        assert is_valid is False
        assert 'exceeds max' in reason
        
    def test_record_trade_result_profit(self):
        """Test recording profitable trade"""
        symbol = 'AAPL'
        pnl = Decimal('100')
        
        self.risk_manager.consecutive_losses = 3
        self.risk_manager.record_trade_result(symbol, pnl)
        
        assert self.risk_manager.daily_pnl == Decimal('100')
        assert self.risk_manager.consecutive_losses == 0
        
    def test_record_trade_result_loss(self):
        """Test recording losing trade"""
        symbol = 'AAPL'
        pnl = Decimal('-50')
        
        self.risk_manager.record_trade_result(symbol, pnl)
        
        assert self.risk_manager.daily_pnl == Decimal('-50')
        assert self.risk_manager.consecutive_losses == 1
        
    def test_stop_loss_check(self):
        """Test stop loss trigger detection"""
        symbol = 'AAPL'
        entry_price = Decimal('150')
        stop_loss = Decimal('147')
        quantity = Decimal('10')
        
        self.risk_manager.add_position(symbol, quantity, entry_price, stop_loss)
        
        # Price above stop loss
        assert self.risk_manager.check_stop_loss(symbol, Decimal('148')) is False
        
        # Price at stop loss
        assert self.risk_manager.check_stop_loss(symbol, Decimal('147')) is True
        
        # Price below stop loss
        assert self.risk_manager.check_stop_loss(symbol, Decimal('146')) is True
        
    def test_trailing_stop_update(self):
        """Test trailing stop loss update"""
        symbol = 'AAPL'
        entry_price = Decimal('150')
        stop_loss = Decimal('147')
        quantity = Decimal('10')
        
        self.risk_manager.add_position(symbol, quantity, entry_price, stop_loss)
        
        # Price moves up
        new_price = Decimal('155')
        self.risk_manager.update_trailing_stop(symbol, new_price, trailing_pct=2.0)
        
        # New stop should be 2% below current price
        expected_stop = new_price * Decimal('0.98')
        actual_stop = self.risk_manager.open_positions[symbol]['stop_loss']
        
        assert abs(actual_stop - expected_stop) < Decimal('0.01')
        assert actual_stop > stop_loss  # Stop moved up
        
    def test_reset_daily_stats(self):
        """Test daily statistics reset"""
        self.risk_manager.daily_pnl = Decimal('-500')
        self.risk_manager.consecutive_losses = 3
        self.risk_manager.trading_halted = True
        
        self.risk_manager.reset_daily_stats()
        
        assert self.risk_manager.daily_pnl == Decimal('0')
        assert self.risk_manager.consecutive_losses == 0
        assert self.risk_manager.trading_halted is False


class TestTechnicalStrategy:
    """Test technical analysis strategies"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.strategy = TechnicalStrategy()
        
        # Generate sample price data
        self.prices = [Decimal(str(100 + i * 0.5)) for i in range(100)]
        
    def test_rsi_oversold_signal(self):
        """Test RSI oversold buy signal"""
        # Create downtrend prices
        prices = [Decimal(str(100 - i * 0.5)) for i in range(50)]
        
        signal, confidence, details = self.strategy.analyze_rsi(prices)
        
        assert signal in ['buy', 'hold']
        assert 0 <= confidence <= 1
        assert 'rsi' in details
        
    def test_rsi_overbought_signal(self):
        """Test RSI overbought sell signal"""
        # Create uptrend prices
        prices = [Decimal(str(100 + i * 0.5)) for i in range(50)]
        
        signal, confidence, details = self.strategy.analyze_rsi(prices)
        
        assert signal in ['sell', 'hold']
        assert 0 <= confidence <= 1
        assert 'rsi' in details
        
    def test_macd_crossover_buy(self):
        """Test MACD bullish crossover"""
        signal, confidence, details = self.strategy.analyze_macd(self.prices)
        
        assert signal in ['buy', 'sell', 'hold']
        assert 0 <= confidence <= 1
        assert 'macd' in details
        assert 'signal' in details
        assert 'histogram' in details
        
    def test_bollinger_bands(self):
        """Test Bollinger Bands analysis"""
        signal, confidence, details = self.strategy.analyze_bollinger_bands(self.prices)
        
        assert signal in ['buy', 'sell', 'hold']
        assert 0 <= confidence <= 1
        assert 'upper_band' in details
        assert 'lower_band' in details
        assert 'middle_band' in details
        
    def test_moving_average_crossover(self):
        """Test moving average crossover"""
        # Need more data for MA crossover
        prices = [Decimal(str(100 + i * 0.1)) for i in range(250)]
        
        signal, confidence, details = self.strategy.analyze_moving_averages(prices)
        
        assert signal in ['buy', 'sell', 'hold']
        assert 0 <= confidence <= 1
        assert 'short_ma' in details
        assert 'long_ma' in details
        
    def test_momentum_indicator(self):
        """Test momentum indicator"""
        signal, confidence, details = self.strategy.analyze_momentum(self.prices)
        
        assert signal in ['buy', 'sell', 'hold']
        assert 0 <= confidence <= 1
        assert 'momentum' in details
        
    def test_combined_analysis(self):
        """Test combined technical analysis"""
        signal, confidence, details = self.strategy.combined_analysis(self.prices)
        
        assert signal in ['buy', 'sell', 'hold']
        assert 0 <= confidence <= 1
        assert 'combined' in details
        assert 'buy_signals' in details['combined']
        assert 'sell_signals' in details['combined']
        
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data"""
        short_prices = [Decimal('100'), Decimal('101')]
        
        signal, confidence, details = self.strategy.analyze_rsi(short_prices)
        
        assert signal == 'hold'
        assert confidence == 0.0
        assert 'error' in details


class TestIntegration:
    """Integration tests for complete trading flow"""
    
    @pytest.mark.asyncio
    async def test_trade_execution_flow(self):
        """Test complete trade execution flow"""
        # This would require mocking broker APIs
        # Placeholder for integration test
        pass
        
    @pytest.mark.asyncio
    async def test_position_monitoring_flow(self):
        """Test position monitoring and stop loss"""
        # Placeholder for integration test
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

