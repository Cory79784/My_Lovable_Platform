#!/usr/bin/env python3
"""
Frontend Development Agent - Main Entry Point

This is the main entry point for the Frontend Development Agent.
It provides a command-line interface for running frontend development tasks
using the ReAct methodology with MCP tool integration.
"""

import asyncio
import argparse
import json
import logging
import sys
import os
from pathlib import Path
from typing import Optional

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.react_agent import FrontendReActAgent
# from agent.mcp_client import MCPManager  # 已替换为内置文件操作 / Replaced with built-in file operations
from database.context_manager import get_context_manager


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("frontend_agent.log")
        ]
    )


async def run_interactive_mode(session_id: Optional[str] = None):
    """Run the agent in interactive mode."""
    print("🎨 Frontend Development Agent - Interactive Mode")
    print("=" * 50)
    
    # Initialize agent (no longer using MCP)
    context_manager = get_context_manager("frontend_agent.db")
    agent = FrontendReActAgent(
        context_manager=context_manager
    )
    
    print("\nAgent initialized successfully!")
    print("\nAvailable commands:")
    print("  - help: Show this help message")
    print("  - task <description>: Execute a frontend development task")
    print("  - component <type> <specs>: Create a UI component")
    print("  - layout <description>: Create a responsive layout")
    print("  - optimize <files>: Optimize performance for files")
    print("  - exit: Exit the agent")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye! 👋")
                break
                
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            # Parse command
            parts = user_input.split(' ', 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command == 'task':
                if not args:
                    print("❌ Please provide a task description")
                    continue
                
                print(f"\n🚀 Executing task: {args}")
                # Generate session name for new tasks if not resuming
                if not session_id:
                    session_name = await agent.generate_session_name(args)
                    print(f"📝 Session: {session_name}")
                    result = await agent.execute_task(args, session_name=session_name)
                else:
                    result = await agent.execute_task(args, session_id=session_id)
                    session_id = result.get("session_id")  # Update for subsequent tasks
                print_result(result)
                
            elif command == 'component':
                if not args:
                    print("❌ Please provide component type and specifications")
                    continue
                
                parts = args.split(' ', 1)
                component_type = parts[0]
                specs = parts[1] if len(parts) > 1 else "basic component"
                
                task_description = f"Create a {component_type} component with the following specifications: {specs}"
                print(f"\n🔧 Creating {component_type} component: {specs}")
                result = await agent.execute_task(task_description)
                print_result(result)
                
            elif command == 'layout':
                if not args:
                    print("❌ Please provide layout description")
                    continue
                
                task_description = f"Create a responsive layout: {args}"
                print(f"\n📱 Creating responsive layout: {args}")
                result = await agent.execute_task(task_description)
                print_result(result)
                
            elif command == 'optimize':
                if not args:
                    print("❌ Please provide files to optimize")
                    continue
                
                files = [f.strip() for f in args.split(',')]
                task_description = f"Optimize the performance of these files: {', '.join(files)}"
                print(f"\n⚡ Optimizing performance for: {', '.join(files)}")
                result = await agent.execute_task(task_description)
                print_result(result)
                
            else:
                print(f"❌ Unknown command: {command}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            logging.error(f"Interactive mode error: {e}")


def print_help():
    """Print help information."""
    help_text = """
🎨 Frontend Development Agent Help

Commands:
  task <description>     - Execute a general frontend development task
  component <type> <specs> - Create a UI component (e.g., 'button responsive with hover effects')
  layout <description>   - Create a responsive layout (e.g., 'three-column layout with sidebar')
  optimize <files>       - Optimize performance for specified files (comma-separated)
  help                   - Show this help message
  exit                   - Exit the agent

Examples:
  > task Create a landing page with hero section and navigation
  > component modal with accessibility features and animations
  > layout responsive dashboard with sidebar and main content area
  > optimize style.css, script.js, images/hero.jpg

Features:
  ✅ ReAct reasoning methodology
  ✅ MCP tool integration
  ✅ Context tracking and persistence
  ✅ Frontend-specific expertise
  ✅ Accessibility-first approach
  ✅ Performance optimization
  ✅ Responsive design
"""
    print(help_text)


def print_result(result: dict):
    """Print execution result in a formatted way."""
    print("\n" + "=" * 50)
    
    if result.get("success"):
        print("✅ Task completed successfully!")
    else:
        print("❌ Task failed or incomplete")
        
    if "error" in result:
        print(f"Error: {result['error']}")
        
    print(f"Session ID: {result.get('session_id', 'N/A')}")
    print(f"Steps executed: {len(result.get('steps', []))}")
    
    if result.get("files_generated"):
        print(f"Files generated: {len(result['files_generated'])}")
        for file_info in result['files_generated'][:3]:  # Show first 3 files
            print(f"  - {file_info.get('file_path', 'unknown')}")
        if len(result['files_generated']) > 3:
            print(f"  ... and {len(result['files_generated']) - 3} more")
    
    if result.get("tools_used"):
        print("Tools used:")
        for tool, stats in result['tools_used'].items():
            print(f"  - {tool}: {stats.get('total_calls', 0)} calls")
    
    print("=" * 50)


async def run_single_task(task: str, output_file: Optional[str] = None, session_id: Optional[str] = None):
    """Run a single task and optionally save results to file."""
    print(f"🚀 Executing task: {task}")
    
    # Initialize agent (no longer using MCP)
    context_manager = get_context_manager("frontend_agent.db")
    agent = FrontendReActAgent(
        context_manager=context_manager
    )
    
    try:
        # Generate session name if this is a new session
        if not session_id:
            session_name = await agent.generate_session_name(task)
            print(f"📝 Session: {session_name}")
        else:
            session_name = None
            print(f"📝 Resuming session: {session_id}")
        
        result = await agent.execute_task(task, session_id=session_id, session_name=session_name)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"Results saved to: {output_file}")
        else:
            print_result(result)
            
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Error executing task: {e}")
        logging.error(f"Task execution error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Frontend Development Agent - ReAct-based AI assistant for frontend development"
    )
    
    parser.add_argument(
        "--task", "-t",
        type=str,
        help="Execute a single task and exit"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (default)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for task results (JSON format)"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/mcp_servers.json",  # 已不再使用 / No longer used
        help="Path to MCP servers configuration file"
    )
    
    parser.add_argument(
        "--continue-session",
        action="store_true",
        help="Continue the last conversation session"
    )
    
    parser.add_argument(
        "--resume", "-r",
        type=str,
        help="Resume a specific session by ID or name"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Ensure config directory exists
    config_path = Path(args.config).parent
    config_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Handle session management
        session_id = None
        context_manager = get_context_manager("frontend_agent.db")
        
        if args.continue_session:
            session_id = context_manager.get_last_session_id()
            if session_id:
                print(f"📝 Continuing last session: {session_id[:8]}...")
            else:
                print("⚠️  No previous session found, starting new session")
        
        elif args.resume:
            session_id = context_manager.find_session_by_name_or_id(args.resume)
            if session_id:
                print(f"📝 Resuming session: {args.resume} -> {session_id[:8]}...")
            else:
                print(f"❌ Session '{args.resume}' not found")
                # List recent sessions
                sessions = context_manager.list_recent_sessions(5)
                if sessions:
                    print("Recent sessions:")
                    for session in sessions:
                        print(f"  - {session['session_name']} ({session['session_id'][:8]}...)")
                sys.exit(1)
        
        if args.task:
            # Single task mode
            success = asyncio.run(run_single_task(args.task, args.output, session_id))
            sys.exit(0 if success else 1)
        else:
            # Interactive mode (default)
            asyncio.run(run_interactive_mode(session_id))
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()