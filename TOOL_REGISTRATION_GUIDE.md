# Tool Registration Guide for Elysia

## Problem: "Tool Not Found"

When you see:
```
"No, the tool hashtag_aggregate is not available.
The tools we have are: cited_summarize, text_response, aggregate, query, and visualise."
```

**Root Cause**: The tool exists but **isn't registered** with the Tree.

---

## Understanding Tool Registration

### How Elysia Discovers Tools

```
1. Tree.__init__()
   └─ Sets up self.tools = {}

2. set_branch_initialisation()
   └─ Calls multi_branch_init() or one_branch_init()

3. multi_branch_init()
   └─ Calls add_tool() for default tools:
      ├─ Query
      ├─ Aggregate
      ├─ Visualise
      ├─ CitedSummarizer
      ├─ FakeTextResponse
      └─ SummariseItems

4. Tree searches self.tools for available options
```

**Your custom tool must be added via `add_tool()`!**

---

## Solution 1: Manual Registration (Recommended)

### Quick Start

```python
from elysia import Tree
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate

# Create tree
tree = Tree()

# ⭐ Register your tool
tree.add_tool(
    tool=HashtagAggregate,
    branch_id="search"  # Add to search branch with Query/Aggregate
)

# Use it!
response, objects = tree(
    "Who tweets most with #السلطان_هيثم_يزور_بيلاروس?",
    collection_names=["ArabicTweets"]
)
```

### Understanding Branches

The default Tree has this structure:

```
root: "base"
├─ Tool: cited_summarize (CitedSummarizer)
├─ Tool: text_response (FakeTextResponse)
├─ Tool: visualise (Visualise)
└─ Branch: "search"
   ├─ Tool: query (Query)
   ├─ Tool: aggregate (Aggregate)
   └─ [ADD YOUR TOOL HERE] ⭐
      └─ Tool: hashtag_aggregate (HashtagAggregate)
```

**Why `branch_id="search"`?**
- Retrieval tools belong in the "search" branch
- Keeps organization logical
- LLM can find it when user asks about data retrieval

---

## Solution 2: Using the Convenience Script

### Option A: Direct Python Usage

```python
from scripts.query_hashtag_author import create_tree_with_hashtag_tool

# Get pre-configured tree
tree = create_tree_with_hashtag_tool()

# Use immediately
response, objects = tree(
    "Top authors for #example?",
    collection_names=["Tweets"]
)
```

### Option B: Command Line

```bash
# Activate environment
source .venv/bin/activate

# Run query
python scripts/query_hashtag_author.py "#السلطان_هيثم_يزور_بيلاروس"

# Or specify collection
python scripts/query_hashtag_author.py "#example" ArabicTweets
```

---

## Solution 3: Custom Tree Subclass

For permanent integration, create a custom Tree class:

```python
# elysia/tree/custom_trees.py
from elysia.tree.tree import Tree
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate

class ExtendedTree(Tree):
    """Tree with additional custom tools including HashtagAggregate"""

    def multi_branch_init(self):
        # Call parent initialization
        super().multi_branch_init()

        # Add custom tools
        self.add_tool(
            tool=HashtagAggregate,
            branch_id="search"
        )

# Usage
from elysia.tree.custom_trees import ExtendedTree

tree = ExtendedTree()
# HashtagAggregate is automatically available!
```

---

## Solution 4: Modify Tree Default Initialization

**⚠️ Not Recommended** (changes core Elysia code)

If you want HashtagAggregate available by default:

```python
# elysia/tree/tree.py

# Add import at top
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate

# In multi_branch_init() method (around line 246)
def multi_branch_init(self):
    # ... existing code ...

    self.add_tool(branch_id="search", tool=Query, summariser_in_tree=True)
    self.add_tool(branch_id="search", tool=Aggregate)

    # ⭐ ADD THIS LINE
    self.add_tool(branch_id="search", tool=HashtagAggregate)

    # ... rest of code ...
```

**Drawback**: Your changes will be overwritten on updates

---

## Complete Working Example

```python
#!/usr/bin/env python3
"""
Complete example showing tool registration and usage
"""

from elysia import Tree
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate


def main():
    print("Creating Tree with HashtagAggregate tool...")

    # Step 1: Create tree
    tree = Tree()
    print(f"✓ Tree created")
    print(f"  Default tools: {list(tree.tools.keys())}")

    # Step 2: Register custom tool
    tree.add_tool(
        tool=HashtagAggregate,
        branch_id="search"
    )
    print(f"✓ HashtagAggregate registered")
    print(f"  Updated tools: {list(tree.tools.keys())}")

    # Step 3: Verify registration
    if "hashtag_aggregate" in tree.tools:
        print("✓ Tool successfully registered!")
    else:
        print("✗ Tool registration failed!")
        return

    # Step 4: Use the tool
    print("\nExecuting query...")
    response, objects = tree(
        "Who tweets most frequently with #السلطان_هيثم_يزور_بيلاروس?",
        collection_names=["ArabicTweets"]
    )

    print(f"\nResponse: {response}")

    # Step 5: Display results
    if objects:
        for obj in objects:
            if 'collections' in obj:
                for collection_data in obj['collections']:
                    for coll_name, data in collection_data.items():
                        if 'authors' in data:
                            print(f"\nTop authors:")
                            for author_data in data['authors'][:5]:
                                print(f"  - {author_data['author']}: {author_data['count']}")


if __name__ == "__main__":
    main()
```

---

## Understanding `add_tool()` Parameters

### Basic Usage
```python
tree.add_tool(tool=HashtagAggregate, branch_id="search")
```

### Advanced Options

