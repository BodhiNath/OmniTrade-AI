"""
Technical Analysis Trading Strategies
Implements RSI, MACD, Bollinger Bands, Moving Averages, and more
"""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging

import pandas as pd
import numpy as np
import ta

logger = logging.getLogger(__name__)


class TechnicalStrategy:
    """Technical analysis strategy engine"""
    
    def __init__(self, name: str = "Technical"):
        self.name = name
        
    def analyze_rsi(
        self,
        prices: List[Decimal],
        period: int = 14,
        oversold: int = 30,
        overbought: int = 70
    ) -> Tuple[str, float, Dict]:
        """
        RSI (Relative Strength Index) analysis
        
        Returns:
            (signal, confidence, details)
            signal: 'buy', 'sell', or 'hold'
            confidence: 0.0 to 1.0
        """
        if len(prices) < period + 1:
            return 'hold', 0.0, {'error': 'Insufficient data'}
            
        df = pd.DataFrame({'close': [float(p) for p in prices]})
        rsi = ta.momentum.RSIIndicator(df['close'], window=period).rsi()
        current_rsi = rsi.iloc[-1]
        
        # Generate signal
        if current_rsi < oversold:
            signal = 'buy'
            confidence = min((oversold - current_rsi) / oversold, 1.0)
        elif current_rsi > overbought:
            signal = 'sell'
            confidence = min((current_rsi - overbought) / (100 - overbought), 1.0)
        else:
            signal = 'hold'
            confidence = 0.0
            
        details = {
            'rsi': round(current_rsi, 2),
            'oversold_threshold': oversold,
            'overbought_threshold': overbought,
            'period': period
        }
        
        logger.info(f"RSI Analysis: {signal.upper()} (RSI: {current_rsi:.2f}, Confidence: {confidence:.2f})")
        return signal, confidence, details
        
    def analyze_macd(
        self,
        prices: List[Decimal],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[str, float, Dict]:
        """
        MACD (Moving Average Convergence Divergence) analysis
        """
        if len(prices) < slow_period + signal_period:
            return 'hold', 0.0, {'error': 'Insufficient data'}
            
        df = pd.DataFrame({'close': [float(p) for p in prices]})
        macd_indicator = ta.trend.MACD(
            df['close'],
            window_fast=fast_period,
            window_slow=slow_period,
            window_sign=signal_period
        )
        
        macd_line = macd_indicator.macd()
        signal_line = macd_indicator.macd_signal()
        histogram = macd_indicator.macd_diff()
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_hist = histogram.iloc[-1]
        prev_hist = histogram.iloc[-2]
        
        # Generate signal based on crossover
        if current_hist > 0 and prev_hist <= 0:
            signal = 'buy'
            confidence = min(abs(current_hist) / abs(current_signal), 1.0) if current_signal != 0 else 0.5
        elif current_hist < 0 and prev_hist >= 0:
            signal = 'sell'
            confidence = min(abs(current_hist) / abs(current_signal), 1.0) if current_signal != 0 else 0.5
        else:
            signal = 'hold'
            confidence = 0.0
            
        details = {
            'macd': round(current_macd, 4),
            'signal': round(current_signal, 4),
            'histogram': round(current_hist, 4),
            'crossover': signal != 'hold'
        }
        
        logger.info(f"MACD Analysis: {signal.upper()} (Hist: {current_hist:.4f}, Confidence: {confidence:.2f})")
        return signal, confidence, details
        
    def analyze_bollinger_bands(
        self,
        prices: List[Decimal],
        period: int = 20,
        std_dev: int = 2
    ) -> Tuple[str, float, Dict]:
        """
        Bollinger Bands analysis
        """
        if len(prices) < period:
            return 'hold', 0.0, {'error': 'Insufficient data'}
            
        df = pd.DataFrame({'close': [float(p) for p in prices]})
        bb_indicator = ta.volatility.BollingerBands(
            df['close'],
            window=period,
            window_dev=std_dev
        )
        
        upper_band = bb_indicator.bollinger_hband()
        lower_band = bb_indicator.bollinger_lband()
        middle_band = bb_indicator.bollinger_mavg()
        
        current_price = float(prices[-1])
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_middle = middle_band.iloc[-1]
        
        band_width = current_upper - current_lower
        
        # Generate signal
        if current_price <= current_lower:
            signal = 'buy'
            confidence = min((current_lower - current_price) / band_width, 1.0)
        elif current_price >= current_upper:
            signal = 'sell'
            confidence = min((current_price - current_upper) / band_width, 1.0)
        else:
            signal = 'hold'
            confidence = 0.0
            
        details = {
            'current_price': round(current_price, 2),
            'upper_band': round(current_upper, 2),
            'middle_band': round(current_middle, 2),
            'lower_band': round(current_lower, 2),
            'band_width': round(band_width, 2)
        }
        
        logger.info(f"Bollinger Bands: {signal.upper()} (Price: {current_price:.2f}, Confidence: {confidence:.2f})")
        return signal, confidence, details
        
    def analyze_moving_averages(
        self,
        prices: List[Decimal],
        short_period: int = 50,
        long_period: int = 200
    ) -> Tuple[str, float, Dict]:
        """
        Moving Average Crossover (Golden Cross / Death Cross)
        """
        if len(prices) < long_period:
            return 'hold', 0.0, {'error': 'Insufficient data'}
            
        df = pd.DataFrame({'close': [float(p) for p in prices]})
        
        short_ma = df['close'].rolling(window=short_period).mean()
        long_ma = df['close'].rolling(window=long_period).mean()
        
        current_short = short_ma.iloc[-1]
        current_long = long_ma.iloc[-1]
        prev_short = short_ma.iloc[-2]
        prev_long = long_ma.iloc[-2]
        
        # Detect crossover
        if current_short > current_long and prev_short <= prev_long:
            signal = 'buy'  # Golden Cross
            confidence = min(abs(current_short - current_long) / current_long, 1.0)
        elif current_short < current_long and prev_short >= prev_long:
            signal = 'sell'  # Death Cross
            confidence = min(abs(current_long - current_short) / current_long, 1.0)
        else:
            signal = 'hold'
            confidence = 0.0
            
        details = {
            'short_ma': round(current_short, 2),
            'long_ma': round(current_long, 2),
            'short_period': short_period,
            'long_period': long_period,
            'crossover': signal != 'hold'
        }
        
        logger.info(f"MA Crossover: {signal.upper()} (Short: {current_short:.2f}, Long: {current_long:.2f})")
        return signal, confidence, details
        
    def analyze_momentum(
        self,
        prices: List[Decimal],
        period: int = 14
    ) -> Tuple[str, float, Dict]:
        """
        Momentum indicator analysis
        """
        if len(prices) < period + 1:
            return 'hold', 0.0, {'error': 'Insufficient data'}
            
        current_price = float(prices[-1])
        past_price = float(prices[-period-1])
        
        momentum = ((current_price - past_price) / past_price) * 100
        
        # Generate signal based on momentum
        if momentum > 5:
            signal = 'buy'
            confidence = min(momentum / 20, 1.0)
        elif momentum < -5:
            signal = 'sell'
            confidence = min(abs(momentum) / 20, 1.0)
        else:
            signal = 'hold'
            confidence = 0.0
            
        details = {
            'momentum': round(momentum, 2),
            'current_price': round(current_price, 2),
            'past_price': round(past_price, 2),
            'period': period
        }
        
        logger.info(f"Momentum: {signal.upper()} ({momentum:.2f}%, Confidence: {confidence:.2f})")
        return signal, confidence, details
        
    def combined_analysis(
        self,
        prices: List[Decimal],
        indicators: Optional[List[str]] = None
    ) -> Tuple[str, float, Dict]:
        """
        Combined technical analysis using multiple indicators
        
        Args:
            prices: Historical price data
            indicators: List of indicators to use (default: all)
            
        Returns:
            (signal, confidence, details)
        """
        if indicators is None:
            indicators = ['rsi', 'macd', 'bollinger', 'ma', 'momentum']
            
        results = {}
        signals = []
        confidences = []
        
        # Run each indicator
        if 'rsi' in indicators:
            signal, conf, details = self.analyze_rsi(prices)
            results['rsi'] = {'signal': signal, 'confidence': conf, 'details': details}
            if signal != 'hold':
                signals.append(signal)
                confidences.append(conf)
                
        if 'macd' in indicators:
            signal, conf, details = self.analyze_macd(prices)
            results['macd'] = {'signal': signal, 'confidence': conf, 'details': details}
            if signal != 'hold':
                signals.append(signal)
                confidences.append(conf)
                
        if 'bollinger' in indicators:
            signal, conf, details = self.analyze_bollinger_bands(prices)
            results['bollinger'] = {'signal': signal, 'confidence': conf, 'details': details}
            if signal != 'hold':
                signals.append(signal)
                confidences.append(conf)
                
        if 'ma' in indicators:
            signal, conf, details = self.analyze_moving_averages(prices)
            results['ma'] = {'signal': signal, 'confidence': conf, 'details': details}
            if signal != 'hold':
                signals.append(signal)
                confidences.append(conf)
                
        if 'momentum' in indicators:
            signal, conf, details = self.analyze_momentum(prices)
            results['momentum'] = {'signal': signal, 'confidence': conf, 'details': details}
            if signal != 'hold':
                signals.append(signal)
                confidences.append(conf)
        
        # Aggregate signals
        if not signals:
            return 'hold', 0.0, results
            
        buy_signals = signals.count('buy')
        sell_signals = signals.count('sell')
        
        if buy_signals > sell_signals:
            final_signal = 'buy'
            avg_confidence = sum(c for s, c in zip(signals, confidences) if s == 'buy') / buy_signals
        elif sell_signals > buy_signals:
            final_signal = 'sell'
            avg_confidence = sum(c for s, c in zip(signals, confidences) if s == 'sell') / sell_signals
        else:
            final_signal = 'hold'
            avg_confidence = 0.0
            
        results['combined'] = {
            'signal': final_signal,
            'confidence': avg_confidence,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_signals': len(signals)
        }
        
        logger.info(f"Combined Analysis: {final_signal.upper()} (Buy: {buy_signals}, Sell: {sell_signals}, Confidence: {avg_confidence:.2f})")
        return final_signal, avg_confidence, results

