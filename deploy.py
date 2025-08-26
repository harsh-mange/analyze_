#!/usr/bin/env python3
"""
Production deployment script for Stock Analyzer application.
This script sets up the environment and runs the app with production settings.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

def create_streamlit_config():
    """Create Streamlit configuration file."""
    config_dir = Path.home() / '.streamlit'
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / 'config.toml'
    
    config_content = f"""
[server]
port = {Config.STREAMLIT_SERVER_PORT}
address = "{Config.STREAMLIT_SERVER_ADDRESS}"
headless = {str(Config.STREAMLIT_SERVER_HEADLESS).lower()}
enableCORS = {str(Config.STREAMLIT_SERVER_ENABLE_CORS).lower()}
enableXsrfProtection = {str(Config.STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION).lower()}

[browser]
gatherUsageStats = {str(Config.STREAMLIT_BROWSER_GATHER_USAGE_STATS).lower()}

[logger]
level = "{Config.LOG_LEVEL}"
"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    logger.info(f"Created Streamlit config at {config_file}")
    return config_file

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'yfinance', 
        'python-dotenv', 'requests', 'numpy', 'ta'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        logger.info("Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
        logger.info("All packages installed successfully")
    else:
        logger.info("All required packages are installed")

def run_production_app():
    """Run the production Streamlit app."""
    try:
        # Create Streamlit config
        create_streamlit_config()
        
        # Set environment variables for production
        env = os.environ.copy()
        env.update({
            'STREAMLIT_SERVER_HEADLESS': 'true',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
            'STREAMLIT_SERVER_ENABLE_CORS': 'true',
            'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'true',
        })
        
        # Run the app
        logger.info("Starting Stock Analyzer in production mode...")
        logger.info(f"Server will be available at: http://{Config.STREAMLIT_SERVER_ADDRESS}:{Config.STREAMLIT_SERVER_PORT}")
        
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', str(Config.STREAMLIT_SERVER_PORT),
            '--server.address', Config.STREAMLIT_SERVER_ADDRESS,
            '--server.headless', str(Config.STREAMLIT_SERVER_HEADLESS).lower(),
            '--browser.gatherUsageStats', str(Config.STREAMLIT_BROWSER_GATHER_USAGE_STATS).lower(),
            '--server.enableCORS', str(Config.STREAMLIT_SERVER_ENABLE_CORS).lower(),
            '--server.enableXsrfProtection', str(Config.STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION).lower(),
        ], env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)

def main():
    """Main deployment function."""
    logger.info("Stock Analyzer Production Deployment")
    logger.info("=" * 40)
    
    # Check dependencies
    check_dependencies()
    
    # Run the production app
    run_production_app()

if __name__ == "__main__":
    main()