```python
tree.add_tool(
    tool=HashtagAggregate,           # Required: Tool class or instance
    branch_id="search",              # Which branch to add to
    from_tool_ids=[],                # Add after specific tools
    root=False,                      # Add to root branch
    logger=custom_logger,            # Custom logger instance
    # ... any tool-specific kwargs
)
```

#### Parameters Explained:

**`tool`** (required)
- Tool class (e.g., `HashtagAggregate`) or instance
- Must inherit from `elysia.objects.Tool`

**`branch_id`** (optional)
- Which branch to add the tool to
- Common values: `"base"`, `"search"`
- Default: root branch

**`from_tool_ids`** (optional)
- Add tool after specific tools in the branch
- Example: `from_tool_ids=["query"]` adds after Query tool
- Creates sub-decision nodes

**`root`** (optional)
- If `True`, adds to root branch (ignores `branch_id`)
- Default: `False`

**`**kwargs`** (optional)
- Additional arguments passed to tool's `__init__`
- Example: `logger=custom_logger`

---

## Verification Checklist

After registering your tool:

```python
# 1. Check tool is in dictionary
assert "hashtag_aggregate" in tree.tools
print("✓ Tool in registry")

# 2. Check tool is correct type
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate
assert isinstance(tree.tools["hashtag_aggregate"], HashtagAggregate)
print("✓ Tool is correct type")

# 3. Check branch has tool
search_branch = tree.decision_nodes["search"]
assert "hashtag_aggregate" in search_branch.options
print("✓ Tool in search branch")

# 4. Test tool execution
response, objects = tree(
    "Test hashtag query",
    collection_names=["TestCollection"]
)
print("✓ Tool executes successfully")
```

---

## Common Issues & Solutions

### Issue 1: "Tool not found" error

**Problem:**
```python
tree = Tree()
response, objects = tree("Who tweets most with #hashtag?", ...)
# Error: "No tool named hashtag_aggregate available"
```

**Solution:**
```python
tree = Tree()
tree.add_tool(tool=HashtagAggregate, branch_id="search")  # ⭐ Add this!
response, objects = tree("Who tweets most with #hashtag?", ...)
```

### Issue 2: "Branch not found" error

**Problem:**
```python
tree.add_tool(tool=HashtagAggregate, branch_id="nonexistent")
# ValueError: Branch 'nonexistent' not found
```

**Solution:**
```python
# Use existing branch
tree.add_tool(tool=HashtagAggregate, branch_id="search")

# OR create branch first
tree.add_branch(branch_id="custom", root=True, instruction="...")
tree.add_tool(tool=HashtagAggregate, branch_id="custom")
```

### Issue 3: Tool registered but not used

**Problem:**
```python
tree.add_tool(tool=HashtagAggregate, branch_id="search")
response, objects = tree("Count total tweets by author", ...)
# Uses Aggregate instead of HashtagAggregate
```

**Solution:**
This is expected! The LLM chooses the tool based on:
- User query wording
- Tool descriptions

Make your query specific:
```python
# Better query wording
response, objects = tree(
    "Who tweets most frequently with hashtag #example?",  # ⭐ Mention "hashtag"
    collection_names=["Tweets"]
)
```

---

## Best Practices

### 1. **Register Once, Use Many Times**
```python
# Good: Register once
tree = Tree()
tree.add_tool(tool=HashtagAggregate, branch_id="search")

# Use multiple times
result1 = tree("Query 1 with #hashtag1", ...)
result2 = tree("Query 2 with #hashtag2", ...)
```

### 2. **Use Helper Functions**
```python
def create_configured_tree():
    """Create tree with all custom tools"""
    tree = Tree()
    tree.add_tool(tool=HashtagAggregate, branch_id="search")
    # Add other custom tools...
    return tree

# Use everywhere
tree = create_configured_tree()
```

### 3. **Verify Registration**
```python
tree = Tree()
tree.add_tool(tool=HashtagAggregate, branch_id="search")

# Verify before using
if "hashtag_aggregate" not in tree.tools:
    raise RuntimeError("HashtagAggregate not registered!")
```

### 4. **Clear Query Wording**
```python
# Good: Explicit hashtag mention
tree("Who tweets most with hashtag #example?", ...)

# Less good: Ambiguous
tree("Who tweets most about the event?", ...)
```

---

## Summary

### The Problem
Custom tools are **not automatically discovered**. You must explicitly register them.

### The Solution
```python
tree = Tree()
tree.add_tool(tool=HashtagAggregate, branch_id="search")
```

### Quick Reference
| Method | Use Case | Complexity |
|--------|----------|-----------|
| Manual `add_tool()` | Testing, development | Low |
| Helper script | Repeated use | Low |
| Custom Tree subclass | Permanent integration | Medium |
| Modify defaults | Organization-wide | High |

### Files You Need
- **Tool**: `elysia/tools/retrieval/hashtag_aggregate.py` ✅ (created)
- **Helper**: `scripts/query_hashtag_author.py` ✅ (created)
- **Guide**: This file ✅

---

## Next Steps

1. **Test registration:**
   ```bash
   source .venv/bin/activate
   python scripts/query_hashtag_author.py "#السلطان_هيثم_يزور_بيلاروس"
   ```

2. **Integrate into your workflow:**
   ```python
   from scripts.query_hashtag_author import create_tree_with_hashtag_tool
   tree = create_tree_with_hashtag_tool()
   ```

3. **Get your validated answer!**
   ```python
   response, objects = tree(
       "Who tweets most frequently with #السلطان_هيثم_يزور_بيلاروس?",
       collection_names=["ArabicTweets"]
   )
   ```

---

**Status**: 🟢 Solution Complete
**Next**: Run the helper script to get your validated answer!
