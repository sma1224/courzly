#!/bin/bash
set -e

echo "🧪 Running Courzly Test Suite..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Test backend
echo -e "${BLUE}🐍 Running Backend Tests...${NC}"
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run unit tests
echo -e "${BLUE}Running unit tests...${NC}"
pytest tests/unit/ -m "not slow" --cov-report=term-missing

# Run integration tests
echo -e "${BLUE}Running integration tests...${NC}"
pytest tests/integration/ --cov-append

# Run E2E tests (optional, slower)
if [ "$1" = "--e2e" ]; then
    echo -e "${BLUE}Running E2E tests...${NC}"
    pytest tests/e2e/ -m e2e --cov-append
fi

cd ..

# Test frontend
echo -e "${BLUE}⚛️ Running Frontend Tests...${NC}"
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    npm ci
fi

# Run tests
npm test -- --coverage --watchAll=false

cd ..

echo -e "${GREEN}✅ All tests completed!${NC}"

# Generate combined coverage report
echo -e "${BLUE}📊 Generating coverage reports...${NC}"
echo "Backend coverage: backend/htmlcov/index.html"
echo "Frontend coverage: frontend/coverage/lcov-report/index.html"