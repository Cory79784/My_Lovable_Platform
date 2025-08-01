# My Lovable Platform

This project is my own way to reproduce the core workflow of [lovable.dev](https://lovable.dev/) — A comprehensive AI-powered development platform that integrates gpt-engineer with streaming capabilities and real-time project preview using iframes. Not affiliated with the original Lovable.

## 🚀 Features

### Core Functionality
- **Multi-dialogue Chat System** - Support for multiple concurrent chat sessions
- **agent Integration** - Using self defined agent in reAct paradigm 
- **Streaming Logs** - Real-time output streaming from my own agent to frontend
- **Iframe Project Preview** - Automatic display and refresh of generated projects
- **File Upload & Processing** - Support for PDF, DOCX, Excel, and CSV files
- **Vector Database Integration** - RAG (Retrieval-Augmented Generation) capabilities (waiting for integrated).
- **Semantic shadcn/ui wrapper**: Aim to ensure a consistent look and feel, improving visual quality  

### Project Preview Features
- **Automatic Refresh** - Iframe automatically refreshes after each generation
- **Real-time Updates** - Polling for project updates during generation
- **File Browser** - Display generated files with main file detection
- **External Preview** - Open projects in new tabs
- **Error Handling** - Graceful error handling and retry mechanisms

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                        │
│  - Multi-dialogue chat interface                          │
│  - Project preview with iframe                            │
│  - Real-time streaming display                            │
├─────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI)                       │
│  - Chat routes with streaming                             │
│  - Project file serving and preview                       │
├─────────────────────────────────────────────────────────────┤
│                    Agent                                  │
│  - Project generation from prompts                        │
│  - File system output                                     │
└─────────────────────────────────────────────────────────────┘
backend and agent waiting for integration in unified fastAPI
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Create `.env` file in backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🧪 Test Cases

### 1. Basic Project Generation
**Test Case:** Generate a simple HTML project
```bash
# Backend test
curl -X POST "http://localhost:8000/chat/generate-project" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "test_html_project",
    "prompt": "Create a simple HTML page with a header, navigation, and footer"
  }'
```

**Expected Result:**
- Project directory created in `gpt_projects/test_html_project/`
- HTML file generated with basic structure
- Iframe preview displays the generated page

### 2. Streaming Project Generation
**Test Case:** Generate project with streaming output

```bash
# Backend test
curl -X POST "http://localhost:8000/chat/generate-project/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "test_streaming_project",
    "prompt": "Create a React todo app with add, delete, and mark complete functionality"
  }'
```

**Expected Result:**
- Real-time streaming of gpt-engineer output
- Frontend receives and displays streaming logs
- Project files generated progressively
- Iframe updates automatically when generation completes

### 3. Multi-dialogue Chat
**Test Case:** Create multiple chat sessions
```bash
# Create new chat
curl -X POST "http://localhost:8000/chat/new_chat"

# Send message to chat
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "generated_chat_id",
    "message": "Create a weather dashboard"
  }'
```

**Expected Result:**
- Multiple chat sessions maintained independently
- Each chat has its own project generation
- Iframe previews specific to each chat session

### 4. File Upload and RAG
**Test Case:** Upload document and use RAG
```bash
# Upload file
curl -X POST "http://localhost:8000/upload/chat_id" \
  -F "file=@document.pdf"

# Chat with RAG
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "chat_id",
    "message": "Based on the uploaded document, create a summary page"
  }'
```

**Expected Result:**
- File processed and stored in vector database
- RAG-enabled responses based on document content
- Generated project incorporates document information

### 5. Iframe Preview Functionality
**Test Case:** Test iframe auto-refresh and display
```javascript
// Frontend test
const projectName = "test_iframe_project";
const previewComponent = <ProjectPreview projectName={projectName} isGenerating={true} />;
```

**Expected Result:**
- Iframe displays project preview
- Automatic refresh every 2 seconds during generation
- Manual refresh button works
- External link opens project in new tab
- Error handling for missing projects

