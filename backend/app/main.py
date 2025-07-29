from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat_routes, history_routes, project_routes
# from app.routes import file_routes, voice_routes  # Temporarily commented out
from app.database import init_db
from app.utils import get_llm, load_conversations
import os
print(os.getenv("OPENAI_API_KEY"))
# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = get_llm()

# Initialize database
init_db()
conversations = load_conversations(llm)

# Instantiate the LLM model

# Include routes
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
app.include_router(history_routes.router, prefix="/history", tags=["History"])
# app.include_router(file_routes.router, prefix="/upload", tags=["Upload"])  # Temporarily commented out
# app.include_router(voice_routes.router, prefix="/voice", tags=["Voice"])  # Temporarily commented out
app.include_router(project_routes.router, prefix="/api", tags=["Projects"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)