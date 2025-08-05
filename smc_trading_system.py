"""
Smart Money Concept Trading System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from smc_analysis import SMCAnalyzer, SMCSignal, SignalType, MarketStructure
from smc_statistics import SMCStatistics, SignalResult, SignalStatus

logger = logging.getLogger(__name__)

class SMCTradingSystem:
    def __init__(self):
        self.analyzer = SMCAnalyzer()
        self.statistics = SMCStatistics()
        self.active_signals: Dict[str, SMCSignal] = {}
        self.min_confidence = 0.7  # Минимальная уверенность для входа
        
    def analyze_market_data(self, df: pd.DataFrame) -> List[SMCSignal]:
        """Анализ рыночных данных и генерация сигналов"""
        try:
            # Проверяем достаточность данных
            if len(df) < 50:
                logger.warning("Недостаточно данных для анализа SMC")
                return []
            
            # Генерируем сигналы
            signals = self.analyzer.generate_smc_signals(df)
            
            # Фильтруем по уверенности
            filtered_signals = [s for s in signals if s.confidence >= self.min_confidence]
            
            logger.info(f"Сгенерировано {len(signals)} сигналов, отфильтровано {len(filtered_signals)}")
            
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Ошибка анализа рыночных данных: {e}")
            return []
    
    def process_new_signals(self, signals: List[SMCSignal], current_price: float) -> List[str]:
        """Обработка новых сигналов"""
        new_signal_ids = []
        
        for signal in signals:
            # Проверяем, нет ли уже активного сигнала того же типа
            existing_signals = [s for s in self.active_signals.values() if s.signal_type == signal.signal_type]
            
            if not existing_signals:  # Только если нет активных сигналов того же типа
                signal_id = self.statistics.add_signal(signal)
                self.active_signals[signal_id] = signal
                new_signal_ids.append(signal_id)
                
                logger.info(f"Новый сигнал: {signal_id} - {signal.signal_type.value} @ {signal.entry_price:.4f}")
        
        return new_signal_ids
    
    def update_active_signals(self, current_price: float) -> List[str]:
        """Обновление активных сигналов (проверка SL/TP)"""
        closed_signals = []
        
        for signal_id, signal in list(self.active_signals.items()):
            # Проверяем стоп-лосс
            if self.statistics.check_stop_loss(signal_id, current_price):
                closed_signals.append(signal_id)
                del self.active_signals[signal_id]
                logger.info(f"Сигнал {signal_id} закрыт по стоп-лоссу @ {current_price:.4f}")
                continue
            
            # Проверяем тейк-профит
            if self.statistics.check_take_profit(signal_id, current_price):
                closed_signals.append(signal_id)
                del self.active_signals[signal_id]
                logger.info(f"Сигнал {signal_id} закрыт по тейк-профиту @ {current_price:.4f}")
                continue
        
        return closed_signals
    
    def get_signal_recommendation(self, signal: SMCSignal) -> str:
        """Генерация рекомендации для сигнала"""
        direction = "🟢 LONG" if signal.signal_type == SignalType.LONG else "🔴 SHORT"
        
        recommendation = f"""
🎯 SMC Сигнал: {direction}

💰 Entry: {signal.entry_price:.4f}
🛑 Stop Loss: {signal.stop_loss:.4f}
🎯 Take Profit: {signal.take_profit:.4f}

📊 Детали:
• Уверенность: {signal.confidence:.1%}
• Структура рынка: {signal.market_structure.value}
• Order Block: {signal.order_block.direction} (сила: {signal.order_block.strength:.1%})

