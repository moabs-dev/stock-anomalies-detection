import yfinance as yf
import ta
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import streamlit as st
import pandas as pd

# Sidebar
st.sidebar.title("📈 Stock Anomaly Detector")
ticker = st.sidebar.selectbox("Choose a stock", ['AAPL', 'GOOG', 'TSLA'])

# Download data
data = yf.download(ticker, start="2018-01-01", end="2024-12-31")['Close']
data = data.reset_index()
data.fillna(method='ffill', inplace=True)

# Preprocess
df = data.rename(columns={'Date': 'Date', ticker: 'y'})  # Make sure correct ticker is selected
df.set_index('Date', inplace=True)
df['SMA'] = ta.trend.sma_indicator(df['y'], window=20)
df['EMA'] = ta.trend.ema_indicator(df['y'], window=20)
df['RSI'] = ta.momentum.RSIIndicator(df['y']).rsi()
bb = ta.volatility.BollingerBands(df['y'])
df['BB_High'] = bb.bollinger_hband()
df['BB_Low'] = bb.bollinger_lband()

# Anomaly detection
df_clean = df[['y', 'SMA', 'EMA', 'RSI', 'BB_High', 'BB_Low']].dropna()
clf = IsolationForest(contamination=0.01, random_state=42)
df.loc[df_clean.index, 'anomaly_if'] = clf.fit_predict(df_clean)
df['anomaly_if'] = df['anomaly_if'].apply(lambda x: 1 if x == -1 else 0)


# Prepare for Prophet
df_prophet = df[['y']].reset_index().rename(columns={'Date': 'ds'})  # Prophet: ds = date
model = Prophet()
model.fit(df_prophet)

# Forecast future
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Residual-based anomaly
df_forecast = forecast[['ds', 'yhat']]
merged = df_prophet.merge(df_forecast, on='ds')
merged['residual'] = merged['y'] - merged['yhat']
merged['forecast_anomaly'] = merged['residual'].apply(
    lambda x: 1 if abs(x) > merged['residual'].std() * 2 else 0
)

# Plotting
st.subheader(f"📊 Anomaly Detection for {ticker}")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['y'], name='Close Price'))
fig.add_trace(go.Scatter(
    x=df[df['anomaly_if'] == 1].index,
    y=df[df['anomaly_if'] == 1]['y'],
    mode='markers', marker=dict(color='red', size=8),
    name='Isolation Forest Anomalies'
))
st.plotly_chart(fig)

# Download button
anomalies = df[df['anomaly_if'] == 1][['y']]
anomalies.to_csv("detected_anomalies.csv")
st.download_button("📥 Download Anomalies CSV", open("detected_anomalies.csv", "rb"),
                   file_name="anomalies.csv")
