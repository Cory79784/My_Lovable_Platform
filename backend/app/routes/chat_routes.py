import os
import sys
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import ChatRequest, ChatResponse, ChatSummary, ChatDetail
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

# 递归读取文件夹，返回目录树和文件内容
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
        return {"chat_id": chat_id}
    except Exception as e:
        print("Error creating a new chat:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats", response_model=list[ChatSummary])
async def get_chats():
    try:
        chat_summaries = [{"chat_id": chat_id, "title": data["title"]} for chat_id, data in conversations.items()]
        return chat_summaries
    except Exception as e:
        print("Error fetching chats:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{chat_id}", response_model=ChatDetail)
async def get_chat_history(chat_id: str):
    if chat_id not in conversations:
        raise HTTPException(status_code=404, detail="Chat ID not found.")
    memory = conversations[chat_id]["memory"]
    print("Memory object1:", memory)  # Debug print to check memory object
    messages = []
    for message in memory.messages:
        # 兼容dict和对象
        role = message["role"] if isinstance(message, dict) else getattr(message, "role", None)
        content = message["content"] if isinstance(message, dict) else getattr(message, "content", None)
        messages.append({"role": role, "content": content})
    return {"chat_id": chat_id, "messages": messages}

@router.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    # 删除内存中的会话
    if chat_id in conversations:
        del conversations[chat_id]
    # 删除数据库中的会话和消息
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.commit()
    # 删除向量库目录
    import shutil
    import os
    vector_store_path = os.path.join(VECTOR_STORE_DIR, chat_id)
    if os.path.exists(vector_store_path):
        shutil.rmtree(vector_store_path)
    # 删除全局文件映射
    if chat_id in chat_file_mapping:
        del chat_file_mapping[chat_id]
    return {"success": True}

class GenerateProjectRequest(BaseModel):
    project_name: str
    prompt: str

class GenerateProjectResponse(BaseModel):
    stdout: str
    stderr: str
    returncode: int

@router.post("/generate-project", response_model=GenerateProjectResponse)
async def generate_project(data: GenerateProjectRequest = Body(...)):
    project_name = data.project_name
    prompt = data.prompt
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../gpt_projects"))
    os.makedirs(BASE_DIR, exist_ok=True)
    project_path = os.path.join(BASE_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)
    with open(os.path.join(project_path, "main_prompt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    import subprocess
    result = subprocess.run(
        ["gpt-engineer", project_path],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
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
    project_name = data.project_name
    prompt = data.prompt
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../gpt_projects"))
    os.makedirs(BASE_DIR, exist_ok=True)
    project_path = os.path.join(BASE_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)
    with open(os.path.join(project_path, "main_prompt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    def stream_logs():
        yield f"Starting gpt-engineer for project: {project_name}\n"
        process = subprocess.Popen(
            ["gpt-engineer", project_path],
            cwd=BASE_DIR,
            env=os.environ.copy(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # 自动把prompt再输入一遍，模拟人工输入
        process.stdin.write(prompt + "\n")
        process.stdin.flush()
        for line in iter(process.stdout.readline, ""):
            yield line
        process.stdout.close()
        process.stdin.close()
        process.wait()
        yield f"\nProcess finished with return code: {process.returncode}\n"
    return StreamingResponse(stream_logs(), media_type="text/plain")