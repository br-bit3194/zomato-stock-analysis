# zomato-stock-analysis

## Workspace

Collecting workspace information

The zomato-stock-analysis project is a real-time stock analysis and visualization tool for Zomato's stock data. It consists of two main components: a data producer and a web application.

## Project Structure

- **README.md**: Contains the project title.
- **requirements.txt**: Lists all the dependencies required for the project.
- **streamlit_web_app.py**: Implements the Streamlit web application for visualizing Zomato's stock data.
- **zomato_data_producer.py**: Produces real-time stock data for Zomato and sends it to a Kafka topic.

## Components

### Data Producer

The data producer (`zomato_data_producer.py`) fetches real-time stock data for Zomato using the Yahoo Finance API and sends it to a Kafka topic named `zomato_stock`. It runs in an infinite loop, producing data every 12 seconds.

### Web Application

The web application (`streamlit_web_app.py`) is built using Streamlit and provides the following features:

- **Live Chart**: Displays real-time stock price updates.
- **Historical Analysis**: Shows historical stock data, financial metrics, and balance sheets.
- **News**: Displays the latest news related to Zomato.

The application uses a Kafka consumer to receive real-time stock data and updates the live chart accordingly. It also fetches historical data and financial information from Yahoo Finance.

## Dependencies

The project relies on various Python libraries, including:

- `confluent_kafka` for Kafka integration
- `dotenv` for loading environment variables
- `streamlit` for building the web application
- `yfinance` for fetching stock data
- `plotly` for data visualization

For a complete list of dependencies, refer to the `requirements.txt` file.