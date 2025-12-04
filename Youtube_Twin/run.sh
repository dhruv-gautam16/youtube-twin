#!/bin/bash

################################################################################
# YouTube Twin - Linux/Mac Startup Script
# This script sets up and runs both frontend and backend
################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' 

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║              🎥 YOUTUBE TWIN 🤖                       ║"
echo "║          AI-Powered Video Chat Assistant              ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

if ! command_exists pip3; then
    echo -e "${RED}❌ pip3 is not installed. Please install pip3.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

echo -e "\n${YELLOW}[2/6] Setting up backend...${NC}"

cd backend || exit

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip --quiet

echo "Installing Python dependencies..."
echo "(This may take a few minutes...)"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    echo -e "${YELLOW}Try running: pip install -r requirements.txt${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found.${NC}"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${RED}⚠️  IMPORTANT: Please edit backend/.env and add your OPENAI_API_KEY${NC}"
        echo -e "${RED}⚠️  Press Enter after you've added your API key to continue...${NC}"
        read
    else
        echo -e "${RED}❌ .env.example not found. Please create .env manually.${NC}"
        exit 1
    fi
fi

if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${RED}❌ OPENAI_API_KEY not configured in .env file${NC}"
    echo -e "${YELLOW}Please add your OpenAI API key to backend/.env${NC}"
    echo -e "${YELLOW}Format: OPENAI_API_KEY=sk-your-key-here${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend setup complete${NC}"

cd ..

echo -e "\n${YELLOW}[3/6] Setting up frontend...${NC}"

cd frontend || exit

if [ ! -f "index.html" ] || [ ! -f "style.css" ] || [ ! -f "script.js" ]; then
    echo -e "${RED}❌ Frontend files missing. Please ensure all files are present.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"

cd ..

echo -e "\n${YELLOW}[4/6] Checking for existing processes...${NC}"

if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Stopping process on port 5000..."
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Stopping process on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

echo -e "${GREEN}✅ Ports cleared${NC}"

echo -e "\n${YELLOW}[5/6] Starting backend server...${NC}"

cd backend

source venv/bin/activate
nohup python app.py > backend.log 2>&1 &
BACKEND_PID=$!

sleep 2

if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"
    echo "   Backend logs: backend/backend.log"
    echo "   API running at: http://localhost:5000"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
    echo "Check backend/backend.log for errors"
    exit 1
fi

cd ..

echo -e "\n${YELLOW}[6/6] Starting frontend server...${NC}"

cd frontend

if command_exists python3; then
    nohup python3 -m http.server 8000 > frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    sleep 2
    
    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"
        echo "   Frontend logs: frontend/frontend.log"
        echo "   Frontend running at: http://localhost:8000"
    else
        echo -e "${RED}❌ Frontend server failed to start${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
else
    echo -e "${RED}❌ Could not start frontend server${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

cd ..

echo -e "\n${YELLOW}Waiting for servers to initialize...${NC}"
sleep 1

echo -e "\n${CYAN}Performing health check...${NC}"
HEALTH_CHECK=$(curl -s http://localhost:5000/health 2>/dev/null || echo "failed")

if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may still be starting up${NC}"
fi

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ YouTube Twin is now running!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "\n${BLUE}📱 Access the application:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:8000${NC}"
echo -e "   Backend API: ${GREEN}http://localhost:5000${NC}"
echo -e "\n${BLUE}📋 Process IDs:${NC}"
echo -e "   Backend PID: ${CYAN}$BACKEND_PID${NC}"
echo -e "   Frontend PID: ${CYAN}$FRONTEND_PID${NC}"
echo -e "\n${BLUE}🛑 To stop the servers:${NC}"
echo -e "   Press ${YELLOW}Ctrl+C${NC} or run:"
echo -e "   ${YELLOW}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "\n${BLUE}📝 View Logs:${NC}"
echo -e "   Backend: ${YELLOW}tail -f backend/backend.log${NC}"
echo -e "   Frontend: ${YELLOW}tail -f frontend/frontend.log${NC}"
echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"

echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

if command_exists xdg-open; then
    echo -e "\n${CYAN}Opening browser...${NC}"
    xdg-open http://localhost:8000 2>/dev/null &
elif command_exists open; then
    echo -e "\n${CYAN}Opening browser...${NC}"
    open http://localhost:8000 2>/dev/null &
fi

trap cleanup INT TERM

cleanup() {
    echo -e "\n\n${YELLOW}Shutting down servers...${NC}"
    
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✅ Backend server stopped${NC}"
        fi
        rm .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}✅ Frontend server stopped${NC}"
        fi
        rm .frontend.pid
    fi
    
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ All servers stopped successfully${NC}"
    exit 0
}

echo -e "\n${YELLOW}Press Ctrl+C to stop all servers...${NC}\n"

wait