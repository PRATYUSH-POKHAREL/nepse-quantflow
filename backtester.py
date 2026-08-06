"""
NEPSE Backtesting Engine
Multiple strategies: MA Crossover, RSI, Bollinger Bands, Buy & Hold
"""

import numpy as np
import pandas as pd
from nepal_data import NEPALDataHandler


# ==========================================
# STRATEGIES
# ==========================================

class MACrossover:
    """Moving Average Crossover Strategy."""
    
    def __init__(self, fast=20, slow=50):
        self.fast = fast
        self.slow = slow
        self.position = 'FLAT'
        self.signals = 0
        self.name = f'MA Crossover ({fast}/{slow})'

    def evaluate(self, handler):
        bars = handler.bars(self.slow)
        if bars is None or len(bars) < self.slow:
            return None
        closes = bars['Close'].to_numpy().ravel().astype(float)
        if len(closes) < self.slow:
            return None
        fast_now = np.mean(closes[-self.fast:])
        slow_now = np.mean(closes[-self.slow:])
        fast_prev = np.mean(closes[-(self.fast+1):-1])
        slow_prev = np.mean(closes[-(self.slow+1):-1])
        if fast_prev <= slow_prev and fast_now > slow_now and self.position != 'LONG':
            self.position = 'LONG'; self.signals += 1; return 'BUY'
        if fast_prev >= slow_prev and fast_now < slow_now and self.position != 'SHORT':
            self.position = 'SHORT'; self.signals += 1; return 'SELL'
        return None


class RSIStrategy:
    """RSI Overbought/Oversold Strategy."""
    
    def __init__(self, period=14, oversold=35, overbought=65):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.position = 'FLAT'
        self.signals = 0
        self.prev_rsi = None
        self.name = f'RSI ({period}, {oversold}/{overbought})'

    def _calculate_rsi(self, closes):
        if len(closes) < self.period + 1:
            return None
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-self.period:])
        avg_loss = np.mean(losses[-self.period:])
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return float(100 - (100 / (1 + rs)))

    def evaluate(self, handler):
        bars = handler.bars(self.period + 5)
        if bars is None or len(bars) < self.period + 1:
            return None
        closes = bars['Close'].to_numpy().ravel().astype(float)
        rsi = self._calculate_rsi(closes)
        if rsi is None:
            return None
        signal = None
        if self.prev_rsi is not None:
            if self.prev_rsi <= self.oversold and rsi > self.oversold and self.position != 'LONG':
                self.position = 'LONG'; self.signals += 1; signal = 'BUY'
            elif self.prev_rsi >= self.overbought and rsi < self.overbought and self.position != 'SHORT':
                self.position = 'SHORT'; self.signals += 1; signal = 'SELL'
        self.prev_rsi = rsi
        return signal


class BollingerStrategy:
    """Bollinger Bands Mean Reversion Strategy."""
    
    def __init__(self, period=20, std_dev=2.0):
        self.period = period
        self.std_dev = std_dev
        self.position = 'FLAT'
        self.signals = 0
        self.name = f'Bollinger ({period}, {std_dev}σ)'

    def evaluate(self, handler):
        bars = handler.bars(self.period)
        if bars is None or len(bars) < self.period:
            return None
        closes = bars['Close'].to_numpy().ravel().astype(float)
        if len(closes) < self.period:
            return None
        sma = np.mean(closes[-self.period:])
        std = np.std(closes[-self.period:])
        upper = sma + (self.std_dev * std)
        lower = sma - (self.std_dev * std)
        current_price = closes[-1]
        if current_price <= lower and self.position != 'LONG':
            self.position = 'LONG'; self.signals += 1; return 'BUY'
        if current_price >= upper and self.position != 'SHORT':
            self.position = 'SHORT'; self.signals += 1; return 'SELL'
        return None


class BuyAndHold:
    """Buy on day 1, sell on last day."""
    
    def __init__(self):
        self.position = 'FLAT'
        self.signals = 0
        self.bought = False
        self.name = 'Buy & Hold'

    def evaluate(self, handler):
        if not self.bought:
            self.bought = True
            self.position = 'LONG'
            self.signals += 1
            return 'BUY'
        return None


# ==========================================
# NEPAL COSTS
# ==========================================

class NepalCosts:
    BROKER_COMMISSION = 0.004
    SEBON_FEE = 0.00015
    DP_CHARGE = 25

    @staticmethod
    def calculate(price, qty):
        value = price * qty
        return (value * NepalCosts.BROKER_COMMISSION) + (value * NepalCosts.SEBON_FEE) + NepalCosts.DP_CHARGE


# ==========================================
# PORTFOLIO
# ==========================================