💡 Логика:
• Стоп размещен за границей Order Block
• Тейк рассчитан на основе размера OB (2x)
• Сигнал основан на {signal.market_structure.value} структуре
"""
        
        if signal.fvg:
            recommendation += f"• Fair Value Gap: {signal.fvg.direction} ({signal.fvg.low:.4f} - {signal.fvg.high:.4f})\n"
        
        return recommendation
    
    def get_market_analysis(self, df: pd.DataFrame) -> str:
        """Анализ текущего состояния рынка"""
        if len(df) < 20:
            return "Недостаточно данных для анализа"
        
        market_structure = self.analyzer.analyze_market_structure(df)
        current_price = df.iloc[-1]['close']
        
        # Поиск Order Blocks
        bullish_obs = self.analyzer.find_order_blocks(df, "bullish")
        bearish_obs = self.analyzer.find_order_blocks(df, "bearish")
        
        # Поиск FVG
        fvgs = self.analyzer.find_fair_value_gaps(df)
        
        analysis = f"""
📊 Анализ рынка:

🎯 Структура: {market_structure.value.upper()}
💰 Текущая цена: {current_price:.4f}

📦 Order Blocks:
• Bullish: {len(bullish_obs)}
• Bearish: {len(bearish_obs)}

🕳️ Fair Value Gaps: {len(fvgs)}

🔄 Активных сигналов: {len(self.active_signals)}
"""
        
        if self.active_signals:
            analysis += "\n📋 Активные сигналы:\n"
            for signal_id, signal in self.active_signals.items():
                status = "🟢" if signal.signal_type == SignalType.LONG else "🔴"
                analysis += f"• {status} {signal_id}: {signal.signal_type.value} @ {signal.entry_price:.4f}\n"
        
        return analysis
    
    def get_performance_report(self, days: int = 30) -> str:
        """Отчет о производительности"""
        return self.statistics.generate_report(days)
    
    def export_statistics(self, filename: str = None) -> str:
        """Экспорт статистики в CSV"""
        if filename is None:
            filename = f"smc_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df = self.statistics.export_to_dataframe()
        df.to_csv(filename, index=False)
        
        logger.info(f"Статистика экспортирована в {filename}")
        return filename
    
    def validate_signal_logic(self, signal: SMCSignal) -> bool:
        """Валидация логики сигнала"""
        # Проверяем логичность стопов и тейков
        if signal.signal_type == SignalType.LONG:
            # Для лонга: стоп должен быть ниже входа, тейк выше
            if signal.stop_loss >= signal.entry_price:
                logger.warning(f"Некорректный стоп для LONG: {signal.stop_loss} >= {signal.entry_price}")
                return False
            if signal.take_profit <= signal.entry_price:
                logger.warning(f"Некорректный тейк для LONG: {signal.take_profit} <= {signal.entry_price}")
                return False
        else:  # SHORT
            # Для шорта: стоп должен быть выше входа, тейк ниже
            if signal.stop_loss <= signal.entry_price:
                logger.warning(f"Некорректный стоп для SHORT: {signal.stop_loss} <= {signal.entry_price}")
                return False
            if signal.take_profit >= signal.entry_price:
                logger.warning(f"Некорректный тейк для SHORT: {signal.take_profit} >= {signal.entry_price}")
                return False
        
        # Проверяем размер Order Block
        ob_size = signal.order_block.high - signal.order_block.low
        if ob_size <= 0:
            logger.warning("Некорректный размер Order Block")
            return False
        
        return True
    
    def run_analysis_cycle(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Полный цикл анализа и обработки сигналов"""
        try:
            # Обновляем активные сигналы
            closed_signals = self.update_active_signals(current_price)
            
            # Анализируем рынок
            new_signals = self.analyze_market_data(df)
            
            # Валидируем сигналы
            valid_signals = [s for s in new_signals if self.validate_signal_logic(s)]
            
            # Обрабатываем новые сигналы
            new_signal_ids = self.process_new_signals(valid_signals, current_price)
            
            return {
                "new_signals": new_signal_ids,
                "closed_signals": closed_signals,
                "active_signals": len(self.active_signals),
                "total_analyzed": len(new_signals),
                "valid_signals": len(valid_signals)
            }
            
        except Exception as e:
            logger.error(f"Ошибка в цикле анализа: {e}")
            return {
                "new_signals": [],
                "closed_signals": [],
                "active_signals": len(self.active_signals),
                "total_analyzed": 0,
                "valid_signals": 0,
                "error": str(e)
            } 