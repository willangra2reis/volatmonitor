#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technical Indicators - Cálculo de Indicadores Técnicos
Implementa Hull MA, Z-Score, SMA, EMA, RSI e outros indicadores
"""

import math
from collections import deque
from typing import List, Optional, Dict


class TechnicalIndicators:
    """
    Classe para cálculo de indicadores técnicos
    """
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> Optional[float]:
        """
        Simple Moving Average (SMA)
        
        Args:
            prices: Lista de preços
            period: Período da média
            
        Returns:
            Valor da SMA ou None se não houver dados suficientes
        """
        if len(prices) < period:
            return None
        
        recent_prices = list(prices)[-period:]
        return sum(recent_prices) / period
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int, previous_ema: Optional[float] = None) -> Optional[float]:
        """
        Exponential Moving Average (EMA)
        
        Args:
            prices: Lista de preços
            period: Período da média
            previous_ema: EMA anterior (para cálculo incremental)
            
        Returns:
            Valor da EMA ou None se não houver dados suficientes
        """
        if len(prices) < period:
            return None
        
        # Se não há EMA anterior, usa SMA como base
        if previous_ema is None:
            return TechnicalIndicators.calculate_sma(prices, period)
        
        # Fator de suavização
        multiplier = 2 / (period + 1)
        
        # EMA = (Preço Atual * Multiplicador) + (EMA Anterior * (1 - Multiplicador))
        current_price = prices[-1]
        ema = (current_price * multiplier) + (previous_ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def calculate_wma(prices: List[float], period: int) -> Optional[float]:
        """
        Weighted Moving Average (WMA)
        
        Args:
            prices: Lista de preços
            period: Período da média
            
        Returns:
            Valor da WMA ou None se não houver dados suficientes
        """
        if len(prices) < period:
            return None
        
        recent_prices = list(prices)[-period:]
        weights = list(range(1, period + 1))
        weight_sum = sum(weights)
        
        wma = sum(p * w for p, w in zip(recent_prices, weights)) / weight_sum
        return wma
    
    @staticmethod
    def calculate_hull_ma(prices: List[float], period: int = 20) -> Optional[float]:
        """
        Hull Moving Average (HMA)
        Fórmula: HMA(n) = WMA(2 * WMA(n/2) - WMA(n), sqrt(n))
        
        Args:
            prices: Lista de preços
            period: Período da média (padrão: 20)
            
        Returns:
            Valor da Hull MA ou None se não houver dados suficientes
        """
        if len(prices) < period:
            return None
        
        # Passo 1: Calcular WMA(n/2)
        half_period = period // 2
        wma_half = TechnicalIndicators.calculate_wma(prices, half_period)
        
        # Passo 2: Calcular WMA(n)
        wma_full = TechnicalIndicators.calculate_wma(prices, period)
        
        if wma_half is None or wma_full is None:
            return None
        
        # Passo 3: Calcular 2 * WMA(n/2) - WMA(n)
        raw_hma = 2 * wma_half - wma_full
        
        # Passo 4: Calcular WMA(sqrt(n)) do resultado
        # Para isso, precisamos de uma série de valores raw_hma
        # Simplificação: retornar raw_hma (versão básica)
        # Para versão completa, seria necessário manter histórico de raw_hma
        
        sqrt_period = int(math.sqrt(period))
        
        # Versão simplificada (retorna raw_hma)
        # Em produção, deveria manter histórico de raw_hma e calcular WMA sobre ele
        return raw_hma
    
    @staticmethod
    def calculate_zscore(prices: List[float], window: int = 20) -> Optional[float]:
        """
        Z-Score
        Fórmula: Z = (Preço Atual - Média) / Desvio Padrão
        
        Args:
            prices: Lista de preços
            window: Janela para cálculo (padrão: 20)
            
        Returns:
            Valor do Z-Score ou None se não houver dados suficientes
        """
        if len(prices) < window:
            return None
        
        recent_prices = list(prices)[-window:]
        
        # Calcular média
        mean = sum(recent_prices) / window
        
        # Calcular desvio padrão
        variance = sum((x - mean) ** 2 for x in recent_prices) / window
        std_dev = math.sqrt(variance)
        
        # Evitar divisão por zero
        if std_dev == 0:
            return 0
        
        # Calcular Z-Score
        current_price = prices[-1]
        zscore = (current_price - mean) / std_dev
        
        return zscore
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Relative Strength Index (RSI)
        
        Args:
            prices: Lista de preços
            period: Período do RSI (padrão: 14)
            
        Returns:
            Valor do RSI (0-100) ou None se não houver dados suficientes
        """
        if len(prices) < period + 1:
            return None
        
        # Calcular mudanças de preço
        changes = []
        for i in range(len(prices) - period, len(prices)):
            if i > 0:
                changes.append(prices[i] - prices[i-1])
        
        # Separar ganhos e perdas
        gains = [change if change > 0 else 0 for change in changes]
        losses = [-change if change < 0 else 0 for change in changes]
        
        # Calcular média de ganhos e perdas
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        # Evitar divisão por zero
        if avg_loss == 0:
            return 100
        
        # Calcular RS e RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev_multiplier: float = 2.0) -> Optional[Dict[str, float]]:
        """
        Bollinger Bands
        
        Args:
            prices: Lista de preços
            period: Período da média (padrão: 20)
            std_dev_multiplier: Multiplicador do desvio padrão (padrão: 2.0)
            
        Returns:
            Dicionário com upper, middle, lower ou None
        """
        if len(prices) < period:
            return None
        
        recent_prices = list(prices)[-period:]
        
        # Calcular SMA (banda do meio)
        middle = sum(recent_prices) / period
        
        # Calcular desvio padrão
        variance = sum((x - middle) ** 2 for x in recent_prices) / period
        std_dev = math.sqrt(variance)
        
        # Calcular bandas superior e inferior
        upper = middle + (std_dev_multiplier * std_dev)
        lower = middle - (std_dev_multiplier * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'std_dev': std_dev
        }
    
    @staticmethod
    def calculate_atr(high_prices: List[float], low_prices: List[float], close_prices: List[float], period: int = 14) -> Optional[float]:
        """
        Average True Range (ATR)
        
        Args:
            high_prices: Lista de preços máximos
            low_prices: Lista de preços mínimos
            close_prices: Lista de preços de fechamento
            period: Período do ATR (padrão: 14)
            
        Returns:
            Valor do ATR ou None
        """
        if len(high_prices) < period + 1 or len(low_prices) < period + 1 or len(close_prices) < period + 1:
            return None
        
        true_ranges = []
        
        for i in range(len(close_prices) - period, len(close_prices)):
            if i > 0:
                high_low = high_prices[i] - low_prices[i]
                high_close = abs(high_prices[i] - close_prices[i-1])
                low_close = abs(low_prices[i] - close_prices[i-1])
                
                true_range = max(high_low, high_close, low_close)
                true_ranges.append(true_range)
        
        atr = sum(true_ranges) / len(true_ranges)
        return atr
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Optional[Dict[str, float]]:
        """
        Moving Average Convergence Divergence (MACD)
        
        Args:
            prices: Lista de preços
            fast_period: Período da EMA rápida (padrão: 12)
            slow_period: Período da EMA lenta (padrão: 26)
            signal_period: Período da linha de sinal (padrão: 9)
            
        Returns:
            Dicionário com macd, signal, histogram ou None
        """
        if len(prices) < slow_period + signal_period:
            return None
        
        # Calcular EMAs
        ema_fast = TechnicalIndicators.calculate_ema(prices, fast_period)
        ema_slow = TechnicalIndicators.calculate_ema(prices, slow_period)
        
        if ema_fast is None or ema_slow is None:
            return None
        
        # MACD Line
        macd_line = ema_fast - ema_slow
        
        # Signal Line (EMA do MACD) - simplificado
        # Em produção, deveria manter histórico de MACD e calcular EMA sobre ele
        signal_line = macd_line  # Simplificação
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }


