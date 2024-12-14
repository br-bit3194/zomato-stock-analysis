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
- `confluent_kafka` for Kafka integration (using a Confluent Kafka cluster from [Confluent Cloud](https://login.confluent.io/)) --> Create free account for month, no need to setup kafka on local machine. Create cluster, then topic name, also create api key for connecing the cluster
That's it. Kafka is setup.

- `dotenv` for loading environment variables
- `streamlit` for building the web application
- `yfinance` for fetching stock data
- `plotly` for data visualization

For a complete list of dependencies, refer to the `requirements.txt` file.

## Steps to run the application

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/zomato-stock-analysis.git
    cd zomato-stock-analysis
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the root directory and add the necessary environment variables. Refer to `.env` for the required variables.

5. **Start the data producer**:
    ```sh
    python zomato_data_producer.py
    ```

6. **Run the Streamlit web application**:
    ```sh
    streamlit run streamlit_web_app.py
    ```

7. **Access the application**:
    Open your web browser and go to `http://localhost:8501` to view the application.