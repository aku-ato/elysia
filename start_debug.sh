#!/bin/bash
# Debug startup script for Elysia backend
# Starts uvicorn with or without debugpy based on PYTHON_DEBUG env variable

set -e

echo "🚀 Starting Elysia Backend..."

if [ "$PYTHON_DEBUG" = "true" ] || [ "$PYTHON_DEBUG" = "1" ]; then
    echo "🐛 Debug mode enabled - Starting with debugpy on port 5678"
    echo "   Waiting for debugger to attach..."
    echo "   VS Code: Use 'Python: Remote Attach (Docker)' configuration"

    # Start with debugpy and wait for client
    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client \
        -m uvicorn elysia.api.app:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
else
    echo "▶️  Normal mode - Starting without debugger"

    # Start normally
    uvicorn elysia.api.app:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
fi
