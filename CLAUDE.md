# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Elysia is an open-source agentic framework for searching and retrieving data, powered by decision trees. It uses Weaviate as the default retrieval backend and supports custom tool creation. The project consists of:

- **Python backend** (`elysia/`): Core decision tree framework, tools, and FastAPI app
- **Frontend**: Separate repository at [elysia-frontend](https://github.com/weaviate/elysia-frontend)
- **Documentation**: MkDocs site at https://weaviate.github.io/elysia/

## Key Commands

### Installation and Setup
```bash
# Install from PyPI
pip install elysia-ai

# Install from source (development)
pip install -e .

# Install with dev dependencies for testing
pip install ".[dev]"
```

### Running the Application
```bash
# Start the FastAPI app (default: http://localhost:8000)
elysia start

# With custom port/host
elysia start --port 8080 --host 0.0.0.0

# Without auto-reload
elysia start --reload False
```

### Testing
```bash
# Run tests without external requirements (recommended for contributors)
pytest tests/no_reqs

# Run all tests (requires API keys and Weaviate cluster)
pytest tests

# Run with coverage
pytest --cov=elysia tests/no_reqs
```

**Important**: Tests are split into two categories:
- `tests/no_reqs/`: No external dependencies, should always pass
- `tests/requires_env/`: Requires Weaviate cluster, OpenAI API key, OpenRouter API key (may incur costs)

### Documentation
```bash
# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

### Code Formatting
```bash
# Format with black
black elysia/ tests/
```

## Architecture

### Core Components

**Tree (`elysia/tree/tree.py`)**
- `Tree` class: Main decision tree orchestrator
- Manages LLM-based decision making across multiple branches
- Supports four initialization modes: `"default"`, `"one_branch"`, `"multi_branch"`, `"empty"`
- Uses DSPy for LLM interactions and structured outputs

**Objects (`elysia/objects.py`)**
- `Tool`: Base class for all tools (uses metaclass for metadata extraction)
- Response types: `Text`, `Update`, `Warning`, `Error`, `Completed`, `Result`, `Retrieval`
- `@tool` decorator: Register custom functions as tools

**Tools (`elysia/tools/`)**
- `retrieval/`: Weaviate integration (Query, Aggregate, Chunk tools)
- `text/`: Text generation tools (CitedSummarizer, FakeTextResponse)
- `visualisation/`: Data visualization tools
- `postprocessing/`: Result processing tools (SummariseItems)

**Configuration (`elysia/config.py`)**
- `Settings` class: Manages API keys, model selection, Weaviate connection
- Supports multiple providers: OpenAI, Anthropic, OpenRouter, Gemini, Azure, etc.
- Uses LiteLLM for model abstraction
- Loads from `.env` file automatically

**API (`elysia/api/`)**
- FastAPI application in `app.py`
- CLI entry point in `cli.py`
- Routes split across `routes/` directory
- User management and authentication in `core/` and `dependencies/`

**Preprocessing (`elysia/preprocessing/collection.py`)**
- `preprocess()`: Analyze Weaviate collections for Elysia usage
- Creates metadata collections with `ELYSIA_` prefix in Weaviate
- Functions: `preprocess`, `preprocessed_collection_exists`, `edit_preprocessed_collection`, `delete_preprocessed_collection`, `view_preprocessed_collection`

**Utilities (`elysia/util/`)**
- `client.py`: `ClientManager` for Weaviate client connections
- `elysia_chain_of_thought.py`: Custom chain-of-thought reasoning
- `objects.py`: `Tracker`, `TrainingUpdate`, `TreeUpdate` for state management
- `parsing.py`: Text and response parsing utilities
- `collection.py`: Collection name retrieval

### Tool Creation Pattern

Custom tools should inherit from `Tool` and implement:

```python
from elysia import Tool, Return

class MyTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Detailed description for LLM",
            inputs={
                "param1": {
                    "description": "Parameter description",
                    "type": "str",
                    "required": True
                }
            },
            end=False  # Set True if this tool ends the decision tree
        )

    async def run(self, param1: str) -> Return:
        # Implementation
        return Text("Result")
```

Or use the decorator:

```python
from elysia import tool, Tree

tree = Tree()

@tool(tree=tree)
async def my_function(x: int, y: int) -> int:
    return x + y
```

## Branch Strategy

- `main`: Active development for next release (new features go here)
- `release/vX.Y.x`: Stable release branches for bug fixes
- Feature branches: `feature/<description>`
- Bug fixes: `bugfix/<description>` (PR to `release/vX.Y.x`)
- Urgent fixes: `hotfix/<description>`
- Documentation: `docs/<description>`

## Environment Variables

Key environment variables (see `.env.example`):

**Weaviate Connection**
- `WCD_URL`: Weaviate Cloud URL
- `WCD_API_KEY`: Weaviate Cloud API key
- `WEAVIATE_IS_LOCAL`: `True` for local Docker instance
- `LOCAL_WEAVIATE_PORT`: Port for local Weaviate (default 8080)
- `LOCAL_WEAVIATE_GRPC_PORT`: gRPC port (default 50051)

**LLM Provider Keys** (one or more required)
- `OPENROUTER_API_KEY`: Recommended for multi-model access
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- Additional: `COHERE_API_KEY`, `MISTRAL_API_KEY`, `HUGGINGFACE_API_KEY`, etc.

**Model Configuration**
- `BASE_MODEL`: Fast model for simple decisions (e.g., `gemini-2.0-flash-001`)
- `COMPLEX_MODEL`: Powerful model for complex reasoning (e.g., `claude-sonnet-4-20250514`)
- `BASE_PROVIDER`: Provider prefix (e.g., `openrouter/google`)
- `COMPLEX_PROVIDER`: Provider prefix

## Python Usage Patterns

**Basic usage**:
```python
from elysia import Tree, tool

tree = Tree()

@tool(tree=tree)
async def add(x: int, y: int) -> int:
    return x + y

tree("What is 5 + 3?")
```

**With Weaviate collections**:
```python
from elysia import Tree

tree = Tree()
response, objects = tree(
    "Find the 10 most expensive items",
    collection_names=["Ecommerce"]
)
```

**Preprocess collections**:
```python
from elysia.preprocessing.collection import preprocess

preprocess(collection_names=["YourCollectionName"])
```

**Custom settings**:
```python
from elysia import Tree, Settings

settings = Settings(
    base_model="gpt-4o-mini",
    complex_model="gpt-4o",
    wcd_url="https://your-cluster.weaviate.network",
    wcd_api_key="your-key"
)

tree = Tree(settings=settings)
```

## Package Management

- Build system: Hatchling
- Python version: `>=3.10.0, <3.13.0`
- Main dependencies: `dspy-ai`, `fastapi`, `weaviate-client`, `litellm`, `spacy`, `rich`
- CLI entry point: `elysia` command maps to `elysia.api.cli:cli`

## Important Notes

- Elysia stores metadata in Weaviate collections with `ELYSIA_` prefix
- The framework uses async/await patterns extensively
- LLM behavior can vary; issues may be LLM-specific rather than code bugs
- Local models require significant context length support (8k+ tokens recommended)
- The project uses Rich for terminal output formatting
- First-time startup triggers Spacy model download (`en_core_web_sm`)