### 6. Project File Serving
**Test Case:** Access project files via API
```bash
# List projects
curl "http://localhost:8000/api/projects"

# Get project info
curl "http://localhost:8000/api/projects/test_project"

# Get project files
curl "http://localhost:8000/api/projects/test_project/files"

# Get specific file
curl "http://localhost:8000/api/projects/test_project/files/index.html"

# Get project preview
curl "http://localhost:8000/api/projects/test_project/preview"
```

**Expected Result:**
- Project listing returns all generated projects
- Project info includes file list and main file
- File serving works for all project files
- Preview endpoint returns HTML for iframe display

### 7. Error Handling
**Test Case:** Test various error scenarios
```bash
# Non-existent project
curl "http://localhost:8000/api/projects/nonexistent_project"

# Invalid file path
curl "http://localhost:8000/api/projects/test_project/files/../../../etc/passwd"

# gpt-engineer failure
curl -X POST "http://localhost:8000/chat/generate-project" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "test_error_project",
    "prompt": "invalid prompt that causes gpt-engineer to fail"
  }'
```

**Expected Result:**
- 404 errors for non-existent projects
- 403 errors for path traversal attempts
- Graceful handling of gpt-engineer failures
- Frontend displays appropriate error messages

### 8. Performance Testing
**Test Case:** Test with large projects
```bash
# Generate large project
curl -X POST "http://localhost:8000/chat/generate-project" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "large_project",
    "prompt": "Create a full-stack web application with user authentication, database, API, and frontend"
  }'
```

**Expected Result:**
- Generation completes without timeout
- Iframe loads large projects efficiently
- File browser handles many files
- Memory usage remains reasonable

## 🔧 API Endpoints

### Chat Routes
- `POST /chat/` - Send message and get streaming response
- `POST /chat/new_chat` - Create new chat session
- `GET /chat/chats` - List all chat sessions
- `GET /chat/{chat_id}` - Get chat history
- `DELETE /chat/{chat_id}` - Delete chat session
- `POST /chat/generate-project` - Generate project (non-streaming)
- `POST /chat/generate-project/stream` - Generate project (streaming)

### Project Routes
- `GET /api/projects` - List all projects
- `GET /api/projects/{project_name}` - Get project info
- `GET /api/projects/{project_name}/files` - List project files
- `GET /api/projects/{project_name}/files/{file_path}` - Get specific file
- `GET /api/projects/{project_name}/preview` - Get project preview
- `DELETE /api/projects/{project_name}` - Delete project
- `POST /api/projects/{project_name}/serve` - Serve project

### File Upload Routes
- `POST /upload/{chat_id}` - Upload file for chat session

## 🎯 Usage Examples

### 1. Generate a Simple Website
```javascript
// Frontend
const prompt = "Create a personal portfolio website with about, projects, and contact sections";
const projectName = `project_${Date.now()}`;

const response = await fetch("http://localhost:8000/chat/generate-project/stream", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt, project_name: projectName })
});

// Iframe will automatically display the generated website
```

### 2. Create a React Application
```javascript
const prompt = "Build a React todo app with TypeScript, Tailwind CSS, and local storage";
// Project will be generated and displayed in iframe
```

### 3. Generate API Documentation
```javascript
const prompt = "Create a REST API documentation page with examples and interactive testing";
// Documentation site will be generated and previewed
```

## 🐛 Troubleshooting

### Common Issues

1. **Iframe not loading**
   - Check CORS settings
   - Verify project files exist
   - Check browser console for errors

2. **Streaming not working**
   
   - Ensure backend is running on correct port
   - Check network connectivity
   - Verify streaming response headers
   
33. **Project preview not updating**
   - Check iframe refresh interval
   - Verify project generation completed
   - Check file permissions

### Debug Commands
```bash
# Check if gpt-engineer is installed
which gpt-engineer

# Test project generation manually
cd gpt_projects
gpt-engineer test_project

# Check backend logs
tail -f backend/logs/app.log
Get-Content backend/logs/app.log -Wait

# Test API endpoints
curl -v "http://localhost:8000/api/projects"
```

