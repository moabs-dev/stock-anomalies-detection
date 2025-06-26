# 📈 Stock Price Anomaly Detection App

This is a Dockerized Streamlit web app that identifies anomalies in stock price trends using:

- Technical Indicators (SMA, EMA, RSI, Bollinger Bands)
- Machine Learning (Isolation Forest)
- Forecasting (Prophet)

---

## 🚀 Features

✅ Choose a stock (AAPL, GOOG, TSLA)  
✅ Detect sudden market movements/anomalies  
✅ See results visually  
✅ Download anomaly reports (CSV)  
✅ No setup issues — Docker ensures consistent environments  

---

## 🧰 How to Run (with Docker)

```bash
git clone https://github.com/moabs-dev/stock-anomalies.git
cd stock-anomalies
docker build -t anomaly-app .
docker run -p 8501:8501 anomaly-app
