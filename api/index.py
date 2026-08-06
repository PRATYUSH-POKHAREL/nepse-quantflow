from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from backtester import run, run_comparison
from optimizer import optimize_ma_crossover, optimize_rsi, optimize_bollinger
from market_data import get_live_market, get_stock_profile
from nepal_stocks import get_all_stocks, get_sectors, get_stocks_by_sector, search_stocks, get_stock
import secrets
import os
import json
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import io

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = secrets.token_hex(32)

# Google OAuth (disabled on Vercel - use email login only)
GOOGLE_ENABLED = False

USERS = {
    'demo@quantflow.com': 'password',
    'pratyush@quantflow.com': 'demo123',
}

ONBOARDED_USERS = set()


# ==========================================
# AUTH ROUTES
# ==========================================

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return redirect('/market')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
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
            return redirect('/market')
        else:
            error = 'Invalid email or password'
    
    return render_template('login.html', google_enabled=False, error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


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
        return jsonify({'ok': False}), 401
    try:
        payload = request.get_json()
        symbols = payload.get('symbols', [])
        results = []
        for symbol in symbols:
            result = run(symbol, payload.get('start_date', '2020-01-01'),
                        payload.get('end_date', '2026-07-16'),
                        float(payload.get('capital', 100000)),
                        payload.get('strategy', 'ma_crossover'),
                        fast_ma=20, slow_ma=50, rsi_period=14, rsi_oversold=35,
                        rsi_overbought=65, bb_period=20, bb_std=2.0)
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


# ==========================================
# BUILDER
# ==========================================

@app.route('/builder')
def builder_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('builder.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


# ==========================================
# PORTFOLIO
# ==========================================

@app.route('/portfolio')
def portfolio_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('portfolio.html', user=session.get('user'),
                          user_name=session.get('user_name'),
                          user_picture=session.get('user_picture'),
                          stocks=get_all_stocks())


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


# ==========================================
# LEARN
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
            rsi_period=14, rsi_oversold=35, rsi_overbought=65,
            bb_period=20, bb_std=2.0
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
        pdf.set_font('Helvetica', '', 10)
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


@app.route('/api/stocks')
def api_stocks():
    return jsonify(get_all_stocks())


@app.route('/api/sectors')
def api_sectors():
    sectors = get_sectors()
    return jsonify({'sectors': sectors, 'counts': {s: len(get_stocks_by_sector(s)) for s in sectors}})