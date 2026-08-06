"""
NEPSE Data Handler
Handles downloading, caching, and streaming Nepali stock data.
Falls back to realistic synthetic data when Yahoo Finance is unavailable.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import os

CACHE_DIR = 'cache'


class NEPALDataHandler:
    """Data handler for a single NEPSE stock."""

    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol.upper()
        self.start = start_date
        self.end = end_date
        self.current_idx = 0
        self.data = None
        self.timestamps = []

        os.makedirs(CACHE_DIR, exist_ok=True)
        self._load()

    def _cache_path(self):
        safe_symbol = self.symbol.replace('/', '_').replace('.', '_')
        return f"{CACHE_DIR}/{safe_symbol}_{self.start}_{self.end}.csv"

    def _load(self):
        path = self._cache_path()

        if os.path.exists(path):
            print(f"  📦 {self.symbol} (cached)")
            self.data = pd.read_csv(path, index_col=0, parse_dates=True)
        else:
            print(f"  ⬇️  {self.symbol} (downloading)")
            self.data = self._try_download()

            if self.data is None or self.data.empty:
                print(f"  🔧 {self.symbol} (generating synthetic)")
                self.data = self._generate_data()

            if self.data is not None and not self.data.empty:
                self.data.to_csv(path)

        if self.data is None or self.data.empty:
            raise ValueError(f"No data for {self.symbol}")

        self.timestamps = self.data.index.tolist()
        print(f"  ✅ {self.symbol}: {len(self.timestamps)} bars | {self.timestamps[0].date()} to {self.timestamps[-1].date()}")

    def _try_download(self):
        """Try Yahoo Finance with .NP suffix."""
        yf_symbol = f"{self.symbol}.NP"
        try:
            df = yf.download(yf_symbol, start=self.start, end=self.end, progress=False, auto_adjust=True)
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                if 'Close' in df.columns:
                    return df
        except Exception:
            pass
        return None

    def _generate_data(self):
        """
        Generate realistic NEPSE synthetic data.
        Based on actual NEPSE characteristics:
        - Trading hours: 11 AM - 3 PM (Sun-Thu)
        - Circuit breakers: +/- 10% for most stocks
        - Generally moderate volatility
        """
        # Use Nepal business days (Sun-Thu) - approximate with all weekdays
        dates = pd.date_range(start=self.start, end=self.end, freq='B')
        n = len(dates)

        # Realistic base prices for NEPSE stocks
        base_prices = {
            'NABIL': 820, 'NICA': 680, 'GBIME': 340, 'NIMB': 420,
            'SCB': 650, 'HBL': 420, 'EBL': 520, 'SANIMA': 340,
            'PRVU': 280, 'MBL': 300, 'NBL': 320, 'SBI': 380,
            'NTC': 920, 'CHCL': 580, 'API': 310, 'UPPER': 430,
            'NLIC': 2100, 'LICN': 1600, 'CIT': 2400, 'HIDCL': 320,
            'SHIVM': 560, 'UNL': 42000,
            'MNBBL': 380, 'CBBL': 1200, 'NIFRA': 290,
            'PRIN': 1800, 'IGI': 450, 'NIL': 520,
        }

        base = base_prices.get(self.symbol, 500)

        np.random.seed(hash(self.symbol) % 2**31)

        # Daily returns with slight positive drift and moderate volatility
        daily_returns = np.random.normal(0.0002, 0.016, n)
        daily_returns[0] = 0

        # Add market trend
        trend_options = [-0.25, -0.10, 0.0, 0.10, 0.25, 0.40]
        trend = np.random.choice(trend_options)
        trend_line = np.linspace(0, trend, n)
        daily_returns = daily_returns + trend_line * 0.002

        # Generate prices
        prices = base * np.exp(np.cumsum(daily_returns))
        prices = np.clip(prices, base * 0.3, base * 3)  # Keep realistic

        # Build OHLC DataFrame
        df = pd.DataFrame(index=dates)
        df['Close'] = prices
        df['Open'] = np.roll(prices, 1)
        df['Open'].iloc[0] = base
        df['Open'] = df['Open'] * (1 + np.random.normal(0, 0.004, n))

        noise_high = np.abs(np.random.normal(0, 0.008, n))
        noise_low = np.abs(np.random.normal(0, 0.008, n))
        df['High'] = np.maximum(df['Open'], df['Close']) * (1 + noise_high)
        df['Low'] = np.minimum(df['Open'], df['Close']) * (1 - noise_low)
        df['Volume'] = np.random.randint(1000, 100000, n)

        return df

    @property
    def current_time(self):
        if self.current_idx < len(self.timestamps):
            return self.timestamps[self.current_idx]
        return None

    def current_bar(self):
        if self.current_idx >= len(self.data):
            return None
        row = self.data.iloc[self.current_idx]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[0]
        return row

    def bars(self, n):
        if self.current_idx < n - 1:
            return None
        return self.data.iloc[self.current_idx - n + 1:self.current_idx + 1]

    def advance(self):
        self.current_idx += 1
        return self.current_idx < len(self.timestamps)