#!/usr/bin/env python3
"""
Test script for the Stock Analyzer application.
This script tests all major components without requiring API credentials.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from config import Config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Config: {e}")
        return False
    
    try:
        from utils import generate_sample_stock_data, calculate_technical_indicators
        print("✅ Utils module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Utils: {e}")
        return False
    
    try:
        from chart_utils import ChartCreator
        print("✅ Chart Utils module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Chart Utils: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Plotly: {e}")
        return False
    
    return True

def test_sample_data_generation():
    """Test sample data generation functionality."""
    print("\n🔍 Testing sample data generation...")
    
    try:
        from utils import generate_sample_stock_data
        
        # Generate sample data
        df = generate_sample_stock_data("NSE:RELIANCE", 30)
        
        if df.empty:
            print("❌ Sample data generation failed - empty DataFrame")
            return False
        
        print(f"✅ Generated sample data: {len(df)} rows")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
        
        # Check required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns present")
        
        # Check technical indicators
        indicator_columns = ['SMA20', 'SMA50', 'RSI', 'MACD']
        present_indicators = [col for col in indicator_columns if col in df.columns]
        print(f"✅ Technical indicators: {present_indicators}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data generation test failed: {e}")
        return False

def test_chart_creation():
    """Test chart creation functionality."""
    print("\n🔍 Testing chart creation...")
    
    try:
        from utils import generate_sample_stock_data
        from chart_utils import ChartCreator
        
        # Generate sample data
        df = generate_sample_stock_data("NSE:TCS", 20)
        
        if df.empty:
            print("❌ Cannot test charts - no sample data")
            return False
        
        # Test candlestick chart
        try:
            candlestick_fig = ChartCreator.create_candlestick_chart(df, "NSE:TCS")
            print("✅ Candlestick chart created successfully")
        except Exception as e:
            print(f"❌ Candlestick chart creation failed: {e}")
            return False
        
        # Test technical indicators chart
        try:
            indicators_fig = ChartCreator.create_technical_indicators_chart(df, "NSE:TCS")
            print("✅ Technical indicators chart created successfully")
        except Exception as e:
            print(f"❌ Technical indicators chart creation failed: {e}")
            return False
        
        # Test prediction chart
        try:
            prediction_data = {
                'prediction': df['close'].iloc[-1] * 1.01,
                'trend': 'Bullish',
                'confidence': 0.7
            }
            prediction_fig = ChartCreator.create_prediction_chart(df, prediction_data, "NSE:TCS")
            print("✅ Prediction chart created successfully")
        except Exception as e:
            print(f"❌ Prediction chart creation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Chart creation test failed: {e}")
        return False

def test_utility_functions():
    """Test utility functions."""
    print("\n🔍 Testing utility functions...")
    
    try:
        from utils import (
            validate_stock_symbol, format_currency, format_percentage,
            calculate_price_change, create_summary_stats
        )
        
        # Test symbol validation
        test_symbols = [
            ("NSE:RELIANCE", True),
            ("BSE:TCS", True),
            ("INVALID", False),
            ("NSE:", False),
            ("", False)
        ]
        
        for symbol, expected in test_symbols:
            is_valid, message = validate_stock_symbol(symbol)
            if is_valid == expected:
                print(f"✅ Symbol validation: {symbol} -> {is_valid}")
            else:
                print(f"❌ Symbol validation: {symbol} -> {is_valid} (expected {expected})")
                return False
        
        # Test formatting functions
        try:
            currency = format_currency(1234.56)
            percentage = format_percentage(0.05)
            print(f"✅ Formatting: {currency}, {percentage}")
        except Exception as e:
            print(f"❌ Formatting functions failed: {e}")
            return False
        
        # Test price change calculation
        try:
            change_data = calculate_price_change(110, 100)
            if change_data['change'] == 10 and change_data['change_percent'] == 10:
                print("✅ Price change calculation successful")
            else:
                print("❌ Price change calculation failed")
                return False
        except Exception as e:
            print(f"❌ Price change calculation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import Config
        
        # Test configuration attributes
        print(f"✅ Default stock symbol: {Config.DEFAULT_STOCK_SYMBOL}")
        print(f"✅ Historical days: {Config.HISTORICAL_DAYS}")
        print(f"✅ Kite login URL: {Config.KITE_LOGIN_URL}")
        
        # Test credential validation (should fail without .env file)
        try:
            Config.validate_credentials()
            print("⚠️  Credentials validation passed (credentials may be set)")
        except ValueError as e:
            print(f"✅ Credentials validation correctly failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary."""
    print("🚀 Starting Stock Analyzer Application Tests\n")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Sample Data Generation", test_sample_data_generation),
        ("Chart Creation", test_chart_creation),
        ("Utility Functions", test_utility_functions),
        ("Configuration", test_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("  • For demo mode: streamlit run demo_mode.py")
        print("  • For real data: streamlit run app.py (requires .env setup)")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 