import json
import os
from datetime import datetime

ALERTS_DIR = 'portfolios'


class AlertManager:
    def __init__(self, user_email):
        safe_email = user_email.replace('@', '_').replace('.', '_')
        self.alerts_dir = os.path.join(ALERTS_DIR, safe_email)
        os.makedirs(self.alerts_dir, exist_ok=True)
        self.alerts_file = os.path.join(self.alerts_dir, 'alerts.json')
        self._load()

    def _load(self):
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file) as f:
                self.alerts = json.load(f)
        else:
            self.alerts = {'active': [], 'history': []}

    def _save(self):
        with open(self.alerts_file, 'w') as f:
            json.dump(self.alerts, f, indent=2, default=str)

    def create(self, symbol, strategy_type, params, alert_type='both'):
        alert = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'symbol': symbol,
            'strategy_type': strategy_type,
            'params': params,
            'alert_type': alert_type,
            'active': True,
            'created': datetime.now().isoformat(),
            'last_triggered': None,
            'trigger_count': 0
        }
        self.alerts['active'].append(alert)
        self._save()
        return alert

    def get_all(self):
        return self.alerts['active']

    def get_history(self):
        return self.alerts['history']

    def toggle(self, alert_id):
        for alert in self.alerts['active']:
            if alert['id'] == alert_id:
                alert['active'] = not alert['active']
                self._save()
                return alert
        return None

    def delete(self, alert_id):
        self.alerts['active'] = [a for a in self.alerts['active'] if a['id'] != alert_id]
        self._save()