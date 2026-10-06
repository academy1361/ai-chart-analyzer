# AI Chart Analyzer Complete

نسخه کامل‌تر اجرایی شامل:
Analyze، Dashboard، History، Backtest، Scanner، Watchlist، Alerts، Analytics، Reports، Settings و Account.
Backend با FastAPI/SQLAlchemy، JWT، Binance provider، RSI/MACD/Ichimoku/EMA/ATR/PSAR، Confluence، Risk Levels، Backtest آموزشی، Docker و Railway.

اجرا:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload

سپس http://127.0.0.1:8000

هشدار: این پروژه سفارش واقعی ارسال نمی‌کند. Xypher به‌دلیل نبود فرمول مرجع عمومی دقیق، به‌صورت canonical ادعا نشده است.