# Classe para gerenciar histórico de indicadores
class IndicatorHistory:
    """
    Gerencia histórico de indicadores para um símbolo
    """
    
    def __init__(self, symbol: str, max_length: int = 500):
        """
        Inicializa histórico de indicadores
        
        Args:
            symbol: Símbolo do ativo
            max_length: Tamanho máximo do histórico
        """
        self.symbol = symbol
        self.max_length = max_length
        
        # Históricos de indicadores
        self.hull_ma = deque(maxlen=max_length)
        self.sma = deque(maxlen=max_length)
        self.ema = deque(maxlen=max_length)
        self.zscore = deque(maxlen=max_length)
        self.rsi = deque(maxlen=max_length)
        self.bollinger = deque(maxlen=max_length)
        self.macd = deque(maxlen=max_length)
        
        # Timestamps
        self.timestamps = deque(maxlen=max_length)
    
    def add_indicators(self, timestamp: str, prices: List[float], **kwargs):
        """
        Calcula e adiciona indicadores ao histórico
        
        Args:
            timestamp: Timestamp do cálculo
            prices: Lista de preços para cálculo
            **kwargs: Parâmetros adicionais (períodos, etc.)
        """
        calc = TechnicalIndicators()
        
        # Parâmetros padrão
        hull_period = kwargs.get('hull_period', 20)
        sma_period = kwargs.get('sma_period', 20)
        ema_period = kwargs.get('ema_period', 20)
        zscore_window = kwargs.get('zscore_window', 20)
        rsi_period = kwargs.get('rsi_period', 14)
        bb_period = kwargs.get('bb_period', 20)
        
        # Calcular indicadores
        hull_value = calc.calculate_hull_ma(prices, hull_period)
        sma_value = calc.calculate_sma(prices, sma_period)
        ema_value = calc.calculate_ema(prices, ema_period)
        zscore_value = calc.calculate_zscore(prices, zscore_window)
        rsi_value = calc.calculate_rsi(prices, rsi_period)
        bb_value = calc.calculate_bollinger_bands(prices, bb_period)
        macd_value = calc.calculate_macd(prices)
        
        # Adicionar ao histórico
        self.timestamps.append(timestamp)
        self.hull_ma.append(hull_value)
        self.sma.append(sma_value)
        self.ema.append(ema_value)
        self.zscore.append(zscore_value)
        self.rsi.append(rsi_value)
        self.bollinger.append(bb_value)
        self.macd.append(macd_value)
    
    def get_latest(self) -> Dict:
        """
        Retorna os últimos valores calculados
        
        Returns:
            Dicionário com os últimos valores
        """
        return {
            'timestamp': self.timestamps[-1] if self.timestamps else None,
            'hull_ma': self.hull_ma[-1] if self.hull_ma else None,
            'sma': self.sma[-1] if self.sma else None,
            'ema': self.ema[-1] if self.ema else None,
            'zscore': self.zscore[-1] if self.zscore else None,
            'rsi': self.rsi[-1] if self.rsi else None,
            'bollinger': self.bollinger[-1] if self.bollinger else None,
            'macd': self.macd[-1] if self.macd else None
        }
    
    def get_history(self) -> Dict:
        """
        Retorna todo o histórico de indicadores
        
        Returns:
            Dicionário com histórico completo
        """
        return {
            'symbol': self.symbol,
            'timestamps': list(self.timestamps),
            'hull_ma': list(self.hull_ma),
            'sma': list(self.sma),
            'ema': list(self.ema),
            'zscore': list(self.zscore),
            'rsi': list(self.rsi),
            'bollinger': list(self.bollinger),
            'macd': list(self.macd)
        }


