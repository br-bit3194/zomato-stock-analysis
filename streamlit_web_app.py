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
# Load environment variables from .env file
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

# Create Kafka consumer instance
consumer = Consumer(config)

# Subscribe to Kafka topic
kafka_topic = 'zomato_stock'
consumer.subscribe([kafka_topic])

# Display Zomato logo
col1, col2 = st.columns([1, 3])
with col1:
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/7/75/Zomato_logo.png"
    st.image(logo_url, width=100)
with col2:
    st.title('Zomato')
    current_price_placeholder = st.empty()

# Create tabs for live chart and historical analysis
tab1, tab2, tab3 = st.tabs(["Live Chart", "Historical Analysis", "News"])

with tab2:
    # Fetch historical market data from Yahoo Finance
    ticker = 'ZOMATO.NS'
    stock_data = yf.Ticker(ticker)
    
    # Additional dashboard components
    st.sidebar.title("Company Details")

    # Fetch company info from Yahoo Finance
    company_info = stock_data.info
    # Display company financials
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
        if 'dividendYield' in company_info and company_info['dividendYield'] is not None:
            st.markdown(f"<p style='font-size:12px'>Dividend Yield: <br>{company_info['dividendYield'] * 100:.2f}%</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:12px'>Dividend Yield: <br>0.00%</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>Profit Margin: <br>{format_value(company_info['profitMargins'] * 100)}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>Revenue Growth (YoY): <br>{format_value(company_info['revenueGrowth'] * 100)}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>Net Income (TTM): <br>₹{company_info['netIncomeToCommon']:,}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>EBITDA (TTM): <br>₹{company_info['ebitda']:,}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>Debt to Equity Ratio: <br>{company_info['debtToEquity']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px'>Book Value: <br>₹{company_info['bookValue']}</p>", unsafe_allow_html=True)
    
    # Fetch historical market data from Yahoo Finance
    ticker = 'ZOMATO.NS'
    stock_data = yf.Ticker(ticker)

    #############
    st.subheader("Historical Stock Price")
    # display ["1d", "5d", "1mo", "1y", "5y", "Max"] stock price chart
    # provide option of selecting the time period and based on that show the chart. by default show 1y chart
    time_period = st.selectbox("Select Time Period", ["1d", "5d", "1mo", "1y", "Max"])
    if time_period == "1d":
        hist = stock_data.history(period="1d", interval="1m")
    elif time_period == "5d":
        hist = stock_data.history(period="5d", interval="30m")
    elif time_period == "1mo":
        hist = stock_data.history(period="1mo", interval="1d")
    elif time_period == "1y":
        hist = stock_data.history(period="1y", interval="1wk")
    else:
        hist = stock_data.history(period="max", interval="1wk")
    
    # show two selection points for the user to select the candlestick chart or line chart
    chart_type = st.radio(
        "Select Chart Type",
        options=["Candlestick", "Line"],
        format_func=lambda x: "📈" if x == "Line" else "🕯️"
    )

    fig_box = go.Figure()
    if chart_type == 'Candlestick':
        fig_box.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']))
        fig_box.update_layout(title='Stock Price Chart', xaxis_title='Date', yaxis_title='Stock Price (INR)')
        st.plotly_chart(fig_box)
    else:
        fig_hist = px.line(hist, x=hist.index, y='Close', title='Stock Price Chart', labels={'Close': 'Stock Price (INR)', 'Date': 'Date'})
        st.plotly_chart(fig_hist)
    
    ############
    hist = stock_data.history(period="1y", interval="1mo")
    hist_df = hist.reset_index()
    hist_df['Date'] = hist_df['Date'].dt.strftime('%Y-%m')
    hist_df = hist_df.groupby('Date')['Volume'].sum().reset_index()
    
    # Display historical stock volume data
    st.subheader("Volume Chart by Month")
    fig_bar = px.bar(hist_df, y='Date', x='Volume', title='Stock Volume Chart', labels={'Volume': 'Volume', 'Date': 'Date'})
    st.plotly_chart(fig_bar)

    # Display historical stock data in a table
    st.subheader("Historical Stock Data")
    st.dataframe(hist)

    # Display additional financial metrics
    st.subheader("Financial Metrics")
    financials = stock_data.financials
    financials.columns = [col.strftime("%Y") for col in financials.columns]
    st.write(financials)

    # Display additional financial metrics
    st.subheader("Balance Sheet")
    balance_sheet = stock_data.balance_sheet
    balance_sheet.columns = [col.strftime("%Y") for col in balance_sheet.columns]
    st.write(balance_sheet)

with tab3:

    stock_news = stock_data.news[:5]
    for idx, news in enumerate(stock_news):
        publish_date = datetime.datetime.fromtimestamp(news['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
        days_ago = (datetime.datetime.now() - datetime.datetime.fromtimestamp(news['providerPublishTime'])).days
        if days_ago==0:
            days_ago_txt = "(Today)"
        else:
            days_ago_txt = f"({days_ago} days ago)"
        st.write(f"{idx+1}. {news['title']}")
        st.markdown(f"<small>Published by {news['publisher']} - {days_ago_txt}</small><a href='{news['link']}' target='_blank'> Click here</a>", unsafe_allow_html=True)
        # st.markdown(f"<a href='{news['link']}' target='_blank'>link</a>", unsafe_allow_html=True)
        
    
with tab1:

    # Create an empty DataFrame to store the stock data
    df = pd.DataFrame(columns=['Date', 'Close'])

    # Create a placeholder for the chart
    chart_placeholder = st.empty()
    print("*************** started *****************")
    cnt = 0
    # Function to update the chart with new streaming data
    while cnt < 10:
        # Receive new streaming data
        time.sleep(12)
        message = consumer.poll(1.0)
        print(cnt)
        if message is None:
            cnt += 1
            continue

        if message.error():
            print(f"Error: {message.error()}")
            cnt += 1
            continue
        
        cnt = 0
        # Process the received message
        value = message.value().decode('utf-8')
        value = json.loads(value)
        print(f"Received message: {value}")

        current_price_placeholder.markdown(f"<p style='font-size:25px'> ₹{round(value['Price'],2)}</p>", unsafe_allow_html=True)
        # Commit the consumed message offset
        consumer.commit(message)

        # Extract the relevant data from the received message and convert Timestamp to human readable date time
        try:
            value['Timestamp'] = pd.to_datetime(value['Timestamp'], unit='ms')
            timestamp = pd.to_datetime(value['Timestamp'])
            streaming_data = [timestamp, round(value['Price'], 3)]
        except Exception as e:
            print(f"error for value={value}: {e}")
            continue

        # Convert streaming data to pandas DataFrame
        new_data = pd.DataFrame([streaming_data], columns=['Date', 'Close'])

        # Append new data to the existing DataFrame
        df = pd.concat([df, new_data], ignore_index=True)

        df = df.iloc[-20:]
        # Update the plotly chart with the new data
        fig_line_chart = px.line(df, x='Date', y='Close', title='Stock Data Visualization', \
                        labels={'Close': 'Stock Price (INR)', 'Date': 'Timestamp'}, markers=True)
        fig_line_chart.update_traces(textposition="bottom center")

        chart_placeholder.plotly_chart(fig_line_chart)

