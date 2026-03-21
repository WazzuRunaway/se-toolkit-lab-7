"""Status and system information handlers."""


def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message with available commands.
    """
    return """👋 Welcome to the LMS Bot!

I can help you with:
• /help - Show all available commands
• /health - Check system status
• /labs - List available labs
• /scores <lab> - Get scores for a lab

Send me any command to get started!"""


def handle_help() -> str:
    """Handle /help command.

    Returns:
        Help message with all available commands.
    """
    return """📋 Available Commands:

🔧 System Commands:
/start - Welcome message
/help - Show this help
/health - Check backend status

📊 Data Commands:
/labs - List all available labs
/scores <lab> - Get scores for a specific lab

💬 Natural Language (Task 3):
Just type questions like:
"What labs are available?"
"Show me scores for lab-04"
"How am I doing?"

Send any command to get started!"""


def handle_health() -> str:
    """Handle /health command.

    Returns:
        System health status message.
    """
    return "✅ Bot is running and ready to help!"
