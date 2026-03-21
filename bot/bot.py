#!/usr/bin/env python3
"""LMS Telegram Bot.

Entry point that supports both Telegram bot mode and test mode.
"""

import asyncio
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, BotCommand, DefaultBotProperties
from aiogram.enums import ParseMode

try:
    from config import settings
    CONFIG_AVAILABLE = True
except Exception:
    CONFIG_AVAILABLE = False
    settings = None

# Import handlers
try:
    from handlers.commands import handle_start, handle_help, handle_health, handle_labs, handle_scores
    HANDLERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import handlers: {e}")
    HANDLERS_AVAILABLE = False
    # Fallback if handlers not available
    def handle_start(): return "👋 Welcome! (handlers not loaded)"
    def handle_help(): return "📋 Help not available"
    def handle_health(): return "✅ System status unknown"
    def handle_labs(): return "📚 Labs not available"
    def handle_scores(lab=""): return f"📊 Scores for {lab} not available"


def parse_command(text: str) -> tuple[str, str]:
    """Parse command and arguments from text.

    Returns (command, args) where command is lowercase without /.
    """
    text = text.strip()
    if not text.startswith('/'):
        return "natural", text

    parts = text[1:].split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    return command, args


def handle_test_command(command_text: str) -> str:
    """Handle a command in test mode (no Telegram)."""
    command, args = parse_command(command_text)

    if command == "start":
        return handle_start()
    elif command == "help":
        return handle_help()
    elif command == "health":
        return handle_health()
    elif command == "labs":
        return handle_labs()
    elif command == "scores":
        return handle_scores(args)
    elif command == "natural":
        # For Task 3 - natural language processing
        return f"🤖 Natural language processing: '{args}' (implemented in Task 3)"
    else:
        return f"❓ Unknown command: /{command}. Type /help for available commands."


async def run_telegram_bot():
    """Run the Telegram bot."""
    if not settings or not settings.bot_token:
        print("❌ BOT_TOKEN not set in environment. Configure .env.bot.secret")
        return

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Register command handlers
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        """Handle /start command."""
        response = handle_start()
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        """Handle /help command."""
        response = handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: Message):
        """Handle /health command."""
        response = handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: Message):
        """Handle /labs command."""
        response = handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: Message):
        """Handle /scores command."""
        # Extract lab name from command arguments
        args = message.text.split(maxsplit=1)
        lab = args[1] if len(args) > 1 else ""
        response = handle_scores(lab)
        await message.answer(response)

    @dp.message()
    async def handle_message(message: Message):
        """Handle regular messages (for Task 3 - NLU)."""
        # For now, show help on unknown messages
        response = f"ℹ️ I don't understand that. Type /help for available commands."
        await message.answer(response)

    # Set up bot commands in Telegram
    await bot.set_my_commands([
        BotCommand(command="start", description="Welcome message"),
        BotCommand(command="help", description="Show all commands"),
        BotCommand(command="health", description="Check bot status"),
        BotCommand(command="labs", description="List available labs"),
        BotCommand(command="scores", description="Get your scores"),
    ])

    print("🤖 Telegram bot started. Listening for messages...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("❌ Usage: python bot.py --test \"/command\"")
            sys.exit(1)

        command_text = sys.argv[2]
        result = handle_test_command(command_text)
        print(result)
        sys.exit(0)

    # Telegram bot mode
    print("🤖 Starting Telegram bot...")
    try:
        asyncio.run(run_telegram_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()