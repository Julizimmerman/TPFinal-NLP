"""Just forward to the package CLI for convenience."""
from bot.cli import chat
import asyncio

if __name__ == "__main__":
    asyncio.run(chat())
