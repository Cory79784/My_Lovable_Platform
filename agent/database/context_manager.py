"""
Context Manager for Frontend Development Agent 

This module provides context management capabilities including conversation tracking, / 此模块提供上下文管理功能，包括对话跟踪、
tool call logging, and state persistence using SQLite database. / 工具调用日志记录和使用SQLite数据库的状态持久化
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import asyncio
from contextlib import contextmanager

from .models import (
    DatabaseManager, Conversation, ToolCall, ContextSnapshot, GeneratedFile,
    MessageType, ToolCallStatus
)


class ContextManager:
    """
    Manages conversation context, tool calls, and state persistence / 管理对话上下文、工具调用和状态持久化
    for the Frontend Development Agent. / 用于前端开发代理
    """

    def __init__(self, db_path: str = "frontend_agent.db"):
        """Initialize the context manager. / 初始化上下文管理器"""
        self.db = DatabaseManager(db_path)
        self.current_session_id: Optional[str] = None
        self.context_stack: List[Dict[str, Any]] = []
        self.active_tool_calls: Dict[str, ToolCall] = {}
        self.callbacks: Dict[str, List[Callable]] = {
            'conversation_added': [],
            'tool_call_started': [],
            'tool_call_completed': [],
            'context_snapshot_saved': [],
            'file_generated': []
        }

    def start_session(self, session_id: Optional[str] = None, session_name: Optional[str] = None) -> str:
        """Start a new conversation session. / 启动新的对话会话"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        self.current_session_id = session_id
        self.context_stack = []
        self.active_tool_calls = {}
        
        # Save session metadata
        if session_name:
            self.save_session_metadata(session_id, session_name)
        
        # Save initial system context
        self.add_conversation(
            MessageType.SYSTEM,
            "Frontend Development Agent session started",
            {"session_start": True, "timestamp": datetime.now().isoformat()}
        )
        
        return session_id

    def save_session_metadata(self, session_id: str, session_name: str):
        """Save session metadata to database. / 将会话元数据保存到数据库"""
        try:
            # First ensure the session_metadata table exists / 首先确保session_metadata表存在
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS session_metadata (
                    session_id TEXT PRIMARY KEY,
                    session_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL
                )
            """)
            
            self.db.execute_query("""
                INSERT OR REPLACE INTO session_metadata 
                (session_id, session_name, created_at, last_activity)
                VALUES (?, ?, ?, ?)
            """, (session_id, session_name, datetime.now().isoformat(), datetime.now().isoformat()))
        except Exception as e:
            print(f"Warning: Could not save session metadata: {e}")
    
    def get_last_session_id(self) -> Optional[str]:
        """Get the ID of the most recent session. / 获取最近会话的ID"""
        try:
            result = self.db.execute_query("""
                SELECT session_id FROM session_metadata 
                ORDER BY last_activity DESC LIMIT 1
            """)
            return result[0][0] if result else None
        except Exception:
            # Fallback to conversations table / 回退到conversations表
            try:
                result = self.db.execute_query("""
                    SELECT session_id FROM conversations 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                return result[0][0] if result else None
            except Exception:
                return None
    
    def find_session_by_name_or_id(self, search_term: str) -> Optional[str]:
        """Find session by name or ID. / 通过名称或ID查找会话"""
        try:
            # First try exact ID match / 首先尝试精确ID匹配
            if len(search_term) == 36:  # UUID length
                result = self.db.execute_query("""
                    SELECT session_id FROM session_metadata 
                    WHERE session_id = ?
                """, (search_term,))
                if result:
                    return result[0][0]
            
            # Then try name search / 然后尝试名称搜索
            result = self.db.execute_query("""
                SELECT session_id FROM session_metadata 
                WHERE session_name LIKE ? OR session_id LIKE ?
                ORDER BY last_activity DESC LIMIT 1
            """, (f"%{search_term}%", f"{search_term}%"))
            
            return result[0][0] if result else None
        except Exception:
            return None
    
    def list_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent sessions with metadata. / 列出带有元数据的最近会话"""
        try:
            result = self.db.execute_query("""
                SELECT session_id, session_name, created_at, last_activity
                FROM session_metadata 
                ORDER BY last_activity DESC LIMIT ?
            """, (limit,))
            
            sessions = []
            for row in result:
                sessions.append({
                    'session_id': row[0],
                    'session_name': row[1],
                    'created_at': row[2],
                    'last_activity': row[3]
                })
            return sessions
        except Exception:
            return []

    def end_session(self):
        """End the current conversation session. / 结束当前对话会话"""
        if self.current_session_id:
            # Update last activity / 更新最后活动时间
            try:
                self.db.execute_query("""
                    UPDATE session_metadata 
                    SET last_activity = ? 
                    WHERE session_id = ?
                """, (datetime.now().isoformat(), self.current_session_id))
            except Exception:
                pass
                
            self.add_conversation(
                MessageType.SYSTEM,
                "Frontend Development Agent session ended",
                {"session_end": True, "timestamp": datetime.now().isoformat()}
            )
            
            # Save final context snapshot
            self.save_context_snapshot(
                "session_end",
                self.get_current_context(),
                "Final context state at session end"
            )
            
            self.current_session_id = None
            self.context_stack = []
            self.active_tool_calls = {}

    def add_conversation(self, message_type: MessageType, content: str, 
                        metadata: Optional[Dict[str, Any]] = None,
                        parent_id: Optional[str] = None) -> str:
        """Add a conversation message to the context."""
        if not self.current_session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        conversation = Conversation.create(
            session_id=self.current_session_id,
            message_type=message_type,
            content=content,
            metadata=metadata,
            parent_id=parent_id
        )
        
        success = self.db.save_conversation(conversation)
        if success:
            # Trigger callbacks
            for callback in self.callbacks['conversation_added']:
                try:
                    callback(conversation)
                except Exception as e:
                    print(f"Error in conversation callback: {e}")
            
            return conversation.id
        else:
            raise RuntimeError("Failed to save conversation to database")

    def add_human_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a human message to the conversation."""
        return self.add_conversation(MessageType.HUMAN, content, metadata)

    def add_ai_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an AI message to the conversation."""
        return self.add_conversation(MessageType.AI, content, metadata)

    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a system message to the conversation."""
        return self.add_conversation(MessageType.SYSTEM, content, metadata)

    def start_tool_call(self, tool_name: str, parameters: Dict[str, Any],
                       conversation_id: Optional[str] = None) -> str:
        """Start a new tool call and return its ID."""
        if not self.current_session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        if conversation_id is None:
            conversation_id = self.add_conversation(
                MessageType.TOOL_CALL,
                f"Starting tool call: {tool_name}",
                {"tool_name": tool_name, "parameters": parameters}
            )
        
        tool_call = ToolCall.create(
            conversation_id=conversation_id,
            session_id=self.current_session_id,
            tool_name=tool_name,
            parameters=parameters
        )
        
        success = self.db.save_tool_call(tool_call)
        if success:
            self.active_tool_calls[tool_call.id] = tool_call
            
            # Trigger callbacks
            for callback in self.callbacks['tool_call_started']:
                try:
                    callback(tool_call)
                except Exception as e:
                    print(f"Error in tool call started callback: {e}")
            
            return tool_call.id
        else:
            raise RuntimeError("Failed to save tool call to database")

    def complete_tool_call(self, tool_call_id: str, result: Dict[str, Any],
                          duration_ms: Optional[int] = None) -> bool:
        """Mark a tool call as completed with results."""
        success = self.db.update_tool_call(
            tool_call_id=tool_call_id,
            result=result,
            status=ToolCallStatus.COMPLETED,
            duration_ms=duration_ms
        )
        
        if success and tool_call_id in self.active_tool_calls:
            tool_call = self.active_tool_calls[tool_call_id]
            tool_call.result = result
            tool_call.status = ToolCallStatus.COMPLETED
            tool_call.duration_ms = duration_ms
            
            # Add result message to conversation
            self.add_conversation(
                MessageType.TOOL_RESULT,
                f"Tool call completed: {tool_call.tool_name}",
                {"tool_call_id": tool_call_id, "result": result}
            )
            
            # Remove from active calls
            del self.active_tool_calls[tool_call_id]
            
            # Trigger callbacks
            for callback in self.callbacks['tool_call_completed']:
                try:
                    callback(tool_call)
                except Exception as e:
                    print(f"Error in tool call completed callback: {e}")
        
        return success

    def fail_tool_call(self, tool_call_id: str, error_message: str,
                      duration_ms: Optional[int] = None) -> bool:
        """Mark a tool call as failed with error message."""
        success = self.db.update_tool_call(
            tool_call_id=tool_call_id,
            result=None,
            status=ToolCallStatus.FAILED,
            duration_ms=duration_ms,
            error_message=error_message
        )
        
        if success and tool_call_id in self.active_tool_calls:
            tool_call = self.active_tool_calls[tool_call_id]
            tool_call.status = ToolCallStatus.FAILED
            tool_call.error_message = error_message
            tool_call.duration_ms = duration_ms
            
            # Add error message to conversation
            self.add_conversation(
                MessageType.TOOL_RESULT,
                f"Tool call failed: {tool_call.tool_name}",
                {"tool_call_id": tool_call_id, "error": error_message}
            )
            
            # Remove from active calls
            del self.active_tool_calls[tool_call_id]
        
        return success

    @contextmanager
    def tool_call_context(self, tool_name: str, parameters: Dict[str, Any]):
        """Context manager for tool calls with automatic timing and error handling."""
        start_time = datetime.now()
        tool_call_id = self.start_tool_call(tool_name, parameters)
        
        try:
            yield tool_call_id
            # If we get here, the tool call was successful
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.complete_tool_call(tool_call_id, {"success": True}, duration_ms)
        except Exception as e:
            # Tool call failed
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.fail_tool_call(tool_call_id, str(e), duration_ms)
            raise

    def save_context_snapshot(self, snapshot_name: str, state_data: Dict[str, Any],
                            description: Optional[str] = None) -> bool:
        """Save a snapshot of the current context state."""
        if not self.current_session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        snapshot = ContextSnapshot.create(
            session_id=self.current_session_id,
            snapshot_name=snapshot_name,
            state_data=state_data,
            description=description
        )
        
        success = self.db.save_context_snapshot(snapshot)
        if success:
            # Trigger callbacks
            for callback in self.callbacks['context_snapshot_saved']:
                try:
                    callback(snapshot)
                except Exception as e:
                    print(f"Error in context snapshot callback: {e}")
        
        return success

    def load_context_snapshot(self, snapshot_name: str) -> Optional[Dict[str, Any]]:
        """Load a context snapshot."""
        if not self.current_session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        snapshot = self.db.get_context_snapshot(self.current_session_id, snapshot_name)
        return snapshot['state_data'] if snapshot else None

    def push_context(self, context: Dict[str, Any]):
        """Push a new context onto the context stack."""
        self.context_stack.append(context)

    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop the most recent context from the stack."""
        return self.context_stack.pop() if self.context_stack else None

    def get_current_context(self) -> Dict[str, Any]:
        """Get the current context state."""
        return {
            'session_id': self.current_session_id,
            'context_stack': self.context_stack,
            'active_tool_calls': {
                call_id: {
                    'tool_name': call.tool_name,
                    'parameters': call.parameters,
                    'status': call.status.value,
                    'timestamp': call.timestamp.isoformat()
                }
                for call_id, call in self.active_tool_calls.items()
            },
            'timestamp': datetime.now().isoformat()
        }

    def save_generated_file(self, file_path: str, content: str, file_type: str,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save information about a generated file."""
        if not self.current_session_id:
            raise ValueError("No active session. Call start_session() first.")
        
        file_record = GeneratedFile.create(
            session_id=self.current_session_id,
            file_path=file_path,
            content=content,
            file_type=file_type,
            metadata=metadata
        )
        
        success = self.db.save_generated_file(file_record)
        if success:
            # Add to conversation
            self.add_conversation(
                MessageType.SYSTEM,
                f"Generated file: {file_path}",
                {
                    "file_path": file_path,
                    "file_type": file_type,
                    "content_length": len(content),
                    "checksum": file_record.checksum
                }
            )
            
            # Trigger callbacks
            for callback in self.callbacks['file_generated']:
                try:
                    callback(file_record)
                except Exception as e:
                    print(f"Error in file generated callback: {e}")
        
        return success

    def get_conversation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the conversation history for the current session."""
        if not self.current_session_id:
            return []
        
        return self.db.get_conversation_history(self.current_session_id, limit)

    def get_tool_call_statistics(self) -> Dict[str, Any]:
        """Get tool call statistics for the current session."""
        if not self.current_session_id:
            return {}
        
        return self.db.get_tool_call_statistics(self.current_session_id)

    def get_generated_files(self) -> List[Dict[str, Any]]:
        """Get all generated files for the current session."""
        if not self.current_session_id:
            return []
        
        return self.db.get_generated_files(self.current_session_id)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        if not self.current_session_id:
            return {}
        
        return self.db.get_session_summary(self.current_session_id)

    def add_callback(self, event_type: str, callback: Callable):
        """Add a callback for specific events."""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
        else:
            raise ValueError(f"Unknown event type: {event_type}")

    def remove_callback(self, event_type: str, callback: Callable):
        """Remove a callback for specific events."""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)

    def export_session_data(self, output_path: str) -> bool:
        """Export all session data to a JSON file."""
        if not self.current_session_id:
            raise ValueError("No active session to export.")
        
        try:
            data = {
                'session_summary': self.get_session_summary(),
                'conversation_history': self.get_conversation_history(),
                'tool_call_statistics': self.get_tool_call_statistics(),
                'generated_files': self.get_generated_files(),
                'current_context': self.get_current_context()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
        except Exception as e:
            print(f"Error exporting session data: {e}")
            return False

    def cleanup_old_sessions(self, days_to_keep: int = 30) -> bool:
        """Clean up old session data."""
        return self.db.cleanup_old_data(days_to_keep)


# Context manager instance for global use
_context_manager = None

def get_context_manager(db_path: str = "frontend_agent.db") -> ContextManager:
    """Get the global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager(db_path)
    return _context_manager