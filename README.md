# 📈 Stock Analyzer & Predictor - Professional Edition

A production-ready, professional stock analysis and prediction application built with Streamlit, featuring real-time market data, technical analysis, and predictive modeling.

## 🚀 Features

- **Real-time Market Data**: Live stock prices and historical data from Yahoo Finance
- **Technical Analysis**: Advanced charts with moving averages, RSI, MACD, Bollinger Bands
- **Professional UI**: Modern, responsive interface optimized for production use
- **Global Stock Support**: Analyze stocks from any major exchange worldwide
- **Production Ready**: Optimized for deployment with proper security and performance settings

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start
1. Clone the repository:
```bash
git clone <repository-url>
cd analyze
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
# Development mode
streamlit run app.py

# Production mode
python start_production.py
```

## 🚀 Production Deployment

### Method 1: Using Production Script (Recommended)
```bash
python start_production.py
```

### Method 2: Using Batch File (Windows)
```bash
start_production.bat
```

### Method 3: Manual Streamlit Command
```bash
streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false \
  --server.enableCORS true \
  --server.enableXsrfProtection true
```

## ⚙️ Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```env
# Server Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# Security Settings
STREAMLIT_SERVER_ENABLE_CORS=true
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Application Settings
DEFAULT_STOCK_SYMBOL=RELIANCE.NS
HISTORICAL_DAYS=60
LOG_LEVEL=INFO
```

## 🌐 Access URLs

- **Local Access**: http://localhost:8501
- **Network Access**: http://YOUR_IP_ADDRESS:8501
- **Production**: Configure your domain/IP in the server settings

## 🔒 Security Features

- **CORS Protection**: Configurable cross-origin resource sharing
- **XSRF Protection**: Built-in CSRF attack prevention
- **Usage Statistics**: Disabled by default for privacy
- **Environment-based Configuration**: Secure configuration management

## 📊 Data Sources

- **Primary**: Yahoo Finance (free, no API key required)
- **Real-time**: Live market data with automatic updates
- **Historical**: Configurable time periods (default: 60 days)
- **Global**: Support for stocks from major exchanges worldwide

## 🏗️ Architecture

```
analyze/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration management
├── yfinance_client.py    # Yahoo Finance data client
├── chart_utils.py        # Chart creation utilities
├── utils.py              # Helper functions
├── start_production.py   # Production startup script
├── deploy.py             # Deployment automation
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Deployment Options

### 1. Local Production
- Run `python start_production.py`
- Access via http://localhost:8501

### 2. Network Production
- Configure `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- Access via http://YOUR_IP:8501

### 3. Cloud Deployment
- Deploy to AWS, Azure, Google Cloud, or Heroku
- Use the production configuration settings
- Configure load balancers and reverse proxies as needed

### 4. Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["python", "start_production.py"]
```