# Testes unitários
if __name__ == '__main__':
    print("="*60)
    print("🧪 TESTANDO TECHNICAL INDICATORS")
    print("="*60)
    
    # Dados de teste
    test_prices = [
        2640.00, 2641.50, 2643.00, 2642.00, 2644.50,
        2645.00, 2646.50, 2645.00, 2647.00, 2648.50,
        2647.00, 2649.00, 2650.50, 2649.00, 2651.00,
        2652.50, 2651.00, 2653.00, 2654.50, 2653.00,
        2655.00, 2656.50, 2655.00, 2657.00, 2658.50
    ]
    
    calc = TechnicalIndicators()
    
    # Teste 1: SMA
    print("\n📊 Teste 1: Simple Moving Average (SMA)")
    sma = calc.calculate_sma(test_prices, 20)
    print(f"  SMA(20): {sma:.2f}" if sma else "  SMA(20): Dados insuficientes")
    
    # Teste 2: EMA
    print("\n📈 Teste 2: Exponential Moving Average (EMA)")
    ema = calc.calculate_ema(test_prices, 20)
    print(f"  EMA(20): {ema:.2f}" if ema else "  EMA(20): Dados insuficientes")
    
    # Teste 3: Hull MA
    print("\n🎯 Teste 3: Hull Moving Average (HMA)")
    hull = calc.calculate_hull_ma(test_prices, 20)
    print(f"  Hull MA(20): {hull:.2f}" if hull else "  Hull MA(20): Dados insuficientes")
    
    # Teste 4: Z-Score
    print("\n📉 Teste 4: Z-Score")
    zscore = calc.calculate_zscore(test_prices, 20)
    print(f"  Z-Score(20): {zscore:.4f}" if zscore else "  Z-Score(20): Dados insuficientes")
    
    # Teste 5: RSI
    print("\n💪 Teste 5: Relative Strength Index (RSI)")
    rsi = calc.calculate_rsi(test_prices, 14)
    print(f"  RSI(14): {rsi:.2f}" if rsi else "  RSI(14): Dados insuficientes")
    
    # Teste 6: Bollinger Bands
    print("\n📊 Teste 6: Bollinger Bands")
    bb = calc.calculate_bollinger_bands(test_prices, 20)
    if bb:
        print(f"  Upper: {bb['upper']:.2f}")
        print(f"  Middle: {bb['middle']:.2f}")
        print(f"  Lower: {bb['lower']:.2f}")
    else:
        print("  Bollinger Bands: Dados insuficientes")
    
    # Teste 7: Histórico de Indicadores
    print("\n📚 Teste 7: Histórico de Indicadores")
    history = IndicatorHistory('XAUUSD')
    history.add_indicators('2025-10-06T17:00:00', test_prices)
    latest = history.get_latest()
    print(f"  Símbolo: {history.symbol}")
    print(f"  Hull MA: {latest['hull_ma']:.2f}" if latest['hull_ma'] else "  Hull MA: None")
    print(f"  Z-Score: {latest['zscore']:.4f}" if latest['zscore'] else "  Z-Score: None")
    
    print("\n" + "="*60)
    print("✅ Testes concluídos!")
    print("="*60)
