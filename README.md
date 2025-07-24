# Lovable Platform (Self-Reproduction)

This project is my own way to reproduce the core workflow of [lovable.dev](https://lovable.dev/) — an AI-powered platform for building web apps by chatting with AI.

## Project Structure
- **frontend/**: React-based web UI (with npm/yarn/bun)
- **backend/**: FastAPI + LangChain + gpt-engineer integration
- **gpt_projects/**: Where gpt-engineer generated code projects are stored

---

## How to Deploy (Windows)

### Backend
1. Open a terminal and navigate to the `backend` directory:
   ```sh
   cd backend
   python -m pip install -r requirements.txt
   ```
2. Make sure you have a `.env` file in `backend/` with your OpenAI API key and model name:
   ```env
   MODEL_NAME=gpt-4o-mini
   OPENAI_API_KEY=sk-...your-key...
   ```
3. Start the FastAPI server:
   ```sh
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
4. (Optional) Make sure `gpt-engineer` CLI is installed globally and available in your PATH.

### Frontend
1. Open a new terminal and navigate to the `frontend` directory:
   ```sh
   cd frontend
   npm install
   # or
   yarn install
   # or
   bun install
   ```
2. Start the frontend dev server:
   ```sh
   npm run dev
   # or
   yarn dev
   # or
   bun run dev
   ```
3. Swagger：http://127.0.0.1:8000/docs
4. Make sure to set your OpenAI API key in the appropriate `.env` file if the frontend needs it (for direct API calls).

---

## How the Backend Calls gpt-engineer
- The backend exposes a POST API `/chat/generate-project` and `/chat/generate-project/stream`.
- When called, it:
  1. Creates a new folder under `gpt_projects/` with the given project name.
  2. Writes the prompt to a `main_prompt` file in that folder.
  3. Uses Python's `subprocess` to call `gpt-engineer <project_path>`, automatically passing the prompt to stdin.
  4. Streams the logs/output back to the frontend (if using `/stream`).
- All required environment variables (like `OPENAI_API_KEY`, `MODEL_NAME`) are loaded from `.env`.

---

## gpt-engineer Installation (Windows)

1. **Recommended:** Install gpt-engineer globally via pip:
   ```sh
   python -m pip install gpt-engineer
   ```

**Note:** Using a virtual environment (venv or poetry) is highly recommended to avoid dependency conflicts, especially on Windows.


---

## Current Issues / Limitations
- **gpt-engineer integration is not fully robust**: Some prompts may cause the process to hang or not generate files as expected, due to the CLI's interactive nature.
- **No advanced job management**: All project generations are blocking (unless using the `/stream` endpoint for logs).
- **No real-time file system watcher**: The frontend only gets the code after generation, not during.
- **Path is hardcoded**: The backend uses a relative path for `gpt_projects/`, which may need adjustment for other deployments.
- **No authentication or user management**: This is a prototype for personal/experimental use.

---

## About
This is a personal, experimental reproduction of the lovable.dev platform, for learning and research purposes only. Not affiliated with the original [lovable.dev](https://lovable.dev/). 