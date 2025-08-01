#!/bin/bash

# Frontend Development Agent Installation Script

echo "🎨 Frontend Development Agent - Installation Script"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if [ -f "requirements_fixed.txt" ]; then
    pip install -r requirements_fixed.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Fallback to essential packages
    echo "Installing essential Python packages..."
    pip install openai>=1.0.0 python-dotenv>=0.19.0 aiohttp>=3.8.0 dataclasses-json>=0.5.7 aiosqlite>=0.17.0
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    if [ -f ".env.template" ]; then
        cp .env.template .env
    else
        echo "# OpenAI API Configuration" > .env
        echo "OPENAI_API_KEY=your_api_key_here" >> .env
        echo "OPENAI_BASE_URL=https://api.openai.com/v1" >> .env
        echo "OPENAI_MODEL=gpt-4o" >> .env
        echo "OPENAI_TEMPERATURE=0.1" >> .env
        echo "OPENAI_MAX_TOKENS=4096" >> .env
    fi
    echo "⚠️  Please edit .env file and add your OpenAI API key"
fi

# Create project directory structure
echo ""
echo "📁 Creating project directory structure..."
mkdir -p project/{assets/images,components,pages,scripts,styles}

# Run simple test
echo ""
echo "🔍 Running system test..."
if python3 run.py --task "Test system: list directory and check environment" --log-level ERROR; then
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file and add your OpenAI API key"
    echo "2. Run: python3 run.py --interactive"
    echo "3. Try: Create a simple HTML page with responsive design"
else
    echo ""
    echo "⚠️  Installation completed with warnings."
    echo "Please check your OpenAI API key in .env file."
    echo "You can still run: python3 run.py --interactive"
fi

echo ""
echo "📖 For more information, see README.md"