## 📈 Performance Metrics

### Benchmarks
- **Project Generation**: 30-120 seconds (depending on complexity)
- **Iframe Load Time**: < 2 seconds
- **Streaming Latency**: < 100ms
- **File Serving**: < 50ms per file

### Monitoring
- Monitor gpt-engineer process memory usage
- Track iframe refresh frequency
- Monitor API response times
- Check for memory leaks in long-running sessions

## 🔮 Future Enhancements

1. **Real-time Collaboration** - Multiple users editing same project
2. **Project Templates** - Pre-built templates for common use cases
3. **Version Control** - Git integration for project history
4. **Deployment Integration** - Direct deployment to hosting platforms
5. **Advanced Preview** - Live editing in iframe
6. **Project Analytics** - Usage statistics and performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Current Issues / Blockers

1. Integration with Agent
   - Current implementation relies on CLI calls via `subprocess`, which is fragile and error-prone.  


2. Iframe Rendering for Complex Builds  
   - Simple static builds render correctly, but framework-based builds fail.  
   - Causes include routing issues, absolute asset paths, and CSP restrictions.  
   - work around: Requires additional build configuration or running a local server.




# My own way of doing an Agent

An intelligent agent based on the ReAct pattern, specifically designed for frontend development tasks, utilizing built-in Python tools for file operations and development support.

## 🌟 Features

- **ReAct Methodology**: Combines reasoning (Reasoning) and acting (Acting) for intelligent decision-making
- **Built-in Tool Integration**: Uses built-in Python functions for file operations, content search, and command execution
- **Frontend Specialization**: Optimized for HTML, CSS, JavaScript, and modern frontend frameworks
- **Context Management**: Uses an SQLite database to persist conversation history and tool call records
- **System Environment Awareness**: Automatically detects OS, shell environment, and available tools
- **Responsive Design**: Supports mobile-first responsive layout design
- **Accessibility Support**: Implements accessibility following WCAG (Web Content Accessibility Guidelines) standards
- **Performance Optimization**: Provides built-in frontend performance optimization suggestions and tools

## 🏗️ Architecture Design

### Core Components

1. **ReAct Agent**: The core intelligent agent implementing the reasoning–acting loop
2. **File Operations**: Built-in file operation system replacing MCP dependencies
3. **Context Manager**: Manages conversation context and persistent storage
4. **Frontend Prompts**: Prompt system specialized for frontend development
5. **Database Layer**: SQLite database layer storing session and tool call history

### Built-in Tools

- **read_file**: Reads file content
- **write_file**: Creates or updates files
- **delete_file**: Deletes files or directories
- **list_dir**: Lists directory contents and file information
- **grep**: Searches text content within directories (supports regular expressions)
- **bash**: Executes shell commands (with safety checks)

### Workflow

```
imput → Thought (analysis) → Action (tool calling) → Observation (obervation result) → cycle until finish
```



Data Flow

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    User Input   │ ────▶ │   ReAct Agent   │ ────▶│   Built-in Tools │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                 │                          │
                                 ▼                          ▼
                       ┌─────────────────┐       ┌─────────────────┐
                       │ Context Manager │       │ File Operations │
                       └─────────────────┘       └─────────────────┘
                                 │                          │
                                 ▼                          ▼
                       ┌─────────────────┐       ┌─────────────────┐
                       │ SQLite Database │       │  Project Files  │
                       └─────────────────┘       └─────────────────┘
