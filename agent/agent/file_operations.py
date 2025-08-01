"""
Direct File Operations Module for Frontend Development Agent / 前端开发代理的直接文件操作模块

This module provides direct file operations without relying on MCP filesystem server, / 此模块提供直接的文件操作，不依赖MCP文件系统服务器，
which can have async issues and dependency problems. / 后者可能存在异步问题和依赖问题
"""

import os
import json
import logging
import shutil
import glob
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import mimetypes
from datetime import datetime


class FileOperationsError(Exception):
    """Base exception for file operations errors. / 文件操作错误的基础异常类"""
    pass


class FileOperations:
    """
    Direct file operations for the Frontend Development Agent. / 前端开发代理的直接文件操作类
    Replaces MCP filesystem server with simple Python file operations. / 用简单的Python文件操作替换MCP文件系统服务器
    """

    def __init__(self, project_root: Optional[str] = None):
        """Initialize file operations. / 初始化文件操作"""
        self.project_root = Path(project_root or os.getcwd())  # 设置项目根目录 / Set project root directory
        self.logger = logging.getLogger("file_operations")      # 初始化日志记录器 / Initialize logger
        
        # Create project directory structure
        self.project_dir = self.project_root / "project"
        self._ensure_project_structure()

    def _ensure_project_structure(self):
        """Ensure project directory structure exists. / 确保项目目录结构存在"""
        directories = [
            self.project_dir,                    
            self.project_dir / "pages",         
            self.project_dir / "components",     
            self.project_dir / "styles",       
            self.project_dir / "scripts",        
            self.project_dir / "assets",        
            self.project_dir / "assets" / "images"  
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)  # 创建目录（如果不存在） / Create directory if not exists
            self.logger.debug(f"Ensured directory exists: {directory}")  # 记录目录创建 / Log directory creation

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to project root or absolute. / 解析相对于项目根目录的路径或绝对路径"""
        path_obj = Path(path)  # 将字符串转换为Path对象 / Convert string to Path object
        
        if path_obj.is_absolute():  # 如果是绝对路径 / If it's an absolute path
            return path_obj
        
        # Check if it's meant to be in project directory / 检查是否应该在项目目录中
        if not str(path_obj).startswith(('..', '/')):
            project_path = self.project_dir / path_obj
            if project_path.parent.exists() or any(part in str(path_obj) for part in ['pages', 'components', 'styles', 'scripts', 'assets']):
                return project_path  # 返回项目目录中的路径 / Return path in project directory
        
        return self.project_root / path_obj  # 返回相对于项目根目录的路径 / Return path relative to project root

    def read_file(self, path: str) -> str:
        """Read file content. / 读取文件内容"""
        try:
            file_path = self._resolve_path(path)  # 解析文件路径 / Resolve file path
            
            if not file_path.exists():  # 检查文件是否存在 / Check if file exists
                raise FileOperationsError(f"File not found: {file_path}")
            
            if not file_path.is_file():  # 检查路径是否为文件 / Check if path is a file
                raise FileOperationsError(f"Path is not a file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:  # 以UTF-8编码打开文件 / Open file with UTF-8 encoding
                content = f.read()  # 读取文件内容 / Read file content
            
            self.logger.info(f"Read file: {file_path} ({len(content)} characters)")  # 记录读取操作 / Log read operation
            return content  # 返回文件内容 / Return file content
            
        except Exception as e:  # 捕获所有异常 / Catch all exceptions
            error_msg = f"Failed to read file {path}: {str(e)}"  # 构建错误消息 / Build error message
            self.logger.error(error_msg)  # 记录错误 / Log error
            raise FileOperationsError(error_msg)  # 抛出自定义异常 / Raise custom exception

    def write_file(self, path: str, content: str) -> bool:
        """Write content to file. / 将内容写入文件"""
        try:
            file_path = self._resolve_path(path)  # 解析文件路径 / Resolve file path
            
            # Create parent directories if they don't exist / 创建父目录（如果不存在）
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:  # 以写入模式打开文件 / Open file in write mode
                f.write(content)  # 写入文件内容 / Write file content
            
            self.logger.info(f"Wrote file: {file_path} ({len(content)} characters)")  # 记录写入操作 / Log write operation
            return True  # 返回成功状态 / Return success status
            
        except Exception as e:  # 捕获所有异常 / Catch all exceptions
            error_msg = f"Failed to write file {path}: {str(e)}"  # 构建错误消息 / Build error message
            self.logger.error(error_msg)  # 记录错误 / Log error
            raise FileOperationsError(error_msg)  # 抛出自定义异常 / Raise custom exception

    def create_directory(self, path: str) -> bool:
        """Create directory. / 创建目录"""
        try:
            dir_path = self._resolve_path(path)  # 解析目录路径 / Resolve directory path
            dir_path.mkdir(parents=True, exist_ok=True)  # 创建目录（包括父目录） / Create directory including parent directories
            
            self.logger.info(f"Created directory: {dir_path}")  # 记录目录创建 / Log directory creation
            return True  # 返回成功状态 / Return success status
            
        except Exception as e:  # 捕获所有异常 / Catch all exceptions
            error_msg = f"Failed to create directory {path}: {str(e)}"  # 构建错误消息 / Build error message
            self.logger.error(error_msg)  # 记录错误 / Log error
            raise FileOperationsError(error_msg)  # 抛出自定义异常 / Raise custom exception

    def list_directory(self, path: str = ".") -> List[Dict[str, Any]]:
        """List directory contents with file information. / 列出目录内容及文件信息"""
        try:
            dir_path = self._resolve_path(path)  # 解析目录路径 / Resolve directory path
            
            if not dir_path.exists():  # 检查目录是否存在 / Check if directory exists
                raise FileOperationsError(f"Directory not found: {dir_path}")
            
            if not dir_path.is_dir():  # 检查路径是否为目录 / Check if path is a directory
                raise FileOperationsError(f"Path is not a directory: {dir_path}")
            
            items = []  # 存储目录项列表 / Store list of directory items
            for item in dir_path.iterdir():  # 遍历目录中的所有项目 / Iterate through all items in directory
                try:
                    stat = item.stat()  # 获取文件状态信息 / Get file status information
                    mime_type, _ = mimetypes.guess_type(str(item))  # 猜测MIME类型 / Guess MIME type
                    
                    items.append({
                        "name": item.name,  # 项目名称 / Item name
                        "path": str(item.relative_to(self.project_root)),  # 相对路径 / Relative path
                        "type": "directory" if item.is_dir() else "file",  # 项目类型 / Item type
                        "size": stat.st_size if item.is_file() else None,  # 文件大小 / File size
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),  # 修改时间 / Modification time
                        "mime_type": mime_type  # MIME类型 / MIME type
                    })
                except Exception as e:
                    self.logger.warning(f"Error getting info for {item}: {e}")  # 记录获取信息错误 / Log error getting info
            
            # Sort by type (directories first) then by name / 按类型排序（目录在前）然后按名称排序
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            self.logger.info(f"Listed directory: {dir_path} ({len(items)} items)")  # 记录目录列表操作 / Log directory listing operation
            return items  # 返回目录项列表 / Return directory items list
            
        except Exception as e:  # 捕获所有异常 / Catch all exceptions
            error_msg = f"Failed to list directory {path}: {str(e)}"  # 构建错误消息 / Build error message
            self.logger.error(error_msg)  # 记录错误 / Log error
            raise FileOperationsError(error_msg)  # 抛出自定义异常 / Raise custom exception

    def move_file(self, source: str, destination: str) -> bool:
        """Move/rename file or directory. / 移动/重命名文件或目录"""
        try:
            source_path = self._resolve_path(source)
            dest_path = self._resolve_path(destination)
            
            if not source_path.exists():  # 检查源路径是否存在 / Check if source path exists
                raise FileOperationsError(f"Source not found: {source_path}")
            
            # Create destination parent directories / 创建目标父目录
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))  # 移动文件或目录 / Move file or directory
            
            self.logger.info(f"Moved: {source_path} -> {dest_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to move {source} to {destination}: {str(e)}"
            self.logger.error(error_msg)
            raise FileOperationsError(error_msg)

    def copy_file(self, source: str, destination: str) -> bool:
        """Copy file or directory. / 复制文件或目录"""
        try:
            source_path = self._resolve_path(source)
            dest_path = self._resolve_path(destination)
            
            if not source_path.exists():
                raise FileOperationsError(f"Source not found: {source_path}")
            
            # Create destination parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_file():  # 如果是文件 / If it's a file
                shutil.copy2(str(source_path), str(dest_path))  # 复制文件（保留元数据） / Copy file (preserve metadata)
            else:  # 如果是目录 / If it's a directory
                shutil.copytree(str(source_path), str(dest_path), dirs_exist_ok=True)  # 复制目录树 / Copy directory tree
            
            self.logger.info(f"Copied: {source_path} -> {dest_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to copy {source} to {destination}: {str(e)}"
            self.logger.error(error_msg)
            raise FileOperationsError(error_msg)

    def delete_file(self, path: str) -> bool:
        """Delete file or directory. / 删除文件或目录"""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                raise FileOperationsError(f"Path not found: {file_path}")
            
            if file_path.is_file():  # 如果是文件 / If it's a file
                file_path.unlink()  # 删除文件 / Delete file
            else:  # 如果是目录 / If it's a directory
                shutil.rmtree(str(file_path))  # 删除目录树 / Delete directory tree
            
            self.logger.info(f"Deleted: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete {path}: {str(e)}"
            self.logger.error(error_msg)
            raise FileOperationsError(error_msg)

    def search_files(self, pattern: str, path: str = ".", include_content: bool = False) -> List[Dict[str, Any]]:
        """Search for files matching pattern. / 搜索匹配模式的文件"""
        try:
            search_path = self._resolve_path(path)
            
            if not search_path.exists():
                raise FileOperationsError(f"Search path not found: {search_path}")
            
            results = []  # 存储搜索结果 / Store search results
            
            # Use glob for file name pattern matching / 使用glob进行文件名模式匹配
            pattern_path = search_path / "**" / pattern
            for file_path in glob.glob(str(pattern_path), recursive=True):  # 递归搜索匹配的文件 / Recursively search for matching files
                file_obj = Path(file_path)
                if file_obj.is_file():  # 只处理文件 / Only process files
                    try:
                        stat = file_obj.stat()
                        result = {
                            "path": str(file_obj.relative_to(self.project_root)),  # 相对路径 / Relative path
                            "name": file_obj.name,  # 文件名 / File name
                            "size": stat.st_size,  # 文件大小 / File size
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()  # 修改时间 / Modification time
                        }
                        
                        if include_content:  # 如果需要包含文件内容 / If content should be included
                            try:
                                with open(file_obj, 'r', encoding='utf-8') as f:  # 读取文件内容 / Read file content
                                    result["content"] = f.read()
                            except Exception:  # 如果读取失败 / If reading fails
                                result["content"] = "[Binary or unreadable file]"  # 标记为不可读文件 / Mark as unreadable file
                        
                        results.append(result)  # 添加到结果列表 / Add to results list
                    except Exception as e:
                        self.logger.warning(f"Error processing {file_path}: {e}")
            
            self.logger.info(f"Found {len(results)} files matching pattern '{pattern}' in {search_path}")
            return results
            
        except Exception as e:
            error_msg = f"Failed to search files with pattern {pattern}: {str(e)}"
            self.logger.error(error_msg)
            raise FileOperationsError(error_msg)

    def file_exists(self, path: str) -> bool:
        """Check if file exists. / 检查文件是否存在"""
        try:
            file_path = self._resolve_path(path)
            return file_path.exists()
        except Exception:
            return False

    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get detailed file information. / 获取详细的文件信息"""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                raise FileOperationsError(f"File not found: {file_path}")
            
            stat = file_path.stat()  # 获取文件状态信息 / Get file status information
            mime_type, encoding = mimetypes.guess_type(str(file_path))  # 猜测MIME类型和编码 / Guess MIME type and encoding
            
            return {
                "path": str(file_path.relative_to(self.project_root)),  # 相对路径 / Relative path
                "name": file_path.name, 
                "type": "directory" if file_path.is_dir() else "file",  
                "size": stat.st_size,  
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),  
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),  
                "mime_type": mime_type,  # MIME类型 / MIME type
                "encoding": encoding,  # 编码 / Encoding
                "extension": file_path.suffix,  # 文件扩展名 / File extension
                "parent": str(file_path.parent.relative_to(self.project_root))  # 父目录 / Parent directory
            }
            
        except Exception as e:
            error_msg = f"Failed to get file info for {path}: {str(e)}"
            self.logger.error(error_msg)
            raise FileOperationsError(error_msg)

    def create_project_file(self, file_type: str, name: str, content: str) -> str:
        """Create a file in the appropriate project subdirectory."""
        type_mapping = {  # 文件类型到目录的映射 / File type to directory mapping
            "html": "pages",      # HTML文件放在pages目录 / HTML files go to pages directory
            "page": "pages",      # 页面文件放在pages目录 / Page files go to pages directory
            "css": "styles",      # CSS文件放在styles目录 / CSS files go to styles directory
            "style": "styles",    # 样式文件放在styles目录 / Style files go to styles directory
            "js": "scripts",      # JavaScript文件放在scripts目录 / JavaScript files go to scripts directory
            "javascript": "scripts",  # JS文件放在scripts目录 / JS files go to scripts directory
            "script": "scripts",  # 脚本文件放在scripts目录 / Script files go to scripts directory
            "component": "components"  # 组件文件放在components目录 / Component files go to components directory
        }
        
        subdir = type_mapping.get(file_type.lower(), "pages")  # 获取对应的子目录 / Get corresponding subdirectory
        
        # Add appropriate file extension if not present / 如果没有扩展名则添加适当的文件扩展名
        if file_type.lower() in ["html", "page"] and not name.endswith(".html"):  # HTML文件添加.html扩展名 / Add .html extension for HTML files
            name += ".html"
        elif file_type.lower() in ["css", "style"] and not name.endswith(".css"):  # CSS文件添加.css扩展名 / Add .css extension for CSS files
            name += ".css"
        elif file_type.lower() in ["js", "javascript", "script"] and not name.endswith(".js"):  # JS文件添加.js扩展名 / Add .js extension for JS files
            name += ".js"
        
        file_path = f"project/{subdir}/{name}"  # 构建完整的文件路径 / Build complete file path
        self.write_file(file_path, content)  # 写入文件内容 / Write file content
        
        return file_path

    def get_project_structure(self) -> Dict[str, Any]:
        """Get the complete project directory structure."""
        def build_tree(path: Path) -> Dict[str, Any]:  # 构建目录树的内部函数 / Internal function to build directory tree
            if not path.exists():  # 如果路径不存在 / If path doesn't exist
                return {}
            
            result = {
                "name": path.name,  # 项目名称 / Item name
                "type": "directory" if path.is_dir() else "file",  # 项目类型 / Item type
                "path": str(path.relative_to(self.project_root))  # 相对路径 / Relative path
            }
            
            if path.is_dir():  # 如果是目录 / If it's a directory
                result["children"] = []  # 初始化子项目列表 / Initialize children list
                try:
                    for child in sorted(path.iterdir()):  # 遍历排序后的子项目 / Iterate through sorted children
                        result["children"].append(build_tree(child))  # 递归构建子目录树 / Recursively build child tree
                except PermissionError:  # 如果权限被拒绝 / If permission denied
                    result["error"] = "Permission denied"  # 记录权限错误 / Log permission error
            else:  # 如果是文件 / If it's a file
                try:
                    stat = path.stat()  # 获取文件状态 / Get file status
                    result["size"] = stat.st_size  # 文件大小 / File size
                    result["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()  # 修改时间 / Modification time
                except Exception:  # 如果获取信息失败 / If getting info fails
                    pass  # 忽略错误 / Ignore error
            
            return result  # 返回构建的树结构 / Return built tree structure
        
        return build_tree(self.project_dir)


# Global instance / 全局实例
_file_ops_instance: Optional[FileOperations] = None


def get_file_operations(project_root: Optional[str] = None) -> FileOperations:
    """Get the global FileOperations instance. / 获取全局FileOperations实例"""
    global _file_ops_instance  # 声明全局变量 / Declare global variable
    if _file_ops_instance is None:  # 如果实例不存在 / If instance doesn't exist
        _file_ops_instance = FileOperations(project_root)  # 创建新实例 / Create new instance
    return _file_ops_instance  # 返回全局实例 / Return global instance