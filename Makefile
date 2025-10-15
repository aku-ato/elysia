# Makefile for Elysia Backend Development
# Orchestrates virtualenv, Docker, and development workflows

# Configuration
VENV_DIR := .venv
PYTHON := python3
PIP := $(VENV_DIR)/bin/pip
PYTHON_VENV := $(VENV_DIR)/bin/python
PYTEST := $(VENV_DIR)/bin/pytest
ELYSIA := $(VENV_DIR)/bin/elysia
MKDOCS := $(VENV_DIR)/bin/mkdocs
BLACK := $(VENV_DIR)/bin/black

# Docker configuration
DOCKER_IMAGE := elysia-backend
DOCKER_TAG := latest
DOCKER_PORT := 8000
CONTAINER_NAME := elysia-dev

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)Elysia Backend Makefile$(NC)"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ==============================================================================
# Virtual Environment Management
# ==============================================================================

.PHONY: venv
venv: ## Create virtual environment
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)Virtual environment created at $(VENV_DIR)$(NC)"

.PHONY: install
install: venv ## Install dependencies in virtual environment
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -e .
	@$(PYTHON_VENV) -m spacy download en_core_web_sm
	@echo "$(GREEN)Dependencies installed$(NC)"

.PHONY: install-dev
install-dev: venv ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -e ".[dev]"
	@$(PYTHON_VENV) -m spacy download en_core_web_sm
	@echo "$(GREEN)Development dependencies installed$(NC)"

.PHONY: clean-venv
clean-venv: ## Remove virtual environment
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	@rm -rf $(VENV_DIR)
	@echo "$(GREEN)Virtual environment removed$(NC)"

# ==============================================================================
# Docker Operations
# ==============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	@docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "$(GREEN)Running Docker container...$(NC)"
	@docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(DOCKER_PORT):8000 \
		--env-file .env \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)Container running at http://localhost:$(DOCKER_PORT)$(NC)"

.PHONY: docker-run-interactive
docker-run-interactive: ## Run Docker container interactively
	@echo "$(GREEN)Running Docker container interactively...$(NC)"
	@docker run -it --rm \
		--name $(CONTAINER_NAME) \
		-p $(DOCKER_PORT):8000 \
		--env-file .env \
		-v $(PWD):/app \
		$(DOCKER_IMAGE):$(DOCKER_TAG) /bin/bash

.PHONY: docker-stop
docker-stop: ## Stop Docker container
	@echo "$(YELLOW)Stopping Docker container...$(NC)"
	@docker stop $(CONTAINER_NAME) || true
	@docker rm $(CONTAINER_NAME) || true
	@echo "$(GREEN)Container stopped$(NC)"

.PHONY: docker-logs
docker-logs: ## Show Docker container logs
	@docker logs -f $(CONTAINER_NAME)

.PHONY: docker-clean
docker-clean: docker-stop ## Remove Docker images and containers
	@echo "$(YELLOW)Cleaning Docker artifacts...$(NC)"
	@docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) || true
	@echo "$(GREEN)Docker artifacts cleaned$(NC)"

.PHONY: docker-rebuild
docker-rebuild: docker-clean docker-build ## Rebuild Docker image from scratch

# ==============================================================================
# Application Development
# ==============================================================================

.PHONY: dev
dev: install-dev ## Start development server with auto-reload
	@echo "$(GREEN)Starting development server...$(NC)"
	@$(ELYSIA) start --reload True

.PHONY: dev-custom
dev-custom: install-dev ## Start development server with custom port (use PORT=8080 make dev-custom)
	@echo "$(GREEN)Starting development server on port $(PORT)...$(NC)"
	@$(ELYSIA) start --port $(PORT) --reload True

.PHONY: run
run: install ## Run application in production mode
	@echo "$(GREEN)Starting application...$(NC)"
	@$(ELYSIA) start --reload False

# ==============================================================================
# Testing
# ==============================================================================

.PHONY: test
test: install-dev ## Run tests (no external requirements)
	@echo "$(GREEN)Running tests...$(NC)"
	@$(PYTEST) tests/no_reqs -v

.PHONY: test-all
test-all: install-dev ## Run all tests (requires API keys and Weaviate)
	@echo "$(YELLOW)Running all tests (requires external services)...$(NC)"
	@$(PYTEST) tests -v

.PHONY: test-cov
test-cov: install-dev ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@$(PYTEST) --cov=elysia tests/no_reqs -v
	@echo "$(GREEN)Coverage report generated$(NC)"

# ==============================================================================
# Code Quality
# ==============================================================================

.PHONY: format
format: install-dev ## Format code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	@$(BLACK) elysia/ tests/
	@echo "$(GREEN)Code formatted$(NC)"

.PHONY: format-check
format-check: install-dev ## Check code formatting
	@echo "$(GREEN)Checking code formatting...$(NC)"
	@$(BLACK) --check elysia/ tests/

# ==============================================================================
# Documentation
# ==============================================================================

.PHONY: docs-serve
docs-serve: install-dev ## Serve documentation locally
	@echo "$(GREEN)Serving documentation...$(NC)"
	@$(MKDOCS) serve

.PHONY: docs-build
docs-build: install-dev ## Build documentation
	@echo "$(GREEN)Building documentation...$(NC)"
	@$(MKDOCS) build
	@echo "$(GREEN)Documentation built$(NC)"

# ==============================================================================
# Cleanup
# ==============================================================================

.PHONY: clean
clean: ## Clean temporary files and caches
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf build/ dist/ site/
	@echo "$(GREEN)Cleanup complete$(NC)"

.PHONY: clean-all
clean-all: clean clean-venv docker-clean ## Complete cleanup (venv + docker + temp files)
	@echo "$(GREEN)Complete cleanup finished$(NC)"

# ==============================================================================
# Quick Start Workflows
# ==============================================================================

.PHONY: setup
setup: install-dev ## Complete setup for new developers
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)Elysia Backend Setup Complete!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run 'make dev' to start development server"
	@echo "  3. Run 'make test' to verify installation"
	@echo ""

.PHONY: quickstart
quickstart: setup test dev ## Complete quickstart: setup + test + run

.PHONY: docker-quickstart
docker-quickstart: docker-build docker-run ## Quick Docker setup and run
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)Docker Container Running!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "Access the API at: http://localhost:$(DOCKER_PORT)"
	@echo "View logs with: make docker-logs"
	@echo "Stop container with: make docker-stop"
	@echo ""

# ==============================================================================
# Status and Information
# ==============================================================================

.PHONY: status
status: ## Show development environment status
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)Elysia Backend Status$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "Virtual Environment:"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "  ✓ Present at $(VENV_DIR)"; \
		if [ -f "$(ELYSIA)" ]; then \
			echo "  ✓ Elysia CLI installed"; \
		else \
			echo "  ✗ Elysia CLI not installed (run 'make install')"; \
		fi \
	else \
		echo "  ✗ Not created (run 'make venv' or 'make install')"; \
	fi
	@echo ""
	@echo "Docker:"
	@if docker images | grep -q $(DOCKER_IMAGE); then \
		echo "  ✓ Image built: $(DOCKER_IMAGE):$(DOCKER_TAG)"; \
	else \
		echo "  ✗ Image not built (run 'make docker-build')"; \
	fi
	@if docker ps | grep -q $(CONTAINER_NAME); then \
		echo "  ✓ Container running: $(CONTAINER_NAME)"; \
	else \
		echo "  ✗ Container not running"; \
	fi
	@echo ""

# Default target
.DEFAULT_GOAL := help