```



Database Schema

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                  Frontend Development Agent Database Schema                  │
│                        (Session-based Context Storage)                       │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Conversations (Conversation Records)                                         │
│──────────────────────────────────────────────────────────────────────────────│
│ id (TEXT PRIMARY KEY)        # Unique conversation message ID                │
│ session_id (TEXT NOT NULL)   # Session this message belongs to               │
│ message_type (TEXT NOT NULL) # human | ai | system | tool_call | tool_result │
│ content (TEXT NOT NULL)      # Message content text                          │
│ metadata (TEXT DEFAULT '{}') # JSON metadata (context, tags, etc.)           │
│ timestamp (DATETIME NOT NULL)# Message creation time                         │
│ parent_id (TEXT)             # Optional: links to parent message (self FK)   │
│ FOREIGN KEY(parent_id) → conversations(id)                                   │
└──────────────────────────────────────────────────────────────────────────────┘
                     │
                     │ 1
                     │
                     │ N
┌──────────────────────────────────────────────────────────────────────────────┐
│ Tool Calls (Tool Invocation Records)                                         │
│──────────────────────────────────────────────────────────────────────────────│
│ id (TEXT PRIMARY KEY)        # Unique tool call ID                           │
│ conversation_id (TEXT NOT NULL) # Links to triggering conversation message   │
│ session_id (TEXT NOT NULL)   # Session this tool call belongs to             │
│ tool_name (TEXT NOT NULL)    # Name of invoked tool                          │
│ parameters (TEXT NOT NULL)   # Input parameters (JSON)                       │
│ result (TEXT)                # Execution result (JSON)                       │
│ status (TEXT NOT NULL)       # pending | in_progress | completed | failed    │
│ duration_ms (INTEGER)        # Execution time in milliseconds                │
│ error_message (TEXT)         # Optional error info                           │
│ timestamp (DATETIME NOT NULL)# Time of execution                             │
│ FOREIGN KEY(conversation_id) → conversations(id)                             │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Context Snapshots (Context State Snapshots)                                  │
│──────────────────────────────────────────────────────────────────────────────│
│ id (TEXT PRIMARY KEY)        # Unique snapshot ID                            │
│ session_id (TEXT NOT NULL)   # Session this snapshot belongs to              │
│ snapshot_name (TEXT NOT NULL)# Human-readable name (e.g., "after refactor")  │
│ state_data (TEXT NOT NULL)   # Stored state (JSON)                           │
│ description (TEXT)           # Optional description                          │
│ created_at (DATETIME NOT NULL)# Snapshot creation time                       │
└──────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ Indexes & Relationships                                                      │
│──────────────────────────────────────────────────────────────────────────────│         
│                                                                              │
│ Relationships:                                                               │
│ Conversations 1 ── N Tool Calls                                              │
│ Conversations self-reference: parent_id → id                                 │
│ Session-based grouping for all tables (session_id as foreign key scope)      │
└──────────────────────────────────────────────────────────────────────────────┘
```



Here’s the **English version** of your “Quick Start” documentation:

------

## 🚀 Quick Start

### Environment Requirements

- Python 3.8+
- SQLite 3
- Supported Operating Systems: macOS, Linux, Windows

### Install Dependencies

```bash
# Quick installation script
./install.sh  # Linux/macOS
# or
install.bat   # Windows

# Manual installation
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```bash
cp .env.template .env
# Edit the .env file and add your OpenAI API Key
```

### Basic Usage

#### Interactive Mode

```bash
python run.py --interactive
```

#### Single Task Mode

```bash
python run.py --task "Create a responsive landing page with navigation and hero section"
```

#### Session Management

```bash
# Continue the last conversation
python run.py --continue-session --interactive