class Portfolio:
    def __init__(self, capital=100000):
        self.initial = capital
        self.cash = capital
        self.shares = 0
        self.buy_price = 0
        self.curve = []
        self.trades = []

    def get_equity(self, price):
        return self.cash + (self.shares * price)

    def record(self, ts, price):
        self.curve.append({'timestamp': ts, 'equity': self.get_equity(price)})

    def buy(self, price, ts):
        if self.shares > 0:
            return
        cost_per_share = NepalCosts.calculate(price, 1)
        shares = int((self.cash * 0.95) / (price + cost_per_share))
        if shares < 1:
            return
        total = (price * shares) + NepalCosts.calculate(price, shares)
        if total > self.cash:
            return
        self.cash -= total
        self.shares = shares
        self.buy_price = price
        self.trades.append({'timestamp': ts, 'action': 'BUY', 'shares': shares, 'price': price})

    def sell(self, price, ts):
        if self.shares == 0:
            return
        gross = price * self.shares
        costs = NepalCosts.calculate(price, self.shares)
        self.cash += (gross - costs)
        self.trades.append({'timestamp': ts, 'action': 'SELL', 'shares': self.shares, 'price': price})
        self.shares = 0
        self.buy_price = 0


# ==========================================
# PERFORMANCE REPORT
# ==========================================

class Report:
    def __init__(self, curve, trades, initial, strategy_name=""):
        self.df = pd.DataFrame(curve).set_index('timestamp')
        self.df['ret'] = self.df['equity'].pct_change()
        self.trades = trades
        self.initial = initial
        self.strategy_name = strategy_name

    def total_return(self):
        return float(((self.df['equity'].iloc[-1] / self.initial) - 1) * 100)

    def sharpe(self):
        r = self.df['ret'].dropna()
        if len(r) < 2 or r.std() == 0:
            return 0.0
        return float(np.sqrt(252) * r.mean() / r.std())

    def max_dd(self):
        cum = (1 + self.df['ret'].fillna(0)).cumprod()
        peak = cum.expanding().max()
        return float(((cum - peak) / peak).min() * 100)

    def win_rate(self):
        pairs = []
        for i in range(len(self.trades) - 1):
            if self.trades[i]['action'] == 'BUY' and self.trades[i+1]['action'] == 'SELL':
                pairs.append((self.trades[i], self.trades[i+1]))
        if not pairs:
            return 0.0
        wins = sum(1 for b, s in pairs if s['price'] > b['price'])
        return float((wins / len(pairs)) * 100)

    def to_dict(self):
        eq = self.df['equity']
        if len(eq) > 52:
            eq = eq.resample('W').last().dropna()
        return {
            'strategy': self.strategy_name,
            'initial_capital': self.initial,
            'final_equity': round(float(self.df['equity'].iloc[-1]), 2),
            'total_return': round(self.total_return(), 2),
            'sharpe_ratio': round(self.sharpe(), 2),
            'max_drawdown': round(self.max_dd(), 2),
            'win_rate': round(self.win_rate(), 1),
            'total_trades': len(self.trades),
            'equity_curve': [
                {'date': str(i.date()), 'equity': round(float(v), 2)}
                for i, v in eq.items()
            ],
            'trades': [
                {'date': str(t['timestamp'].date()), 'action': t['action'],
                 'shares': t['shares'], 'price': round(float(t['price']), 2)}
                for t in self.trades
            ]
        }


# ==========================================
# STRATEGY FACTORY
# ==========================================

def get_strategy(strategy_type, **params):
    if strategy_type == 'ma_crossover':
        return MACrossover(
            fast=int(params.get('fast_ma', 20)),
            slow=int(params.get('slow_ma', 50))
        )
    elif strategy_type == 'rsi':
        return RSIStrategy(
            period=int(params.get('rsi_period', 14)),
            oversold=int(params.get('rsi_oversold', 35)),
            overbought=int(params.get('rsi_overbought', 65))
        )
    elif strategy_type == 'bollinger':
        return BollingerStrategy(
            period=int(params.get('bb_period', 20)),
            std_dev=float(params.get('bb_std', 2.0))
        )
    elif strategy_type == 'buy_hold':
        return BuyAndHold()
    else:
        return MACrossover()


# ==========================================
# RUN BACKTEST
# ==========================================

def run(symbol, start, end, capital=100000, strategy_type='ma_crossover', **params):
    handler = NEPALDataHandler(symbol, start, end)
    strategy = get_strategy(strategy_type, **params)
    portfolio = Portfolio(capital)

    while handler.advance():
        bar = handler.current_bar()
        if bar is None:
            break
        price = float(bar['Close'])
        signal = strategy.evaluate(handler)
        if signal == 'BUY':
            portfolio.buy(price, handler.current_time)
        elif signal == 'SELL':
            portfolio.sell(price, handler.current_time)
        portfolio.record(handler.current_time, price)

    report = Report(portfolio.curve, portfolio.trades, capital, strategy.name)
    return report.to_dict()


def run_comparison(symbol, start, end, capital=100000):
    """Run all strategies and return comparison."""
    strategies = [
        ('ma_crossover', {'fast_ma': 20, 'slow_ma': 50}),
        ('rsi', {'rsi_period': 14, 'rsi_oversold': 35, 'rsi_overbought': 65}),
        ('bollinger', {'bb_period': 20, 'bb_std': 2.0}),
        ('buy_hold', {}),
    ]
    
    results = []
    for stype, params in strategies:
        result = run(symbol, start, end, capital, stype, **params)
        results.append(result)
    
    return results