"""
SQLite database models for Frontend Development Agent / 前端开发代理的SQLite数据库模型

This module defines the database schema for storing conversation history, / 此模块定义了用于存储对话历史、
tool calls, context snapshots, and generated files. / 工具调用、上下文快照和生成文件的数据库模式
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum


class MessageType(Enum):
    """Enumeration for message types in conversations. / 对话中消息类型的枚举"""
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class ToolCallStatus(Enum):
    """Enumeration for tool call status. / 工具调用状态的枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Conversation:
    """Data class representing a conversation record. / 表示对话记录的数据类"""
    id: str
    session_id: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    parent_id: Optional[str] = None

    @classmethod
    def create(cls, session_id: str, message_type: MessageType, content: str, 
               metadata: Optional[Dict[str, Any]] = None, parent_id: Optional[str] = None):
        """Create a new conversation record. / 创建新的对话记录"""
        return cls(
            id=str(uuid.uuid4()),
            session_id=session_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
            parent_id=parent_id
        )


@dataclass
class ToolCall:
    """Data class representing a tool call record. / 表示工具调用记录的数据类"""
    id: str
    conversation_id: str
    session_id: str
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    status: ToolCallStatus
    duration_ms: Optional[int]
    error_message: Optional[str]
    timestamp: datetime

    @classmethod
    def create(cls, conversation_id: str, session_id: str, tool_name: str, 
               parameters: Dict[str, Any]):
        """Create a new tool call record. / 创建新的工具调用记录"""
        return cls(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            session_id=session_id,
            tool_name=tool_name,
            parameters=parameters,
            result=None,
            status=ToolCallStatus.PENDING,
            duration_ms=None,
            error_message=None,
            timestamp=datetime.now()
        )


@dataclass
class ContextSnapshot:
    """Data class representing a context snapshot. / 表示上下文快照的数据类"""
    id: str
    session_id: str
    snapshot_name: str
    state_data: Dict[str, Any]
    description: Optional[str]
    created_at: datetime

    @classmethod
    def create(cls, session_id: str, snapshot_name: str, state_data: Dict[str, Any],
               description: Optional[str] = None):
        """Create a new context snapshot. / 创建新的上下文快照"""
        return cls(
            id=str(uuid.uuid4()),
            session_id=session_id,
            snapshot_name=snapshot_name,
            state_data=state_data,
            description=description,
            created_at=datetime.now()
        )


@dataclass
class GeneratedFile:
    """Data class representing a generated file record. / 表示生成文件记录的数据类"""
    id: str
    session_id: str
    file_path: str
    content: str
    file_type: str
    version: int
    checksum: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, session_id: str, file_path: str, content: str, 
               file_type: str, metadata: Optional[Dict[str, Any]] = None):
        """Create a new generated file record. / 创建新的生成文件记录"""
        import hashlib
        checksum = hashlib.sha256(content.encode()).hexdigest()
        
        return cls(
            id=str(uuid.uuid4()),
            session_id=session_id,
            file_path=file_path,
            content=content,
            file_type=file_type,
            version=1,
            checksum=checksum,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )


