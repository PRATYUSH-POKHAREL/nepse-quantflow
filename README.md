# 🇳🇵 NEPSE QuantFlow

> A personal quantitative finance project for backtesting trading strategies on the Nepal Stock Exchange.

---

## ⚠️ Disclaimer

**This project is for personal educational use only.**

- This is NOT financial advice
- This is NOT a commercial product
- Past performance does NOT guarantee future results
- The data used may be synthetic/demo data, NOT real market data
- Do NOT use this for actual trading decisions
- I am NOT responsible for any financial losses incurred
- This project makes no guarantees about data accuracy or strategy profitability

**If you use this code, you do so entirely at your own risk.**

---

## 📖 What Is This?

NEPSE QuantFlow is a web-based backtesting platform I built to learn quantitative finance. It lets you test trading strategies on historical NEPSE data without risking real money — like a flight simulator for stock trading.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13, Flask |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Data | pandas, NumPy, yfinance |
| Auth | Google OAuth (optional), email/password |
| Export | FPDF (PDF), pandas (CSV) |

---

## 🚀 Quick Start

```bash
git clone https://github.com/PRATYUSH-POKHAREL/nepse-quantflow.git
cd nepse-quantflow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p portfolios cache exports
python app.py




Open http://localhost:8080/login

Demo Login: demo@quantflow.com / password

📊 Features
📊 Market Overview
Simulated NEPSE index, top gainers, top losers, sector performance with auto-refresh.

🔬 Backtesting Engine
4 strategies: MA Crossover, RSI, Bollinger Bands, Buy & Hold

Event-driven simulation with no look-ahead bias

Realistic NEPSE costs: 0.4% broker + 0.015% SEBON + NPR 25 DP charge

⚡ Strategy Optimizer
Tests hundreds of parameter combinations, ranked by Sharpe ratio.

🔮 Walk-Forward Analysis
Rolling window validation to check if strategies are robust or overfitted.

🧩 Strategy Builder
No-code condition builder. Create custom strategies with AND/OR logic.

🔄 Stock Comparison
Run the same strategy on 2-4 stocks side by side.

💼 Portfolio Tracker
Create virtual portfolios, add NEPSE stocks, track P&L over time.

🔔 Alerts & Signals
Set alerts for when strategies generate BUY/SELL signals.

📚 Learning Center
Glossary, strategy guides, risk management, common mistakes, NEPSE facts, FAQ.

📊 Available Strategies
Strategy	Description
MA Crossover	Buy when fast MA crosses above slow MA. Sell on opposite cross.
RSI	Buy when oversold (<35). Sell when overbought (>65).
Bollinger Bands	Buy at lower band. Sell at upper band. Mean reversion.
Buy & Hold	Buy on day 1, sell on last day. Benchmark.
💰 Simulated NEPSE Costs
Cost	Rate
Broker Commission	0.4%
SEBON Fee	0.015%
DP Charge	NPR 25 flat
⚠️ Data Notice
This project attempts Yahoo Finance for NEPSE data. Where unavailable, it uses synthetic simulated data for demonstration. This is NOT real market data. Do NOT trade with it.

📁 Project Structure
text
nepse-quantflow/
├── app.py                  # Main Flask server
├── backtester.py           # Backtesting engine
├── optimizer.py            # Parameter optimizer
├── walkforward.py          # Walk-forward validation
├── portfolio.py            # Virtual portfolio
├── alerts.py               # Signal alerts
├── strategy_builder.py     # No-code builder
├── market_data.py          # Simulated market
├── nepal_stocks.py         # 50+ NEPSE stocks
├── nepal_data.py           # Data handler
├── templates/              # HTML pages
├── static/                 # CSS & JS
└── requirements.txt        # Dependencies
🔮 Future Plans
Real NEPSE data via API

Paper trading with live prices

More technical indicators

Dark mode

Mobile app

👤 Author
Pratyush Pokharel

CSE Data Science, Chandigarh University

GitHub: @PRATYUSH-POKHAREL

📝 License
Personal educational project. Learn from it, but don't use it commercially without permission. Attribution appreciated.

Built with ❤️ for the Nepal Stock Market 🇳🇵
