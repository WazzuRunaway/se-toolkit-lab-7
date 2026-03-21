"""System handlers for bot status and health checks.

These handlers are plain functions separated from the Telegram transport layer.
They handle system-level commands like /start, /help, and /health.
"""

from .status import handle_start, handle_help, handle_health

__all__ = ["handle_start", "handle_help", "handle_health"]
