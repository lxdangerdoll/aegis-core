#!/usr/bin/env python3
"""
WhisperEngine Bot Launcher - Infrastructure Setup
This launcher handles environment loading and logging configuration before delegating to the bot logic.
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load appropriate environment configuration
from env_manager import load_environment

if not load_environment():  # Auto-detects development vs production mode
    sys.exit(1)

# Configure logging using the proper logging configuration
from src.utils.logging_config import setup_logging

debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
# Check both ENVIRONMENT and ENV_MODE for compatibility
environment = os.getenv("ENVIRONMENT") or os.getenv("ENV_MODE", "development")
log_dir = os.getenv("LOG_DIR", "logs")
app_name = os.getenv("LOG_APP_NAME", "discord_bot")

setup_logging(debug=debug_mode, environment=environment, log_dir=log_dir, app_name=app_name)

# Import and run the main function (logging is now configured)
import asyncio
import logging
from src.main import main as bot_async_main  # Import the real async entry point

logger = logging.getLogger(__name__)


async def launcher_main():
    """Launcher entry point with automatic database initialization."""
    # Auto-migrate database before starting bot
    try:
        from src.utils.auto_migrate import DatabaseMigrator
        
        logger.info("🔧 Checking database initialization...")
        migrator = DatabaseMigrator()
        
        # Wait for PostgreSQL to be available
        if not await migrator.wait_for_database():
            logger.error("❌ Failed to connect to PostgreSQL. Exiting.")
            return 1
        
        # Check if database needs initialization
        if not await migrator.database_exists():
            logger.info("🔧 Database not initialized. Running migrations...")
            success = await migrator.run_migrations()
            if success:
                logger.info("✅ Database initialization complete!")
            else:
                logger.error("❌ Database initialization failed. Exiting.")
                return 1
        else:
            logger.info("✅ Database already initialized. Checking for pending migrations...")
            # Run migrations in case there are new ones
            await migrator.run_migrations()
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        logger.info("⚠️ Continuing bot startup despite database initialization error...")
    
    # Delegate to the bot's async main
    return await bot_async_main()


def main():  # Keep a sync facade if other tooling imports run:main
    try:
        return asyncio.run(launcher_main())
    except KeyboardInterrupt:
        # If Ctrl+C occurs before internal graceful shutdown handlers are registered
        print("\n🛑 Shutdown requested (Ctrl+C). Attempting graceful cleanup...")
        return 130  # Conventional exit code for SIGINT


if __name__ == "__main__":
    sys.exit(main())
