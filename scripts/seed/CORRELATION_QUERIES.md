# Cross-Collection Correlation Query Examples

This document provides example queries to test the correlation capabilities of Elysia using the `SocialMediaPosts` and `AudioTranscriptions` collections.

## 📊 Collection Overview

### SocialMediaPosts
- **Records**: ~13 multilingual tweets
- **Languages**: Arabic (ar), English (en), Italian (it)
- **Key Fields**: post_id, content, language, timestamp, author_id, topic, sentiment, hashtags, event_id, location

### AudioTranscriptions
- **Records**: ~10 multilingual transcripts
- **Languages**: Arabic (ar), English (en), Italian (it)
- **Key Fields**: transcription_id, transcript, language, duration_seconds, timestamp, speaker_id, topic, audio_quality, keywords, event_id, session_type

## 🔗 Correlation Keys

Both collections share these fields for correlation:
1. **event_id** - Same event/conference
2. **author_id / speaker_id** - Same person
3. **topic** - Related topics
4. **timestamp** - Temporal correlation
5. **language** - Language-based analysis

---

## 📝 Example Query Scenarios

### 1. Event-Based Correlation

**Query**: "Show me all content from the tech conference 2025 (both posts and transcripts)"

**Expected Result**:
- All 13 posts with `event_id: "tech_conf_2025"`
- All 10 transcripts with `event_id: "tech_conf_2025"`
- Displays combined results from both collections

---

### 2. Person-Based Correlation

**Query**: "Find all contributions from Ahmed (both social posts and speeches)"

**Expected Result**:
- Posts where `author_id: "user_ahmed"` (3 posts)
- Transcripts where `speaker_id: "user_ahmed"` (3 keynote transcripts)
- Shows Ahmed's activity across platforms

**Variant**: "What did Sarah say in her talks vs what she posted on social media?"

---

### 3. Topic Correlation

**Query**: "Compare discussions about machine learning in medicine across social media and conference sessions"

**Expected Result**:
- Posts with `topic: "ML in Medicine"` (3 posts)
- Transcripts with `topic: "ML in Medicine"` (3 panel transcripts)
- Reveals how the topic is discussed in different contexts

---

### 4. Multilingual Analysis

**Query**: "Show me all Italian content from the conference (posts and speeches)"

**Expected Result**:
- Posts where `language: "it"` (4 Italian posts)
- Transcripts where `language: "it"` (4 Italian transcripts)
- Language-specific perspective

**Variant**: "Compare sentiment about the workshop in Arabic vs English vs Italian"

---

### 5. Temporal Correlation

**Query**: "What were people posting during the ML basics workshop?"

**Expected Result**:
- Workshop started at 14:00 (5 hours after base_time)
- Posts timestamped around 14:00-15:00 (negative sentiment)
- Transcripts from the workshop session
- Shows real-time social reaction to live events

**Variant**: "Show the timeline of all activities on January 15, 2025"

---

### 6. Sentiment vs Content Analysis

**Query**: "Compare the sentiment in social posts about the keynote with the actual keynote content"

**Expected Result**:
- Keynote transcripts (topic: "AI in Healthcare", positive technical content)
- Social posts about keynote (all positive sentiment)
- Reveals alignment between content and reception

**Variant**: "Which sessions generated negative reactions on social media?"

---

### 7. Speaker-Audience Interaction

**Query**: "Find sessions where Marco asked questions and compare with his social posts"

**Expected Result**:
- Marco's posts (tw_008, tw_010, others)
- Workshop transcript where Marco is mentioned (aud_010 Q&A)
- Shows participant engagement across channels

---

### 8. Keyword Correlation

**Query**: "Find all content mentioning 'diagnostics' or 'medical' across both collections"

**Expected Result**:
- Transcripts with keywords: ["Medical", "Diagnostics"] (aud_002, aud_003, etc.)
- Posts with hashtags: ["#Healthcare"] or content mentioning medical topics
- Cross-collection semantic search

---

### 9. Session Type Analysis

**Query**: "Compare social media sentiment for keynotes vs workshops vs panels"

**Expected Result**:
- Keynote posts: mostly positive
- Workshop posts: mixed/negative (too basic)
- Panel posts: very positive
- Aggregated by session_type from transcripts

---

### 10. Cross-Language Person Tracking

**Query**: "Track Ahmed's contributions in all languages"

**Expected Result**:
- Arabic post (tw_001) + Arabic keynote (aud_001, aud_002)
- English keynote (aud_005) + English Q&A (aud_009)
- Italian keynote (aud_008)
- Shows multilingual participation

---

## 🎯 Advanced Query Patterns

### Pattern 1: Aggregation Across Collections
```
"What is the overall sentiment distribution for the conference?"
→ Aggregate sentiment from SocialMediaPosts
→ Correlate with session types from AudioTranscriptions
```

### Pattern 2: Temporal Clustering
```
"Group all conference activities by hour and show the mix of social posts and sessions"
→ Filter both collections by timestamp
→ Group by hour bucket
→ Display mixed results
```

### Pattern 3: Topic Evolution
```
"How did the discussion about AI evolve throughout the day?"
→ Order both collections by timestamp
→ Filter by topic containing "AI"
→ Show chronological progression
```

### Pattern 4: Language Distribution
```
"Show the language breakdown for each topic discussed"
→ Group by topic
→ Count by language in both collections
→ Compare coverage across languages
```

### Pattern 5: Quality vs Sentiment
```
"Do high-quality audio sessions get more positive social reactions?"
→ Filter transcripts by audio_quality: "high"
→ Join with posts by topic + timestamp proximity
→ Analyze sentiment correlation
```

---

## 🔍 Testing Methodology

1. **Start Simple**: Test single-collection queries first
2. **Add Correlation**: Introduce cross-collection filters
3. **Test Multilingua**: Query across languages
4. **Complex Aggregations**: Test grouping and statistics
5. **Temporal Analysis**: Test time-based correlations

---

## 📈 Expected Capabilities

After analyzing both collections, Elysia should be able to:

✅ Query multiple collections simultaneously
✅ Correlate data via common fields (event_id, author_id/speaker_id)
✅ Handle multilingual content (ar, en, it)
✅ Perform semantic search across languages
✅ Aggregate and group by correlation keys
✅ Filter with complex temporal logic
✅ Track entities (people, topics) across collections

---

## 🚀 Next Steps

1. Analyze both collections in Elysia frontend
2. Try natural language versions of these queries
3. Verify cross-collection results
4. Test semantic search across languages
5. Evaluate correlation accuracy

---

## 💡 Tips for Effective Testing

- **Be Specific**: Mention both collection names when needed
- **Use Natural Language**: Elysia understands conversational queries
- **Test Edge Cases**: Try queries that span all languages
- **Verify Metadata**: Check that correlation fields are correctly mapped
- **Analyze Results**: Review how Elysia combines results from multiple sources

---

**Generated for Elysia Cross-Collection Correlation Testing**
*Collections: SocialMediaPosts, AudioTranscriptions*
*Event: Tech Conference 2025 (tech_conf_2025)*
