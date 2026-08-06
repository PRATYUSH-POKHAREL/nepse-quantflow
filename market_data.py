"""
NEPSE Market Data
Simulated live market overview for the dashboard.
"""

import random
from datetime import datetime, timedelta
from nepal_stocks import get_all_stocks


def get_live_market():
    """Generate simulated live NEPSE market data."""
    random.seed(int(datetime.now().timestamp() / 60))  # Changes every minute
    
    # NEPSE Index
    base_index = random.uniform(2600, 3200)
    index_change = round(random.uniform(-25, 25), 2)
    index_change_pct = round((index_change / base_index) * 100, 2)
    
    # Market stats
    turnover = round(random.uniform(1.5, 8.5), 2)
    volume = random.randint(8, 35)
    advances = random.randint(35, 85)
    declines = random.randint(25, 65)
    unchanged = random.randint(5, 20)
    
    # Top movers
    all_stocks = get_all_stocks()
    top_stocks = random.sample(all_stocks, min(15, len(all_stocks)))
    
    movers = []
    for stock in top_stocks:
        price = round(random.uniform(200, 5000), 2)
        change_pct = round(random.uniform(-8, 8), 2)
        change = round((change_pct / 100) * price, 2)
        movers.append({
            'symbol': stock['symbol'],
            'name': stock['name'],
            'sector': stock['sector'],
            'price': price,
            'change': change,
            'change_pct': change_pct,
            'volume': random.randint(1000, 100000)
        })
    
    # Sort by absolute change
    movers.sort(key=lambda x: abs(x['change_pct']), reverse=True)
    gainers = [m for m in movers if m['change_pct'] > 0][:5]
    losers = [m for m in movers if m['change_pct'] < 0][:5]
    losers.sort(key=lambda x: x['change_pct'])
    
    # Sector performance
    sectors = list(set(s['sector'] for s in all_stocks))
    sector_perf = []
    for sector in sectors[:8]:
        chg = round(random.uniform(-3, 3), 2)
        sector_perf.append({'sector': sector, 'change_pct': chg})
    sector_perf.sort(key=lambda x: x['change_pct'], reverse=True)
    
    # Market hours
    now = datetime.now()
    market_open = now.replace(hour=11, minute=0, second=0)
    market_close = now.replace(hour=15, minute=0, second=0)
    is_market_open = market_open <= now <= market_close and now.weekday() < 5
    
    return {
        'index': round(base_index, 2),
        'index_change': index_change,
        'index_change_pct': index_change_pct,
        'turnover': f'NPR {turnover} Arba',
        'volume': f'{volume} Lakh',
        'advances': advances,
        'declines': declines,
        'unchanged': unchanged,
        'gainers': gainers,
        'losers': losers,
        'sectors': sector_perf,
        'market_open': is_market_open,
        'last_updated': now.strftime('%B %d, %Y %I:%M %p'),
        'trading_hours': 'Sun-Thu, 11:00 AM - 3:00 PM NPT'
    }


def get_stock_profile(symbol):
    """Get detailed profile for a stock."""
    from nepal_stocks import get_stock
    stock = get_stock(symbol)
    if not stock:
        return None
    
    random.seed(hash(symbol))
    
    return {
        **stock,
        'market_cap': f'NPR {random.uniform(5, 200):.1f} Arba',
        'pe_ratio': round(random.uniform(8, 45), 2),
        'eps': round(random.uniform(10, 150), 2),
        'book_value': round(random.uniform(100, 800), 2),
        '52w_high': round(random.uniform(500, 6000), 2),
        '52w_low': round(random.uniform(150, 2000), 2),
        'avg_volume': f'{random.randint(5, 200)}K',
        'shares_outstanding': f'{random.uniform(10, 500):.1f}M',
        'sector_pe': round(random.uniform(10, 50), 2),
    }