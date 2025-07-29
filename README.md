# My Lovable Platform

A comprehensive AI-powered development platform that integrates gpt-engineer with streaming capabilities and real-time project preview using iframes.

## 🚀 Features

### Core Functionality
- **Multi-dialogue Chat System** - Support for multiple concurrent chat sessions
- **gpt-engineer Integration** - Automated project generation using Python subprocess
- **Streaming Logs** - Real-time output streaming from gpt-engineer to frontend
- **Iframe Project Preview** - Automatic display and refresh of generated projects
- **File Upload & Processing** - Support for PDF, DOCX, Excel, and CSV files
- **Vector Database Integration** - RAG (Retrieval-Augmented Generation) capabilities

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
│  - gpt-engineer subprocess management                     │
│  - Project file serving and preview                       │
├─────────────────────────────────────────────────────────────┤
│                    gpt-engineer                            │
│  - Project generation from prompts                        │
│  - File system output                                     │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- gpt-engineer installed globally

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file .env
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

1. **gpt-engineer not found**
   ```bash
   pip install gpt-engineer
   ```

2. **Iframe not loading**
   - Check CORS settings
   - Verify project files exist
   - Check browser console for errors

3. **Streaming not working**
   
   - Ensure backend is running on correct port
   - Check network connectivity
   - Verify streaming response headers
   
4. **Project preview not updating**
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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 