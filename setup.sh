#!/bin/bash

# Drug Interaction Checker Setup Script
# This script sets up the development environment

echo "🏥 Drug Interaction Checker - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment for backend
echo ""
echo "📦 Setting up backend virtual environment..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo ""
echo "📥 Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Backend dependencies installed successfully"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p data models/trained logs

echo "✓ Directory structure created"

# Initialize data files (if they don't exist)
echo ""
echo "📊 Checking data files..."
if [ ! -f "data/drugs.json" ]; then
    echo "⚠️  Drug database not found. Please ensure data files are present."
fi

if [ ! -f "data/interactions.json" ]; then
    echo "⚠️  Interactions database not found. Please ensure data files are present."
fi

# Return to root directory
cd ..

# Frontend setup (if Node.js is available)
if command -v npm &> /dev/null; then
    echo ""
    echo "📦 Setting up frontend..."
    cd frontend
    
    if [ -f "package.json" ]; then
        npm install
        echo "✓ Frontend dependencies installed"
    else
        echo "ℹ️  No package.json found. Using static HTML."
    fi
    
    cd ..
else
    echo ""
    echo "ℹ️  npm not found. Frontend will use static HTML (no build step needed)."
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Backend Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=app/main.py

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Database (optional)
# DATABASE_URL=sqlite:///drug_checker.db
EOF
    echo "✓ .env file created"
fi

# Display success message
echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo ""
echo "To start the application:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app/main.py"
echo ""
echo "2. Open the frontend:"
echo "   Open frontend/index.html in your browser"
echo "   or serve it with: python -m http.server 3000"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:5000"
echo ""
echo "Happy coding! 💊🏥"
echo "=========================================="
