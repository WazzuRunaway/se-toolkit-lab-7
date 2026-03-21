"""Command handlers for the LMS bot.

These handlers are testable without Telegram - they just take input and return text.
Handlers are organized by functionality:
- system/: System commands (/start, /help, /health)
- data/: Data query commands (/labs, /scores)
"""

# Import from nested handler modules (new structure)
from .system import handle_start, handle_help, handle_health
from .data import handle_labs, handle_scores

# Keep legacy commands.py imports for backward compatibility
from .commands import handle_start as _handle_start, handle_help as _handle_help, \
    handle_health as _handle_health, handle_labs as _handle_labs, handle_scores as _handle_scores

__all__ = ["handle_start", "handle_help", "handle_health", "handle_labs", "handle_scores"]