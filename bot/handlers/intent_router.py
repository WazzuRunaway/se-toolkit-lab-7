"""Intent-based natural language routing using LLM tool calling."""

import httpx
import json
import sys
from pathlib import Path
from typing import Optional, Any

# Add bot directory to path for proper config loading
bot_dir = Path(__file__).parent.parent
sys.path.insert(0, str(bot_dir))

# Import settings from bot.config
from config import settings

# Import LMS client functions
from handlers.data.lms_queries import get_lms_client, LMSClient


# =============================================================================
# Tool Definitions - 9 backend endpoints as LLM-callable tools
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks in the system. Use this to discover what labs are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups. Use this to find information about students.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab. Use this to see how scores are distributed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab. Use this to see pass rates for tasks within a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab. Use this to see activity over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab. Use this to compare group performance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab. Use this to find the best performing students.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, e.g. 5, 10",
                        "default": 5,
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab. Use this to see how many students completed the lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker. Use this when data seems outdated.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that can fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. Analyze what information they need
2. Call the appropriate tool(s) to get that information
3. If you need to compare multiple labs, call the tool for each lab
4. Once you have the data, provide a clear, helpful answer

For greetings like "hello" or "hi", respond warmly and mention what you can help with.
For unclear messages, politely ask for clarification and suggest what you can do.

Always be helpful and provide specific data when available. If you can't find information, explain why."""


# =============================================================================
# LLM Client
# =============================================================================

