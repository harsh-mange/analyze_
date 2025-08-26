#!/usr/bin/env python3
"""
Startup script for the Stock Analyzer Demo Mode.
This script provides an easy way to launch the demo application.
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import pandas
        import plotly
        import numpy
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def start_demo():
    """Start the demo application."""
    print("🚀 Starting Stock Analyzer Demo Mode...")
    print("📊 This will open a web browser with the demo application")
    print("⏳ Please wait...")
    
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        demo_file = os.path.join(script_dir, "demo_mode.py")
        
        # Check if demo file exists
        if not os.path.exists(demo_file):
            print(f"❌ Demo file not found: {demo_file}")
            return False
        
        # Start Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", demo_file]
        
        print(f"🔧 Running: {' '.join(cmd)}")
        subprocess.run(cmd)
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting demo: {e}")
        return False

def main():
    """Main function."""
    print("📈 Stock Analyzer & Predictor - Demo Mode")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    print("✅ Dependencies check passed")
    print("\n🎯 Starting demo application...")
    print("💡 The application will open in your default web browser")
    print("🔄 To stop the demo, press Ctrl+C in this terminal")
    print("-" * 50)
    
    # Start demo
    return start_demo()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Failed to start demo. Please check the errors above.")
        input("Press Enter to exit...")
        sys.exit(1) 