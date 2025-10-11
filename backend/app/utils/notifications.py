"""
Notification system for alerts and updates
Supports Telegram, SMS (Twilio), and Email
"""
import logging
from typing import Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manage notifications across multiple channels"""
    
    def __init__(self):
        self.telegram_enabled = bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
        self.sms_enabled = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        self.email_enabled = bool(settings.ALERT_EMAIL)
        
        if self.telegram_enabled:
            try:
                from telegram import Bot
                self.telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                logger.info("Telegram notifications enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram: {e}")
                self.telegram_enabled = False
                
        if self.sms_enabled:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                logger.info("SMS notifications enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
                self.sms_enabled = False
                
    async def send_telegram(self, message: str, parse_mode: str = 'HTML'):
        """Send Telegram notification"""
        if not self.telegram_enabled:
            return False
            
        try:
            await self.telegram_bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=parse_mode
            )
            logger.debug(f"Telegram notification sent: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
            
    def send_sms(self, message: str, phone_number: Optional[str] = None):
        """Send SMS notification"""
        if not self.sms_enabled:
            return False
            
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_FROM_NUMBER,
                to=phone_number or settings.ALERT_EMAIL  # Fallback to configured number
            )
            logger.debug(f"SMS notification sent: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return False
            
    async def notify_trade_executed(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        order_id: str
    ):
        """Notify when trade is executed"""
        message = (
            f"🔔 <b>Trade Executed</b>\n\n"
            f"Symbol: {symbol}\n"
            f"Side: {side.upper()}\n"
            f"Quantity: {quantity}\n"
            f"Price: ${price:.4f}\n"
            f"Value: ${quantity * price:.2f}\n"
            f"Order ID: {order_id}\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        await self.send_telegram(message)
        
    async def notify_position_closed(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        exit_price: float,
        pnl: float,
        pnl_pct: float
    ):
        """Notify when position is closed"""
        emoji = "✅" if pnl > 0 else "❌"
        
        message = (
            f"{emoji} <b>Position Closed</b>\n\n"
            f"Symbol: {symbol}\n"
            f"Quantity: {quantity}\n"
            f"Entry: ${entry_price:.4f}\n"
            f"Exit: ${exit_price:.4f}\n"
            f"P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        await self.send_telegram(message)
        
    async def notify_stop_loss_triggered(
        self,
        symbol: str,
        quantity: float,
        stop_price: float,
        current_price: float
    ):
        """Notify when stop loss is triggered"""
        message = (
            f"⚠️ <b>Stop Loss Triggered</b>\n\n"
            f"Symbol: {symbol}\n"
            f"Quantity: {quantity}\n"
            f"Stop Price: ${stop_price:.4f}\n"
            f"Current Price: ${current_price:.4f}\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        await self.send_telegram(message)
        
    async def notify_risk_alert(
        self,
        alert_type: str,
        severity: str,
        message_text: str
    ):
        """Notify risk management alerts"""
        emoji_map = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '⚡',
            'low': 'ℹ️'
        }
        
        emoji = emoji_map.get(severity.lower(), 'ℹ️')
        
        message = (
            f"{emoji} <b>Risk Alert - {severity.upper()}</b>\n\n"
            f"Type: {alert_type}\n"
            f"Message: {message_text}\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        await self.send_telegram(message)
        
        # Send SMS for critical alerts
        if severity.lower() == 'critical' and self.sms_enabled:
            sms_message = f"CRITICAL ALERT: {alert_type} - {message_text}"
            self.send_sms(sms_message)
            
    async def notify_daily_summary(
        self,
        pnl: float,
        pnl_pct: float,
        trades: int,
        wins: int,
        losses: int,
        portfolio_value: float
    ):
        """Send daily trading summary"""
        win_rate = (wins / trades * 100) if trades > 0 else 0
        emoji = "📈" if pnl > 0 else "📉"
        
        message = (
            f"{emoji} <b>Daily Summary</b>\n\n"
            f"P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)\n"
            f"Total Trades: {trades}\n"
            f"Wins: {wins} | Losses: {losses}\n"
            f"Win Rate: {win_rate:.1f}%\n"
            f"Portfolio Value: ${portfolio_value:.2f}\n"
            f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}"
        )
        
        await self.send_telegram(message)
        
    async def notify_system_status(
        self,
        status: str,
        message_text: str
    ):
        """Notify system status changes"""
        emoji_map = {
            'started': '🟢',
            'stopped': '🔴',
            'error': '❌',
            'warning': '⚠️'
        }
        
        emoji = emoji_map.get(status.lower(), 'ℹ️')
        
        message = (
            f"{emoji} <b>System Status: {status.upper()}</b>\n\n"
            f"{message_text}\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        await self.send_telegram(message)


# Global notification manager instance
notification_manager = NotificationManager()

