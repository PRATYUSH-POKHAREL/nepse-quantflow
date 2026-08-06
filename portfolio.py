import json
import os
from datetime import datetime

PORTFOLIO_DIR = 'portfolios'


class PortfolioManager:
    def __init__(self, user_email):
        self.user_email = user_email
        safe_email = user_email.replace('@', '_').replace('.', '_')
        self.portfolio_dir = os.path.join(PORTFOLIO_DIR, safe_email)
        os.makedirs(self.portfolio_dir, exist_ok=True)
        self.portfolios_file = os.path.join(self.portfolio_dir, 'portfolios.json')
        self._load()

    def _load(self):
        if os.path.exists(self.portfolios_file):
            with open(self.portfolios_file) as f:
                self.portfolios = json.load(f)
        else:
            self.portfolios = {}

    def _save(self):
        with open(self.portfolios_file, 'w') as f:
            json.dump(self.portfolios, f, indent=2, default=str)

    def create(self, name, description=''):
        pid = datetime.now().strftime('%Y%m%d%H%M%S%f')
        self.portfolios[pid] = {
            'id': pid,
            'name': name,
            'description': description,
            'created': datetime.now().isoformat(),
            'holdings': [],
            'total_invested': 0,
            'total_current': 0,
            'total_pnl': 0,
            'total_pnl_pct': 0
        }
        self._save()
        return self.portfolios[pid]

    def get_all(self):
        return list(self.portfolios.values())

    def get(self, pid):
        return self.portfolios.get(pid)

    def delete(self, pid):
        if pid in self.portfolios:
            del self.portfolios[pid]
            self._save()
            return True
        return False

    def add_holding(self, pid, symbol, shares, buy_price, buy_date):
        if pid not in self.portfolios:
            return None
        holding = {
            'symbol': symbol,
            'shares': shares,
            'buy_price': buy_price,
            'buy_date': buy_date,
            'invested': shares * buy_price,
            'current_price': buy_price,
            'pnl': 0,
            'pnl_pct': 0
        }
        self.portfolios[pid]['holdings'].append(holding)
        self._recalculate(pid)
        return holding

    def remove_holding(self, pid, index):
        if pid not in self.portfolios:
            return False
        holdings = self.portfolios[pid]['holdings']
        if 0 <= index < len(holdings):
            holdings.pop(index)
            self._recalculate(pid)
            return True
        return False

    def _recalculate(self, pid):
        pf = self.portfolios[pid]
        total_invested = sum(h['shares'] * h['buy_price'] for h in pf['holdings'])
        total_current = sum(h['shares'] * h.get('current_price', h['buy_price']) for h in pf['holdings'])
        pf['total_invested'] = total_invested
        pf['total_current'] = total_current
        pf['total_pnl'] = total_current - total_invested
        pf['total_pnl_pct'] = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
        self._save()

    def update_prices(self, pid, prices):
        if pid not in self.portfolios:
            return None
        pf = self.portfolios[pid]
        for h in pf['holdings']:
            current_price = prices.get(h['symbol'], h['buy_price'])
            h['current_price'] = current_price
            h['pnl'] = (current_price - h['buy_price']) * h['shares']
            h['pnl_pct'] = ((current_price - h['buy_price']) / h['buy_price']) * 100
        self._recalculate(pid)
        return pf