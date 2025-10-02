.PHONY: help setup seed cleanup test-connection clean

# Colors for output
BLUE := \033[94m
GREEN := \033[92m
YELLOW := \033[93m
RED := \033[91m
RESET := \033[0m

# Python and virtual environment
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python

# Default target
help:
	@echo "$(BLUE)Elysia Collection Seed Scripts$(RESET)"
	@echo ""
	@echo "Available commands:"
	@echo "  $(GREEN)make setup$(RESET)           - Create virtualenv and install dependencies"
	@echo "  $(GREEN)make seed$(RESET)            - Populate example collections"
	@echo "  $(GREEN)make cleanup$(RESET)         - Remove example collections"
	@echo "  $(GREEN)make test-connection$(RESET) - Test backend API connection"
	@echo "  $(GREEN)make clean$(RESET)           - Remove virtualenv and cached files"
	@echo "  $(GREEN)make help$(RESET)            - Show this help message"
	@echo ""
	@echo "$(YELLOW)Workflow:$(RESET)"
	@echo "  1. make setup"
	@echo "  2. cp .env.example .env  (and configure)"
	@echo "  3. make seed"
	@echo "  4. Test in Elysia frontend"
	@echo "  5. make cleanup  (optional)"

setup:
	@echo "$(BLUE)Setting up Python environment...$(RESET)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(GREEN)Creating virtual environment...$(RESET)"; \
		$(PYTHON) -m venv $(VENV); \
	else \
		echo "$(YELLOW)Virtual environment already exists$(RESET)"; \
	fi
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	@$(PIP) install --upgrade pip > /dev/null 2>&1
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Setup complete!$(RESET)"
	@echo ""
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)⚠ Don't forget to create .env file:$(RESET)"; \
		echo "  cp .env.example .env"; \
		echo "  nano .env"; \
	fi

test-connection:
	@echo "$(BLUE)Testing backend connection...$(RESET)"
	@if [ ! -f ".env" ]; then \
		echo "$(RED)✗ .env file not found!$(RESET)"; \
		echo "  Run: cp .env.example .env"; \
		exit 1; \
	fi
	@. $(VENV_BIN)/activate && $(PYTHON_VENV) -c "import os; from dotenv import load_dotenv; import requests; load_dotenv(); backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000'); r = requests.get(f'{backend_url}/api/health', timeout=5); r.raise_for_status(); print('$(GREEN)✓ Backend is reachable at', backend_url, '$(RESET)')" || (echo "$(RED)✗ Backend connection failed$(RESET)" && exit 1)

seed: test-connection
	@echo "$(BLUE)Seeding example collections...$(RESET)"
	@echo ""
	@$(PYTHON_VENV) seed_correlation_collections.py
	@echo "$(GREEN)✓ Collections seeded successfully!$(RESET)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Open Elysia frontend (http://localhost:3000)"
	@echo "  2. Analyze the collections (SocialMediaPosts, AudioTranscriptions)"
	@echo "  3. Test cross-collection queries"
	@echo "  4. See CORRELATION_QUERIES.md for example queries"

cleanup:
	@echo "$(YELLOW)Removing example collections...$(RESET)"
	@echo ""
	@$(PYTHON_VENV) cleanup_collections.py

clean:
	@echo "$(BLUE)Cleaning up environment...$(RESET)"
	@rm -rf $(VENV)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete!$(RESET)"
