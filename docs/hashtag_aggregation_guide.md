# Hashtag Aggregation Tool Guide

## Overview

The `HashtagAggregate` tool is a custom Elysia tool designed to solve the limitation where standard aggregation queries cannot filter by hashtag content. This tool enables you to accurately count tweets (or other text content) by author when filtered by a specific hashtag.

## Problem Statement

**Challenge**: The standard `aggregate` tool in Elysia cannot filter aggregations by hashtag patterns within text fields. If you want to know "which author tweets most frequently with hashtag #example", the standard aggregate tool can only count total tweets by author, not hashtag-specific tweets.

**Solution**: `HashtagAggregate` retrieves all objects containing the specified hashtag and then performs post-query aggregation by author, providing accurate hashtag-specific counts.

## Architecture

```
User Query
    ↓
HashtagAggregate Tool
    ↓
Weaviate Query (with LIKE filter for hashtag)
    ↓
Retrieve matching objects
    ↓
Post-process: Count by author
    ↓
Return aggregated results
```

## Features

- ✅ **Hashtag-specific filtering**: Accurately filter by hashtag content
- ✅ **Author aggregation**: Count tweets per author
- ✅ **Flexible configuration**: Customize property names, limits
- ✅ **Rich output**: Sorted results with metadata
- ✅ **Elysia integration**: Works seamlessly with the Elysia framework
- ✅ **Async support**: Fully asynchronous for performance

## Installation

The tool is included in the Elysia codebase at:
```
elysia/tools/retrieval/hashtag_aggregate.py
```

No additional dependencies are required beyond Elysia's standard requirements.

## Usage

### Basic Usage with Tree

```python
from elysia import Tree
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate

# Initialize tree and add the tool
tree = Tree()
hashtag_tool = HashtagAggregate()
tree.tools.append(hashtag_tool)

# Query naturally
response, objects = tree(
    "Who tweets most frequently with #example?",
    collection_names=["Tweets"]
)

print(response)
```

### Advanced Configuration

```python
# Direct tool invocation with custom parameters
from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
import dspy

# Setup
tree_data = TreeData(
    user_prompt="Find top tweeter for hashtag",
    collection_names=["ArabicTweets"],
    settings=Settings()
)
client_manager = ClientManager(settings)
hashtag_tool = HashtagAggregate()

inputs = {
    "hashtag": "#السلطان_هيثم_يزور_بيلاروس",
    "collection_name": "ArabicTweets",
    "author_property": "author",  # Property containing author name
    "text_property": "text",      # Property containing tweet text
    "limit": 1000                  # Max tweets to retrieve
}

async for result in hashtag_tool(
    tree_data=tree_data,
    inputs=inputs,
    client_manager=client_manager,
    base_lm=base_lm,
    complex_lm=complex_lm
):
    # Process results
    if hasattr(result, 'metadata'):
        print(result.metadata['top_author'])
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `hashtag` | str | Yes | - | The hashtag to filter by (with or without # prefix) |
| `collection_name` | str | Yes | - | Weaviate collection containing the tweets |
| `author_property` | str | No | `"author"` | Property name for author information |
| `text_property` | str | No | `"text"` | Property name for tweet text content |
| `limit` | int | No | `1000` | Maximum number of tweets to retrieve |

## Output Format

The tool yields multiple response types:

### 1. Status Messages
```python
Response(text="Searching for tweets with hashtag #example...")
Status("Found 150 tweets from 42 authors")
```

### 2. Aggregation Results
```python
Aggregation(
    objects=[{
        "num_items": 150,
        "collections": [{
            "Tweets": {
                "authors": [
                    {"author": "user1", "count": 32},
                    {"author": "user2", "count": 28},
                    # ... sorted by count descending
                ]
            }
        }]
    }],
    metadata={
        "collection_name": "Tweets",
        "hashtag": "#example",
        "total_tweets": 150,
        "unique_authors": 42,
        "top_author": ("user1", 32),
        "author_counts": {"user1": 32, "user2": 28, ...}
    }
)
```

### 3. Summary Text
```python
Text(text="The author who tweets most frequently with #example is **user1** with 32 tweets...")
```

## Performance Considerations

### Scalability
- **Limit Parameter**: The tool retrieves up to `limit` tweets. For very large datasets, consider:
  - Setting appropriate limits (default: 1000)
  - Running multiple queries with different time ranges if needed
  - Using pagination for very large result sets

### Optimization Tips
1. **Limit Setting**: Balance between completeness and performance
   - Small datasets: `limit=10000` for comprehensive results
   - Large datasets: `limit=1000` for quick analysis

2. **Property Selection**: Only request necessary properties
   - Default: `[author_property, text_property]`
   - Reduces data transfer overhead

3. **Hashtag Specificity**: More specific hashtags = faster queries
   - Good: `#specific_event_2024`
   - Less optimal: `#news` (very common)

