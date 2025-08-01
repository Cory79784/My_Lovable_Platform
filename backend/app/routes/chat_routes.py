import os
import sys
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import ChatRequest, ChatResponse, ChatSummary, ChatDetail, RenameChatRequest
from app.utils import create_retriever, create_chain, create_new_conversation, get_llm, save_conversations, load_conversations
from app.database import save_message, get_db_connection
import asyncio
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.globals import chat_file_mapping
from fastapi import BackgroundTasks
import subprocess
import tempfile
import shutil
from fastapi import Request
from pydantic import BaseModel
from fastapi import Body

# Recursively read folder, return directory tree and file content
import os

def read_project_tree(root_path):
    tree = []
    for entry in os.scandir(root_path):
        if entry.is_dir():
            tree.append({
                "type": "folder",
                "name": entry.name,
                "children": read_project_tree(entry.path)
            })
        else:
            with open(entry.path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            tree.append({
                "type": "file",
                "name": entry.name,
                "content": content
            })
    return tree

router = APIRouter()

# Instantiate the LLM model using the utility function
llm = get_llm()
VECTOR_STORE_DIR = "./vector_store"
VECTOR_STORE_NAME = "simple-rag"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Base directory for projects
BASE_PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../gpt_projects"))

# Load conversations from storage
conversations = load_conversations(llm)

def get_vector_db(chat_id):
    """Always load fresh from persistence"""
    if chat_id not in chat_file_mapping or not chat_file_mapping[chat_id]:
        return None  

    vector_store_path = os.path.join(VECTOR_STORE_DIR, chat_id)
    if os.path.exists(vector_store_path):
        try:
            return Chroma(
                persist_directory=vector_store_path,
                embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
                collection_name=chat_id  # Load collection by chat_id
            )
        except Exception as e:
            print(f"Error loading vector DB: {str(e)}")
            return None
    return None

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print("Received request:", request)
        
        chat_id = request.chat_id or create_new_conversation(conversations, llm, VECTOR_STORE_DIR, EMBEDDING_MODEL)
        if chat_id not in conversations:
            raise HTTPException(status_code=400, detail="Invalid chat_id. Please start a new conversation.")
        
        vector_db = get_vector_db(chat_id)
        print(f"Vector DB valid: {vector_db is not None}")

        conversation = conversations.get(chat_id, {}).get("conversation")
        if not conversation:
            raise HTTPException(status_code=500, detail="Conversation object not found.")
        
        memory = conversations[chat_id]["memory"]

        # Add user message to memory in the correct format
        user_message = {"role": "user", "content": request.message}
        memory.add_message(user_message)
        print(f"Added user message to memory: {memory.messages}")

        response_text = ""

        async def generate_response_stream():
            nonlocal response_text
            try:     
                if vector_db:
                    print(f"Using vector DB instance: {id(vector_db)}")
                    retriever = create_retriever(vector_db, llm)
                    rag_chain = create_chain(retriever, llm)
                    input_data = {
                        "question": request.message,
                    }
                    print("Success until chain")
                    # Stream from RAG chain
                    async for token in rag_chain.astream(input_data):
                        token_str = token.content if hasattr(token, "content") else str(token)
                        response_text += token_str
                        yield token_str
                        await asyncio.sleep(0.01)

                else:
                    # Use existing conversation (no RAG)
                    for token in conversation.stream(request.message):  
                        token_str = token.content if hasattr(token, "content") else str(token)
                        response_text += token_str
                        yield token_str
                        await asyncio.sleep(0.01)
                
                if conversations[chat_id]["title"] == "New Chat":
                    new_title = request.message[:30] or "Untitled Chat"

                    # Update in-memory title
                    conversations[chat_id]["title"] = new_title

                    # Persist title update in the database
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE chats SET title = ? WHERE chat_id = ?", (new_title, chat_id))
                        conn.commit()
                    print(f"Chat title updated to: {new_title}")

                if response_text.strip():  # Ensure response_text is not empty
                    ai_message = {"role": "ai", "content": response_text}
                    memory.add_message(ai_message)
                    print(f"Added AI message to memory: {ai_message}")

                    save_message(chat_id, "user", request.message)
                    save_message(chat_id, "ai", response_text)
                    save_conversations(chat_id, memory)
                else:
                    print("Response text is empty. Skipping save_message.")
            except Exception as e:
                print(f"Error during streaming: {e}")
                yield f"Error generating response: {str(e)}"

        return StreamingResponse(
            generate_response_stream(),
            media_type="text/event-stream",  # Change to event-stream
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/new_chat")
async def new_chat():
    try:
        chat_id = create_new_conversation(conversations, llm, VECTOR_STORE_DIR, EMBEDDING_MODEL)
        print(f"Created new chat with ID: {chat_id}")
        
        # Verify the chat was created in database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM chats WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            if result:
                print(f"Chat {chat_id} title in database: {result[0]}")
            else:
                print(f"Chat {chat_id} not found in database!")
        
        return {"chat_id": chat_id}
    except Exception as e:
        print("Error creating a new chat:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/chats")
async def debug_chats():
    """Debug endpoint to see all chats in database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id, title FROM chats")
            chats = cursor.fetchall()
            print(f"Debug: Found {len(chats)} chats in database")
            for chat_id, title in chats:
                print(f"  Chat {chat_id}: {title}")
            return {"chats": [{"chat_id": chat_id, "title": title} for chat_id, title in chats]}
    except Exception as e:
        print(f"Debug error: {e}")
        return {"error": str(e)}

@router.post("/remix-project")
async def remix_project(request: dict):
    """Remix a community project by creating a new chat with the project files"""
    try:
        project_name = request.get("project_name")
        project_description = request.get("project_description", "")
        original_author = request.get("original_author", "Community")
        
        # Create a new chat
        chat_id = create_new_conversation(conversations, llm, VECTOR_STORE_DIR, EMBEDDING_MODEL)
        print(f"Created new chat for remix: {chat_id}")
        
        # Set a descriptive title for the remixed project
        remix_title = f"Remix: {project_name}"
        
        # Update the chat title in database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chats SET title = ? WHERE chat_id = ?",
                (remix_title, chat_id)
            )
            conn.commit()
            print(f"Updated chat {chat_id} title to: {remix_title}")
        
        # Read the actual main_prompt file from the project
        main_prompt_content = ""
        try:
            project_path = os.path.join(BASE_PROJECTS_DIR, project_name)
            main_prompt_path = os.path.join(project_path, "main_prompt")
            if os.path.exists(main_prompt_path):
                with open(main_prompt_path, 'r', encoding='utf-8') as f:
                    main_prompt_content = f.read().strip()
                print(f"Read main_prompt from {project_name}: {len(main_prompt_content)} characters")
            else:
                print(f"main_prompt file not found for {project_name}")
        except Exception as e:
            print(f"Error reading main_prompt: {e}")
            main_prompt_content = f"Original prompt for {project_name} project"
        
        # Create the initial remix message with the actual prompt
        initial_message = f"I want to remix the '{project_name}' project by {original_author}. {project_description}\n\nOriginal prompt:\n{main_prompt_content}"
        
        # Add the message to the conversation
        if chat_id in conversations:
            conversations[chat_id]["memory"].add_message({"role": "user", "content": initial_message})
            print(f"Added remix message to chat {chat_id}")
        else:
            print(f"Warning: chat_id {chat_id} not found in conversations after creation")
        
        # Save the message to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (chat_id, "user", initial_message, datetime.now().isoformat())
            )
            conn.commit()
            print(f"Saved remix message to database for chat {chat_id}")
        
        return {
            "chat_id": chat_id,
            "title": remix_title,
            "message": "Project remixed successfully"
        }
        
    except Exception as e:
        print(f"Error remixing project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remix project: {str(e)}")

def get_project_context(project_name: str) -> str:
    """Get sample project context for community projects"""
    project_contexts = {
        "pulse-robot-template": """This is an interactive robot animation template with:
- HTML5 Canvas for smooth animations
- CSS animations for robot movements
- JavaScript for interactive controls
- Responsive design for mobile devices

Key features:
- Pulsing robot animation
- Interactive controls
- Smooth transitions
- Mobile-friendly design""",
        
        "cryptocurrency-trading-dashboard": """This is a real-time crypto trading interface with:
- Real-time price data from APIs
- Interactive charts and graphs
- Portfolio tracking
- Trading simulation

Key features:
- Live price updates
- Interactive charts
- Portfolio management
- Trading history""",
        
        "wrlds-ai-integration": """This is an AI-powered world building tool with:
- AI-generated content
- Interactive world maps
- Character generation
- Story elements

Key features:
- AI content generation
- Interactive maps
- Character creation
- Story development""",
        
        "crypto-trade-template": """This is a secure crypto trading platform with:
- User authentication
- Secure trading interface
- Portfolio management
- Transaction history

Key features:
- Secure authentication
- Trading interface
- Portfolio tracking
- Transaction logs"""
    }
    
    return project_contexts.get(project_name, f"Sample project: {project_name}")

@router.get("/chats", response_model=list[ChatSummary])
async def get_chats():
    try:
        chat_summaries = []
        for chat_id, data in conversations.items():
            # Get message count and title from database
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,))
                    message_count = cursor.fetchone()[0]
                    print(f"Chat {chat_id}: message_count from DB = {message_count}")
                    
                    # Get title from database
                    cursor.execute("SELECT title FROM chats WHERE chat_id = ?", (chat_id,))
                    title_result = cursor.fetchone()
                    title = title_result[0] if title_result else "Untitled Chat"
                    print(f"Chat {chat_id}: title from DB = {title}")
            except Exception as e:
                print(f"Error getting message count/title for chat {chat_id}: {e}")
                message_count = 0
                title = "Untitled Chat"
            
            # Check if chat has associated project and get project path
            has_project = False
            project_path = None
            if chat_id in chat_file_mapping and chat_file_mapping[chat_id]:
                has_project = True
                # Try to find the actual project folder
                BASE_PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../gpt_projects"))
                if os.path.exists(BASE_PROJECTS_DIR):
                    # Look for project folder that contains the chat_id
                    for project_folder in os.listdir(BASE_PROJECTS_DIR):
                        project_folder_path = os.path.join(BASE_PROJECTS_DIR, project_folder)
                        if os.path.isdir(project_folder_path) and chat_id in project_folder:
                            project_path = project_folder
                            break
            
            # Get last updated time from database
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(created_at) FROM messages WHERE chat_id = ?", (chat_id,))
                    result = cursor.fetchone()
                    last_updated = result[0] if result and result[0] else datetime.now().isoformat()
            except Exception as e:
                print(f"Error getting last updated for chat {chat_id}: {e}")
                last_updated = datetime.now().isoformat()
            
            chat_summaries.append({
                "chat_id": chat_id, 
                "title": title,
                "message_count": message_count,
                "has_project": has_project,
                "project_path": project_path,
                "last_updated": last_updated
            })
        return chat_summaries
    except Exception as e:
        print("Error fetching chats:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{chat_id}", response_model=ChatDetail)
async def get_chat_history(chat_id: str):
    if chat_id not in conversations:
        raise HTTPException(status_code=404, detail="Chat ID not found.")
    memory = conversations[chat_id]["memory"]
    
    # Get title from database
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM chats WHERE chat_id = ?", (chat_id,))
            title_result = cursor.fetchone()
            title = title_result[0] if title_result else "Untitled Chat"
            print(f"Chat {chat_id}: title from DB = {title}")
    except Exception as e:
        print(f"Error getting title for chat {chat_id}: {e}")
        title = "Untitled Chat"
    
    print("Memory object1:", memory)  # Debug print to check memory object
    messages = []
    for message in memory.messages:
        # Compatible with dict and object
        role = message["role"] if isinstance(message, dict) else getattr(message, "role", None)
        content = message["content"] if isinstance(message, dict) else getattr(message, "content", None)
        messages.append({"role": role, "content": content})
    return {"chat_id": chat_id, "title": title, "messages": messages}

@router.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    # Delete session from memory
    if chat_id in conversations:
        del conversations[chat_id]
    # Delete session and messages from database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.commit()
    # Delete vector store directory
    import shutil
    import os
    vector_store_path = os.path.join(VECTOR_STORE_DIR, chat_id)
    if os.path.exists(vector_store_path):
        shutil.rmtree(vector_store_path)
    # Delete global file mapping
    if chat_id in chat_file_mapping:
        del chat_file_mapping[chat_id]
    return {"success": True}

@router.put("/{chat_id}/rename")
async def rename_chat(chat_id: str, request: RenameChatRequest):
    """Rename a chat session"""
    try:
        print(f"Renaming chat {chat_id} to '{request.title}'")
        
        # Check if chat exists in database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM chats WHERE chat_id = ?", (chat_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
            
            # Update in database
            cursor.execute(
                "UPDATE chats SET title = ? WHERE chat_id = ?", 
                (request.title, chat_id)
            )
            conn.commit()
            print(f"Database updated for chat {chat_id}")
            
        # Update in memory if exists
        if chat_id in conversations:
            conversations[chat_id]["title"] = request.title
            print(f"Memory updated for chat {chat_id}")
        else:
            print(f"Chat {chat_id} not found in memory")
                
        return {"success": True, "title": request.title}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error renaming chat {chat_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to rename chat: {str(e)}")

class GenerateProjectRequest(BaseModel):
    # project_name: str  # Not needed for agent calls
    prompt: str

class GenerateProjectResponse(BaseModel):
    stdout: str
    stderr: str
    returncode: int

@router.post("/generate-project", response_model=GenerateProjectResponse)
async def generate_project(data: GenerateProjectRequest = Body(...)):
    # project_name = data.project_name  # Not needed
    prompt = data.prompt
    
    # Get the agent directory path
    agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../agent"))
    
    import subprocess
    result = subprocess.run(
        ["python", "run.py"],
        input=f"task \"{prompt}\"",
        capture_output=True,
        text=True,
        cwd=agent_dir,
        env=os.environ.copy()
    )
    return GenerateProjectResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode
    )

@router.post("/generate-project/stream")
async def generate_project_stream(data: GenerateProjectRequest = Body(...)):
    import subprocess
    import time
    import os
    # project_name = data.project_name  # Not needed
    prompt = data.prompt
    
    # Get the agent directory path
    agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../agent"))
    
    def stream_logs():
        yield f"Starting agent for task\n"
        yield f"Task: {prompt}\n"
        
        # Change to agent directory and run the agent
        process = subprocess.Popen(
            ["python", "run.py"],
            cwd=agent_dir,
            env=os.environ.copy(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # Send the task command to stdin
        process.stdin.write(f"task \"{prompt}\"\n")
        process.stdin.flush()
        
        for line in iter(process.stdout.readline, ""):
            yield line
        process.stdout.close()
        process.stdin.close()
        process.wait()
        yield f"\nProcess finished with return code: {process.returncode}\n"
    return StreamingResponse(stream_logs(), media_type="text/plain")