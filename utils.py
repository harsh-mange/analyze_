import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def generate_sample_stock_data(symbol: str = "NSE:RELIANCE", days: int = 60) -> pd.DataFrame:
    """
    Generate sample stock data for testing and development purposes.
    
    Args:
        symbol: Stock symbol
        days: Number of days of data to generate
        
    Returns:
        DataFrame with OHLCV data and technical indicators
    """
    try:
        # Generate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate base price data (starting from a realistic price)
        base_price = 2500.0  # Starting price for Reliance
        np.random.seed(42)  # For reproducible results
        
        # Generate price movements
        returns = np.random.normal(0.001, 0.02, len(date_range))  # Daily returns
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 100))  # Minimum price of 100
        
        # Create OHLCV data
        data = []
        for i, (date, close) in enumerate(zip(date_range, prices)):
            # Generate realistic OHLC from close price
            volatility = 0.02  # 2% daily volatility
            
            high = close * (1 + abs(np.random.normal(0, volatility)))
            low = close * (1 - abs(np.random.normal(0, volatility)))
            open_price = close * (1 + np.random.normal(0, volatility * 0.5))
            
            # Ensure OHLC relationship
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # Generate volume (correlated with price movement)
            base_volume = 1000000  # Base volume
            volume = int(base_volume * (1 + abs(returns[i]) * 10))
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        logger.info(f"Generated sample data for {symbol}: {len(df)} days")
        return df
        
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for the given DataFrame.
    
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
        
        return df
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        return df

def validate_stock_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Validate stock symbol format.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not symbol or not isinstance(symbol, str):
            return False, "Symbol must be a non-empty string"
        
        # Check format: EXCHANGE:SYMBOL
        if ':' not in symbol:
            return False, "Symbol must be in format: EXCHANGE:SYMBOL (e.g., NSE:RELIANCE)"
        
        exchange, trading_symbol = symbol.split(':', 1)
        
        # Validate exchange
        valid_exchanges = ['NSE', 'BSE', 'NFO', 'CDS', 'MCX']
        if exchange.upper() not in valid_exchanges:
            return False, f"Invalid exchange. Must be one of: {', '.join(valid_exchanges)}"
        
        # Validate trading symbol
        if not trading_symbol or len(trading_symbol) < 1:
            return False, "Trading symbol cannot be empty"
        
        if len(trading_symbol) > 20:
            return False, "Trading symbol too long (max 20 characters)"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        if any(char in trading_symbol for char in invalid_chars):
            return False, "Trading symbol contains invalid characters"
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Error validating symbol {symbol}: {e}")
        return False, f"Validation error: {str(e)}"

def format_currency(amount: float, currency: str = "₹") -> str:
    """
    Format currency amount with proper formatting.
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    try:
        if pd.isna(amount) or amount is None:
            return f"{currency}0.00"
        
        if amount >= 1e9:  # Billions
            return f"{currency}{amount/1e9:.2f}B"
        elif amount >= 1e6:  # Millions
            return f"{currency}{amount/1e6:.2f}M"
        elif amount >= 1e3:  # Thousands
            return f"{currency}{amount/1e3:.2f}K"
        else:
            return f"{currency}{amount:,.2f}"
            
    except Exception as e:
        logger.error(f"Error formatting currency {amount}: {e}")
        return f"{currency}0.00"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format percentage value.
    
    Args:
        value: Percentage value (0.05 for 5%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    try:
        if pd.isna(value) or value is None:
            return "0.00%"
        
        return f"{value * 100:+.{decimal_places}f}%"
        
    except Exception as e:
        logger.error(f"Error formatting percentage {value}: {e}")
        return "0.00%"

def calculate_price_change(current: float, previous: float) -> Dict[str, float]:
    """
    Calculate price change metrics.
    
    Args:
        current: Current price
        previous: Previous price
        
    Returns:
        Dictionary with change amount and percentage
    """
    try:
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return {'change': 0.0, 'change_percent': 0.0}
        
        change = current - previous
        change_percent = (change / previous) * 100
        
        return {
            'change': round(change, 2),
            'change_percent': round(change_percent, 2)
        }
        
    except Exception as e:
        logger.error(f"Error calculating price change: {e}")
        return {'change': 0.0, 'change_percent': 0.0}

def get_market_hours() -> Dict[str, str]:
    """
    Get Indian market trading hours.
    
    Returns:
        Dictionary with market hours
    """
    return {
        'pre_market': '09:00 - 09:08',
        'market_open': '09:08 - 09:15',
        'trading': '09:15 - 15:30',
        'market_close': '15:30 - 15:40',
        'post_market': '15:40 - 16:00'
    }

def is_market_open() -> bool:
    """
    Check if Indian market is currently open.
    
    Returns:
        True if market is open, False otherwise
    """
    try:
        current_time = datetime.now().time()
        market_open = datetime.strptime('09:15', '%H:%M').time()
        market_close = datetime.strptime('15:30', '%H:%M').time()
        
        return market_open <= current_time <= market_close
        
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        return False

def get_next_market_open() -> datetime:
    """
    Get the next market open time.
    
    Returns:
        Next market open datetime
    """
    try:
        current_time = datetime.now()
        market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
        
        # If market is already open today, get next day
        if current_time.time() >= datetime.strptime('09:15', '%H:%M').time():
            market_open += timedelta(days=1)
        
        # Skip weekends (Saturday = 5, Sunday = 6)
        while market_open.weekday() >= 5:
            market_open += timedelta(days=1)
        
        return market_open
        
    except Exception as e:
        logger.error(f"Error getting next market open: {e}")
        return datetime.now()

def create_summary_stats(df: pd.DataFrame) -> Dict[str, float]:
    """
    Create summary statistics for the stock data.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Dictionary with summary statistics
    """
    try:
        if df.empty:
            return {}
        
        stats = {
            'total_return': 0.0,
            'volatility': 0.0,
            'max_price': 0.0,
            'min_price': 0.0,
            'avg_volume': 0.0,
            'price_range': 0.0
        }
        
        if len(df) > 1:
            # Calculate returns
            returns = df['close'].pct_change().dropna()
            stats['total_return'] = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
            stats['volatility'] = returns.std() * np.sqrt(252) * 100  # Annualized volatility
        
        # Price statistics
        stats['max_price'] = df['high'].max()
        stats['min_price'] = df['low'].min()
        stats['price_range'] = stats['max_price'] - stats['min_price']
        stats['avg_volume'] = df['volume'].mean()
        
        # Round values
        for key in stats:
            if isinstance(stats[key], float):
                stats[key] = round(stats[key], 2)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error creating summary stats: {e}")
        return {}

def export_data_to_csv(df: pd.DataFrame, filename: str) -> bool:
    """
    Export DataFrame to CSV file.
    
    Args:
        df: DataFrame to export
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        df.to_csv(filename, index=True)
        logger.info(f"Data exported to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting data to {filename}: {e}")
        return False

def load_data_from_csv(filename: str) -> pd.DataFrame:
    """
    Load DataFrame from CSV file.
    
    Args:
        filename: Input filename
        
    Returns:
        Loaded DataFrame
    """
    try:
        df = pd.read_csv(filename, index_col=0, parse_dates=True)
        logger.info(f"Data loaded from {filename}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading data from {filename}: {e}")
        return pd.DataFrame() 