## Comparison with Standard Tools

| Feature | Standard Aggregate | HashtagAggregate |
|---------|-------------------|------------------|
| Count all by author | ✅ | ✅ |
| Filter by hashtag | ❌ | ✅ |
| Native Weaviate aggregation | ✅ | ❌ (post-query) |
| Performance on large datasets | Faster | Good (with limits) |
| Use case | General aggregation | Hashtag-specific analysis |

## Use Cases

### 1. Social Media Analysis
```python
# Find influencers for specific campaign hashtags
"Who tweets most about #product_launch?"
```

### 2. Event Tracking
```python
# Track event participation by author
"Which authors are most active with #conference2024?"
```

### 3. Trend Analysis
```python
# Identify top contributors to trending topics
"Top 10 authors tweeting with #breaking_news"
```

### 4. Content Moderation
```python
# Monitor specific hashtag usage patterns
"Authors with highest usage of #sensitive_topic"
```

## Error Handling

The tool handles common errors gracefully:

```python
# Collection not found
Error(error_message="Collection 'InvalidName' not found...")

# No tweets with hashtag
Response(text="No tweets found containing hashtag #rare_tag")

# Connection issues
Error(error_message="Failed to aggregate by hashtag: Connection timeout")
```

## Limitations

1. **Post-Query Aggregation**: Not as efficient as native Weaviate aggregation for very large datasets
2. **Limit Constraint**: Results capped by `limit` parameter (default 1000)
3. **Text Matching**: Uses LIKE operator, may match hashtags in various contexts
4. **Single Hashtag**: Designed for one hashtag per query (use multiple queries for multiple hashtags)

## Future Enhancements

Potential improvements:
- [ ] Multiple hashtag support (AND/OR logic)
- [ ] Time-based filtering (date ranges)
- [ ] Advanced regex patterns for hashtag matching
- [ ] Streaming results for very large datasets
- [ ] Caching frequently queried hashtags
- [ ] Export to CSV/JSON for further analysis

## Troubleshooting

### Issue: "No tweets found"
**Solution**:
- Verify hashtag spelling and case sensitivity
- Check if hashtag exists in the collection
- Try without # prefix: `example` instead of `#example`

### Issue: "Collection not found"
**Solution**:
- Verify collection name spelling
- Ensure collection is added to tree: `tree.collection_names`
- Check Weaviate connection

### Issue: Slow performance
**Solution**:
- Reduce `limit` parameter
- Filter by time range if possible
- Ensure Weaviate indexes are optimized

## API Reference

### Class: `HashtagAggregate`

```python
class HashtagAggregate(Tool):
    """
    Custom tool for aggregating tweet counts by author for a specific hashtag.
    """

    def __init__(self, logger: Logger | None = None, **kwargs)
        """Initialize the hashtag aggregation tool."""

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: dict,
        client_manager: ClientManager,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        **kwargs,
    )
        """
        Execute hashtag aggregation query.

        Yields:
            Response: Status updates
            Aggregation: Aggregated results
            Text: Summary message
            Error: Error messages
        """
```

## Contributing

To extend or modify the tool:

1. Fork the Elysia repository
2. Modify `elysia/tools/retrieval/hashtag_aggregate.py`
3. Add tests in `tests/`
4. Submit a pull request

## License

This tool is part of the Elysia project and follows the same license.

## Support

For issues or questions:
- GitHub Issues: [weaviate/elysia](https://github.com/weaviate/elysia/issues)
- Documentation: [https://weaviate.github.io/elysia/](https://weaviate.github.io/elysia/)
- Community: Weaviate Slack/Discord

## Changelog

### v1.0.0 (Initial Release)
- Basic hashtag filtering and author aggregation
- Configurable property names and limits
- Rich output formatting
- Comprehensive error handling
