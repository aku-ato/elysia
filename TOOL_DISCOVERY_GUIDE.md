# Tool Discovery Guide

## Purpose
Systematically identify which custom tools are **actually needed** vs. which queries work fine with standard `Aggregate` and `Query` tools.

## Discovery Scripts

### 1. **Comprehensive Discovery** (`discover_tool_needs.py`)
Tests multiple query categories to identify patterns:

```bash
.venv/bin/python scripts/query/discover_tool_needs.py
```

**Categories Tested:**
- ✅ **Hashtag Analysis**: Co-occurrence, multi-hashtag filtering
- ✅ **Temporal Analysis**: Time-based aggregations, trends
- ✅ **Author Behavior**: Activity patterns, engagement metrics
- ⚠️  **Content Analysis**: NLP, sentiment (known to need custom tools)
- ⚠️  **Network Analysis**: Mention graphs, reply chains

**Output**:
- Console report with ✅/❌/⏭️ status
- `tool_discovery_results.json` with detailed results

### 2. **Quick Test** (`quick_test.py`)
Fast single-query testing:

```bash
# Edit QUERY variable in the script
.venv/bin/python scripts/query/quick_test.py
```

## Decision Matrix

| Query Pattern | Standard Tools | Custom Tool Needed | Why |
|---------------|---------------|-------------------|-----|
| **Single hashtag + author count** | ✅ Aggregate | ❌ No | `CONTAINS_ANY` filter works |
| **Multiple hashtags (AND)** | ✅ Aggregate | ❌ No | Multiple filters |
| **Multiple hashtags (OR)** | ✅ Aggregate | ❌ No | `CONTAINS_ANY` with array |
| **Hashtag co-occurrence** | ❌ Complex | ✅ **Yes** | Requires array intersection |
| **Time-based aggregation** | ✅ Aggregate | ❌ No | Group by date field |
| **Trending (time comparison)** | ⚠️  Slow | ✅ **Maybe** | Two aggregations + comparison |
| **Author activity patterns** | ✅ Aggregate | ❌ No | Group by + count |
| **Text analysis (NLP)** | ❌ No | ✅ **Yes** | Requires custom processing |
| **Sentiment analysis** | ❌ No | ✅ **Yes** | Requires ML model |
| **Network/graph analysis** | ❌ No | ✅ **Yes** | Requires graph algorithms |

## Custom Tool Candidates

Based on discovery testing, these are strong candidates for custom tools:

### **High Priority**

#### 1. **HashtagCooccurrence**
**Query**: "What other hashtags appear with #X?"
**Why**: Requires array intersection/analysis not supported by standard aggregation
**Use Case**: Discover related topics, trend analysis

```python
# Current workaround: Fetch all + client-side analysis
# Better: Custom tool with efficient hashtag pair counting
```

#### 2. **TrendingHashtags**
**Query**: "Which hashtags are trending this week vs last week?"
**Why**: Requires time-window comparison and delta calculation
**Use Case**: Social media monitoring, emerging topics

```python
# Current workaround: Two separate aggregations + manual comparison
# Better: Custom tool with built-in time comparison
```

#### 3. **AuthorInsights**
**Query**: "Show posting patterns for @username"
**Why**: Combines multiple metrics (frequency, times, topics)
**Use Case**: Author profiling, influencer analysis

```python
# Current workaround: Multiple queries + aggregation
# Better: Unified author analysis tool
```

### **Medium Priority**

#### 4. **ContentKeywords**
**Query**: "Most common words in tweets about #topic"
**Why**: Requires NLP/text processing
**Use Case**: Content analysis, theme identification

#### 5. **SentimentAnalysis**
**Query**: "Sentiment distribution for #topic"
**Why**: Requires ML sentiment model
**Use Case**: Brand monitoring, opinion tracking

### **Low Priority (Complex)**

#### 6. **NetworkGraph**
**Query**: "Who does @user mention most?"
**Why**: Requires graph analysis
**Use Case**: Influence mapping, community detection

## Testing Methodology

### Step 1: Hypothesis
Identify a query pattern that might need a custom tool.

**Example**: "What hashtags appear together with #X?"

### Step 2: Test with Standard Tools
Edit `quick_test.py`:
```python
QUERY = "What hashtags appear most frequently with #السلطان_هيثم_يزور_بيلاروس?"
```

Run:
```bash
.venv/bin/python scripts/query/quick_test.py
```

### Step 3: Evaluate Results

**✅ Success Criteria**:
- Query completes without errors
- Results are accurate
- Performance is acceptable (<5s for 1000 items)
- LLM selects appropriate tool

**❌ Failure Indicators**:
- Query fails or returns incorrect results
- Requires complex workarounds
- Performance is poor (>10s for simple aggregation)
- LLM can't determine how to answer

**⚠️  Custom Tool Justified When**:
- Standard tools work but require multiple queries + manual processing
- Performance is poor due to client-side processing
- Query pattern is common enough to warrant optimization

### Step 4: Decision

| Result | Action |
|--------|--------|
| ✅ Standard tools work well | **No custom tool needed** |
| ❌ Standard tools fail | **Custom tool required** |
| ⚠️  Works but slow/complex | **Evaluate cost/benefit** |

## Example Discoveries

### ✅ **Discovery 1: Single Hashtag Aggregation**
**Query**: "Top authors for #hashtag"
**Test Result**: ✅ Works perfectly with standard Aggregate
**Conclusion**: ❌ No custom tool needed (even though we built one!)

### ❌ **Discovery 2: Hashtag Co-occurrence**
**Query**: "What hashtags appear with #X?"
**Test Result**: ❌ Aggregate can't do array intersection
**Conclusion**: ✅ Custom tool needed

### ⚠️ **Discovery 3: Trending Analysis**
**Query**: "Trending hashtags this week"
**Test Result**: ⚠️  Requires 2 aggregations + comparison
**Conclusion**: ⚠️  Custom tool optional (depends on usage frequency)

## Implementation Priority

### Tier 1: **Must Have**
Tools that solve unsupported query patterns with high user value:
- HashtagCooccurrence (if used frequently)

### Tier 2: **Should Have**
Tools that improve efficiency for common patterns:
- TrendingHashtags (if monitoring is core use case)
- AuthorInsights (if user profiling is important)

### Tier 3: **Nice to Have**
Tools for advanced/specialized analysis:
- ContentKeywords (NLP analysis)
- SentimentAnalysis (opinion tracking)
- NetworkGraph (influence mapping)

## Running the Full Discovery

```bash
# Run comprehensive test suite
.venv/bin/python scripts/query/discover_tool_needs.py > discovery_log.txt 2>&1

# Review results
cat tool_discovery_results.json | jq '.[] | select(.status == "failed")'

# Identify custom tool candidates
cat tool_discovery_results.json | jq -r '.[] | select(.status == "failed") | "\(.name): \(.expected_tool)"'
```

## Next Steps

1. **Run Discovery**: Execute `discover_tool_needs.py`
2. **Analyze Results**: Review which queries failed
3. **Prioritize**: Use decision matrix to identify real needs
4. **Implement**: Build only justified custom tools
5. **Validate**: Test custom tools improve over standard approach

## Key Principle

> **Only build custom tools when standard tools genuinely can't handle the query OR when performance/UX justifies the maintenance cost.**

The HashtagAggregate lesson: We built a custom tool thinking Weaviate couldn't handle it, but standard Aggregate actually works fine! Let's not repeat that mistake.