# Resume a specific session
python run.py --resume "Landing Page" --task "Add animations"
```



## 📋 Usage Examples

### Create Responsive Component

```bash
python run.py --task "Create a responsive button component with hover effects and accessibility features"
```

### Implement Layout System

```bash
python run.py --task "Implement a three-column responsive dashboard layout with sidebar navigation"
```

### File Operations and Search

```bash
python run.py --task "List project files, search all CSS for button-related styles, and check git status"
```

### Development Tool Integration

```bash
python run.py --task "Run npm install to install dependencies, then start the development server"
```

------

## 🛠️ Tool Usage

### Built-in Tool Call Format

During conversations, the AI automatically calls tools using the following format:

```
**Action:** Use read_file with parameters: {"path": "index.html"}
**Action:** Use write_file with parameters: {"path": "style.css", "content": "body { margin: 0; }"}
**Action:** Use list_dir with parameters: {"path": "."}
**Action:** Use grep with parameters: {"pattern": "button", "file_pattern": "*.css"}
**Action:** Use bash with parameters: {"command": "npm install"}
```

### Logging Configuration

Set the log level using the `--log-level` parameter:

```bash
python run.py --log-level DEBUG --interactive
```

------

## 📁 Project Structure

```
frontend-agent/
├── agent/
│   ├── react_agent.py         # ReAct Agent implementation (built-in tools)
│   ├── file_operations.py     # File operations module
│   └── frontend_prompts.py    # Frontend prompt management
├── database/
│   ├── models.py              # Database models
│   └── context_manager.py     # Context manager
├── prompts/
│   ├── design_system          # Design system guidance
│   ├── component_structure    # Component architecture
│   ├── styling_approach       # Styling methodology
│   ├── interaction_patterns   # Interaction patterns
│   └── responsive_design      # Responsive design
├── project/                   # Working directory (AI-generated files)
│   ├── assets/
│   ├── components/
│   ├── pages/
│   ├── scripts/
│   └── styles/
├── run.py                     # Main entry point (recommended)
├── main.py                    # Core program logic
└── README.md
```

------

## 🔧 System Environment Information

On startup, the system automatically detects and displays:

- Operating system type and version
- Shell environment
- Python version
- Available development tools (node, npm, git, etc.)

This information helps the AI choose tools and commands more accurately.

------

## 📝 Session Management Features

### Automatic Naming

New sessions are automatically assigned meaningful names based on the task content.

### Persistent Storage

All conversation history, tool calls, and generated files are saved in an SQLite database.

### Session Recovery

Supports restoring previous sessions by name or ID, ensuring conversation continuity.



------

## **Prompt & Context Principles**

- **Clear Prompt Layers**
  - System prompt defines agent behavior and tool usage.
  - Domain-specific hints optimize frontend development tasks.
- **Context Persistence**
  - Store conversation, tool calls, and session state in SQLite.
  - Support session resume and state snapshots.
- **Token Efficiency**
  - Keep system prompt fixed and append only recent steps.
  - Use truncation for long histories to prevent token overflow.
- **Extensible by Design**
  - Modular prompt text and event callbacks enable future customization.

```
User Input ─┐
            ▼
        [ Prompt ]
            │
            ▼
        [ Agent ]
            │
            ▼
   ┌────────────────┐
   │   Context DB   │
   │ (sessions, log │
   │  & snapshots)  │
   └────────────────┘
