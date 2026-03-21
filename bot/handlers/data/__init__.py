"""Data handlers for LMS information queries.

These handlers are plain functions separated from the Telegram transport layer.
They handle data retrieval commands like /labs and /scores.
"""

from .lms_queries import handle_labs, handle_scores

__all__ = ["handle_labs", "handle_scores"]
