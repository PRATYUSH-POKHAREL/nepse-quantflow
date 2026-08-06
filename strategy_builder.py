import numpy as np


class Condition:
    def __init__(self, indicator, operator, value=None, period=14):
        self.indicator = indicator
        self.operator = operator
        self.value = value
        self.period = period

    def to_dict(self):
        return {
            'indicator': self.indicator,
            'operator': self.operator,
            'value': self.value,
            'period': self.period
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            indicator=data.get('indicator', 'close'),
            operator=data.get('operator', '>'),
            value=data.get('value'),
            period=data.get('period', 14)
        )


class CustomStrategy:
    def __init__(self, name, entry_conditions, exit_conditions, entry_logic='AND', exit_logic='AND'):
        self.name = name
        self.entry_conditions = entry_conditions
        self.exit_conditions = exit_conditions
        self.entry_logic = entry_logic
        self.exit_logic = exit_logic
        self.position = 'FLAT'
        self.signals = 0

    def evaluate_condition(self, condition, handler):
        indicator = condition.indicator
        operator = condition.operator
        period = condition.period

        bars = handler.bars(max(period, 20))
        if bars is None or len(bars) < period:
            return False

        closes = bars['Close'].to_numpy().ravel().astype(float)
        current_price = closes[-1]

        if indicator == 'close':
            indicator_value = current_price
        elif indicator == 'ma':
            indicator_value = closes[-period:].mean() if len(closes) >= period else current_price
        elif indicator == 'rsi':
            indicator_value = self.calculate_rsi(closes, period)
        elif indicator == 'volume':
            volumes = bars['Volume'].to_numpy().ravel().astype(float)
            indicator_value = volumes[-1] if len(volumes) > 0 else 0
        elif indicator == 'bb_lower':
            sma = closes[-period:].mean()
            std = closes[-period:].std()
            indicator_value = sma - (2 * std)
        elif indicator == 'bb_upper':
            sma = closes[-period:].mean()
            std = closes[-period:].std()
            indicator_value = sma + (2 * std)
        else:
            return False

        if operator == 'crosses_above' and condition.value:
            prev_val = self.get_prev_indicator(indicator, closes, period)
            threshold = float(condition.value)
            return prev_val <= threshold and indicator_value > threshold
        elif operator == 'crosses_below' and condition.value:
            prev_val = self.get_prev_indicator(indicator, closes, period)
            threshold = float(condition.value)
            return prev_val >= threshold and indicator_value < threshold
        elif condition.value is not None:
            threshold = float(condition.value)
            if operator == '>':
                return indicator_value > threshold
            elif operator == '<':
                return indicator_value < threshold
            elif operator == '>=':
                return indicator_value >= threshold
            elif operator == '<=':
                return indicator_value <= threshold
            elif operator == '==':
                return abs(indicator_value - threshold) < 0.01

        return False

    def calculate_rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50
        deltas = np.diff(closes[-(period + 1):])
        gains = np.sum(deltas[deltas > 0]) / period if len(deltas[deltas > 0]) > 0 else 0
        losses = -np.sum(deltas[deltas < 0]) / period if len(deltas[deltas < 0]) > 0 else 0
        if losses == 0:
            return 100
        rs = gains / losses
        return float(100 - (100 / (1 + rs)))

    def get_prev_indicator(self, indicator, closes, period):
        if len(closes) < 2:
            return 0
        prev_closes = closes[:-1]
        if indicator == 'close':
            return prev_closes[-1]
        elif indicator == 'ma':
            return prev_closes[-period:].mean() if len(prev_closes) >= period else prev_closes[-1]
        elif indicator == 'rsi':
            return self.calculate_rsi(prev_closes, period)
        return 0

    def evaluate(self, handler):
        entry_results = [self.evaluate_condition(c, handler) for c in self.entry_conditions]
        exit_results = [self.evaluate_condition(c, handler) for c in self.exit_conditions]

        entry_signal = all(entry_results) if self.entry_logic == 'AND' else any(entry_results)
        exit_signal = all(exit_results) if self.exit_logic == 'AND' else any(exit_results)

        if entry_signal and self.position != 'LONG' and self.entry_conditions:
            self.position = 'LONG'
            self.signals += 1
            return 'BUY'

        if exit_signal and self.position != 'SHORT' and self.exit_conditions:
            self.position = 'SHORT'
            self.signals += 1
            return 'SELL'

        return None

    def to_dict(self):
        return {
            'name': self.name,
            'entry_conditions': [c.to_dict() for c in self.entry_conditions],
            'exit_conditions': [c.to_dict() for c in self.exit_conditions],
            'entry_logic': self.entry_logic,
            'exit_logic': self.exit_logic
        }

    @classmethod
    def from_dict(cls, data):
        entry = [Condition.from_dict(c) for c in data.get('entry_conditions', [])]
        exit_ = [Condition.from_dict(c) for c in data.get('exit_conditions', [])]
        return cls(
            name=data.get('name', 'Custom Strategy'),
            entry_conditions=entry,
            exit_conditions=exit_,
            entry_logic=data.get('entry_logic', 'AND'),
            exit_logic=data.get('exit_logic', 'AND')
        )