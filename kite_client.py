import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from typing import Dict, List, Optional, Tuple
import logging
from datetime import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KiteClient:
    """Wrapper class for Zerodha Kite Connect API operations."""
    
    def __init__(self, api_key: str, access_token: str):
        """Initialize Kite Connect client."""
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self._instruments_cache = None
        self._last_cache_update = None
    
    def get_instruments(self, force_refresh: bool = False) -> pd.DataFrame:
        """Get all instruments with caching for performance."""
        current_time = datetime.now()
        
        # Refresh cache if forced or older than 1 hour
        if (force_refresh or 
            self._instruments_cache is None or 
            self._last_cache_update is None or
            (current_time - self._last_cache_update).seconds > 3600):
            
            try:
                logger.info("Fetching instruments from Kite Connect...")
                instruments = self.kite.instruments()
                self._instruments_cache = pd.DataFrame(instruments)
                self._last_cache_update = current_time
                logger.info(f"Fetched {len(instruments)} instruments")
            except Exception as e:
                logger.error(f"Error fetching instruments: {e}")
                if self._instruments_cache is None:
                    raise
                # Use cached data if available
        
        return self._instruments_cache
    
    def get_instrument_token(self, symbol: str) -> Optional[int]:
        """Get instrument token for a given symbol."""
        try:
            instruments_df = self.get_instruments()
            
            # Handle different symbol formats
            if ':' in symbol:
                exchange, trading_symbol = symbol.split(':', 1)
            else:
                exchange = 'NSE'
                trading_symbol = symbol
            
            # Search for the instrument
            instrument = instruments_df[
                (instruments_df['exchange'] == exchange) & 
                (instruments_df['tradingsymbol'] == trading_symbol)
            ]
            
            if instrument.empty:
                logger.warning(f"Instrument not found for symbol: {symbol}")
                return None
            
            token = instrument.iloc[0]['instrument_token']
            logger.info(f"Found token {token} for symbol {symbol}")
            return token
            
        except Exception as e:
            logger.error(f"Error getting instrument token for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, days: int = 60) -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data for a symbol."""
        try:
            token = self.get_instrument_token(symbol)
            if token is None:
                return None
            
            # Calculate date range
            to_date = datetime.now().date()
            from_date = to_date - timedelta(days=days)
            
            logger.info(f"Fetching historical data for {symbol} from {from_date} to {to_date}")
            
            # Fetch historical data
            historical_data = self.kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval='day'
            )
            
            if not historical_data:
                logger.warning(f"No historical data found for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Ensure all required columns are present
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return None
            
            # Calculate technical indicators
            df = self._calculate_technical_indicators(df)
            
            logger.info(f"Successfully fetched {len(df)} days of data for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the data."""
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
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """Get live price data for a symbol."""
        try:
            token = self.get_instrument_token(symbol)
            if token is None:
                return None
            
            # Get LTP (Last Traded Price)
            ltp_data = self.kite.ltp(f"NSE:{symbol.split(':')[-1]}")
            
            if not ltp_data:
                logger.warning(f"No LTP data found for {symbol}")
                return None
            
            # Extract the relevant data
            symbol_key = list(ltp_data.keys())[0]
            price_data = ltp_data[symbol_key]
            
            live_data = {
                'symbol': symbol,
                'last_price': price_data.get('last_price', 0),
                'change': price_data.get('change', 0),
                'change_percent': price_data.get('change_percent', 0),
                'volume': price_data.get('volume', 0),
                'high': price_data.get('high', 0),
                'low': price_data.get('low', 0),
                'open': price_data.get('open', 0),
                'previous_close': price_data.get('previous_close', 0),
                'timestamp': datetime.now()
            }
            
            logger.info(f"Live price for {symbol}: {live_data['last_price']}")
            return live_data
            
        except Exception as e:
            logger.error(f"Error fetching live price for {symbol}: {e}")
            return None
    
    def get_market_status(self) -> Dict:
        """Get current market status."""
        try:
            # This is a simplified market status check
            # In a real implementation, you might want to check actual market hours
            current_time = datetime.now().time()
            market_open = time(9, 15)  # 9:15 AM
            market_close = time(15, 30)  # 3:30 PM
            
            is_market_open = market_open <= current_time <= market_close
            
            return {
                'is_open': is_market_open,
                'current_time': current_time.strftime('%H:%M:%S'),
                'market_open': market_open.strftime('%H:%M'),
                'market_close': market_close.strftime('%H:%M')
            }
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {'is_open': False, 'error': str(e)}
    
    def predict_next_day(self, df: pd.DataFrame) -> Dict:
        """Simple prediction using technical indicators."""
        try:
            if df.empty or len(df) < 20:
                return {'prediction': 'Insufficient data', 'confidence': 0}
            
            # Get latest values
            latest_close = df['close'].iloc[-1]
            latest_sma20 = df['SMA20'].iloc[-1]
            latest_sma50 = df['SMA50'].iloc[-1]
            latest_rsi = df['RSI'].iloc[-1]
            
            # Simple trend analysis
            trend = 'Bullish' if latest_sma20 > latest_sma50 else 'Bearish'
            
            # RSI analysis
            rsi_signal = 'Oversold' if latest_rsi < 30 else 'Overbought' if latest_rsi > 70 else 'Neutral'
            
            # Price vs SMA20
            price_vs_sma = 'Above' if latest_close > latest_sma20 else 'Below'
            
            # Simple prediction (placeholder for ML models)
            if trend == 'Bullish' and price_vs_sma == 'Above':
                prediction = latest_close * 1.01  # 1% increase
                confidence = 0.7
            elif trend == 'Bearish' and price_vs_sma == 'Below':
                prediction = latest_close * 0.99  # 1% decrease
                confidence = 0.7
            else:
                prediction = latest_close
                confidence = 0.5
            
            return {
                'prediction': round(prediction, 2),
                'trend': trend,
                'rsi_signal': rsi_signal,
                'price_vs_sma': price_vs_sma,
                'confidence': confidence,
                'method': 'Technical Analysis (SMA + RSI)'
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {'prediction': 'Error in prediction', 'confidence': 0} 