```

------

 

## Future deployment and scale suggestion（AWS example）

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                   AWS Cloud‑Native Architecture for Lovable                  │
└──────────────────────────────────────────────────────────────────────────────┘

                ┌──────────────────────────┐
                │      Web Clients         │
                └─────────────┬────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │    Amazon API Gateway    │
                │  - Rate limiting         │
                │  - Authentication        │
                └─────────────┬────────────┘
                              │
              ┌───────────────┴─────────────────┐
              │                                 │
              ▼                                 ▼
   ┌─────────────────────┐          ┌─────────────────────┐
   │   AWS Lambda (Sync) │          │    Amazon SQS       │
   │ - MCP server calls  │          │ - Async buffering   │
   └─────────┬───────────┘          └─────────┬───────────┘
             │                                 │
             │                          ┌──────┴───────┐
             │                          │ AWS Lambda   │
             │                          │   (Worker)   │
             │                          │ - Async jobs │
             │                          └──────┬───────┘
             │                                 │
             │                          ┌──────┴────────────────────────────┐
             │                          │     Amazon Bedrock (Claude 3.5)   │
             │                          │     OpenAI GPT‑4o (via Secrets)   │
             │                          └───────────────────────────────────┘
             │
┌────────────┴─────────────────────────┐
│          Data & Storage              │
│  ┌───────────────────────────────┐   │
│  │ Amazon RDS (Aurora PostgreSQL)│   │
│  │  - Core relational data       │   │
│  └───────────────────────────────┘   │
│  ┌───────────────────────────────┐   │
│  │ Amazon DynamoDB               │   │
│  │  - Session & cache            │   │
│  └───────────────────────────────┘   │
│  ┌───────────────────────────────┐   │
│  │ Amazon S3                     │   │
│  │  - Artifacts & uploads        │   │
│  └───────────────────────────────┘   │
└──────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Security & Secrets                                                           │
│  - AWS Secrets Manager (API keys)                                            │
│  - IAM Roles (least privilege)                                               │
│  - Encryption (KMS, SSL/HTTPS)                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Monitoring & Ops                                                             │
│  - Amazon CloudWatch (metrics, logs, alarms)                                 │
│  - AWS Cost Explorer + Anomaly Detection                                     │
│  - CloudTrail (audit)                                                        │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ Docker/ECS Option                                                            │
│  - Containerize when Lambda runtime limitations encountered                  │
│  - Supports resident processes and custom runtimes                           │
└──────────────────────────────────────────────────────────────────────────────┘

Key Priorities:
1. Parameter Management → Secrets Manager + Parameter Store
2. Security → IAM Roles + KMS + SSL/HTTPS
3. Scalability → Auto Scaling (ECS/EC2/Lambda) + Load Balancing + Stateless design
4. Cost Optimization → Spot Instances + S3 Lifecycle + Budget alarms
5. High Availability → Multi-AZ (RDS/ECS) + Backup + Disaster Recovery
6. Monitoring → CloudWatch + CloudTrail + Alarm Notifications
```





## Future Database Expansion

------

```
   ┌───────────────┐
   │    Users      │
   │────────────── │
   │ user_id (PK)  │
   │ name          │
   │ email         │
   │ ...           │
   └─────┬─────────┘
         │1
         │
         │N
 ┌───────▼──────────┐        ┌─────────────────┐
 │    Sessions      │        │      Chats      │
 │───────────────── │        │──────────────── │
 │ session_id (PK)  │        │ chat_id (PK)    │
 │ user_id (FK)─────┼────────┤ user_id (FK)    │
 │ device_info      │        │ title           │
 │ expires_at       │        │ created_at      │
 │ ...              │        │ ...             │
 └──────────────────┘        └─────┬───────────┘
                                    │1
                                    │
                                    │N
                           ┌────────▼─────────────┐
                           │       Messages       │
                           │───────────────────── │
                           │ message_id (PK)     │
                           │ chat_id (FK)────────┘
                           │ role                │
                           │ content             │
                           │ created_at          │
                           └─────────────────────┘
```

### 



### Common Issues

------

## 🐛 Troubleshooting

### Common Issues

1. **ImportError**: Make sure to use `run.py` instead of running `main.py` directly
2. **API Key Error**: Check whether the `.env` file is correctly configured
3. **Permission Issues**: Ensure read/write access to the `project` directory

### Debug Mode

```bash
python run.py --log-level DEBUG --task "your task"
```

------

## 📊 Performance Advantages

Compared to the MCP solution:

- **Improved Stability**: No external server, eliminating connection failures

- **Faster Response**: Direct Python function calls for quicker responses

- **Simplified Architecture**: Fewer external dependencies, easier maintenance

- **Enhanced Features**: Added grep search and bash command execution

  

## Comparision of different agent paradigm

| Method                   | Features                                       | Integration Effort           |
| ------------------------ | ---------------------------------------------- | ---------------------------- |
| CoT (Chain of Thought)   | Generates reasoning chain, no direct actions   | Medium‑High                  |
| Single‑Step Action Agent | Calls one fixed tool, no multi‑tool logic      | Low (but limited capability) |
| Planner‑Executor         | Plans first, executes step‑by‑step actions     | Medium‑High (complex design) |
| ReAct                    | Action → Observation → dynamic decision‑making | Low (natural fit)            |



------

## 🤝 Contributing

Contributions are welcome!
 Submit Issues and Pull Requests to help improve this project.

------

## 📄 License

MIT License
