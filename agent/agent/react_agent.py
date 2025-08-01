"""
ReAct (Reasoning and Acting) Agent for Frontend Development

This module implements a ReAct agent that combines reasoning about frontend development
tasks with concrete actions using MCP tools.
"""

import asyncio
import json
import re
import logging
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

from dotenv import load_dotenv

# from agent.mcp_client import MCPManager, MCPClientError  # 已替换为内置文件操作 / Replaced with built-in file operations
from database.context_manager import ContextManager, get_context_manager, MessageType
from agent.frontend_prompts import FrontendPromptManager
from agent.file_operations import FileOperations, FileOperationsError

# Load environment variables
load_dotenv()


class ReActStepType(Enum):
    """Types of ReAct steps."""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    FINAL_ANSWER = "final_answer"


@dataclass
class ReActStep:
    """Represents a single step in the ReAct loop."""
    step_type: ReActStepType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ReActAgent:
    """
    Frontend Development Agent using ReAct (Reasoning and Acting) methodology.
    
    The agent follows a loop of:
    1. Thought: Analyze the current situation and plan next steps
    2. Action: Execute concrete actions using available tools
    3. Observation: Analyze the results of actions
    4. Repeat until task is complete
    """

    def __init__(self, 
                 context_manager: Optional[ContextManager] = None,
                 max_iterations: int = 100,  # 保护上限，防止无限循环 / Protection limit to prevent infinite loops
                 model_name: str = "gpt-4",
                 temperature: float = 0.1):
        """Initialize the ReAct agent."""
        # self.mcp_manager = mcp_manager or MCPManager()  # 已替换为内置文件操作 / Replaced with built-in file operations
        self.context_manager = context_manager or get_context_manager()
        self.prompt_manager = FrontendPromptManager()
        self.max_iterations = max_iterations
        self.model_name = model_name
        self.temperature = temperature
        
        self.logger = logging.getLogger("react_agent")
        self.current_session_id: Optional[str] = None
        self.react_history: List[ReActStep] = []
        self.available_tools: Dict[str, Any] = {}
        
        # Initialize file operations (replaces MCP filesystem)
        self.file_ops = FileOperations()
        
        # Initialize AI client (this would be integrated with your preferred LLM)
        self._init_ai_client()

    def _init_ai_client(self):
        """Initialize the AI client for LLM interactions."""
        try:
            # Try to import and initialize OpenAI client
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            
            if not api_key:
                self.logger.warning("OPENAI_API_KEY not found in environment variables")
                self.ai_client = None
                return
            
            self.ai_client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # Update model name from environment if available
            self.model_name = os.getenv("OPENAI_MODEL", self.model_name)
            self.temperature = float(os.getenv("OPENAI_TEMPERATURE", str(self.temperature)))
            
            self.logger.info(f"Initialized OpenAI client with model: {self.model_name}, base_url: {base_url}")
            
        except ImportError:
            self.logger.warning("OpenAI package not installed. Install with: pip install openai")
            self.ai_client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize AI client: {e}")
            self.ai_client = None

    # Built-in file operations (replacing MCP filesystem)
    def read_file(self, path: str) -> str:
        """
        读取project目录下的文件内容 / Read file content from project directory
        
        Args:
            path: 文件路径（相对于project目录） / File path (relative to project directory)
            
        Returns:
            文件内容字符串 / File content string
            
        Raises:
            FileOperationsError: 文件不存在或读取失败 / File does not exist or read failed
        """
        try:
            # 确保路径是相对于project目录的 / Ensure path is relative to project directory
            if path.startswith('/'):
                path = path[1:]  # 移除开头的斜杠 / Remove leading slash
            
            content = self.file_ops.read_file(path)
            self.logger.info(f"Successfully read file: {path}")
            return content
        except FileOperationsError as e:
            self.logger.error(f"Failed to read file {path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error reading file {path}: {e}")
            raise FileOperationsError(f"Failed to read file {path}: {str(e)}")

    def write_file(self, path: str, content: str) -> bool:
        """
        写入文件到project目录 / Write file to project directory
        
        Args:
            path: 文件路径（相对于project目录） / File path (relative to project directory)
            content: 文件内容 / File content
            
        Returns:
            成功返回True / Returns True on success
            
        Raises:
            FileOperationsError: 写入失败 / Write failed
        """
        try:
            # 确保路径是相对于project目录的 / Ensure path is relative to project directory
            if path.startswith('/'):
                path = path[1:]  # 移除开头的斜杠 / Remove leading slash
            
            result = self.file_ops.write_file(path, content)
            self.logger.info(f"Successfully wrote file: {path} ({len(content)} characters)")
            return result
        except FileOperationsError as e:
            self.logger.error(f"Failed to write file {path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error writing file {path}: {e}")
            raise FileOperationsError(f"Failed to write file {path}: {str(e)}")

    def delete_file(self, path: str) -> bool:
        """
        删除project目录下的文件 / Delete file from project directory
        
        Args:
            path: 文件路径（相对于project目录） / File path (relative to project directory)
            
        Returns:
            成功返回True / Returns True on success
            
        Raises:
            FileOperationsError: 删除失败 / Delete failed
        """
        try:
            # 确保路径是相对于project目录的 / Ensure path is relative to project directory
            if path.startswith('/'):
                path = path[1:]  # 移除开头的斜杠 / Remove leading slash
            
            result = self.file_ops.delete_file(path)
            self.logger.info(f"Successfully deleted file: {path}")
            return result
        except FileOperationsError as e:
            self.logger.error(f"Failed to delete file {path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error deleting file {path}: {e}")
            raise FileOperationsError(f"Failed to delete file {path}: {str(e)}")

    def list_dir(self, path: str = ".") -> List[Dict[str, Any]]:
        """
        列出目录内容，包括文件和子目录信息 / List directory contents including files and subdirectories
        
        Args:
            path: 目录路径（相对于project目录），默认为当前目录 / Directory path (relative to project directory), defaults to current directory
            
        Returns:
            目录内容列表，每个项目包含name、type、size等信息 / List of directory contents, each item contains name, type, size, etc.
            
        Raises:
            FileOperationsError: 目录不存在或读取失败 / Directory does not exist or read failed
        """
        try:
            # 确保路径是相对于project目录的 / Ensure path is relative to project directory
            if path.startswith('/'):
                path = path[1:]  # 移除开头的斜杠 / Remove leading slash
            
            items = self.file_ops.list_directory(path)
            self.logger.info(f"Successfully listed directory: {path} ({len(items)} items)")
            return items
        except FileOperationsError as e:
            self.logger.error(f"Failed to list directory {path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error listing directory {path}: {e}")
            raise FileOperationsError(f"Failed to list directory {path}: {str(e)}")

    def grep(self, pattern: str, path: str = ".", file_pattern: str = "*") -> List[Dict[str, Any]]:
        """
        在目录及子目录中搜索文本内容 / Search text content in directories and subdirectories
        
        Args:
            pattern: 要搜索的文本模式（支持正则表达式） / Text pattern to search (supports regex)
            path: 搜索路径（相对于project目录），默认为当前目录 / Search path (relative to project directory), defaults to current directory
            file_pattern: 文件名模式，如 "*.html", "*.css", "*.js" / File name pattern, e.g. "*.html", "*.css", "*.js"
            
        Returns:
            搜索结果列表，包含匹配的文件和行信息 / List of search results containing matched files and line information
            
        Raises:
            FileOperationsError: 搜索失败 / Search failed
        """
        try:
            import re
            import glob as glob_module
            from pathlib import Path
            
            # 确保路径是相对于project目录的 / Ensure path is relative to project directory
            if path.startswith('/'):
                path = path[1:]
            
            search_path = self.file_ops._resolve_path(path)
            if not search_path.exists():
                raise FileOperationsError(f"Search path not found: {search_path}")
            
            results = []
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            
            # 递归搜索文件 / Recursively search files
            pattern_path = search_path / "**" / file_pattern
            for file_path in glob_module.glob(str(pattern_path), recursive=True):
                file_obj = Path(file_path)
                if file_obj.is_file():
                    try:
                        with open(file_obj, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                        matches = []
                        for line_num, line_content in enumerate(lines, 1):
                            if compiled_pattern.search(line_content):
                                matches.append({
                                    "line_number": line_num,
                                    "line_content": line_content.strip(),
                                    "match_positions": [m.span() for m in compiled_pattern.finditer(line_content)]
                                })
                        
                        if matches:
                            results.append({
                                "file": str(file_obj.relative_to(self.file_ops.project_root)),
                                "matches": matches,
                                "total_matches": len(matches)
                            })
                            
                    except Exception as e:
                        self.logger.warning(f"Error searching in {file_path}: {e}")
            
            self.logger.info(f"Grep search completed: found {len(results)} files with matches for pattern '{pattern}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to grep pattern '{pattern}' in {path}: {e}")
            raise FileOperationsError(f"Failed to grep pattern '{pattern}': {str(e)}")

    def bash(self, command: str, working_dir: str = ".") -> Dict[str, Any]:
        """
        执行shell命令 / Execute shell command
        
        Args:
            command: 要执行的shell命令 / Shell command to execute
            working_dir: 工作目录（相对于project目录），默认为当前目录 / Working directory (relative to project directory), defaults to current directory
            
        Returns:
            执行结果，包含stdout、stderr、return_code等信息 / Execution result containing stdout, stderr, return_code, etc.
            
        Raises:
            FileOperationsError: 命令执行失败 / Command execution failed
        """
        try:
            import subprocess
            import os
            
            # 确保工作目录是相对于project目录的 / Ensure working directory is relative to project directory
            if working_dir.startswith('/'):
                working_dir = working_dir[1:]
                
            work_path = self.file_ops._resolve_path(working_dir)
            if not work_path.exists():
                work_path.mkdir(parents=True, exist_ok=True)
            
            # 安全检查：禁止危险命令 / Security check: block dangerous commands
            dangerous_commands = ['rm -rf /', 'format', 'del /s', 'sudo rm', 'chmod 777']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                raise FileOperationsError(f"Dangerous command detected and blocked: {command}")
            
            self.logger.info(f"Executing bash command: {command} (in {work_path})")
            
            # 执行命令 / Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(work_path),
                timeout=30  # 30秒超时 / 30 second timeout
            )
            
            response = {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "working_directory": str(work_path.relative_to(self.file_ops.project_root))
            }
            
            if result.returncode == 0:
                self.logger.info(f"Command executed successfully: {command}")
            else:
                self.logger.warning(f"Command failed with code {result.returncode}: {command}")
            
            return response
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout: {command}")
            raise FileOperationsError(f"Command timeout after 30 seconds: {command}")
        except Exception as e:
            self.logger.error(f"Failed to execute command '{command}': {e}")
            raise FileOperationsError(f"Failed to execute command '{command}': {str(e)}")

    def _get_system_info(self) -> Dict[str, str]:
        """获取当前系统和shell环境信息 / Get current system and shell environment information"""
        import platform
        import os
        import subprocess
        
        info = {
            "platform": platform.system(),
            "platform_version": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        }
        
        # 获取shell信息 / Get shell information
        try:
            shell = os.environ.get('SHELL', 'unknown')
            info["shell"] = shell.split('/')[-1] if '/' in shell else shell
        except:
            info["shell"] = "unknown"
        
        # 获取当前工作目录 / Get current working directory
        try:
            info["current_directory"] = os.getcwd()
        except:
            info["current_directory"] = "unknown"
        
        # 检查常用工具 / Check common tools
        tools_available = []
        common_tools = ['node', 'npm', 'git', 'python3', 'pip', 'curl', 'wget']
        for tool in common_tools:
            try:
                result = subprocess.run(['which', tool], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    tools_available.append(tool)
            except:
                pass
        
        info["available_tools"] = ", ".join(tools_available) if tools_available else "none detected"
        
        return info

    def get_builtin_tools_schema(self) -> List[Dict[str, Any]]:
        """
        构造OpenAI Function Calling格式的内置工具schema定义 / Construct built-in tools schema definition in OpenAI Function Calling format
        
        Returns:
            工具schema列表，符合OpenAI Function Calling格式 / List of tool schemas conforming to OpenAI Function Calling format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取project目录下的文件内容。支持HTML、CSS、JavaScript等前端文件格式。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件路径，相对于project目录。例如：'index.html', 'styles.css', 'script.js'"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "write_file",
                    "description": "在project目录下创建或更新文件。自动创建必要的子目录。适用于HTML、CSS、JavaScript等前端文件。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件路径，相对于project目录。例如：'index.html', 'styles.css', 'script.js'"
                            },
                            "content": {
                                "type": "string",
                                "description": "文件内容，支持HTML、CSS、JavaScript等代码"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file", 
                    "description": "删除project目录下的文件或目录。请谨慎使用此功能。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "要删除的文件或目录路径，相对于project目录"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "列出目录内容，包括文件和子目录信息。用于浏览项目结构。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "目录路径，相对于project目录。默认为当前目录'.'。例如：'.', 'styles', 'components'"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "grep",
                    "description": "在目录及子目录中搜索文本内容。支持正则表达式搜索。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "要搜索的文本模式，支持正则表达式。例如：'button', 'class=.*btn', 'function\\s+\\w+'"
                            },
                            "path": {
                                "type": "string",
                                "description": "搜索路径，相对于project目录。默认为当前目录'.'。"
                            },
                            "file_pattern": {
                                "type": "string",
                                "description": "文件名模式，用于过滤搜索的文件类型。例如：'*.html', '*.css', '*.js', '*'"
                            }
                        },
                        "required": ["pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "bash",
                    "description": "执行shell命令。用于运行构建工具、包管理器或其他开发命令。具有安全限制。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要执行的shell命令。例如：'npm install', 'ls -la', 'git status'"
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "工作目录，相对于project目录。默认为当前目录'.'。"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

    async def start_session(self, task_description: str, session_name: Optional[str] = None) -> str:
        """Start a new ReAct session for a given task."""
        # Start context manager session
        session_id = self.context_manager.start_session(session_name=session_name)
        self.current_session_id = session_id
        
        # Initialize built-in tools (replaces MCP servers)
        self.available_tools = self.get_builtin_tools_schema()
        
        # Clear history
        self.react_history = []
        
        # Add initial task to context
        self.context_manager.add_human_message(
            f"Task: {task_description}",
            {"task_type": "frontend_development", "start_time": datetime.now().isoformat()}
        )
        
        self.logger.info(f"Started ReAct session {session_id} for task: {task_description}")
        return session_id

    async def end_session(self):
        """End the current ReAct session."""
        if self.current_session_id:
            # Save final results
            await self._save_session_results()
            
            # Clean up (MCP servers no longer needed)
            
            # End context manager session
            self.context_manager.end_session()
            
            self.logger.info(f"Ended ReAct session {self.current_session_id}")
            self.current_session_id = None
            self.react_history = []

    # MCP相关方法已删除，使用内置文件操作函数替代 / MCP-related methods removed, using built-in file operation functions instead

    async def execute_task(self, task_description: str, session_id: Optional[str] = None, session_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a frontend development task using the ReAct methodology.
        
        Args:
            task_description: The task to be executed
            session_id: Optional session ID to resume
            session_name: Optional session name for new sessions
            
        Returns:
            Dictionary containing execution results and metadata
        """
        if session_id:
            # Resume existing session
            self.current_session_id = session_id
            self.context_manager.current_session_id = session_id
        else:
            # Start new session
            session_id = await self.start_session(task_description, session_name=session_name)
        
        try:
            # Generate system prompt for frontend development
            system_prompt = self._build_system_prompt()
            
            # Initialize the ReAct loop
            initial_prompt = self._build_initial_prompt(task_description)
            
            # Execute ReAct loop
            result = await self._react_loop(system_prompt, initial_prompt)
            
            return {
                "session_id": session_id,
                "task_description": task_description,
                "result": result,
                "steps": [self._step_to_dict(step) for step in self.react_history],
                "tools_used": self._get_tools_usage_summary(),
                "files_generated": self.context_manager.get_generated_files(),
                "success": result.get("success", False)
            }
            
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            return {
                "session_id": session_id,
                "task_description": task_description,
                "error": str(e),
                "steps": [self._step_to_dict(step) for step in self.react_history],
                "success": False
            }
        
        finally:
            await self.end_session()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the ReAct agent."""
        tools_description = self._build_tools_description()
        system_info = self._get_system_info()
        
        return f"""You are a Frontend Development Agent using the ReAct (Reasoning and Acting) methodology.

## System Environment Information
- **Platform**: {system_info['platform']} {system_info['platform_version']} ({system_info['architecture']})
- **Shell**: {system_info['shell']}
- **Python**: {system_info['python_version']}
- **Working Directory**: {system_info['current_directory']}
- **Available Tools**: {system_info['available_tools']}

Use this information to make appropriate tool choices and system commands.

Your role is to help create modern, accessible, and performant web interfaces using best practices.

## ReAct Methodology - Tool-Driven Execution
You must follow this exact pattern:

**Thought:** Analyze the current situation, consider what needs to be done next, and plan your approach.
**Action:** Execute a specific action using available tools OR indicate task completion.
**Observation:** Analyze the results of your action and determine next steps.

## Smart Termination Logic
- If you need to use tools, specify them clearly in your **Action:**
- If no tools are needed and the task is complete, state "Task completed" in your **Action:**
- The system will automatically detect when you stop calling tools and end the session

## Available Tools
{tools_description}

## File System Guidelines
**IMPORTANT: All files must be created in the project directory. Use simple filenames like:**
- **HTML files**: `login.html`, `index.html`, `about.html`
- **CSS files**: `styles.css`, `login.css`, `main.css` 
- **JS files**: `script.js`, `app.js`, `main.js`
- **DO NOT create directories** - just use filenames directly

## Tool Usage Format
When you need to use a tool, format your action like this:
**Action:** Use tool_name with parameters: {{parameter1: "value1", parameter2: "value2"}}

Examples:
- **Action:** Use read_file with parameters: {{"path": "index.html"}}
- **Action:** Use write_file with parameters: {{"path": "login.html", "content": "<!DOCTYPE html>..."}}
- **Action:** Use write_file with parameters: {{"path": "styles.css", "content": "body {{ margin: 0; }}"}}
- **Action:** Use delete_file with parameters: {{"path": "old_file.html"}}
- **Action:** Use list_dir with parameters: {{"path": "."}}
- **Action:** Use grep with parameters: {{"pattern": "button", "file_pattern": "*.html"}}
- **Action:** Use bash with parameters: {{"command": "npm install"}}

## Task Completion
When your task is finished, simply state:
**Action:** Task completed successfully. [Brief summary of what was accomplished]

## Frontend Development Guidelines
- Follow mobile-first responsive design principles
- Use semantic HTML for accessibility
- Implement proper ARIA attributes where needed
- Follow modern CSS best practices (Grid, Flexbox, Custom Properties)
- Ensure cross-browser compatibility
- Optimize for performance (minimize bundle size, lazy loading, etc.)
- Use component-based architecture when appropriate
- Follow established design systems and patterns

## Important Rules
1. Always start with a **Thought:** to analyze the task
2. Be specific about which tools you need in **Action:**
3. If no tools are needed, clearly state task completion
4. Be concise but thorough in your reasoning
5. Always consider accessibility and performance implications

Begin your response with **Thought:** to analyze the given task."""

    def _build_tools_description(self) -> str:
        """Build description of available built-in tools."""
        descriptions = ["\n### FILE OPERATIONS Tools:"]
        
        # 描述内置的文件操作工具 / Describe built-in file operation tools
        for tool_schema in self.available_tools:
            function_info = tool_schema.get('function', {})
            name = function_info.get('name', 'unnamed')
            description = function_info.get('description', 'No description available')
            descriptions.append(f"- **{name}**: {description}")
        
        return "\n".join(descriptions)

    def _build_initial_prompt(self, task_description: str) -> str:
        """Build the initial prompt for the task."""
        return f"""Task: {task_description}

Please analyze this frontend development task and execute it step by step using the ReAct methodology.

Key Points:
1. Start with **Thought:** to understand and break down the task
2. Use **Action:** to call tools when needed, or state "Task completed" when finished
3. The system will automatically end when you stop calling tools
4. Be specific about which tools you need and their parameters
5. Focus on creating clean, accessible, and performant frontend code

Begin now with your first **Thought:**"""

    async def _react_loop(self, system_prompt: str, initial_prompt: str) -> Dict[str, Any]:
        """Execute the main ReAct reasoning and acting loop."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_prompt}
        ]
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            self.logger.info(f"ReAct iteration {iteration}")
            
            try:
                # Get AI response
                response = await self._get_ai_response(messages)
                self.logger.info(f"AI Response: {response[:200]}..." if len(response) > 200 else f"AI Response: {response}")
                
                # Parse the response into ReAct steps
                steps = self._parse_react_response(response)
                
                # Check if AI wants to call any tools
                has_tool_calls = False
                task_completed = False
                
                # Process each step
                for step in steps:
                    self.react_history.append(step)
                    self.logger.info(f"Step: {step.step_type.value} - {step.content[:100]}..." if len(step.content) > 100 else f"Step: {step.step_type.value} - {step.content}")
                    
                    # Add to conversation context
                    self.context_manager.add_ai_message(
                        f"{step.step_type.value.title()}: {step.content}",
                        {"step_type": step.step_type.value, "iteration": iteration}
                    )
                    
                    if step.step_type == ReActStepType.ACTION:
                        # Check if this action involves tool calls
                        tool_call = self._parse_builtin_tool_call(step.content)
                        
                        if tool_call:
                            has_tool_calls = True
                            tool_name, arguments = tool_call
                            self.logger.info(f"Tool call detected: {tool_name} with args: {arguments}")
                            
                            # Execute the action
                            observation = await self._execute_action(step.content)
                            self.logger.info(f"Tool execution result: {observation[:200]}..." if len(observation) > 200 else f"Tool execution result: {observation}")
                            
                            # Create observation step
                            obs_step = ReActStep(
                                step_type=ReActStepType.OBSERVATION,
                                content=observation,
                                metadata={"iteration": iteration, "tool_used": tool_name}
                            )
                            self.react_history.append(obs_step)
                            
                            # Add observation to messages
                            messages.append({"role": "assistant", "content": response})
                            messages.append({"role": "user", "content": f"**Observation:** {observation}"})
                        else:
                            # No tool call detected, check if it's a completion statement
                            if self._is_completion_statement(step.content):
                                task_completed = True
                                self.logger.info("Task completion detected (no more tools needed)")
                                return {
                                    "success": True,
                                    "final_answer": step.content,
                                    "iterations": iteration,
                                    "total_steps": len(self.react_history),
                                    "completion_reason": "No more tools needed"
                                }
                        
                    elif step.step_type == ReActStepType.FINAL_ANSWER:
                        # Explicit final answer
                        task_completed = True
                        self.logger.info("Task completed with explicit Final Answer")
                        return {
                            "success": True,
                            "final_answer": step.content,
                            "iterations": iteration,
                            "total_steps": len(self.react_history),
                            "completion_reason": "Explicit Final Answer"
                        }
                
                # If no tool calls were made in this iteration, consider task complete
                if not has_tool_calls and not task_completed:
                    self.logger.info("No tool calls detected in this iteration - checking if task is complete")
                    # Give AI one more chance to provide final answer
                    messages.append({"role": "assistant", "content": response})
                    messages.append({"role": "user", "content": "**Observation:** No tool calls were detected. If the task is complete, please provide your final answer. If more work is needed, specify what tools you need to use."})
                    continue
                
                # Add assistant response to messages if task not completed
                if not task_completed:
                    messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                self.logger.error(f"Error in ReAct iteration {iteration}: {e}")
                
                # Add error observation
                error_obs = ReActStep(
                    step_type=ReActStepType.OBSERVATION,
                    content=f"Error occurred: {str(e)}",
                    metadata={"error": True, "iteration": iteration}
                )
                self.react_history.append(error_obs)
                
                # Continue with error information
                messages.append({
                    "role": "user", 
                    "content": f"**Observation:** An error occurred: {str(e)}. Please analyze this error and continue with a new approach."
                })
        
        # Max iterations reached (safety limit)
        self.logger.warning(f"Reached maximum iterations ({self.max_iterations}) - stopping for safety")
        return {
            "success": False,
            "reason": f"Maximum iterations reached ({self.max_iterations}) - safety limit",
            "iterations": self.max_iterations,
            "total_steps": len(self.react_history)
        }

    def _parse_react_response(self, response: str) -> List[ReActStep]:
        """Parse AI response into ReAct steps."""
        steps = []
        
        # Patterns for different step types
        patterns = {
            ReActStepType.THOUGHT: r'\*\*Thought:\*\*\s*(.*?)(?=\*\*(?:Action|Observation|Final Answer):\*\*|$)',
            ReActStepType.ACTION: r'\*\*Action:\*\*\s*(.*?)(?=\*\*(?:Thought|Observation|Final Answer):\*\*|$)',
            ReActStepType.OBSERVATION: r'\*\*Observation:\*\*\s*(.*?)(?=\*\*(?:Thought|Action|Final Answer):\*\*|$)',
            ReActStepType.FINAL_ANSWER: r'\*\*(?:Action:\s*)?Final Answer:\*\*\s*(.*?)$'
        }
        
        for step_type, pattern in patterns.items():
            matches = re.finditer(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                content = match.group(1).strip()
                if content:
                    steps.append(ReActStep(
                        step_type=step_type,
                        content=content
                    ))
        
        # Sort steps by their position in the text
        step_positions = []
        for step in steps:
            for step_type, pattern in patterns.items():
                if step.step_type == step_type:
                    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                    if match and step.content in match.group(1):
                        step_positions.append((match.start(), step))
                        break
        
        # Sort by position and return steps
        step_positions.sort(key=lambda x: x[0])
        return [step for _, step in step_positions]

    async def _execute_action(self, action_content: str) -> str:
        """Execute an action using built-in functions and return the observation."""
        try:
            # Check if it's a Final Answer or task completion
            if any(phrase in action_content.lower() for phrase in ["final answer", "task completed", "task complete"]):
                return "Task completed."
            
            # Parse tool call from action content
            tool_call = self._parse_builtin_tool_call(action_content)
            
            if tool_call:
                tool_name, arguments = tool_call
                
                # Execute the built-in tool function with context tracking
                with self.context_manager.tool_call_context(tool_name, arguments) as tool_call_id:
                    result = await self._call_builtin_function(tool_name, arguments)
                    
                    # Update context with results
                    self.context_manager.complete_tool_call(tool_call_id, result)
                    
                    return self._format_builtin_result(tool_name, result, arguments)
            
            else:
                # Direct action without tool call
                return f"Action noted: {action_content}"
                
        except Exception as e:
            self.logger.error(f"Error executing action '{action_content}': {e}")
            return f"Error executing action: {str(e)}"

    def _parse_builtin_tool_call(self, action_content: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parse built-in tool call from action content.
        
        Expected formats:
        - Use read_file with parameters: {path: "file.html"}
        - Use write_file with parameters: {path: "file.html", content: "..."}
        - Use delete_file with parameters: {path: "file.html"}
        """
        # Pattern: Use tool_name with parameters: {json}
        pattern = r'use\s+(\w+)\s+with\s+parameters:\s*(\{.+\})'
        match = re.search(pattern, action_content, re.IGNORECASE)
        if match:
            tool_name, params_str = match.groups()
            try:
                arguments = json.loads(params_str)
                return tool_name, arguments
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON parameters: {params_str}, error: {e}")
                return None
        
        return None

    async def _call_builtin_function(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call the appropriate built-in function based on tool name."""
        try:
            if tool_name == "read_file":
                path = arguments.get("path")
                if not path:
                    raise ValueError("Missing required parameter: path")
                return self.read_file(path)
            
            elif tool_name == "write_file":
                path = arguments.get("path")
                content = arguments.get("content")
                if not path or content is None:
                    raise ValueError("Missing required parameters: path and/or content")
                return self.write_file(path, content)
            
            elif tool_name == "delete_file":
                path = arguments.get("path")
                if not path:
                    raise ValueError("Missing required parameter: path")
                return self.delete_file(path)
            
            elif tool_name == "list_dir":
                path = arguments.get("path", ".")
                return self.list_dir(path)
            
            elif tool_name == "grep":
                pattern = arguments.get("pattern")
                if not pattern:
                    raise ValueError("Missing required parameter: pattern")
                path = arguments.get("path", ".")
                file_pattern = arguments.get("file_pattern", "*")
                return self.grep(pattern, path, file_pattern)
            
            elif tool_name == "bash":
                command = arguments.get("command")
                if not command:
                    raise ValueError("Missing required parameter: command")
                working_dir = arguments.get("working_dir", ".")
                return self.bash(command, working_dir)
            
            else:
                raise ValueError(f"Unknown tool name: {tool_name}")
                
        except Exception as e:
            self.logger.error(f"Error calling builtin function {tool_name}: {e}")
            raise

    def _format_builtin_result(self, tool_name: str, result: Any, arguments: Dict[str, Any]) -> str:
        """Format the result of a built-in function call."""
        try:
            if tool_name == "read_file":
                path = arguments.get("path", "unknown")
                if isinstance(result, str):
                    content_preview = result[:200] + "..." if len(result) > 200 else result
                    return f"Successfully read file '{path}' ({len(result)} characters):\n{content_preview}"
                else:
                    return f"Successfully read file '{path}': {result}"
            
            elif tool_name == "write_file":
                path = arguments.get("path", "unknown")
                content_length = len(arguments.get("content", ""))
                return f"Successfully wrote file '{path}' ({content_length} characters)"
            
            elif tool_name == "delete_file":
                path = arguments.get("path", "unknown")
                return f"Successfully deleted file '{path}'"
            
            elif tool_name == "list_dir":
                path = arguments.get("path", ".")
                if isinstance(result, list):
                    items_summary = []
                    for item in result[:10]:  # 只显示前10个项目 / Only show the first 10 items
                        item_type = item.get("type", "unknown")
                        item_name = item.get("name", "unknown")
                        item_size = item.get("size")
                        if item_type == "file" and item_size is not None:
                            items_summary.append(f"{item_name} ({item_size} bytes)")
                        else:
                            items_summary.append(f"{item_name} [{item_type}]")
                    
                    summary = f"Directory listing for '{path}' ({len(result)} items):\n" + "\n".join(items_summary)
                    if len(result) > 10:
                        summary += f"\n... and {len(result) - 10} more items"
                    return summary
                else:
                    return f"Listed directory '{path}': {result}"
            
            elif tool_name == "grep":
                pattern = arguments.get("pattern", "unknown")
                if isinstance(result, list):
                    total_files = len(result)
                    total_matches = sum(item.get("total_matches", 0) for item in result)
                    
                    summary = f"Grep search for '{pattern}' found {total_matches} matches in {total_files} files:"
                    for file_result in result[:5]:  # 只显示前5个文件的结果 / Only show the first 5 files
                        file_path = file_result.get("file", "unknown")
                        matches = file_result.get("matches", [])
                        summary += f"\n- {file_path}: {len(matches)} matches"
                        for match in matches[:3]:  # 每个文件只显示前3个匹配 / Only show the first 3 matches per file
                            line_num = match.get("line_number", "?")
                            line_content = match.get("line_content", "")[:100]  # 截断长行 / Truncate long lines
                            summary += f"\n  Line {line_num}: {line_content}"
                    
                    if total_files > 5:
                        summary += f"\n... and {total_files - 5} more files"
                    return summary
                else:
                    return f"Grep search for '{pattern}' completed: {result}"
            
            elif tool_name == "bash":
                command = arguments.get("command", "unknown")
                if isinstance(result, dict):
                    return_code = result.get("return_code", "unknown")
                    stdout = result.get("stdout", "").strip()
                    stderr = result.get("stderr", "").strip()
                    
                    summary = f"Command '{command}' completed with exit code {return_code}"
                    if stdout:
                        stdout_preview = stdout[:500] + "..." if len(stdout) > 500 else stdout
                        summary += f"\nOutput:\n{stdout_preview}"
                    if stderr:
                        stderr_preview = stderr[:200] + "..." if len(stderr) > 200 else stderr
                        summary += f"\nErrors:\n{stderr_preview}"
                    return summary
                else:
                    return f"Command '{command}' completed: {result}"
            
            else:
                return f"Function {tool_name} completed with result: {result}"
                
        except Exception as e:
            self.logger.error(f"Error formatting result for {tool_name}: {e}")
            return f"Function {tool_name} completed but failed to format result: {str(e)}"

    # 旧的MCP相关解析方法已删除，使用新的内置函数调用机制 / Old MCP-related parsing methods removed, using new built-in function call mechanism

    async def _get_ai_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from AI model."""
        if self.ai_client is None:
            self.logger.warning("AI client not available, using mock response")
            return self._generate_mock_response(messages)
        
        try:
            # Get max tokens from environment
            max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
            
            response = await self.ai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            # Log token usage if available
            if hasattr(response, 'usage') and response.usage:
                self.logger.debug(f"Token usage - Prompt: {response.usage.prompt_tokens}, "
                                f"Completion: {response.usage.completion_tokens}, "
                                f"Total: {response.usage.total_tokens}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            # Fallback to mock response
            return self._generate_mock_response(messages)

    def _generate_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a mock response for testing purposes."""
        last_message = messages[-1]['content'] if messages else ""
        
        if "task:" in last_message.lower():
            return """**Thought:** I need to analyze this frontend development task and break it down into specific steps. Let me understand what needs to be built and plan my approach.

**Action:** Use list_directory with path="."

**Observation:** I'll examine the current directory structure to understand the project context."""
        
        elif "observation:" in last_message.lower():
            return """**Thought:** Based on the observation, I can see the current state. Now I need to plan the next step in the development process.

**Action:** Final Answer: I have analyzed the task and completed the requested frontend development work. The solution includes proper HTML structure, responsive CSS styling, and interactive JavaScript functionality following modern web development best practices."""
        
        else:
            return """**Thought:** I need to continue working on this task systematically.

**Action:** Final Answer: Task completed successfully."""

    def _is_completion_statement(self, action_content: str) -> bool:
        """Check if the action content indicates task completion without tool calls."""
        completion_indicators = [
            "task is complete",
            "task completed",
            "work is done",
            "finished",
            "no more tools needed",
            "no further action",
            "completed successfully",
            "task accomplished"
        ]
        
        content_lower = action_content.lower()
        return any(indicator in content_lower for indicator in completion_indicators)

    def _step_to_dict(self, step: ReActStep) -> Dict[str, Any]:
        """Convert ReAct step to dictionary."""
        return {
            "step_type": step.step_type.value,
            "content": step.content,
            "metadata": step.metadata,
            "timestamp": step.timestamp.isoformat() if step.timestamp else None
        }

    def _get_tools_usage_summary(self) -> Dict[str, Any]:
        """Get summary of tools used during the session."""
        return self.context_manager.get_tool_call_statistics()
    
    async def generate_session_name(self, task_description: str) -> str:
        """Generate a descriptive session name based on the task."""
        try:
            # Create a simple prompt for session naming
            naming_prompt = f"""Based on this frontend development task, provide a short, descriptive session name (2-6 words):

Task: {task_description}

Requirements:
- Keep it concise and descriptive
- Focus on the main goal/component being created
- Use frontend terminology when appropriate
- Examples: "Landing Page Creation", "Button Component Design", "Dashboard Layout"

Session name:"""

            response = await self.ai_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": naming_prompt}],
                max_tokens=50,
                temperature=0.3
            )
            
            session_name = response.choices[0].message.content.strip()
            # Clean up the response and limit length
            session_name = session_name.replace('"', '').replace("'", '')
            if len(session_name) > 50:
                session_name = session_name[:47] + "..."
                
            return session_name
            
        except Exception as e:
            # Fallback to simple extraction from task
            self.logger.warning(f"Could not generate AI session name: {e}")
            return self._extract_simple_name(task_description)
    
    def _extract_simple_name(self, task_description: str) -> str:
        """Extract a simple name from task description as fallback."""
        # Simple keyword-based naming
        task_lower = task_description.lower()
        
        if "button" in task_lower:
            return "Button Creation"
        elif "page" in task_lower or "landing" in task_lower:
            return "Page Development"
        elif "component" in task_lower:
            return "Component Building"
        elif "layout" in task_lower:
            return "Layout Design"
        elif "modal" in task_lower:
            return "Modal Development"
        elif "navigation" in task_lower or "nav" in task_lower:
            return "Navigation Design"
        elif "form" in task_lower:
            return "Form Creation"
        else:
            # Use first few words
            words = task_description.split()[:3]
            return " ".join(words).title()

    async def _save_session_results(self):
        """Save session results and create summary."""
        if not self.current_session_id:
            return
        
        # Create final context snapshot
        final_context = {
            "react_history": [self._step_to_dict(step) for step in self.react_history],
            "tools_usage": self._get_tools_usage_summary(),
            "session_summary": self.context_manager.get_session_summary()
        }
        
        self.context_manager.save_context_snapshot(
            "final_session_state",
            final_context,
            "Complete ReAct session execution results"
        )


class FrontendReActAgent(ReActAgent):
    """
    Specialized ReAct agent for frontend development tasks.
    
    This extends the base ReAct agent with frontend-specific capabilities
    and knowledge.
    """

    def __init__(self, **kwargs):
        """Initialize the frontend ReAct agent."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger("frontend_react_agent")

    def _build_system_prompt(self) -> str:
        """Build frontend-specific system prompt."""
        base_prompt = super()._build_system_prompt()
        
        frontend_specific = """
## Frontend Development Expertise

You specialize in:
- **HTML5**: Semantic markup, accessibility, SEO optimization
- **CSS3**: Grid, Flexbox, Custom Properties, animations, responsive design
- **JavaScript**: ES6+, DOM manipulation, event handling, async programming
- **Frontend Frameworks**: React, Vue, Angular component patterns
- **Build Tools**: Webpack, Vite, Rollup, Parcel
- **CSS Preprocessors**: Sass, Less, PostCSS
- **Package Management**: npm, yarn, pnpm

## Common Frontend Tasks
- Create responsive layouts with CSS Grid and Flexbox
- Implement interactive components with vanilla JavaScript or frameworks
- Set up build toolchains and development environments
- Optimize for performance (bundling, minification, lazy loading)
- Ensure accessibility compliance (WCAG guidelines)
- Cross-browser compatibility testing
- Progressive web app features

## Best Practices to Follow
- Mobile-first responsive design
- Semantic HTML structure
- Progressive enhancement
- Performance optimization
- Accessibility (ARIA labels, keyboard navigation)
- Code organization and maintainability
- Modern CSS methodologies (BEM, CSS Modules, styled-components)
- Component-based architecture
"""
        
        return base_prompt + frontend_specific

    async def create_html_page(self, requirements: str) -> Dict[str, Any]:
        """Create a complete HTML page based on requirements."""
        task = f"Create a complete HTML page with the following requirements: {requirements}"
        return await self.execute_task(task)

    async def create_component(self, component_type: str, specifications: str) -> Dict[str, Any]:
        """Create a reusable UI component."""
        task = f"Create a {component_type} component with these specifications: {specifications}"
        return await self.execute_task(task)

    async def implement_responsive_layout(self, layout_description: str) -> Dict[str, Any]:
        """Implement a responsive layout."""
        task = f"Implement a responsive layout: {layout_description}"
        return await self.execute_task(task)

    async def optimize_performance(self, target_files: List[str]) -> Dict[str, Any]:
        """Optimize frontend performance for specified files."""
        files_str = ", ".join(target_files)
        task = f"Optimize frontend performance for these files: {files_str}"
        return await self.execute_task(task)