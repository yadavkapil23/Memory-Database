#!/bin/bash
# Quick start script - automates Phase 1 setup

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     Episodic AI Memory System - Quick Start Automation        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "\n${YELLOW}[1/6] Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python: $python_version"

required_version="3.11"
if [[ "$python_version" < "$required_version" ]]; then
    echo -e "${RED}✗ Python $required_version+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python OK${NC}"

# Step 2: Create virtual environment
echo -e "\n${YELLOW}[2/6] Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3.11 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Step 3: Install dependencies
echo -e "\n${YELLOW}[3/6] Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 4: Check Docker
echo -e "\n${YELLOW}[4/6] Checking Docker services...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found. Install Docker and try again.${NC}"
    exit 1
fi

echo "  Starting services (Qdrant, Redis, PostgreSQL)..."
docker-compose up -d > /dev/null 2>&1
sleep 5

# Check if services are running
if docker ps | grep -q "qdrant"; then
    echo -e "${GREEN}✓ Qdrant running${NC}"
else
    echo -e "${RED}✗ Qdrant failed to start${NC}"
    exit 1
fi

if docker ps | grep -q "redis"; then
    echo -e "${GREEN}✓ Redis running${NC}"
else
    echo -e "${RED}✗ Redis failed to start${NC}"
    exit 1
fi

if docker ps | grep -q "postgres"; then
    echo -e "${GREEN}✓ PostgreSQL running${NC}"
else
    echo -e "${RED}✗ PostgreSQL failed to start${NC}"
    exit 1
fi

# Step 5: Configure environment
echo -e "\n${YELLOW}[5/6] Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}  ⚠ Please edit .env and add your OpenAI API key${NC}"
    echo -e "${YELLOW}  Get key at: https://platform.openai.com/api/keys${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Step 6: Run validation
echo -e "\n${YELLOW}[6/6] Validating setup...${NC}"
python test_phase1.py

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✓ SETUP COMPLETE!                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}Next steps:${NC}"
echo "  1. Edit .env and add your OpenAI API key"
echo "  2. Run: python cli.py (to try the interactive CLI)"
echo "  3. Read: EXECUTE_PHASE1.md (for week-by-week plan)"
echo ""
echo -e "${GREEN}Happy building! 🚀${NC}"
