"""
Smart Money Concept Statistics Tracking
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from smc_analysis import SMCSignal, SignalType

class SignalStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"

@dataclass
class SignalResult:
    signal_id: str
    signal_type: SignalType
    entry_price: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    status: SignalStatus = SignalStatus.ACTIVE
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    confidence: float = 0.0

class SMCStatistics:
    def __init__(self):
        self.signals: List[SignalResult] = []
        self.current_id = 1
        
    def add_signal(self, signal: SMCSignal) -> str:
        """Добавление нового сигнала"""
        signal_id = f"SMC_{self.current_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = SignalResult(
            signal_id=signal_id,
            signal_type=signal.signal_type,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            entry_time=datetime.now(),
            confidence=signal.confidence
        )
        
        self.signals.append(result)
        self.current_id += 1
        
        return signal_id
    
    def close_signal(self, signal_id: str, exit_price: float, reason: str = "manual") -> bool:
        """Закрытие сигнала"""
        for signal in self.signals:
            if signal.signal_id == signal_id and signal.status == SignalStatus.ACTIVE:
                signal.exit_time = datetime.now()
                signal.exit_price = exit_price
                signal.status = SignalStatus.CLOSED
                
                # Расчет PnL
                if signal.signal_type == SignalType.LONG:
                    signal.pnl = exit_price - signal.entry_price
                    signal.pnl_percent = (signal.pnl / signal.entry_price) * 100
                else:  # SHORT
                    signal.pnl = signal.entry_price - exit_price
                    signal.pnl_percent = (signal.pnl / signal.entry_price) * 100
                
                return True
        return False
    
    def check_stop_loss(self, signal_id: str, current_price: float) -> bool:
        """Проверка стоп-лосса"""
        for signal in self.signals:
            if signal.signal_id == signal_id and signal.status == SignalStatus.ACTIVE:
                if signal.signal_type == SignalType.LONG:
                    if current_price <= signal.stop_loss:
                        return self.close_signal(signal_id, signal.stop_loss, "stop_loss")
                else:  # SHORT
                    if current_price >= signal.stop_loss:
                        return self.close_signal(signal_id, signal.stop_loss, "stop_loss")
        return False
    
    def check_take_profit(self, signal_id: str, current_price: float) -> bool:
        """Проверка тейк-профита"""
        for signal in self.signals:
            if signal.signal_id == signal_id and signal.status == SignalStatus.ACTIVE:
                if signal.signal_type == SignalType.LONG:
                    if current_price >= signal.take_profit:
                        return self.close_signal(signal_id, signal.take_profit, "take_profit")
                else:  # SHORT
                    if current_price <= signal.take_profit:
                        return self.close_signal(signal_id, signal.take_profit, "take_profit")
        return False
    
    def get_active_signals(self) -> List[SignalResult]:
        """Получение активных сигналов"""
        return [s for s in self.signals if s.status == SignalStatus.ACTIVE]
    
    def get_closed_signals(self, days: int = 30) -> List[SignalResult]:
        """Получение закрытых сигналов за последние дни"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [s for s in self.signals if s.status == SignalStatus.CLOSED and s.exit_time >= cutoff_date]
    
    def calculate_statistics(self, days: int = 30) -> Dict:
        """Расчет статистики"""
        closed_signals = self.get_closed_signals(days)
        
        if not closed_signals:
            return {
                "total_signals": 0,
                "win_rate": 0,
                "avg_pnl": 0,
                "avg_pnl_percent": 0,
                "total_pnl": 0,
                "best_trade": 0,
                "worst_trade": 0
            }
        
        total_signals = len(closed_signals)
        winning_signals = [s for s in closed_signals if s.pnl > 0]
        losing_signals = [s for s in closed_signals if s.pnl < 0]
        
        win_rate = len(winning_signals) / total_signals * 100
        avg_pnl = sum(s.pnl for s in closed_signals) / total_signals
        avg_pnl_percent = sum(s.pnl_percent for s in closed_signals) / total_signals
        total_pnl = sum(s.pnl for s in closed_signals)
        
        best_trade = max(s.pnl for s in closed_signals) if closed_signals else 0
        worst_trade = min(s.pnl for s in closed_signals) if closed_signals else 0
        
        return {
            "total_signals": total_signals,
            "win_rate": win_rate,
            "avg_pnl": avg_pnl,
            "avg_pnl_percent": avg_pnl_percent,
            "total_pnl": total_pnl,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "winning_signals": len(winning_signals),
            "losing_signals": len(losing_signals)
        }
    
    def get_signal_details(self, signal_id: str) -> Optional[SignalResult]:
        """Получение деталей сигнала"""
        for signal in self.signals:
            if signal.signal_id == signal_id:
                return signal
        return None
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Экспорт в DataFrame для анализа"""
        data = []
        for signal in self.signals:
            data.append({
                "signal_id": signal.signal_id,
                "signal_type": signal.signal_type.value,
                "entry_price": signal.entry_price,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "entry_time": signal.entry_time,
                "exit_time": signal.exit_time,
                "exit_price": signal.exit_price,
                "status": signal.status.value,
                "pnl": signal.pnl,
                "pnl_percent": signal.pnl_percent,
                "confidence": signal.confidence
            })
        
        return pd.DataFrame(data)
    
    def generate_report(self, days: int = 30) -> str:
        """Генерация отчета"""
        stats = self.calculate_statistics(days)
        active_signals = self.get_active_signals()
        
        report = f"""
📊 SMC Статистика за последние {days} дней:

📈 Общая статистика:
• Всего сигналов: {stats['total_signals']}
• Винрейт: {stats['win_rate']:.1f}%
• Средний PnL: {stats['avg_pnl']:.4f} ({stats['avg_pnl_percent']:.2f}%)
• Общий PnL: {stats['total_pnl']:.4f}

🏆 Лучшая сделка: {stats['best_trade']:.4f}
📉 Худшая сделка: {stats['worst_trade']:.4f}

✅ Прибыльные: {stats['winning_signals']}
❌ Убыточные: {stats['losing_signals']}

🔄 Активных сигналов: {len(active_signals)}
"""
        
        if active_signals:
            report += "\n📋 Активные сигналы:\n"
            for signal in active_signals:
                report += f"• {signal.signal_id}: {signal.signal_type.value} @ {signal.entry_price:.4f}\n"
        
        return report 