class LLMClient:
    """Client for LLM API communication with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        max_tokens: int = 1000,
    ) -> dict:
        """Send chat request to LLM with optional tool definitions.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
            max_tokens: Maximum tokens in response

        Returns:
            Response dict with 'content' and optionally 'tool_calls'
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {})
        except httpx.ConnectError as e:
            return {"content": f"LLM connection error: {str(e)}"}
        except httpx.TimeoutException:
            return {"content": "LLM request timed out. Please try again."}
        except httpx.HTTPStatusError as e:
            return {"content": f"LLM HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"content": f"LLM error: {str(e)}"}


def get_llm_client() -> LLMClient:
    """Create LLM client from settings."""
    return LLMClient(
        base_url=settings.llm_api_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_api_model,
    )


# =============================================================================
# Tool Execution
# =============================================================================

class ToolExecutor:
    """Executes LMS API tools based on tool calls from LLM."""

    def __init__(self):
        self.lms_client = get_lms_client()

    def execute(self, tool_name: str, arguments: dict) -> Any:
        """Execute a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Dict of arguments for the tool

        Returns:
            Tool execution result (usually a dict or list)
        """
        tool_methods = {
            "get_items": self._get_items,
            "get_learners": self._get_learners,
            "get_scores": self._get_scores,
            "get_pass_rates": self._get_pass_rates,
            "get_timeline": self._get_timeline,
            "get_groups": self._get_groups,
            "get_top_learners": self._get_top_learners,
            "get_completion_rate": self._get_completion_rate,
            "trigger_sync": self._trigger_sync,
        }

        method = tool_methods.get(tool_name)
        if not method:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            return method(**arguments)
        except Exception as e:
            return {"error": str(e)}

    def _get_items(self) -> dict:
        """Get all items (labs and tasks)."""
        data, error = self.lms_client._get("/items/")
        if error:
            return {"error": error}
        return {"items": data, "count": len(data) if isinstance(data, list) else len(data.get("items", []))}

    def _get_learners(self) -> dict:
        """Get all learners."""
        data, error = self.lms_client._get("/learners/")
        if error:
            return {"error": error}
        return {"learners": data, "count": len(data) if isinstance(data, list) else len(data.get("learners", []))}

    def _get_scores(self, lab: str) -> dict:
        """Get score distribution for a lab."""
        data, error = self.lms_client._get(f"/analytics/scores?lab={lab}")
        if error:
            return {"error": error}
        return {"scores": data, "lab": lab}

    def _get_pass_rates(self, lab: str) -> dict:
        """Get pass rates for a lab."""
        data, error = self.lms_client._get(f"/analytics/pass-rates?lab={lab}")
        if error:
            return {"error": error}
        return {"pass_rates": data, "lab": lab}

    def _get_timeline(self, lab: str) -> dict:
        """Get timeline for a lab."""
        data, error = self.lms_client._get(f"/analytics/timeline?lab={lab}")
        if error:
            return {"error": error}
        return {"timeline": data, "lab": lab}

    def _get_groups(self, lab: str) -> dict:
        """Get group performance for a lab."""
        data, error = self.lms_client._get(f"/analytics/groups?lab={lab}")
        if error:
            return {"error": error}
        return {"groups": data, "lab": lab}

    def _get_top_learners(self, lab: str, limit: int = 5) -> dict:
        """Get top learners for a lab."""
        data, error = self.lms_client._get(f"/analytics/top-learners?lab={lab}&limit={limit}")
        if error:
            return {"error": error}
        return {"top_learners": data, "lab": lab, "limit": limit}

    def _get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab."""
        data, error = self.lms_client._get(f"/analytics/completion-rate?lab={lab}")
        if error:
            return {"error": error}
        return {"completion_rate": data, "lab": lab}

    def _trigger_sync(self) -> dict:
        """Trigger ETL sync."""
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.lms_client.base_url}/pipeline/sync",
                    headers=self.lms_client.headers,
                    json={},
                    timeout=30.0,
                )
                response.raise_for_status()
                return {"result": response.json()}
        except Exception as e:
            return {"error": str(e)}


def get_tool_executor() -> ToolExecutor:
    """Create tool executor."""
    return ToolExecutor()


# =============================================================================
# Intent Router
# =============================================================================

def route_natural_language(message: str, debug: bool = False) -> str:
    """Route a natural language message using LLM tool calling.

    Args:
        message: User's natural language message
        debug: If True, print debug info to stderr

    Returns:
        Formatted response string
    """
    def log(msg: str):
        if debug:
            print(msg, file=sys.stderr)

    llm = get_llm_client()
    executor = get_tool_executor()

    # Initial conversation messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    # Tool calling loop - max iterations to prevent infinite loops
    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call LLM
        log(f"[llm] Calling LLM (iteration {iteration})...")
        response = llm.chat(messages, tools=TOOL_DEFINITIONS)
        log(f"[llm] Response: {response.get('content', 'None')[:100] if response.get('content') else 'None'}")

        # Check for tool calls
        tool_calls = response.get("tool_calls", [])

        if not tool_calls:
            # No tool calls - LLM provided final answer
            content = response.get("content", "I'm not sure how to help with that. Try asking about labs, scores, or students.")
            log(f"[final] LLM provided final answer: {content[:100]}...")
            return content

        # Execute tool calls
        log(f"[tool] LLM called {len(tool_calls)} tool(s)")

        # Add assistant's message with tool calls to conversation
        messages.append({
            "role": "assistant",
            "content": response.get("content"),
            "tool_calls": tool_calls,
        })

        # Execute each tool and collect results
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name", "unknown")
            try:
                arguments = json.loads(function.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}

            log(f"[tool] Executing: {tool_name}({arguments})")
            result = executor.execute(tool_name, arguments)
            log(f"[tool] Result: {str(result)[:200]}...")

            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", "unknown"),
                "content": json.dumps(result, default=str) if not isinstance(result, str) else result,
            })

        log(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

    # Max iterations reached
    log("[error] Max iterations reached")
    return "I'm having trouble processing your request. Please try rephrasing your question."


# =============================================================================
# Inline Keyboard Helpers
# =============================================================================

def get_quick_actions_keyboard() -> list[list[dict]]:
    """Generate inline keyboard with quick action buttons.

    Returns:
        List of button rows for Telegram InlineKeyboardMarkup
    """
    return [
        [
            {"text": "📚 Available Labs", "callback_data": "action_labs"},
            {"text": "📊 My Scores", "callback_data": "action_scores"},
        ],
        [
            {"text": "🏆 Top Students", "callback_data": "action_top"},
            {"text": "📈 Lab Stats", "callback_data": "action_stats"},
        ],
        [
            {"text": "❓ Help", "callback_data": "action_help"},
        ],
    ]


def format_welcome_with_keyboard() -> tuple[str, list[list[dict]]]:
    """Format welcome message with inline keyboard.

    Returns:
        Tuple of (message_text, keyboard_layout)
    """
    message = """👋 Welcome to the LMS Assistant!

I can help you with:
• Viewing available labs
• Checking your scores and pass rates
• Finding top students
• Comparing group performance

You can ask me questions like:
• "What labs are available?"
• "Show me scores for lab 4"
• "Which lab has the lowest pass rate?"
• "Who are the top 5 students?"

Or use the buttons below!"""

    return message, get_quick_actions_keyboard()
