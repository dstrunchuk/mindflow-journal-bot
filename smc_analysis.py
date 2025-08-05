"""
Smart Money Concept (SMC) Analysis Module
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class MarketStructure(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"

class SignalType(Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class OrderBlock:
    high: float
    low: float
    open: float
    close: float
    direction: str  # "bullish" or "bearish"
    strength: float  # 0-1

@dataclass
class FairValueGap:
    high: float
    low: float
    direction: str  # "bullish" or "bearish"
    filled: bool = False

@dataclass
class SMCSignal:
    signal_type: SignalType
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float  # 0-1
    order_block: OrderBlock
    fvg: Optional[FairValueGap] = None
    market_structure: MarketStructure = MarketStructure.SIDEWAYS

class SMCAnalyzer:
    def __init__(self):
        self.min_ob_strength = 0.6
        self.fvg_threshold = 0.001  # 0.1% для определения FVG
        
    def analyze_market_structure(self, df: pd.DataFrame) -> MarketStructure:
        """Анализ структуры рынка (BOS/CHoCH)"""
        if len(df) < 20:
            return MarketStructure.SIDEWAYS
            
        # Находим последние экстремумы
        highs = df['high'].rolling(5).max()
        lows = df['low'].rolling(5).min()
        
        # Определяем BOS/CHoCH
        recent_highs = highs.tail(10)
        recent_lows = lows.tail(10)
        
        # Проверяем BOS вверх
        if recent_highs.iloc[-1] > recent_highs.iloc[-2]:
            return MarketStructure.BULLISH
        # Проверяем BOS вниз
        elif recent_lows.iloc[-1] < recent_lows.iloc[-2]:
            return MarketStructure.BEARISH
            
        return MarketStructure.SIDEWAYS
    
    def find_order_blocks(self, df: pd.DataFrame, direction: str) -> List[OrderBlock]:
        """Поиск Order Blocks"""
        order_blocks = []
        
        for i in range(2, len(df) - 1):
            current_candle = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bullish OB: красная свеча перед зеленым импульсом
            if direction == "bullish":
                if (current_candle['close'] < current_candle['open'] and  # Красная свеча
                    next_candle['close'] > next_candle['open'] and  # Зеленая свеча
                    next_candle['close'] > current_candle['high']):  # Импульс вверх
                    
                    strength = abs(next_candle['close'] - current_candle['high']) / current_candle['high']
                    if strength > self.min_ob_strength:
                        ob = OrderBlock(
                            high=current_candle['high'],
                            low=current_candle['low'],
                            open=current_candle['open'],
                            close=current_candle['close'],
                            direction="bullish",
                            strength=strength
                        )
                        order_blocks.append(ob)
            
            # Bearish OB: зеленая свеча перед красным импульсом
            elif direction == "bearish":
                if (current_candle['close'] > current_candle['open'] and  # Зеленая свеча
                    next_candle['close'] < next_candle['open'] and  # Красная свеча
                    next_candle['close'] < current_candle['low']):  # Импульс вниз
                    
                    strength = abs(current_candle['low'] - next_candle['close']) / current_candle['low']
                    if strength > self.min_ob_strength:
                        ob = OrderBlock(
                            high=current_candle['high'],
                            low=current_candle['low'],
                            open=current_candle['open'],
                            close=current_candle['close'],
                            direction="bearish",
                            strength=strength
                        )
                        order_blocks.append(ob)
        
        return order_blocks
    
    def find_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """Поиск Fair Value Gaps"""
        fvgs = []
        
        for i in range(1, len(df) - 1):
            prev_candle = df.iloc[i - 1]
            current_candle = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bullish FVG: gap вверх
            if (prev_candle['high'] < current_candle['low'] and
                abs(current_candle['low'] - prev_candle['high']) / prev_candle['high'] > self.fvg_threshold):
                
                fvg = FairValueGap(
                    high=current_candle['low'],
                    low=prev_candle['high'],
                    direction="bullish"
                )
                fvgs.append(fvg)
            
            # Bearish FVG: gap вниз
            elif (next_candle['high'] < current_candle['low'] and
                  abs(current_candle['low'] - next_candle['high']) / current_candle['low'] > self.fvg_threshold):
                
                fvg = FairValueGap(
                    high=current_candle['low'],
                    low=next_candle['high'],
                    direction="bearish"
                )
                fvgs.append(fvg)
        
        return fvgs
    
    def check_liquidity_sweep(self, df: pd.DataFrame, direction: str) -> bool:
        """Проверка Sweep ликвидности"""
        if len(df) < 10:
            return False
            
        recent_data = df.tail(10)
        
        if direction == "bullish":
            # Проверяем sweep под лоями
            recent_low = recent_data['low'].min()
            current_price = df.iloc[-1]['close']
            return current_price > recent_low
        else:
            # Проверяем sweep над хаями
            recent_high = recent_data['high'].max()
            current_price = df.iloc[-1]['close']
            return current_price < recent_high
    
    def calculate_logical_stops(self, signal_type: SignalType, order_block: OrderBlock, 
                              current_price: float) -> Tuple[float, float]:
        """Расчет логичных стопов и тейков"""
        
        if signal_type == SignalType.LONG:
            # Для лонга: стоп под OB, тейк над OB
            stop_loss = order_block.low * 0.999  # Чуть ниже OB
            take_profit = order_block.high * 1.005  # Чуть выше OB
            
            # Адаптивный TP на основе размера OB
            ob_size = order_block.high - order_block.low
            take_profit = current_price + (ob_size * 2)  # 2x размер OB
            
        else:  # SHORT
            # Для шорта: стоп над OB, тейк под OB
            stop_loss = order_block.high * 1.001  # Чуть выше OB
            take_profit = order_block.low * 0.995  # Чуть ниже OB
            
            # Адаптивный TP на основе размера OB
            ob_size = order_block.high - order_block.low
            take_profit = current_price - (ob_size * 2)  # 2x размер OB
        
        return stop_loss, take_profit
    
    def generate_smc_signals(self, df: pd.DataFrame) -> List[SMCSignal]:
        """Генерация SMC сигналов"""
        signals = []
        
        if len(df) < 20:
            return signals
        
        # Анализ структуры рынка
        market_structure = self.analyze_market_structure(df)
        current_price = df.iloc[-1]['close']
        
        # Поиск Order Blocks
        bullish_obs = self.find_order_blocks(df, "bullish")
        bearish_obs = self.find_order_blocks(df, "bearish")
        
        # Поиск FVG
        fvgs = self.find_fair_value_gaps(df)
        
        # Генерация LONG сигналов
        if market_structure == MarketStructure.BULLISH:
            for ob in bullish_obs[-3:]:  # Последние 3 OB
                if current_price >= ob.low and current_price <= ob.high:
                    # Проверяем sweep ликвидности
                    if self.check_liquidity_sweep(df, "bullish"):
                        stop_loss, take_profit = self.calculate_logical_stops(
                            SignalType.LONG, ob, current_price
                        )
                        
                        # Находим ближайший FVG
                        nearest_fvg = None
                        for fvg in fvgs:
                            if fvg.direction == "bullish" and fvg.high > current_price:
                                nearest_fvg = fvg
                                break
                        
                        signal = SMCSignal(
                            signal_type=SignalType.LONG,
                            entry_price=current_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            confidence=ob.strength,
                            order_block=ob,
                            fvg=nearest_fvg,
                            market_structure=market_structure
                        )
                        signals.append(signal)
        
        # Генерация SHORT сигналов
        elif market_structure == MarketStructure.BEARISH:
            for ob in bearish_obs[-3:]:  # Последние 3 OB
                if current_price >= ob.low and current_price <= ob.high:
                    # Проверяем sweep ликвидности
                    if self.check_liquidity_sweep(df, "bearish"):
                        stop_loss, take_profit = self.calculate_logical_stops(
                            SignalType.SHORT, ob, current_price
                        )
                        
                        # Находим ближайший FVG
                        nearest_fvg = None
                        for fvg in fvgs:
                            if fvg.direction == "bearish" and fvg.low < current_price:
                                nearest_fvg = fvg
                                break
                        
                        signal = SMCSignal(
                            signal_type=SignalType.SHORT,
                            entry_price=current_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            confidence=ob.strength,
                            order_block=ob,
                            fvg=nearest_fvg,
                            market_structure=market_structure
                        )
                        signals.append(signal)
        
        return signals 