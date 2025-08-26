import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import logging
from typing import Optional, Dict

# Import our custom modules
from config import Config
from yfinance_client import YahooFinanceClient
from chart_utils import ChartCreator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Stock Analyzer & Predictor - Professional Edition",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .prediction-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .error-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .stock-info {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class StockAnalyzerApp:
    """Main application class for the Stock Analyzer."""
    
    def __init__(self):
        """Initialize the application."""
        self.yf_client = YahooFinanceClient()
        self.current_data = None
        self.live_price_data = None
        self.prediction_data = None
        self.stock_info = None
        
        # Initialize session state
        if 'current_symbol' not in st.session_state:
            st.session_state.current_symbol = Config.DEFAULT_STOCK_SYMBOL
        if 'historical_days' not in st.session_state:
            st.session_state.historical_days = Config.HISTORICAL_DAYS
    
    def render_header(self):
        """Render the main header."""
        st.markdown('<h1 class="main-header">📈 Stock Analyzer & Predictor</h1>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Data source info
        st.success(f"🔗 **Professional Data Source**: Yahoo Finance | 📊 **Real-time market data** | 🌍 **Global stocks supported** | 🚀 **Production Ready**")
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        st.sidebar.title("⚙️ Controls")
        
        # Stock symbol input with search
        symbol = st.sidebar.text_input(
            "Stock Symbol",
            value=st.session_state.current_symbol,
            placeholder="e.g., RELIANCE.NS, AAPL, MSFT",
            help="Enter stock symbol (e.g., RELIANCE.NS for NSE, AAPL for NASDAQ)"
        )
        
        # Quick stock selection
        st.sidebar.markdown("### 🚀 Quick Select")
        popular_stocks = self.yf_client.get_popular_stocks()
        
        # Group by exchange
        nse_stocks = [s for s in popular_stocks if s['exchange'] == 'NSE']
        nasdaq_stocks = [s for s in popular_stocks if s['exchange'] == 'NASDAQ']
        
        if nse_stocks:
            st.sidebar.markdown("**🇮🇳 Indian Stocks (NSE)**")
            for stock in nse_stocks[:5]:
                if st.sidebar.button(f"{stock['name']} ({stock['symbol']})", key=f"btn_{stock['symbol']}"):
                    symbol = stock['symbol']
        
        if nasdaq_stocks:
            st.sidebar.markdown("**🇺🇸 US Stocks (NASDAQ)**")
            for stock in nasdaq_stocks[:5]:
                if st.sidebar.button(f"{stock['name']} ({stock['symbol']})", key=f"btn_{stock['symbol']}"):
                    symbol = stock['symbol']
        
        # Historical data days
        days = st.sidebar.slider(
            "Historical Data (Days)",
            min_value=30,
            max_value=365,
            value=st.session_state.historical_days,
            help="Number of days of historical data to analyze"
        )
        
        # Update session state
        if symbol != st.session_state.current_symbol:
            st.session_state.current_symbol = symbol
            st.session_state.historical_days = days
            st.rerun()
        
        # Market status
        try:
            market_status = self.yf_client.get_market_status()
            st.sidebar.markdown("### 📊 Market Status")
            
            if market_status.get('is_open'):
                st.sidebar.success("🟢 Market Open")
            else:
                st.sidebar.warning("🔴 Market Closed")
            
            st.sidebar.text(f"Time: {market_status.get('current_time', 'N/A')}")
            st.sidebar.text(f"Date: {market_status.get('current_date', 'N/A')}")
            st.sidebar.text(f"Open: {market_status.get('market_open', 'N/A')}")
            st.sidebar.text(f"Close: {market_status.get('market_close', 'N/A')}")
            st.sidebar.text(f"TZ: {market_status.get('timezone', 'N/A')}")
            
        except Exception as e:
            st.sidebar.error(f"Error getting market status: {e}")
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data", type="primary"):
            st.rerun()
        
        # About section
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ About")
        st.sidebar.markdown("""
        This app analyzes stocks using:
        - **Yahoo Finance API** (Real-time data)
        - **Technical Indicators** (SMA, RSI, MACD, BB)
        - **Interactive Charts** (Plotly)
        - **Price Prediction** (Technical analysis)
        """)
        
        st.sidebar.markdown("### 💡 Symbol Examples")
        st.sidebar.markdown("""
        - **Indian**: RELIANCE.NS, TCS.NS, INFY.NS
        - **US**: AAPL, MSFT, GOOGL, TSLA
        - **UK**: BP.L, VOD.L
        - **Japan**: 7203.T, 9984.T
        """)
    
    def fetch_stock_data(self, symbol: str, days: int) -> bool:
        """Fetch stock data and update the application state."""
        try:
            with st.spinner(f"Fetching data for {symbol}..."):
                # Get stock information
                self.stock_info = self.yf_client.get_stock_info(symbol)
                
                # Get historical data
                self.current_data = self.yf_client.get_historical_data(symbol, days)
                if self.current_data is None:
                    st.error(f"Failed to fetch historical data for {symbol}")
                    return False
                
                # Get live price data
                self.live_price_data = self.yf_client.get_live_price(symbol)
                if self.live_price_data is None:
                    st.warning(f"Failed to fetch live price for {symbol}")
                
                # Generate prediction
                self.prediction_data = self.yf_client.predict_next_day(self.current_data)
                
                return True
                
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            logger.error(f"Error in fetch_stock_data: {e}")
            return False
    
    def render_stock_info(self):
        """Render stock information section."""
        if self.stock_info is None:
            return
        
        st.markdown("### 📋 Stock Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Company**: {self.stock_info['name']}")
            st.markdown(f"**Symbol**: {self.stock_info['symbol']}")
            st.markdown(f"**Exchange**: {self.stock_info['exchange']}")
        
        with col2:
            st.markdown(f"**Sector**: {self.stock_info['sector']}")
            st.markdown(f"**Industry**: {self.stock_info['industry']}")
            st.markdown(f"**Country**: {self.stock_info['country']}")
        
        with col3:
            if self.stock_info['market_cap']:
                market_cap = self.stock_info['market_cap']
                if market_cap >= 1e12:
                    market_cap_str = f"${market_cap/1e12:.2f}T"
                elif market_cap >= 1e9:
                    market_cap_str = f"${market_cap/1e9:.2f}B"
                elif market_cap >= 1e6:
                    market_cap_str = f"${market_cap/1e6:.2f}M"
                else:
                    market_cap_str = f"${market_cap:,.0f}"
                st.markdown(f"**Market Cap**: {market_cap_str}")
            else:
                st.markdown("**Market Cap**: N/A")
            st.markdown(f"**Currency**: {self.stock_info['currency']}")
            if self.stock_info['website']:
                st.markdown(f"**Website**: [{self.stock_info['website']}]({self.stock_info['website']})")
    
    def render_price_summary(self):
        """Render the price summary section."""
        if self.live_price_data is None:
            return
        
        st.markdown("### 💰 Price Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                f"${self.live_price_data['last_price']:,.2f}" if self.live_price_data['currency'] == 'USD' else f"₹{self.live_price_data['last_price']:,.2f}",
                f"{self.live_price_data['change']:+,.2f} ({self.live_price_data['change_percent']:+.2f}%)"
            )
        
        with col2:
            st.metric(
                "Open",
                f"${self.live_price_data['open']:,.2f}" if self.live_price_data['currency'] == 'USD' else f"₹{self.live_price_data['open']:,.2f}"
            )
        
        with col3:
            st.metric(
                "High",
                f"${self.live_price_data['high']:,.2f}" if self.live_price_data['currency'] == 'USD' else f"₹{self.live_price_data['high']:,.2f}"
            )
        
        with col4:
            st.metric(
                "Low",
                f"${self.live_price_data['low']:,.2f}" if self.live_price_data['currency'] == 'USD' else f"₹{self.live_price_data['low']:,.2f}"
            )
        
        # Additional metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Previous Close",
                f"${self.live_price_data['previous_close']:,.2f}" if self.live_price_data['currency'] == 'USD' else f"₹{self.live_price_data['previous_close']:,.2f}"
            )
        
        with col2:
            st.metric(
                "Volume",
                f"{self.live_price_data['volume']:,}"
            )
        
        with col3:
            st.metric(
                "Last Updated",
                self.live_price_data['timestamp'].strftime("%H:%M:%S")
            )
    
    def render_prediction_section(self):
        """Render the prediction section."""
        if self.prediction_data is None:
            return
        
        st.markdown("### 🔮 Price Prediction")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if isinstance(self.prediction_data['prediction'], (int, float)):
                currency_symbol = "$" if self.live_price_data is not None and self.live_price_data['currency'] == 'USD' else "₹"
                st.metric(
                    "Next Day Prediction",
                    f"{currency_symbol}{self.prediction_data['prediction']:,.2f}",
                    f"{self.prediction_data['prediction'] - self.live_price_data['last_price']:+,.2f}"
                )
            else:
                st.metric("Next Day Prediction", self.prediction_data['prediction'])
        
        with col2:
            st.metric("Trend", self.prediction_data.get('trend', 'N/A'))
        
        with col3:
            confidence = self.prediction_data.get('confidence', 0)
            st.metric("Confidence", f"{confidence:.1%}")
        
        # Prediction details
        st.markdown("#### Prediction Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Method:** {self.prediction_data.get('method', 'N/A')}")
            st.info(f"**RSI Signal:** {self.prediction_data.get('rsi_signal', 'N/A')}")
            st.info(f"**MACD Signal:** {self.prediction_data.get('macd_signal', 'N/A')}")
        
        with col2:
            st.info(f"**Price vs SMA20:** {self.prediction_data.get('price_vs_sma', 'N/A')}")
            st.info(f"**Analysis:** Based on technical indicators and trend analysis")
        
        # Disclaimer
        st.warning("""
        ⚠️ **Disclaimer:** This prediction is based on technical analysis and should not be considered as financial advice. 
        Always do your own research and consult with financial professionals before making investment decisions.
        """)
    
    def render_charts(self):
        """Render the interactive charts."""
        if self.current_data is None or self.current_data.empty:
            return
        
        st.markdown("### 📊 Technical Analysis Charts")
        
        # Main candlestick chart
        st.markdown("#### Price Chart with Technical Indicators")
        candlestick_fig = ChartCreator.create_candlestick_chart(
            self.current_data, 
            st.session_state.current_symbol
        )
        st.plotly_chart(candlestick_fig, use_container_width=True)
        
        # Technical indicators chart
        st.markdown("#### Technical Indicators")
        indicators_fig = ChartCreator.create_technical_indicators_chart(
            self.current_data, 
            st.session_state.current_symbol
        )
        st.plotly_chart(indicators_fig, use_container_width=True)
        
        # Prediction chart
        if self.prediction_data is not None and isinstance(self.prediction_data.get('prediction'), (int, float)):
            st.markdown("#### Prediction Analysis")
            prediction_fig = ChartCreator.create_prediction_chart(
                self.current_data, 
                self.prediction_data, 
                st.session_state.current_symbol
            )
            st.plotly_chart(prediction_fig, use_container_width=True)
    
    def render_data_table(self):
        """Render the data table section."""
        if self.current_data is None or self.current_data.empty:
            return
        
        st.markdown("### 📋 Historical Data")
        
        # Show last 10 rows by default
        display_data = self.current_data.tail(10)
        
        # Format the data for display
        display_data_formatted = display_data.copy()
        for col in ['open', 'high', 'low', 'close', 'SMA20', 'SMA50']:
            if col in display_data_formatted.columns:
                display_data_formatted[col] = display_data_formatted[col].round(2)
        
        # Add date column back for display
        display_data_formatted = display_data_formatted.reset_index()
        if 'Date' in display_data_formatted.columns:
            display_data_formatted['Date'] = display_data_formatted['Date'].dt.strftime('%Y-%m-%d')
        elif 'date' in display_data_formatted.columns:
            display_data_formatted['date'] = display_data_formatted['date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_data_formatted,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = self.current_data.to_csv()
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"{st.session_state.current_symbol.replace('.', '_')}_data.csv",
            mime="text/csv"
        )
    
    def run(self):
        """Main application loop."""
        try:
            # Render header
            self.render_header()
            
            # Render sidebar
            self.render_sidebar()
            
            # Main content area
            if st.session_state.current_symbol:
                # Fetch data
                if self.fetch_stock_data(st.session_state.current_symbol, st.session_state.historical_days):
                    # Render stock information
                    self.render_stock_info()
                    
                    # Render price summary
                    self.render_price_summary()
                    
                    # Render prediction section
                    self.render_prediction_section()
                    
                    # Render charts
                    self.render_charts()
                    
                    # Render data table
                    self.render_data_table()
                else:
                    st.error("Failed to fetch stock data. Please check the symbol and try again.")
                    st.info("💡 **Tip**: Try using symbols like RELIANCE.NS, AAPL, MSFT, or search for your stock on Yahoo Finance.")
            else:
                st.info("Please enter a stock symbol in the sidebar to begin analysis.")
        
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            logger.error(f"Application error: {e}")

def main():
    """Main function to run the application."""
    app = StockAnalyzerApp()
    app.run()

if __name__ == "__main__":
    main() 