"""LMS data query handlers."""


def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs. In Task 2, this will fetch from the LMS API.
    """
    return "📚 Available labs will be listed here (implemented in Task 2)"


def handle_scores(lab: str = "") -> str:
    """Handle /scores command.

    Args:
        lab: Optional lab identifier to get scores for.

    Returns:
        Scores information for the specified lab or user's overall scores.
    """
    if lab:
        return f"📊 Scores for lab '{lab}' will be shown here (implemented in Task 2)"
    return "📊 Your overall scores will be shown here (implemented in Task 2)"
