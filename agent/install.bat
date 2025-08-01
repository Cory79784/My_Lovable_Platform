@echo off
REM Frontend Development Agent Installation Script for Windows

echo 🎨 Frontend Development Agent - Installation Script
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install Python dependencies
echo.
echo 📦 Installing Python dependencies...
if exist "requirements_fixed.txt" (
    pip install -r requirements_fixed.txt
) else if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    REM Fallback to essential packages
    echo Installing essential Python packages...
    pip install "openai>=1.0.0" "python-dotenv>=0.19.0" "aiohttp>=3.8.0" "dataclasses-json>=0.5.7" "aiosqlite>=0.17.0"
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo.
    echo 📝 Creating .env file...
    if exist ".env.template" (
        copy .env.template .env
    ) else (
        echo # OpenAI API Configuration > .env
        echo OPENAI_API_KEY=your_api_key_here >> .env
        echo OPENAI_BASE_URL=https://api.openai.com/v1 >> .env
        echo OPENAI_MODEL=gpt-4o >> .env
        echo OPENAI_TEMPERATURE=0.1 >> .env
        echo OPENAI_MAX_TOKENS=4096 >> .env
    )
    echo ⚠️  Please edit .env file and add your OpenAI API key
)

REM Create project directory structure
echo.
echo 📁 Creating project directory structure...
if not exist "project" mkdir project
if not exist "project\assets" mkdir project\assets
if not exist "project\assets\images" mkdir project\assets\images
if not exist "project\components" mkdir project\components
if not exist "project\pages" mkdir project\pages
if not exist "project\scripts" mkdir project\scripts
if not exist "project\styles" mkdir project\styles

REM Run simple test
echo.
echo 🔍 Running system test...
python run.py --task "Test system: list directory and check environment" --log-level ERROR
if %errorlevel% equ 0 (
    echo.
    echo 🎉 Installation completed successfully!
    echo.
    echo Next steps:
    echo 1. Edit .env file and add your OpenAI API key
    echo 2. Run: python run.py --interactive
    echo 3. Try: Create a simple HTML page with responsive design
) else (
    echo.
    echo ⚠️  Installation completed with warnings.
    echo Please check your OpenAI API key in .env file.
    echo You can still run: python run.py --interactive
)

echo.
echo 📖 For more information, see README.md
pause