from confluent_kafka import Consumer
from dotenv import load_dotenv
import os
import json
import streamlit as st
import pandas as pd
import time
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import datetime

# Kafka consumer configuration
load_dotenv()

config = {
    'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
    'sasl.username': os.getenv('SASL_USERNAME'),
    'sasl.password': os.getenv('SASL_PASSWORD'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': 'false'
}

def format_value(value):
    if value > 0:
        return f'<span style="color:green">{value:.2f}%</span>'
    else:
        return f'<span style="color:red">{value:.2f}%</span>'

def fetch_company_data(ticker):
    try:
        stock_data = yf.Ticker(ticker)
        return stock_data
    except Exception as e:
        st.error(f"Error fetching company data: {e}")
        return None

def display_company_info(company_info):
    try:
        st.sidebar.title("Company Details")
        st.sidebar.subheader("Financials")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.markdown(f"<p style='font-size:12px'>Market Cap: <br>₹{company_info['marketCap']:,}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>P/E Ratio: <br>{company_info['trailingPE']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>P/B Ratio: <br>{company_info['priceToBook']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>Industry P/E Ratio: <br>{company_info['industry']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>52 Week High: <br>₹{company_info['fiftyTwoWeekHigh']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>52 Week Low: <br>₹{company_info['fiftyTwoWeekLow']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>EPS: <br>{company_info['trailingEps']}</p>", unsafe_allow_html=True)
        with col2:
            dividend_yield = company_info.get('dividendYield', 0) * 100
            st.markdown(f"<p style='font-size:12px'>Dividend Yield: <br>{dividend_yield:.2f}%</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>Profit Margin: <br>{format_value(company_info['profitMargins'] * 100)}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>Revenue Growth (YoY): <br>{format_value(company_info['revenueGrowth'] * 100)}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>Net Income (TTM): <br>₹{company_info['netIncomeToCommon']:,}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>EBITDA (TTM): <br>₹{company_info['ebitda']:,}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>Debt to Equity Ratio: <br>{company_info['debtToEquity']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:12px'>Book Value: <br>₹{company_info['bookValue']}</p>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying company info: {e}")

def fetch_historical_data(stock_data, period, interval):
    try:
        return stock_data.history(period=period, interval=interval)
    except Exception as e:
        st.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()

def display_historical_data(stock_data):
    try:
        st.subheader("Historical Stock Price")
        time_period = st.selectbox("Select Time Period", ["1d", "5d", "1mo", "1y", "Max"])
        interval = {"1d": "1m", "5d": "30m", "1mo": "1d", "1y": "1wk", "Max": "1wk"}[time_period]
        hist = fetch_historical_data(stock_data, time_period, interval)
        
        chart_type = st.radio("Select Chart Type", options=["Candlestick", "Line"], format_func=lambda x: "📈" if x == "Line" else "🕯️")
        fig = go.Figure()
        if chart_type == 'Candlestick':
            fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']))
        else:
            fig = px.line(hist, x=hist.index, y='Close', title='Stock Price Chart', labels={'Close': 'Stock Price (INR)', 'Date': 'Date'})
        fig.update_layout(title='Stock Price Chart', xaxis_title='Date', yaxis_title='Stock Price (INR)')
        st.plotly_chart(fig)

        hist_monthly = fetch_historical_data(stock_data, "1y", "1mo")
        hist_df = hist_monthly.reset_index()
        hist_df['Date'] = hist_df['Date'].dt.strftime('%Y-%m')
        hist_df = hist_df.groupby('Date')['Volume'].sum().reset_index()
        
        st.subheader("Volume Chart by Month")
        fig_bar = px.bar(hist_df, y='Date', x='Volume', title='Stock Volume Chart', labels={'Volume': 'Volume', 'Date': 'Date'})
        st.plotly_chart(fig_bar)

        st.subheader("Historical Stock Data")
        st.dataframe(hist)
    except Exception as e:
        st.error(f"Error displaying historical data: {e}")

def display_financial_metrics(stock_data):
    try:
        st.subheader("Financial Metrics")
        financials = stock_data.financials
        financials.columns = [col.strftime("%Y") for col in financials.columns]
        st.write(financials)

        st.subheader("Balance Sheet")
        balance_sheet = stock_data.balance_sheet
        balance_sheet.columns = [col.strftime("%Y") for col in balance_sheet.columns]
        st.write(balance_sheet)
    except Exception as e:
        st.error(f"Error displaying financial metrics: {e}")

def display_news(stock_data):
    try:
        stock_news = stock_data.news[:5]
        for idx, news in enumerate(stock_news):
            days_ago = (datetime.datetime.now() - datetime.datetime.fromtimestamp(news['providerPublishTime'])).days
            days_ago_txt = "(Today)" if days_ago == 0 else f"({days_ago} days ago)"
            st.write(f"{idx+1}. {news['title']}")
            st.markdown(f"<small>Published by {news['publisher']} - {days_ago_txt}</small><a href='{news['link']}' target='_blank'> Click here</a>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying news: {e}")

def main():
    try:
        consumer = Consumer(config)
        consumer.subscribe(['zomato_stock'])
    except Exception as e:
        st.error(f"Error initializing Kafka consumer or subscribing to topic: {e}")
        return

    try:
        ticker = "ZOMATO.NS"
        col1, col2 = st.columns([1, 3])
        with col1:
            logo_url = "https://upload.wikimedia.org/wikipedia/commons/7/75/Zomato_logo.png"
            st.image(logo_url, width=100)
        with col2:
            st.title('Zomato')
            current_price_placeholder = st.empty()

        stock_data = fetch_company_data(ticker)
        if stock_data is None:
            return

        tab1, tab2, tab3 = st.tabs(["Live Chart", "Historical Analysis", "News"])

        with tab2:
            display_company_info(stock_data.info)
            display_historical_data(stock_data)
            display_financial_metrics(stock_data)

        with tab3:
            display_news(stock_data)

        with tab1:
            df = pd.DataFrame(columns=['Date', 'Close'])
            chart_placeholder = st.empty()
            while True:
                try:
                    message = consumer.poll(1.0)
                    time.sleep(5)
                    if message is None or message.error():
                        continue

                    value = json.loads(message.value().decode('utf-8'))
                    current_price_placeholder.markdown(f"<p style='font-size:25px'> ₹{round(value['Price'], 2)}</p>", unsafe_allow_html=True)
                    consumer.commit(message)

                    try:
                        value['Timestamp'] = pd.to_datetime(value['Timestamp'], unit='ms')
                        timestamp = pd.to_datetime(value['Timestamp'])
                        streaming_data = [timestamp, round(value['Price'], 3)]
                    except Exception as e:
                        print(f"Error processing message value={value}: {e}")
                        continue

                    new_data = pd.DataFrame([streaming_data], columns=['Date', 'Close'])
                    df = pd.concat([df, new_data], ignore_index=True).iloc[-20:]

                    if not df.empty:
                        fig_line_chart = px.line(df, x='Date', y='Close', title='Stock Data Visualization', labels={'Close': 'Stock Price (INR)', 'Date': 'Timestamp'}, markers=True)
                        fig_line_chart.update_traces(textposition="bottom center")
                        chart_placeholder.plotly_chart(fig_line_chart)
                except Exception as e:
                    st.error(f"Error in live chart update: {e}")
    except Exception as e:
        st.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
