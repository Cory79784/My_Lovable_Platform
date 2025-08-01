# Frontend Development Agent

一个基于ReAct模式的前端开发智能体，专门用于前端开发任务，使用MCP (Model Context Protocol) 协议进行工具集成。

## 🌟 特性

- **ReAct方法论**: 结合推理(Reasoning)和行动(Acting)的智能决策
- **MCP协议集成**: 使用标准化的Model Context Protocol进行工具调用
- **前端专业化**: 专门针对HTML、CSS、JavaScript和现代前端框架优化
- **上下文管理**: 使用SQLite数据库持久化对话历史和工具调用记录
- **响应式设计**: 支持移动优先的响应式布局设计
- **无障碍访问**: 遵循WCAG标准的可访问性实现
- **性能优化**: 内置前端性能优化建议和工具

## 🏗️ 架构设计

### 核心组件

1. **ReAct Agent**: 实现推理-行动循环的智能体核心
2. **MCP Client**: 与MCP服务器通信的客户端
3. **Context Manager**: 管理对话上下文和持久化存储
4. **Frontend Prompts**: 前端开发专用的提示词系统
5. **Database Layer**: SQLite数据库层，存储会话和工具调用历史

### 工作流程

```
用户输入 → Thought (分析) → Action (执行) → Observation (观察) → 循环直到完成
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+ (用于MCP filesystem server)
- SQLite 3

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装MCP filesystem server
npm install -g @modelcontextprotocol/server-filesystem
```

### 基本使用

#### 交互模式

```bash
python run.py --interactive
```

#### ## 🛠️ 配置

### MCP服务器配置

编辑 `config/mcp_servers.json` 来配置MCP服务器：

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
    "timeout": 30
  },
  "browser": {
    "command": "mcp-browser-server",
    "args": ["--headless"],
    "timeout": 45
  }
}
```

### ## 📁 项目结构

```
frontend-agent/
├── agent/
│   ├── react_agent.py      # ReAct智能体实现
│   ├── mcp_client.py       # MCP客户端
│   └── frontend_prompts.py # 前端提示词管理
├── database/
│   ├── models.py           # 数据库模型
│   └── context_manager.py  # 上下文管理器
├── prompts/
│   ├── design_system       # 设计系统指导
│   ├── component_structure # 组件架构
│   ├── styling_approach    # 样式方法论
│   ├── interaction_patterns# 交互模式
│   └── responsive_design   # 响应式设计
├── config/
│   └── mcp_servers.json    # MCP服务器配置
├── main.py                 # 主入口文件
└── README.md
```

## 