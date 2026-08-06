"""
NEPSE QuantFlow - Complete Platform v3.0
All features working: Market, Backtest, Compare, Optimizer, Walk-Forward, Builder, Portfolio, Alerts, Learn
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from backtester import run, run_comparison
from optimizer import optimize_ma_crossover, optimize_rsi, optimize_bollinger
from walkforward import run_walkforward
from portfolio import PortfolioManager
from alerts import AlertManager
from strategy_builder import CustomStrategy, Condition
from market_data import get_live_market, get_stock_profile
from nepal_stocks import get_all_stocks, get_sectors, get_stocks_by_sector, search_stocks, get_stock
import secrets
import os
import json
from datetime import datetime
import requests as http_requests
import pandas as pd
from fpdf import FPDF
import io

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ==========================================
# GOOGLE OAUTH CONFIG
# ==========================================
GOOGLE_ENABLED = False
GOOGLE_CLIENT_ID = None
GOOGLE_CLIENT_SECRET = None
GOOGLE_REDIRECT_URI = 'http://localhost:8080/auth/google/callback'

cred_path = os.path.join(os.path.dirname(__file__), 'google_credentials.json')
if os.path.exists(cred_path):
    try:
        with open(cred_path) as f:
            creds = json.load(f)
            web = creds.get('web', {})
            GOOGLE_CLIENT_ID = web.get('client_id')
            GOOGLE_CLIENT_SECRET = web.get('client_secret')
            if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
                GOOGLE_ENABLED = True
                print(f"✅ Google OAuth ENABLED")
    except Exception as e:
        print(f"⚠️  Google credentials error: {e}")

USERS = {'demo@quantflow.com': 'password', 'pratyush@quantflow.com': 'demo123'}
ONBOARDED_USERS = set()
os.makedirs('exports', exist_ok=True)
os.makedirs('cache', exist_ok=True)
os.makedirs('portfolios', exist_ok=True)


# ==========================================
# AUTH ROUTES
# ==========================================

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    if session.get('user') not in ONBOARDED_USERS:
        return redirect('/onboarding')
    return redirect('/market')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        if session.get('user') not in ONBOARDED_USERS:
            return redirect('/onboarding')
        return redirect('/market')
    
    error = request.args.get('error', None)
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        if email in USERS and USERS[email] == password:
            session.clear()
            session['user'] = email
            session['user_name'] = email.split('@')[0].capitalize()
            session['user_picture'] = ''
            session['login_method'] = 'email'
            print(f"✅ Email login: {email}")
            return redirect('/onboarding')
        else:
            error = 'Invalid email or password'
    
    return render_template('login.html', google_enabled=GOOGLE_ENABLED, error=error)


@app.route('/auth/google')
def google_login():
    if not GOOGLE_ENABLED:
        return redirect('/login?error=google_not_configured')
    auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
        f'&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}'
        '&scope=openid%20email%20profile&access_type=offline&prompt=select_account'
    )
    return redirect(auth_url)


@app.route('/auth/google/callback')
def google_callback():
    if not GOOGLE_ENABLED:
        return redirect('/login')
    code = request.args.get('code')
    if not code:
        return redirect('/login?error=no_code')
    try:
        token_resp = http_requests.post('https://oauth2.googleapis.com/token', data={
            'code': code, 'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET, 'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }).json()
        access_token = token_resp.get('access_token')
        userinfo = http_requests.get('https://www.googleapis.com/oauth2/v3/userinfo',
                                     headers={'Authorization': f'Bearer {access_token}'}).json()
        email = userinfo.get('email')
        if not email:
            return redirect('/login?error=no_email')
        session.clear()
        session['user'] = email
        session['user_name'] = userinfo.get('name', email.split('@')[0])
        session['user_picture'] = userinfo.get('picture', '')
        session['login_method'] = 'google'
        return redirect('/onboarding')
    except Exception as e:
        print(f"Google error: {e}")
        return redirect('/login?error=auth_failed')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/onboarding')
def onboarding():
    if 'user' not in session:
        return redirect('/login')
    return render_template('onboarding.html', user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'))


@app.route('/onboarding/complete', methods=['POST'])
def onboarding_complete():
    if 'user' not in session:
        return redirect('/login')
    ONBOARDED_USERS.add(session.get('user'))
    return jsonify({'ok': True, 'redirect': '/market'})


@app.route('/onboarding/skip', methods=['POST'])
def onboarding_skip():
    if 'user' not in session:
        return redirect('/login')
    ONBOARDED_USERS.add(session.get('user'))
    return jsonify({'ok': True, 'redirect': '/market'})


# ==========================================
# MARKET
# ==========================================

@app.route('/market')
def market():
    if 'user' not in session:
        return redirect('/login')
    return render_template('market.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'))


@app.route('/api/market/live')
def api_market_live():
    return jsonify(get_live_market())


# ==========================================
# DASHBOARD
# ==========================================

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks(), sectors=get_sectors(),
                          total_stocks=len(get_all_stocks()),
                          current_date=datetime.now().strftime('%B %d, %Y'))


# ==========================================
# COMPARE
# ==========================================

@app.route('/compare')
def compare_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('compare.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


@app.route('/api/compare/stocks', methods=['POST'])
def api_compare_stocks():
    if 'user' not in session:
        return jsonify({'ok': False, 'error': 'Login required'}), 401
    try:
        payload = request.get_json()
        symbols = payload.get('symbols', [])
        start = payload.get('start_date', '2020-01-01')
        end = payload.get('end_date', '2026-07-16')
        capital = float(payload.get('capital', 100000))
        strategy_type = payload.get('strategy', 'ma_crossover')
        
        results = []
        for symbol in symbols:
            result = run(symbol, start, end, capital, strategy_type,
                        fast_ma=int(payload.get('fast_ma', 20)),
                        slow_ma=int(payload.get('slow_ma', 50)),
                        rsi_period=14, rsi_oversold=35, rsi_overbought=65,
                        bb_period=20, bb_std=2.0)
            result['symbol'] = symbol
            stock_info = get_stock(symbol)
            result['name'] = stock_info['name'] if stock_info else symbol
            results.append(result)
        
        results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        return jsonify({'ok': True, 'results': results})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ==========================================
# OPTIMIZER
# ==========================================

@app.route('/optimizer')
def optimizer_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('optimizer.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    try:
        payload = request.get_json()
        strategy = payload.get('strategy', 'ma_crossover')
        if strategy == 'ma_crossover':
            results = optimize_ma_crossover(payload.get('symbol', 'NABIL'),
                                           payload.get('start_date', '2020-01-01'),
                                           payload.get('end_date', '2026-07-16'),
                                           float(payload.get('capital', 100000)))
        elif strategy == 'rsi':
            results = optimize_rsi(payload.get('symbol', 'NABIL'),
                                  payload.get('start_date', '2020-01-01'),
                                  payload.get('end_date', '2026-07-16'),
                                  float(payload.get('capital', 100000)))
        else:
            results = optimize_bollinger(payload.get('symbol', 'NABIL'),
                                        payload.get('start_date', '2020-01-01'),
                                        payload.get('end_date', '2026-07-16'),
                                        float(payload.get('capital', 100000)))
        return jsonify({'ok': True, 'results': results[:20], 'total_tested': len(results)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ==========================================
# WALK-FORWARD
# ==========================================

@app.route('/walkforward')
def walkforward_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('walkforward.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


@app.route('/api/walkforward', methods=['POST'])
def api_walkforward():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    try:
        payload = request.get_json()
        result = run_walkforward(
            symbol=payload.get('symbol', 'NABIL'),
            start=payload.get('start_date', '2020-01-01'),
            end=payload.get('end_date', '2026-07-16'),
            capital=float(payload.get('capital', 100000)),
            strategy_type=payload.get('strategy', 'ma_crossover'),
            fast_ma=int(payload.get('fast_ma', 20)),
            slow_ma=int(payload.get('slow_ma', 50)),
            rsi_period=14, rsi_oversold=35, rsi_overbought=65,
            bb_period=20, bb_std=2.0
        )
        return jsonify({'ok': True, 'data': result})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ==========================================
# STRATEGY BUILDER
# ==========================================

@app.route('/builder')
def builder_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('builder.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


@app.route('/api/builder/test', methods=['POST'])
def api_builder_test():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    try:
        data = request.get_json()
        strategy_data = data.get('strategy', {})
        custom_strategy = CustomStrategy.from_dict(strategy_data)
        
        from nepal_data import NEPALDataHandler
        from backtester import Portfolio, Report
        
        handler = NEPALDataHandler(data.get('symbol', 'NABIL'),
                                   data.get('start_date', '2020-01-01'),
                                   data.get('end_date', '2026-07-16'))
        portfolio = Portfolio(float(data.get('capital', 100000)))
        
        while handler.advance():
            bar = handler.current_bar()
            if bar is None:
                break
            price = float(bar['Close'])
            signal = custom_strategy.evaluate(handler)
            if signal == 'BUY':
                portfolio.buy(price, handler.current_time)
            elif signal == 'SELL':
                portfolio.sell(price, handler.current_time)
            portfolio.record(handler.current_time, price)
        
        report = Report(portfolio.curve, portfolio.trades, float(data.get('capital', 100000)), custom_strategy.name)
        result = report.to_dict()
        return jsonify({'ok': True, 'data': result})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ==========================================
# PORTFOLIO TRACKER
# ==========================================

@app.route('/portfolio')
def portfolio_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('portfolio.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


@app.route('/api/portfolio', methods=['GET', 'POST', 'DELETE'])
def api_portfolio():
    if 'user' not in session:
        return jsonify({'ok': False, 'error': 'Login required'}), 401
    
    pm = PortfolioManager(session['user'])
    
    if request.method == 'GET':
        portfolios = pm.get_all()
        return jsonify({'ok': True, 'portfolios': portfolios})
    
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')
        
        if action == 'create':
            pf = pm.create(data.get('name', 'New Portfolio'), data.get('description', ''))
            return jsonify({'ok': True, 'portfolio': pf})
        
        elif action == 'add_holding':
            holding = pm.add_holding(
                data['portfolio_id'], data['symbol'],
                int(data['shares']), float(data['buy_price']),
                data.get('buy_date', datetime.now().strftime('%Y-%m-%d'))
            )
            if holding:
                return jsonify({'ok': True, 'holding': holding})
            return jsonify({'ok': False, 'error': 'Portfolio not found'})
        
        elif action == 'remove_holding':
            success = pm.remove_holding(data['portfolio_id'], int(data['index']))
            return jsonify({'ok': success})
        
        elif action == 'update_prices':
            pf = pm.update_prices(data['portfolio_id'], data.get('prices', {}))
            return jsonify({'ok': True, 'portfolio': pf})
    
    if request.method == 'DELETE':
        data = request.get_json()
        pm.delete(data['portfolio_id'])
        return jsonify({'ok': True})


# ==========================================
# ALERTS
# ==========================================

@app.route('/alerts')
def alerts_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('alerts.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


@app.route('/api/alerts', methods=['GET', 'POST', 'DELETE'])
def api_alerts():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    
    am = AlertManager(session['user'])
    
    if request.method == 'GET':
        return jsonify({'ok': True, 'active': am.get_all(), 'history': am.get_history()})
    
    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')
        
        if action == 'create':
            alert = am.create(data['symbol'], data['strategy_type'],
                            data.get('params', {}), data.get('alert_type', 'both'))
            return jsonify({'ok': True, 'alert': alert})
        elif action == 'toggle':
            alert = am.toggle(data['alert_id'])
            return jsonify({'ok': True, 'alert': alert})
    
    if request.method == 'DELETE':
        data = request.get_json()
        am.delete(data['alert_id'])
        return jsonify({'ok': True})


# ==========================================
# BACKTEST API
# ==========================================

@app.route('/api/backtest', methods=['POST'])
def backtest():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    try:
        payload = request.get_json()
        result = run(
            symbol=payload.get('symbol', 'NABIL'),
            start=payload.get('start_date', '2020-01-01'),
            end=payload.get('end_date', '2026-07-16'),
            capital=float(payload.get('capital', 100000)),
            strategy_type=payload.get('strategy', 'ma_crossover'),
            fast_ma=int(payload.get('fast_ma', 20)),
            slow_ma=int(payload.get('slow_ma', 50)),
            rsi_period=int(payload.get('rsi_period', 14)),
            rsi_oversold=int(payload.get('rsi_oversold', 35)),
            rsi_overbought=int(payload.get('rsi_overbought', 65)),
            bb_period=int(payload.get('bb_period', 20)),
            bb_std=float(payload.get('bb_std', 2.0))
        )
        return jsonify({'ok': True, 'data': result})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    try:
        payload = request.get_json()
        results = run_comparison(
            symbol=payload.get('symbol', 'NABIL'),
            start=payload.get('start_date', '2020-01-01'),
            end=payload.get('end_date', '2026-07-16'),
            capital=float(payload.get('capital', 100000))
        )
        return jsonify({'ok': True, 'results': results})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ==========================================
# EXPORT
# ==========================================

@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    try:
        data = request.get_json()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 20)
        pdf.cell(0, 12, 'NEPSE QuantFlow - Report', ln=True, align='C')
        pdf.ln(4)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 7, f"Stock: {data.get('symbol', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Strategy: {data.get('strategy', 'N/A')}", ln=True)
        pdf.set_font('Helvetica', '', 11)
        for key, val in data.get('metrics', {}).items():
            pdf.cell(0, 7, f"{key}: {val}", ln=True)
        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        return send_file(buf, download_name='report.pdf', as_attachment=True, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    if 'user' not in session:
        return jsonify({'ok': False}), 401
    try:
        data = request.get_json()
        trades = data.get('trades', [])
        if not trades:
            return jsonify({'ok': False, 'error': 'No trades'}), 400
        df = pd.DataFrame(trades)
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(io.BytesIO(buf.getvalue().encode()), download_name='trades.csv',
                        as_attachment=True, mimetype='text/csv')
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ==========================================
# LEARN & STOCKS API
# ==========================================

@app.route('/learn')
def learn():
    if 'user' not in session:
        return redirect('/login')
    topic = request.args.get('topic', 'glossary')
    return render_template('learn.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'), topic=topic)


@app.route('/tutorial')
def tutorial():
    if 'user' not in session:
        return redirect('/login')
    return render_template('tutorial.html')


@app.route('/api/stocks')
def api_stocks():
    sector = request.args.get('sector')
    search = request.args.get('search')
    if search:
        return jsonify(search_stocks(search))
    if sector and sector != 'All':
        return jsonify(get_stocks_by_sector(sector))
    return jsonify(get_all_stocks())


@app.route('/api/sectors')
def api_sectors():
    sectors = get_sectors()
    return jsonify({'sectors': sectors, 'counts': {s: len(get_stocks_by_sector(s)) for s in sectors}})


# ==========================================
# RUN
# ==========================================

if __name__ == '__main__':
    print("\n" + "="*55)
    print("  🇳🇵  NEPSE QuantFlow v3.0")
    print("  Market | Backtest | Compare | Optimizer")
    print("  Walk-Forward | Builder | Portfolio | Alerts | Learn")
    print("  🔗 http://localhost:8080/login")
    print("="*55 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8080)