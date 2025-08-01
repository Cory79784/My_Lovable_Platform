"""
Frontend Development Agent

A ReAct-based agent specialized in frontend development tasks using MCP protocol.
"""

from .agent.react_agent import FrontendReActAgent, ReActAgent
# from .agent.mcp_client import MCPManager, MCPClient  # MCP已移除，使用内置文件操作 / MCP removed, using built-in file operations
from .database.context_manager import ContextManager, get_context_manager
from .agent.frontend_prompts import FrontendPromptManager

__version__ = "1.0.0"
__author__ = "Frontend Development Agent Team"

__all__ = [
    "FrontendReActAgent",
    "ReActAgent", 
    "MCPManager",
    "MCPClient",
    "ContextManager",
    "get_context_manager",
    "FrontendPromptManager"
]