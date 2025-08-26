#!/usr/bin/env python3
"""
Production startup script for Stock Analyzer application.
This script runs the app with production-optimized settings.
"""

import os
import sys
import subprocess
import logging
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

def start_production_app():
    """Start the production Streamlit app with optimized settings."""
    try:
        # Set production environment variables
        env = os.environ.copy()
        env.update({
            'STREAMLIT_SERVER_HEADLESS': 'true',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
            'STREAMLIT_SERVER_ENABLE_CORS': 'true',
            'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'true',
            'STREAMLIT_LOGGER_LEVEL': Config.LOG_LEVEL,
        })
        
        logger.info("🚀 Starting Stock Analyzer in PRODUCTION mode...")
        logger.info(f"📍 Server Address: {Config.STREAMLIT_SERVER_ADDRESS}")
        logger.info(f"🔌 Server Port: {Config.STREAMLIT_SERVER_PORT}")
        logger.info(f"🌐 Access URL: http://{Config.STREAMLIT_SERVER_ADDRESS}:{Config.STREAMLIT_SERVER_PORT}")
        logger.info("=" * 60)
        
        # Run Streamlit with production settings
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', str(Config.STREAMLIT_SERVER_PORT),
            '--server.address', Config.STREAMLIT_SERVER_ADDRESS,
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--server.enableCORS', 'true',
            '--server.enableXsrfProtection', 'true',
            '--logger.level', Config.LOG_LEVEL,
        ]
        
        subprocess.run(cmd, env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_production_app()
