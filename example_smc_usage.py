"""
Пример использования Smart Money Concept Trading System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from smc_trading_system import SMCTradingSystem
from smc_analysis import SignalType

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data(symbol: str = "BTCUSDT", days: int = 100) -> pd.DataFrame:
    """Создание тестовых данных"""
    np.random.seed(42)
    
    # Базовые параметры
    start_price = 50000
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                         end=datetime.now(), freq='30min')
    
    # Создаем трендовые данные с шумом
    trend = np.linspace(0, 0.1, len(dates))  # Восходящий тренд
    noise = np.random.normal(0, 0.005, len(dates))
    prices = start_price * (1 + trend + noise)
    
    # Создаем OHLC данные
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # Создаем реалистичные свечи
        volatility = price * 0.002  # 0.2% волатильность
        
        open_price = price + np.random.normal(0, volatility/2)
        high_price = max(open_price, price) + abs(np.random.normal(0, volatility/2))
        low_price = min(open_price, price) - abs(np.random.normal(0, volatility/2))
        close_price = price + np.random.normal(0, volatility/2)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': np.random.uniform(1000, 10000)
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df

def run_smc_demo():
    """Демонстрация работы SMC системы"""
    print("🚀 Запуск демонстрации Smart Money Concept Trading System")
    print("=" * 60)
    
    # Создаем торговую систему
    smc_system = SMCTradingSystem()
    
    # Создаем тестовые данные
    print("📊 Создание тестовых данных...")
    df = create_sample_data("BTCUSDT", days=30)
    print(f"Создано {len(df)} свечей")
    
    # Анализируем рынок
    print("\n🔍 Анализ рынка...")
    market_analysis = smc_system.get_market_analysis(df)
    print(market_analysis)
    
    # Запускаем цикл анализа
    print("\n🔄 Запуск цикла анализа...")
    current_price = df.iloc[-1]['close']
    result = smc_system.run_analysis_cycle(df, current_price)
    
    print(f"Результаты анализа:")
    print(f"• Новых сигналов: {len(result['new_signals'])}")
    print(f"• Закрытых сигналов: {len(result['closed_signals'])}")
    print(f"• Активных сигналов: {result['active_signals']}")
    print(f"• Проанализировано: {result['total_analyzed']}")
    print(f"• Валидных сигналов: {result['valid_signals']}")
    
    # Если есть новые сигналы, показываем рекомендации
    if result['new_signals']:
        print("\n🎯 Новые сигналы:")
        for signal_id in result['new_signals']:
            signal = smc_system.active_signals[signal_id]
            recommendation = smc_system.get_signal_recommendation(signal)
            print(recommendation)
    
    # Показываем статистику
    print("\n📈 Статистика производительности:")
    performance_report = smc_system.get_performance_report(days=30)
    print(performance_report)
    
    # Экспортируем статистику
    print("\n💾 Экспорт статистики...")
    filename = smc_system.export_statistics()
    print(f"Статистика сохранена в: {filename}")
    
    print("\n✅ Демонстрация завершена!")

def test_signal_validation():
    """Тестирование валидации сигналов"""
    print("\n🧪 Тестирование валидации сигналов")
    print("=" * 40)
    
    smc_system = SMCTradingSystem()
    
    # Создаем тестовые данные
    df = create_sample_data("BTCUSDT", days=50)
    
    # Генерируем сигналы
    signals = smc_system.analyze_market_data(df)
    
    print(f"Сгенерировано сигналов: {len(signals)}")
    
    # Валидируем каждый сигнал
    for i, signal in enumerate(signals):
        is_valid = smc_system.validate_signal_logic(signal)
        status = "✅ Валиден" if is_valid else "❌ Невалиден"
        
        print(f"Сигнал {i+1}: {signal.signal_type.value} @ {signal.entry_price:.4f} - {status}")
        
        if not is_valid:
            print(f"  • Entry: {signal.entry_price:.4f}")
            print(f"  • Stop: {signal.stop_loss:.4f}")
            print(f"  • Take Profit: {signal.take_profit:.4f}")

if __name__ == "__main__":
    # Запускаем демонстрацию
    run_smc_demo()
    
    # Тестируем валидацию
    test_signal_validation() 