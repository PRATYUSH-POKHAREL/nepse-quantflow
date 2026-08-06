"""
Strategy Optimizer
Tests multiple parameter combinations to find the best settings.
"""

from backtester import run
import itertools


def optimize_ma_crossover(symbol, start, end, capital=100000):
    """Test multiple MA combinations and return ranked results."""
    fast_options = [5, 10, 15, 20, 30, 40]
    slow_options = [20, 30, 50, 75, 100, 150, 200]
    
    results = []
    total = len(fast_options) * len(slow_options)
    count = 0
    
    for fast, slow in itertools.product(fast_options, slow_options):
        if fast >= slow:
            continue
        
        count += 1
        print(f"  Testing MA {fast}/{slow} ({count}/{total})")
        
        result = run(symbol, start, end, capital, 'ma_crossover', fast_ma=fast, slow_ma=slow)
        result['params'] = f'MA {fast}/{slow}'
        result['fast'] = fast
        result['slow'] = slow
        results.append(result)
    
    # Sort by Sharpe ratio (best first)
    results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
    return results


def optimize_rsi(symbol, start, end, capital=100000):
    """Test multiple RSI parameters."""
    period_options = [7, 10, 14, 21]
    oversold_options = [25, 30, 35, 40]
    overbought_options = [60, 65, 70, 75]
    
    results = []
    
    for period in period_options:
        for oversold in oversold_options:
            for overbought in overbought_options:
                if oversold >= overbought:
                    continue
                
                result = run(symbol, start, end, capital, 'rsi',
                           rsi_period=period, rsi_oversold=oversold, rsi_overbought=overbought)
                result['params'] = f'RSI({period}, {oversold}/{overbought})'
                result['period'] = period
                result['oversold'] = oversold
                result['overbought'] = overbought
                results.append(result)
    
    results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
    return results


def optimize_bollinger(symbol, start, end, capital=100000):
    """Test multiple Bollinger Band parameters."""
    period_options = [10, 15, 20, 25, 30]
    std_options = [1.5, 2.0, 2.5, 3.0]
    
    results = []
    
    for period in period_options:
        for std in std_options:
            result = run(symbol, start, end, capital, 'bollinger', bb_period=period, bb_std=std)
            result['params'] = f'BB({period}, {std}σ)'
            result['period'] = period
            result['std'] = std
            results.append(result)
    
    results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
    return results