"""
Wizard Scripts — Unified Launcher

Runs both the Telegram Bot (Aiogram) and the FastAPI server concurrently.
"""

import asyncio
import logging
import sys

import uvicorn

# Import config first (no other dependencies)
from config import HOST, PORT, BOT_TOKEN

# Import FastAPI app
from api_server import app as fastapi_app

# Import bot components
import bot as bot_module

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("wizard_scripts")


async def run_api() -> None:
    """Run the FastAPI server using uvicorn."""
    config = uvicorn.Config(
        app=fastapi_app,
        host=HOST,
        port=int(PORT),
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_bot() -> None:
    """Run the Telegram bot."""
    await bot_module.main()


async def main() -> None:
    """Run both services concurrently."""
    logger.info("=" * 50)
    logger.info("Wizard Scripts — Starting Services")
    logger.info("=" * 50)

    # Validate configuration
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN not configured! Set it in Environment Variables")
        sys.exit(1)

    logger.info(f"API Server: http://{HOST}:{PORT}")
    logger.info("Telegram Bot: starting polling...")

    # Run both services
    await asyncio.gather(
        run_api(),
        run_bot(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
