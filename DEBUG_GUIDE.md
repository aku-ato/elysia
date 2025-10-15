# VS Code Debugging Guide for Elysia Backend

This guide explains how to debug the Elysia backend using VS Code, both locally and inside Docker containers.

## 📋 Prerequisites

- VS Code with Python extension installed
- Docker and Docker Compose installed (for container debugging)

## 🎯 Debugging Modes

### 1. Local Debugging (Recommended for Development)

**Best for**: Quick iterations, testing changes without rebuilding Docker

**How to use**:
1. Open the backend folder in VS Code: `/home/ppiccolo/projects/elysia/backend`
2. Set breakpoints in your Python code
3. Press `F5` or go to Run → Start Debugging
4. Select **"Python: FastAPI Local"**
5. The app will start with debugger attached on `http://localhost:8000`

**Environment**:
- Uses your local Python environment
- Connects to Weaviate at `localhost:8080`
- Hot-reload enabled (changes apply immediately)

---

### 2. Docker Container Debugging

**Best for**: Debugging issues that only occur in Docker, production-like environment

#### **Method A: Debug Mode (Wait for Attach)**

**How to use**:
1. Enable debug mode in `.env`:
   ```bash
   PYTHON_DEBUG=true
   ```

2. Rebuild and start the container:
   ```bash
   cd /home/ppiccolo/projects/elysia/deploy
   docker-compose up -d --build backend
   ```

3. The container will start and **wait for debugger** to attach:
   ```
   🐛 Debug mode enabled - Starting with debugpy on port 5678
   Waiting for debugger to attach...
   ```

4. In VS Code:
   - Open `/home/ppiccolo/projects/elysia/backend`
   - Set breakpoints in your code
   - Press `F5` and select **"Python: Remote Attach (Docker)"**
   - Debugger will connect and app will start

5. When done, disable debug mode:
   ```bash
   PYTHON_DEBUG=false
   docker-compose restart backend
   ```

#### **Method B: Attach to Running Container**

**How to use**:
1. Keep `PYTHON_DEBUG=false` in `.env`
2. Start container normally:
   ```bash
   docker-compose up -d backend
   ```

3. When you need to debug, enable debug mode and restart:
   ```bash
   # In deploy/.env, change to:
   PYTHON_DEBUG=true

   # Restart backend only
   docker-compose restart backend
   ```

4. Attach debugger as in Method A (step 4)

---

### 3. Debug Current File

**Best for**: Testing standalone scripts or utilities

**How to use**:
1. Open any Python file
2. Press `F5` and select **"Python: Current File"**
3. The file will run with debugger attached

---

## 🔧 Configuration Files

### `.vscode/launch.json`

Three debugging configurations are available:

```json
{
  "configurations": [
    {
      "name": "Python: FastAPI Local",
      // Launches uvicorn locally with debugger
    },
    {
      "name": "Python: Remote Attach (Docker)",
      // Attaches to debugpy running in Docker on port 5678
    },
    {
      "name": "Python: Current File",
      // Runs current file with debugger
    }
  ]
}
```

### `start_debug.sh`

Startup script that checks `PYTHON_DEBUG` environment variable:
- `PYTHON_DEBUG=true` → Starts with debugpy, waits for attach
- `PYTHON_DEBUG=false` → Starts normally without debugger

### `Dockerfile`

Modified to:
- Install `debugpy` package
- Expose port `5678` for debugger
- Copy and use `start_debug.sh` as entrypoint

### `docker-compose.yml`

Modified to:
- Map port `5678:5678` for debugger connection
- Pass `PYTHON_DEBUG` environment variable from `.env`

---

## 🐛 Debugging Tips

### Setting Breakpoints

1. **Line Breakpoints**: Click left of line number (red dot appears)
2. **Conditional Breakpoints**: Right-click breakpoint → Edit Breakpoint → Add condition
3. **Logpoints**: Right-click in gutter → Add Logpoint (logs without stopping)

### Debug Console

While debugging, use the Debug Console to:
- Inspect variables: `collection_name`
- Execute code: `len(results)`
- Call functions: `fetch_collections()`

### Watch Expressions

Add expressions to Watch panel to monitor values:
- Variables: `user_id`
- Expressions: `len(current_toasts)`
- Object properties: `collection.processed`

### Call Stack

View the execution path that led to the current breakpoint:
- Click frames to navigate
- Inspect local variables at each level

---

## ⚠️ Troubleshooting

### "Cannot connect to debugger"

**Problem**: VS Code can't attach to Docker debugger

**Solutions**:
1. Verify debug mode is enabled:
   ```bash
   docker-compose exec backend env | grep PYTHON_DEBUG
   # Should show: PYTHON_DEBUG=true
   ```

2. Check if debugpy is listening:
   ```bash
   docker-compose logs backend | grep debugpy
   # Should show: "Waiting for debugger to attach..."
   ```

3. Verify port mapping:
   ```bash
   docker-compose ps backend
   # Should show: 0.0.0.0:5678->5678/tcp
   ```

4. Try restarting the container:
   ```bash
   docker-compose restart backend
   ```

---

### "Breakpoints not hitting"

**Problem**: Code executes but breakpoints are ignored

**Solutions**:
1. **Check path mappings** in `launch.json`:
   ```json
   "pathMappings": [
     {
       "localRoot": "${workspaceFolder}/elysia",
       "remoteRoot": "/app/elysia"
     }
   ]
   ```

2. **Verify file is in correct location**:
   - Local: `/home/ppiccolo/projects/elysia/backend/elysia/`
   - Docker: `/app/elysia/`

3. **Disable `justMyCode`** to debug library code:
   ```json
   "justMyCode": false
   ```

4. **Check if code is actually running**: Add `print()` statement to verify

---

### "App starts too fast"

**Problem**: App finishes before you can attach debugger

**Solution**: Use `--wait-for-client` flag (already configured in `start_debug.sh`):
```bash
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client ...
```

---

### "Changes not reflecting"

**Problem**: Code changes don't apply during debugging

**Solutions**:
1. **Local debugging**: Hot-reload is enabled, just save the file
2. **Docker debugging**:
   - Volume mount is configured for hot-reload
   - Changes should apply automatically
   - If not, restart: `docker-compose restart backend`

---

## 📚 Additional Resources

- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [debugpy Documentation](https://github.com/microsoft/debugpy)
- [FastAPI Debugging Guide](https://fastapi.tiangolo.com/tutorial/debugging/)

---

## 🎓 Example Debugging Session

### Scenario: Debug WebSocket Analysis Issue

1. **Enable debug mode**:
   ```bash
   # In deploy/.env
   PYTHON_DEBUG=true
   ```

2. **Restart backend**:
   ```bash
   cd /home/ppiccolo/projects/elysia/deploy
   docker-compose restart backend
   ```

3. **Set breakpoint**:
   - Open `elysia/api/routes/processor.py`
   - Set breakpoint at line 28 (inside `process_collection`)

4. **Attach debugger**:
   - Press `F5` in VS Code
   - Select "Python: Remote Attach (Docker)"

5. **Trigger the code**:
   - Go to frontend
   - Click "Analyze" button on a collection

6. **Debug**:
   - Execution pauses at breakpoint
   - Inspect `data` variable (collection_name, user_id)
   - Step through code with F10/F11
   - Check WebSocket connection status

7. **Clean up**:
   ```bash
   # In deploy/.env
   PYTHON_DEBUG=false
   docker-compose restart backend
   ```

---

Happy Debugging! 🐛✨
