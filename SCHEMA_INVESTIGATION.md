# Schema Property Detection Investigation

## Problem Statement

The HashtagAggregate tool was failing with the error:
```
WeaviateQueryError: no such prop with name 'text' found in class 'SocialMediaPosts'
```

This occurred because the tool hardcoded default property names (`text_property="text"`, `author_property="author"`), which didn't match the actual schema of the SocialMediaPosts collection.

## Investigation: How Elysia Handles Property Names

### Key Discovery

**Elysia tools do NOT hardcode property names.** Instead, they follow a pattern where:

1. **Tools only accept minimal inputs** - typically just `collection_names`
2. **The LLM determines which properties to use** by analyzing collection schemas
3. **Schema information is passed to the LLM** via `ElysiaChainOfThought`

### How Query and Aggregate Tools Work

#### 1. Tool Definition (No Property Inputs)

**Query Tool** ([elysia/tools/retrieval/query.py:46-78](elysia/tools/retrieval/query.py#L46-L78)):
```python
def __init__(self, ...):
    super().__init__(
        name="query",
        inputs={
            "collection_names": {
                "description": "the names of the collections...",
                "type": list[str],
                "default": [],
            },
        },
        # NO property name inputs!
    )
```

**Aggregate Tool** ([elysia/tools/retrieval/aggregate.py:28-56](elysia/tools/retrieval/aggregate.py#L28-L56)):
```python
def __init__(self, ...):
    super().__init__(
        name="aggregate",
        inputs={
            "collection_names": {
                "description": "the names of the collections...",
                "type": list[str],
                "default": [],
            },
        },
        # NO property name inputs!
    )
```

#### 2. Schema is Passed to LLM

**ElysiaChainOfThought** ([elysia/util/elysia_chain_of_thought.py:208-232](elysia/util/elysia_chain_of_thought.py#L208-L232)):
```python
if collection_schemas:
    collection_schemas_desc = (
        "Metadata about available collections and their schemas: "
        "This is a dictionary with the following fields: "
        "{\n"
        "    name: collection name,\n"
        "    fields: [\n"
        "        {\n"
        "            name: field_name,\n"
        "            type: the data type of the field.\n"
        "            description: ...\n"
        "        },\n"
        "        ...\n"
        "    ]\n"
        "}\n"
    )
```

The schema is obtained via:
```python
schemas = tree_data.output_collection_metadata(with_mappings=True)
```

#### 3. LLM Generates Query with Correct Property Names

The LLM analyzes the schema and generates appropriate queries that reference the actual property names in the collection. For example:

- If schema shows `{name: "author_name", type: "text"}`, the LLM uses `"author_name"`
- If schema shows `{name: "tweet_content", type: "text"}`, the LLM uses `"tweet_content"`

#### 4. Properties Are Used During Query Execution

**Aggregate Tool** ([elysia/tools/retrieval/aggregate.py:173-178](elysia/tools/retrieval/aggregate.py#L173-L178)):
```python
property_types={
    collection_name: {
        schemas[collection_name]["fields"][i]["name"]:
        schemas[collection_name]["fields"][i]["type"]
        for i in range(len(schemas[collection_name]["fields"]))
    }
    for collection_name in collection_names
}
```

## Solution Applied to HashtagAggregate

### Changes Made

1. **Removed Hardcoded Property Inputs**
   - Removed `author_property` input (was default: `"author"`)
   - Removed `text_property` input (was default: `"text"`)
   - Now only accepts: `hashtag`, `collection_name`, `limit`

2. **Added DSPy Signature for Property Detection**
   ```python
   class HashtagAggregateQuery(BaseModel):
       author_property: str
       text_property: str

   class HashtagQueryPrompt(dspy.Signature):
       collection_schemas: dict = dspy.InputField()
       collection_name: str = dspy.InputField()
       hashtag: str = dspy.InputField()
       query_params: HashtagAggregateQuery = dspy.OutputField()
   ```

3. **LLM Determines Properties at Runtime**
   ```python
   query_generator = dspy.ChainOfThought(HashtagQueryPrompt)
   query_params = await query_generator.aforward(
       lm=complex_lm,
       collection_schemas={collection_name: schemas[collection_name]},
       collection_name=collection_name,
       hashtag=hashtag
   )

   author_property = query_params.query_params.author_property
   text_property = query_params.query_params.text_property
   ```

### Benefits

✅ **Dynamic Schema Adaptation**: Works with any collection schema
✅ **No Hardcoded Assumptions**: LLM determines correct properties
✅ **Consistent with Elysia Pattern**: Follows same approach as Query and Aggregate tools
✅ **Resilient to Schema Changes**: Adapts automatically when schemas change

### Example Scenario

**Before (Hardcoded)**:
```python
# Fails if collection doesn't have "text" property
response = await collection.query.fetch_objects(
    filters=Filter.by_property("text").like(f"*{hashtag}*"),  # ❌ Hardcoded
    return_properties=["author", "text"]  # ❌ Hardcoded
)
```

**After (LLM-Determined)**:
```python
# LLM analyzes schema and determines:
# - SocialMediaPosts has "tweet_content" (not "text")
# - SocialMediaPosts has "author" (correct)
response = await collection.query.fetch_objects(
    filters=Filter.by_property("tweet_content").like(f"*{hashtag}*"),  # ✅ Dynamic
    return_properties=["author", "tweet_content"]  # ✅ Dynamic
)
```

## Schema Structure

The schema provided to tools via `tree_data.output_collection_metadata()` includes:

```python
{
    "collection_name": {
        "fields": [
            {
                "name": "field_name",
                "type": "text" | "number" | "int" | ...,
                "description": "AI-generated description",
                "groups": {...},  # unique values
                "mean": float,    # average length/value
                "range": [min, max]
            },
            ...
        ],
        "length": int,  # number of objects
        "summary": str,  # AI-generated collection summary
        "vectorizer": str | None,
        "named_vectors": [...],
        "mappings": {...}  # frontend display mappings
    }
}
```

## Related Files

- [elysia/tools/retrieval/query.py](elysia/tools/retrieval/query.py) - Query tool implementation
- [elysia/tools/retrieval/aggregate.py](elysia/tools/retrieval/aggregate.py) - Aggregate tool implementation
- [elysia/util/elysia_chain_of_thought.py](elysia/util/elysia_chain_of_thought.py) - LLM context management
- [elysia/tree/objects.py](elysia/tree/objects.py) - Schema metadata (line 816+)
- [elysia/tools/retrieval/hashtag_aggregate.py](elysia/tools/retrieval/hashtag_aggregate.py) - Updated implementation

## Conclusion

The investigation revealed that **Elysia's architecture is designed for schema flexibility**. Tools should not make assumptions about property names, but instead rely on the LLM to analyze collection schemas and determine the appropriate properties to use.

This approach ensures that tools work across different collection schemas without modification, making the system more robust and maintainable.
