from backtester import run
from datetime import datetime, timedelta


def date_range(start, end, step_days=365):
    current = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    windows = []
    while current < end_date:
        train_end = current + timedelta(days=step_days)
        test_end = train_end + timedelta(days=step_days // 2)

        if test_end > end_date:
            test_end = end_date
        if train_end > end_date:
            break

        windows.append({
            'train_start': current.strftime('%Y-%m-%d'),
            'train_end': train_end.strftime('%Y-%m-%d'),
            'test_start': train_end.strftime('%Y-%m-%d'),
            'test_end': test_end.strftime('%Y-%m-%d')
        })

        current = train_end

    return windows


def run_walkforward(symbol, start, end, capital=100000, strategy_type='ma_crossover', **params):
    windows = date_range(start, end, step_days=365)
    results = []

    for i, window in enumerate(windows):
        train_result = run(symbol, window['train_start'], window['train_end'],
                          capital, strategy_type, **params)
        test_result = run(symbol, window['test_start'], window['test_end'],
                         capital, strategy_type, **params)

        results.append({
            'window': i + 1,
            'train_period': f"{window['train_start']} to {window['train_end']}",
            'test_period': f"{window['test_start']} to {window['test_end']}",
            'train_return': train_result['total_return'],
            'test_return': test_result['total_return'],
            'train_sharpe': train_result['sharpe_ratio'],
            'test_sharpe': test_result['sharpe_ratio'],
            'train_trades': train_result['total_trades'],
            'test_trades': test_result['total_trades'],
            'robust': test_result['total_return'] > 0
        })

    robust_count = sum(1 for r in results if r['robust'])
    avg_test_return = sum(r['test_return'] for r in results) / len(results) if results else 0

    return {
        'windows': results,
        'total_windows': len(results),
        'robust_windows': robust_count,
        'robust_pct': (robust_count / len(results) * 100) if results else 0,
        'avg_test_return': round(avg_test_return, 2),
        'verdict': 'RELIABLE' if robust_count >= len(results) * 0.6 else 'UNRELIABLE',
        'explanation': (
            f"Strategy was profitable in {robust_count}/{len(results)} out-of-sample windows. "
            f"{'This suggests the strategy is robust and not overfit.' if robust_count >= len(results) * 0.6 else 'The strategy may be overfit to past data. Proceed with caution.'}"
        )
    }