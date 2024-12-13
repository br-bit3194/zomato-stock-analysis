import yfinance as yf
import json
from time import sleep
import sys
import time
import os
from dotenv import load_dotenv
from confluent_kafka import Producer as KafkaProducer
# Load environment variables from .env file
load_dotenv()

config = {
    # User-specific properties that you must set
    'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
    'sasl.username': os.getenv('SASL_USERNAME'),
    'sasl.password': os.getenv('SASL_PASSWORD'),

    # Fixed properties
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'acks': 'all'
}

# Create Producer instance
producer = KafkaProducer(config)

ticker = "ZOMATO.NS"
kafka_topic = "zomato_stock"
counter = 0
while True:

    zomato = {}

    stock = yf.Ticker(ticker)
    zomato['Price'] = stock.fast_info.last_price
    
    zomato['Name'] = stock.info['shortName']
    zomato['Timestamp'] = time.time()
    print(zomato)

    producer.produce(kafka_topic, json.dumps(zomato))
    sleep(12)
    counter += 1