import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """Client for fetching stock data using Yahoo Finance API."""
    
    def __init__(self):
        """Initialize the Yahoo Finance client with custom session."""
        self._cache = {}
        self._cache_timeout = 300
        
        # Create custom session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set custom headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _get_symbol_mapping(self, symbol: str) -> str:
        """
        Convert user-friendly symbols to Yahoo Finance symbols.
        
        Args:
            symbol: User input symbol (e.g., "NSE:RELIANCE", "RELIANCE.NS")
            
        Returns:
            Yahoo Finance compatible symbol
        """
        try:
            # Handle different symbol formats
            if ':' in symbol:
                exchange, ticker = symbol.split(':', 1)
                exchange = exchange.upper()
                
                # Map exchanges to Yahoo Finance suffixes
                exchange_mapping = {
                    'NSE': '.NS',  # National Stock Exchange (India)
                    'BSE': '.BO',  # Bombay Stock Exchange (India)
                    'NYSE': '',    # New York Stock Exchange (US)
                    'NASDAQ': '',  # NASDAQ (US)
                    'LSE': '.L',   # London Stock Exchange (UK)
                    'TSE': '.T',   # Tokyo Stock Exchange (Japan)
                    'ASX': '.AX',  # Australian Securities Exchange
                }
                
                suffix = exchange_mapping.get(exchange, '.NS')  # Default to NSE
                return f"{ticker}{suffix}"
            
            # If no exchange specified, assume NSE for Indian stocks
            elif not any(symbol.endswith(ext) for ext in ['.NS', '.BO', '.L', '.T', '.AX']):
                return f"{symbol}.NS"
            
            return symbol
            
        except Exception as e:
            logger.error(f"Error mapping symbol {symbol}: {e}")
            return symbol
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get basic stock information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock information
        """
        try:
            yf_symbol = self._get_symbol_mapping(symbol)
            ticker = yf.Ticker(yf_symbol)
            
            info = ticker.info
            
            stock_info = {
                'symbol': symbol,
                'yf_symbol': yf_symbol,
                'name': info.get('longName', info.get('shortName', 'Unknown')),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'INR'),
                'exchange': info.get('exchange', 'NSE'),
                'country': info.get('country', 'India'),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', '')
            }
            
            logger.info(f"Retrieved stock info for {symbol}")
            return stock_info
            
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, days: int = 60, interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data with retry logic."""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                yf_symbol = self._get_symbol_mapping(symbol)
                
                # Add random delay to avoid rate limiting
                time.sleep(random.uniform(0.5, 2.0))
                
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                logger.info(f"Fetching {days} days of data for {symbol} ({yf_symbol}) - Attempt {attempt + 1}")
                
                # Fetch data from Yahoo Finance
                ticker = yf.Ticker(yf_symbol)
                df = ticker.history(start=start_date, end=end_date, interval=interval)
                
                if df.empty:
                    logger.warning(f"No data found for {symbol}")
                    return None
                
                # Rename columns to match our standard format
                df.columns = [col.lower() for col in df.columns]
                
                # Ensure we have the required columns
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_columns):
                    logger.error(f"Missing required columns for {symbol}")
                    return None
                
                # Calculate technical indicators
                df = self._calculate_technical_indicators(df)
                
                logger.info(f"Successfully fetched {len(df)} days of data for {symbol}")
                return df
                
            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol} (Attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts")
                    return None
        
        return None
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """
        Get live/current price data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with current price data
        """
        try:
            yf_symbol = self._get_symbol_mapping(symbol)
            ticker = yf.Ticker(yf_symbol)
            
            # Get current info
            info = ticker.info
            
            # Get recent data for price calculations
            recent_data = ticker.history(period="2d")
            
            if recent_data.empty:
                logger.warning(f"No recent data found for {symbol}")
                return None
            
            # Get the correct column names (yfinance returns capitalized column names)
            close_col = 'Close' if 'Close' in recent_data.columns else 'close'
            volume_col = 'Volume' if 'Volume' in recent_data.columns else 'volume'
            high_col = 'High' if 'High' in recent_data.columns else 'high'
            low_col = 'Low' if 'Low' in recent_data.columns else 'low'
            open_col = 'Open' if 'Open' in recent_data.columns else 'open'
            
            current_price = recent_data[close_col].iloc[-1]
            previous_close = recent_data[close_col].iloc[-2] if len(recent_data) > 1 else current_price
            
            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            live_data = {
                'symbol': symbol,
                'yf_symbol': yf_symbol,
                'last_price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(recent_data[volume_col].iloc[-1]) if volume_col in recent_data.columns else 0,
                'high': round(recent_data[high_col].iloc[-1], 2) if high_col in recent_data.columns else current_price,
                'low': round(recent_data[low_col].iloc[-1], 2) if low_col in recent_data.columns else current_price,
                'open': round(recent_data[open_col].iloc[-1], 2) if open_col in recent_data.columns else current_price,
                'previous_close': round(previous_close, 2),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'INR'),
                'timestamp': datetime.now()
            }
            
            logger.info(f"Live price for {symbol}: {live_data['last_price']}")
            return live_data
            
        except Exception as e:
            logger.error(f"Error fetching live price for {symbol}: {e}")
            return None
    
    def get_market_status(self) -> Dict:
        """
        Get current market status.
        
        Returns:
            Dictionary with market status information
        """
        try:
            # Get current time in IST (UTC+5:30)
            current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
            
            # Indian market hours (9:15 AM - 3:30 PM IST)
            market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
            
            # Check if market is open
            is_market_open = market_open <= current_time <= market_close
            
            # Check if it's a weekday
            is_weekday = current_time.weekday() < 5  # Monday = 0, Friday = 4
            
            market_status = {
                'is_open': is_market_open and is_weekday,
                'current_time': current_time.strftime('%H:%M:%S'),
                'current_date': current_time.strftime('%Y-%m-%d'),
                'market_open': market_open.strftime('%H:%M'),
                'market_close': market_close.strftime('%H:%M'),
                'is_weekday': is_weekday,
                'timezone': 'IST (UTC+5:30)'
            }
            
            return market_status
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {'is_open': False, 'error': str(e)}
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for stocks based on a query.
        
        Args:
            query: Search query (company name, symbol, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching stocks
        """
        try:
            # Use yfinance's search functionality
            search_results = yf.Tickers(query)
            
            stocks = []
            for ticker in list(search_results.tickers)[:limit]:
                try:
                    info = ticker.info
                    stock = {
                        'symbol': ticker.ticker,
                        'name': info.get('longName', info.get('shortName', ticker.ticker)),
                        'exchange': info.get('exchange', 'Unknown'),
                        'country': info.get('country', 'Unknown'),
                        'sector': info.get('sector', 'Unknown')
                    }
                    stocks.append(stock)
                except:
                    continue
            
            logger.info(f"Found {len(stocks)} stocks matching '{query}'")
            return stocks
            
        except Exception as e:
            logger.error(f"Error searching stocks for '{query}': {e}")
            return []
    
    def get_popular_stocks(self) -> List[Dict]:
        """
        Get a list of popular stocks for easy selection.
        
        Returns:
            List of popular stocks
        """
        popular_stocks = [
            {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries', 'exchange': 'NSE'},
            {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services', 'exchange': 'NSE'},
            {'symbol': 'INFY.NS', 'name': 'Infosys', 'exchange': 'NSE'},
            {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'exchange': 'NSE'},
            {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank', 'exchange': 'NSE'},
            {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever', 'exchange': 'NSE'},
            {'symbol': 'ITC.NS', 'name': 'ITC', 'exchange': 'NSE'},
            {'symbol': 'SBIN.NS', 'name': 'State Bank of India', 'exchange': 'NSE'},
            {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel', 'exchange': 'NSE'},
            {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank', 'exchange': 'NSE'},
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'exchange': 'NASDAQ'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ'}
        ]
        
        return popular_stocks
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the data.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added technical indicators
        """
        try:
            # Simple Moving Averages
            df['SMA20'] = df['close'].rolling(window=20).mean()
            df['SMA50'] = df['close'].rolling(window=50).mean()
            
            # Exponential Moving Averages
            df['EMA12'] = df['close'].ewm(span=12).mean()
            df['EMA26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            df['MACD'] = df['EMA12'] - df['EMA26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_Middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            df['Volume_SMA'] = df['volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['volume'] / df['Volume_SMA']
            
            # Additional indicators
            df['ATR'] = self._calculate_atr(df)
            df['Stochastic_K'] = self._calculate_stochastic(df)
            df['Williams_R'] = self._calculate_williams_r(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            return atr
        except:
            return pd.Series(index=df.index)
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.Series:
        """Calculate Stochastic Oscillator %K."""
        try:
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            
            k = 100 * ((df['close'] - low_min) / (high_max - low_min))
            return k
        except:
            return pd.Series(index=df.index)
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Williams %R."""
        try:
            high_max = df['high'].rolling(window=period).max()
            low_min = df['low'].rolling(window=period).min()
            
            wr = -100 * ((high_max - df['close']) / (high_max - low_min))
            return wr
        except:
            return pd.Series(index=df.index)
    
    def predict_next_day(self, df: pd.DataFrame) -> Dict:
        """
        Simple prediction using technical indicators.
        
        Args:
            df: DataFrame with technical indicators
            
        Returns:
            Dictionary with prediction data
        """
        try:
            if df.empty or len(df) < 20:
                return {'prediction': 'Insufficient data', 'confidence': 0}
            
            # Get latest values
            latest_close = df['close'].iloc[-1]
            latest_sma20 = df['SMA20'].iloc[-1]
            latest_sma50 = df['SMA50'].iloc[-1]
            latest_rsi = df['RSI'].iloc[-1]
            latest_macd = df['MACD'].iloc[-1]
            latest_macd_signal = df['MACD_Signal'].iloc[-1]
            
            # Simple trend analysis
            trend = 'Bullish' if latest_sma20 > latest_sma50 else 'Bearish'
            
            # RSI analysis
            rsi_signal = 'Oversold' if latest_rsi < 30 else 'Overbought' if latest_rsi > 70 else 'Neutral'
            
            # MACD analysis
            macd_signal = 'Bullish' if latest_macd > latest_macd_signal else 'Bearish'
            
            # Price vs SMA20
            price_vs_sma = 'Above' if latest_close > latest_sma20 else 'Below'
            
            # Simple prediction (placeholder for ML models)
            confidence = 0.5  # Base confidence
            
            if trend == 'Bullish' and price_vs_sma == 'Above' and macd_signal == 'Bullish':
                prediction = latest_close * 1.01  # 1% increase
                confidence = 0.7
            elif trend == 'Bearish' and price_vs_sma == 'Below' and macd_signal == 'Bearish':
                prediction = latest_close * 0.99  # 1% decrease
                confidence = 0.7
            elif rsi_signal == 'Oversold':
                prediction = latest_close * 1.005  # 0.5% increase
                confidence = 0.6
            elif rsi_signal == 'Overbought':
                prediction = latest_close * 0.995  # 0.5% decrease
                confidence = 0.6
            else:
                prediction = latest_close
                confidence = 0.5
            
            return {
                'prediction': round(prediction, 2),
                'trend': trend,
                'rsi_signal': rsi_signal,
                'macd_signal': macd_signal,
                'price_vs_sma': price_vs_sma,
                'confidence': confidence,
                'method': 'Technical Analysis (SMA + RSI + MACD)'
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {'prediction': 'Error in prediction', 'confidence': 0}