class DatabaseManager:
    """Database manager for the Frontend Development Agent. / 前端开发代理的数据库管理器"""

    def __init__(self, db_path: Union[str, Path] = "frontend_agent.db"):
        """Initialize the database manager."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self._get_schema())

    def _get_schema(self) -> str:
        """Get the database schema SQL."""
        return """
        -- Enable foreign key constraints
        PRAGMA foreign_keys = ON;

        -- Conversations table
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            message_type TEXT NOT NULL CHECK (message_type IN ('human', 'ai', 'system', 'tool_call', 'tool_result')),
            content TEXT NOT NULL,
            metadata TEXT NOT NULL DEFAULT '{}',
            timestamp DATETIME NOT NULL,
            parent_id TEXT,
            FOREIGN KEY (parent_id) REFERENCES conversations (id)
        );

        -- Tool calls table
        CREATE TABLE IF NOT EXISTS tool_calls (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            parameters TEXT NOT NULL,
            result TEXT,
            status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
            duration_ms INTEGER,
            error_message TEXT,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        );

        -- Context snapshots table
        CREATE TABLE IF NOT EXISTS context_snapshots (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            snapshot_name TEXT NOT NULL,
            state_data TEXT NOT NULL,
            description TEXT,
            created_at DATETIME NOT NULL
        );

        -- Generated files table
        CREATE TABLE IF NOT EXISTS generated_files (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            content TEXT NOT NULL,
            file_type TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            checksum TEXT NOT NULL,
            metadata TEXT NOT NULL DEFAULT '{}',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        );

        -- Indexes for better query performance
        CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations (session_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations (timestamp);
        CREATE INDEX IF NOT EXISTS idx_tool_calls_session_id ON tool_calls (session_id);
        CREATE INDEX IF NOT EXISTS idx_tool_calls_status ON tool_calls (status);
        CREATE INDEX IF NOT EXISTS idx_context_snapshots_session_id ON context_snapshots (session_id);
        CREATE INDEX IF NOT EXISTS idx_generated_files_session_id ON generated_files (session_id);
        CREATE INDEX IF NOT EXISTS idx_generated_files_path ON generated_files (file_path);
        """

    def _dict_factory(self, cursor, row):
        """Convert row to dictionary."""
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self._dict_factory
        return conn

    # Conversation methods
    def save_conversation(self, conversation: Conversation) -> bool:
        """Save a conversation record to the database."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO conversations 
                    (id, session_id, message_type, content, metadata, timestamp, parent_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation.id,
                    conversation.session_id,
                    conversation.message_type.value,
                    conversation.content,
                    json.dumps(conversation.metadata),
                    conversation.timestamp.isoformat(),
                    conversation.parent_id
                ))
                return True
        except sqlite3.Error as e:
            print(f"Error saving conversation: {e}")
            return False

    def get_conversation_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            for row in rows:
                row['metadata'] = json.loads(row['metadata'])
                row['message_type'] = MessageType(row['message_type'])
            
            return list(reversed(rows))  # Return in chronological order

    # Tool call methods
    def save_tool_call(self, tool_call: ToolCall) -> bool:
        """Save a tool call record to the database."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO tool_calls 
                    (id, conversation_id, session_id, tool_name, parameters, result, 
                     status, duration_ms, error_message, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tool_call.id,
                    tool_call.conversation_id,
                    tool_call.session_id,
                    tool_call.tool_name,
                    json.dumps(tool_call.parameters),
                    json.dumps(tool_call.result) if tool_call.result else None,
                    tool_call.status.value,
                    tool_call.duration_ms,
                    tool_call.error_message,
                    tool_call.timestamp.isoformat()
                ))
                return True
        except sqlite3.Error as e:
            print(f"Error saving tool call: {e}")
            return False

    def update_tool_call(self, tool_call_id: str, result: Dict[str, Any], 
                        status: ToolCallStatus, duration_ms: int = None,
                        error_message: str = None) -> bool:
        """Update a tool call with results."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE tool_calls 
                    SET result = ?, status = ?, duration_ms = ?, error_message = ?
                    WHERE id = ?
                """, (
                    json.dumps(result) if result else None,
                    status.value,
                    duration_ms,
                    error_message,
                    tool_call_id
                ))
                return True
        except sqlite3.Error as e:
            print(f"Error updating tool call: {e}")
            return False

    def get_tool_call_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get tool call statistics for a session."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    tool_name,
                    COUNT(*) as total_calls,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_calls,
                    AVG(duration_ms) as avg_duration_ms
                FROM tool_calls 
                WHERE session_id = ?
                GROUP BY tool_name
            """, (session_id,))
            
            return {row['tool_name']: {
                'total_calls': row['total_calls'],
                'successful_calls': row['successful_calls'],
                'avg_duration_ms': row['avg_duration_ms']
            } for row in cursor.fetchall()}

    # Context snapshot methods
    def save_context_snapshot(self, snapshot: ContextSnapshot) -> bool:
        """Save a context snapshot."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO context_snapshots 
                    (id, session_id, snapshot_name, state_data, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    snapshot.id,
                    snapshot.session_id,
                    snapshot.snapshot_name,
                    json.dumps(snapshot.state_data),
                    snapshot.description,
                    snapshot.created_at.isoformat()
                ))
                return True
        except sqlite3.Error as e:
            print(f"Error saving context snapshot: {e}")
            return False

    def get_context_snapshot(self, session_id: str, snapshot_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific context snapshot."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM context_snapshots 
                WHERE session_id = ? AND snapshot_name = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (session_id, snapshot_name))
            
            row = cursor.fetchone()
            if row:
                row['state_data'] = json.loads(row['state_data'])
                return row
            return None

    # Generated files methods
    def save_generated_file(self, file_record: GeneratedFile) -> bool:
        """Save a generated file record."""
        try:
            with self._get_connection() as conn:
                # Check if file already exists
                cursor = conn.execute("""
                    SELECT version FROM generated_files 
                    WHERE session_id = ? AND file_path = ?
                    ORDER BY version DESC
                    LIMIT 1
                """, (file_record.session_id, file_record.file_path))
                
                existing = cursor.fetchone()
                if existing:
                    file_record.version = existing['version'] + 1
                
                conn.execute("""
                    INSERT INTO generated_files 
                    (id, session_id, file_path, content, file_type, version, 
                     checksum, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_record.id,
                    file_record.session_id,
                    file_record.file_path,
                    file_record.content,
                    file_record.file_type,
                    file_record.version,
                    file_record.checksum,
                    json.dumps(file_record.metadata),
                    file_record.created_at.isoformat(),
                    file_record.updated_at.isoformat()
                ))
                return True
        except sqlite3.Error as e:
            print(f"Error saving generated file: {e}")
            return False

    def get_generated_files(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all generated files for a session."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM generated_files 
                WHERE session_id = ?
                ORDER BY file_path, version DESC
            """, (session_id,))
            
            rows = cursor.fetchall()
            for row in rows:
                row['metadata'] = json.loads(row['metadata'])
            
            return rows

    def get_file_versions(self, session_id: str, file_path: str) -> List[Dict[str, Any]]:
        """Get all versions of a specific file."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM generated_files 
                WHERE session_id = ? AND file_path = ?
                ORDER BY version DESC
            """, (session_id, file_path))
            
            rows = cursor.fetchall()
            for row in rows:
                row['metadata'] = json.loads(row['metadata'])
            
            return rows

    # Utility methods
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old data older than specified days."""
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
            
            with self._get_connection() as conn:
                # Clean up old conversations
                conn.execute("""
                    DELETE FROM conversations 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                # Clean up old tool calls
                conn.execute("""
                    DELETE FROM tool_calls 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                # Clean up old context snapshots
                conn.execute("""
                    DELETE FROM context_snapshots 
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))
                
                # Clean up old generated files (keep latest version)
                conn.execute("""
                    DELETE FROM generated_files 
                    WHERE created_at < ? AND id NOT IN (
                        SELECT id FROM generated_files gf1
                        WHERE gf1.file_path = generated_files.file_path
                        AND gf1.session_id = generated_files.session_id
                        ORDER BY version DESC
                        LIMIT 1
                    )
                """, (cutoff_date.isoformat(),))
                
                return True
        except sqlite3.Error as e:
            print(f"Error cleaning up old data: {e}")
            return False

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of session activity."""
        with self._get_connection() as conn:
            # Get conversation count
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM conversations WHERE session_id = ?
            """, (session_id,))
            conversation_count = cursor.fetchone()['count']
            
            # Get tool call count
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM tool_calls WHERE session_id = ?
            """, (session_id,))
            tool_call_count = cursor.fetchone()['count']
            
            # Get generated file count
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT file_path) as count FROM generated_files WHERE session_id = ?
            """, (session_id,))
            file_count = cursor.fetchone()['count']
            
            # Get session timespan
            cursor = conn.execute("""
                SELECT MIN(timestamp) as start_time, MAX(timestamp) as end_time
                FROM conversations WHERE session_id = ?
            """, (session_id,))
            timespan = cursor.fetchone()
            
            return {
                'session_id': session_id,
                'conversation_count': conversation_count,
                'tool_call_count': tool_call_count,
                'generated_file_count': file_count,
                'start_time': timespan['start_time'],
                'end_time': timespan['end_time']
            }