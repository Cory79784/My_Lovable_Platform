# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Frontend Development Agent that implements a ReAct (Reasoning and Acting) pattern for frontend development tasks. It uses built-in Python functions for file operations and development tools, designed to help with HTML, CSS, JavaScript, and modern frontend framework development.

## Architecture

The project follows a modular architecture with these key components:

1. **ReAct Agent** (`agent/react_agent.py`) - Core reasoning and action loop implementation with built-in tools
2. **File Operations** (`agent/file_operations.py`) - Built-in file system operations replacing MCP dependencies
3. **Context Manager** (`database/context_manager.py`) - Handles conversation history and persistence
4. **Frontend Prompts** (`agent/frontend_prompts.py`) - Specialized prompts for frontend tasks
5. **Database Layer** (`database/models.py`) - SQLite models for session storage

## Common Development Commands

### Running the Agent

**Entry Point: `run.py` (推荐)**
```bash
# 交互模式
python run.py --interactive

# 执行单个任务
python run.py --task "Create a responsive navigation bar"

# 继续上次对话
python run.py --continue-session --interactive

# 恢复特定session
python run.py --resume "Button Creation" --interactive
python run.py -r "abc123" --task "Add hover effects"

# 启用详细日志
python run.py --interactive --log-level DEBUG
```

**文件说明：**
- `run.py` - **主入口**，推荐使用（自动处理Python路径）
- `main.py` - 核心程序逻辑（不要直接运行，会有import问题）
- `start.py` - 健康检查脚本（仅用于测试MCP服务器状态）

### Installation and Setup

```bash
# Quick installation (Linux/macOS)
./install.sh

# Quick installation (Windows)
install.bat

# Manual installation
pip install -r requirements.txt
# Note: All file operations are now built-in Python functions
# No external MCP servers needed

# Create and configure .env file
cp .env.template .env
# Then edit .env to add your OPENAI_API_KEY
```

### Health Checks and Testing

```bash
# Quick startup test with built-in tools
python run.py --task "Test built-in tools: list directory and check system"

# Run in interactive mode
python run.py --interactive

# Debug mode with detailed logging
python run.py --log-level DEBUG --interactive
```

### Development Tools

```bash
# Install development dependencies (currently commented out in requirements_fixed.txt)
pip install pytest>=7.1.0 pytest-asyncio>=0.21.0 black>=22.0.0

# Format code with Black
black .

# Run tests (when available)
pytest
```

## Key Configuration Files

- **`.env`** - Environment variables (API keys, model settings)
  - Must contain: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`
  
- **`prompts/`** - Frontend development guidance prompts
  - Contains specialized prompts for different aspects of frontend development
  - Includes design system, component structure, and responsive design guidance

## Session Management

The agent now supports session management for conversation continuity:

### Session Features
- **Auto-naming**: New sessions are automatically named by AI based on the task
- **Session persistence**: All conversations and context are stored in SQLite database  
- **Session resume**: Continue previous conversations seamlessly
- **Session search**: Find sessions by name or ID

### Session Commands
```bash
# Continue the most recent session
python run.py --continue-session

# Resume a specific session by name (partial match supported)
python run.py --resume "Button Creation"

# Resume by session ID (full or partial)
python run.py -r "abc123def"

# List recent sessions (shows in error message if session not found)
python run.py --resume "nonexistent"
```

## Built-in Tools

The project uses built-in Python functions for all tool operations:

1. **read_file** - Read file contents from project directory
2. **write_file** - Create or update files in project directory
3. **delete_file** - Remove files or directories
4. **list_dir** - List directory contents with detailed information
5. **grep** - Search for text patterns in files (supports regex)
6. **bash** - Execute shell commands with security restrictions

All tools operate within the project directory for security and include comprehensive error handling.

## Frontend-Specific Features

The agent includes specialized prompts for:
- Component structure (atomic design methodology)
- Design systems
- Responsive design patterns
- Interaction patterns
- Styling approaches

These are located in the `prompts/` directory and guide the agent's frontend development decisions.

## Troubleshooting

### Import Errors
If you encounter `ImportError: attempted relative import beyond top-level package`:
1. Use `run.py` instead of running `main.py` directly
2. The imports in `agent/react_agent.py` have been fixed to use absolute imports
3. If the issue persists, ensure you're running from the project root directory

### Built-in Tools Issues
- All file operations are limited to the project directory for security
- bash commands have a 30-second timeout and dangerous command detection
- Check file permissions if you encounter "Permission denied" errors

### API Key Issues
Ensure `.env` file exists and contains valid OpenAI API key. The agent supports multiple OpenAI-compatible APIs (DeepSeek, Moonshot, Ollama, LM Studio).

### System Environment Detection
The agent automatically detects:
- Operating system and version
- Shell environment (zsh, bash, etc.)
- Available development tools (node, npm, git, etc.)
- Python version and working directory

This information is used to make appropriate tool choices and command suggestions.

## Important Notes

- Always use `run.py` as the entry point to avoid import issues
- The project is designed for frontend development tasks specifically
- Database (`frontend_agent.db`) stores conversation history automatically
- Logs are written to `frontend_agent.log`
- All file operations are now handled by built-in Python functions for better stability
- The system automatically detects your environment and suggests appropriate commands