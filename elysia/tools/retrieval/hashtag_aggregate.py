"""
Hashtag Aggregation Tool for Elysia
Aggregates tweet counts by author filtered by a specific hashtag.
"""
from typing import Dict, List
from logging import Logger
from collections import Counter

from rich import print
from rich.panel import Panel

import dspy
from pydantic import BaseModel, Field

from elysia.objects import Response, Status, Tool, Error, Text
from elysia.tools.retrieval.objects import Aggregation
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
from elysia.util.elysia_chain_of_thought import ElysiaChainOfThought
from weaviate.classes.query import Filter


class HashtagAggregateQuery(BaseModel):
    """
    Schema for hashtag aggregation query parameters.
    Determines which properties to use for filtering and grouping.
    """
    author_property: str = Field(
        description="The name of the property in the collection that contains author information"
    )
    text_property: str = Field(
        description="The name of the property in the collection that contains the text/content where hashtags appear"
    )


class HashtagQueryPrompt(dspy.Signature):
    """
    Given a collection schema, determine which properties contain author information
    and which contain the text content where hashtags would appear.
    """

    collection_schemas: dict = dspy.InputField(
        desc="The schema of the target collection, including field names, types, and descriptions"
    )
    collection_name: str = dspy.InputField(
        desc="The name of the collection to query"
    )
    hashtag: str = dspy.InputField(
        desc="The hashtag to search for"
    )

    query_params: HashtagAggregateQuery = dspy.OutputField(
        desc="The properties to use for author grouping and text filtering"
    )


class HashtagAggregate(Tool):
    """
    Custom tool for aggregating tweet counts by author for a specific hashtag.

    This tool addresses the limitation where standard aggregation cannot filter by hashtag.
    It retrieves tweets containing a specific hashtag and then counts them by author.
    """

    def __init__(
        self,
        logger: Logger | None = None,
        **kwargs,
    ):
        self.logger = logger

        super().__init__(
            name="hashtag_aggregate",
            description="""
            Aggregate tweet counts by author filtered by a specific hashtag.
            Use this tool when you need to count tweets by author that contain a specific hashtag.
            This tool performs hashtag-filtered aggregation which is not available in the standard 'aggregate' tool.
            It automatically determines which properties contain author information and text content based on the collection schema.
            """,
            status="Analyzing hashtag usage...",
            inputs={
                "hashtag": {
                    "description": "The hashtag to filter by (with or without # prefix)",
                    "type": str,
                    "required": True
                },
                "collection_name": {
                    "description": "The name of the collection containing tweets/posts",
                    "type": str,
                    "required": True
                },
                "limit": {
                    "description": "Maximum number of items to retrieve (default: 1000)",
                    "type": int,
                    "default": 1000,
                    "required": False
                }
            },
            end=False,
        )

    async def is_tool_available(
        self,
        tree_data: TreeData,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
    ) -> bool:
        """
        Only available if:
        1. There is a Weaviate connection
        2. There are collections available
        """
        return client_manager.is_client and tree_data.collection_names != []

    def _normalize_hashtag(self, hashtag: str) -> str:
        """Ensure hashtag starts with # symbol"""
        return hashtag if hashtag.startswith('#') else f'#{hashtag}'

    def _aggregate_by_author(
        self,
        tweets: List[Dict],
        author_property: str
    ) -> Dict[str, int]:
        """
        Count tweets by author from retrieved results.

        Args:
            tweets: List of tweet objects
            author_property: Name of the property containing author info

        Returns:
            Dictionary mapping author names to tweet counts
        """
        authors = []
        for tweet in tweets:
            # Ensure tweet is a dictionary
            if not isinstance(tweet, dict):
                if self.logger:
                    self.logger.warning(f"Tweet is not a dict: {type(tweet)}, skipping")
                continue

            # Try to get author property
            if author_property in tweet:
                author = tweet.get(author_property)
                if author is not None:  # Only count non-None authors
                    authors.append(author)
            elif self.logger:
                self.logger.debug(f"Author property '{author_property}' not found in tweet properties: {list(tweet.keys())}")

        return dict(Counter(authors))

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: dict,
        client_manager: ClientManager,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        **kwargs,
    ):
        if self.logger:
            self.logger.debug("HashtagAggregate Tool called!")
            self.logger.debug(f"Arguments received: {inputs}")

        # Extract and normalize inputs
        hashtag = self._normalize_hashtag(inputs["hashtag"])
        collection_name = inputs["collection_name"]
        limit = inputs.get("limit", 1000)

        # Get collection schemas
        schemas = tree_data.output_collection_metadata(with_mappings=True)
        if collection_name not in schemas:
            yield Error(
                error_message=f"Collection '{collection_name}' not found in available collections"
            )
            return

        # Use LLM to determine which properties to use
        query_generator = dspy.ChainOfThought(HashtagQueryPrompt)

        try:
            query_params = await query_generator.aforward(
                lm=complex_lm,
                collection_schemas={collection_name: schemas[collection_name]},
                collection_name=collection_name,
                hashtag=hashtag
            )

            author_property = query_params.query_params.author_property
            text_property = query_params.query_params.text_property

            if self.logger:
                self.logger.info(f"LLM determined properties: author={author_property}, text={text_property}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to determine properties from schema: {str(e)}")
            yield Error(
                error_message=f"Failed to analyze collection schema: {str(e)}"
            )
            return

        yield Response(
            text=f"Searching for items with hashtag {hashtag} in {collection_name}..."
        )

        try:
            # Query Weaviate for tweets containing the hashtag
            async with client_manager.connect_to_async_client() as client:
                collection = client.collections.get(collection_name)

                # Use LIKE operator to match hashtag in text
                response = await collection.query.fetch_objects(
                    filters=Filter.by_property(text_property).like(f"*{hashtag}*"),
                    limit=limit,
                    return_properties=[author_property, text_property]
                )

                if self.logger:
                    self.logger.info(f"Retrieved {len(response.objects)} items with {hashtag}")

                # Extract properties from response objects
                tweets = []
                for obj in response.objects:
                    # Handle different response structures
                    if hasattr(obj, 'properties'):
                        props = obj.properties
                        # Ensure properties is a dictionary
                        if isinstance(props, dict):
                            tweets.append(props)
                        else:
                            # If properties is not a dict, log and skip
                            if self.logger:
                                self.logger.warning(f"Unexpected properties type: {type(props)}, skipping object")
                    else:
                        # If no properties attribute, try to use the object itself if it's a dict
                        if isinstance(obj, dict):
                            tweets.append(obj)
                        else:
                            if self.logger:
                                self.logger.warning(f"Object has no properties attribute and is not a dict: {type(obj)}")

                if not tweets:
                    yield Response(
                        text=f"No posts found containing hashtag {hashtag}"
                    )
                    yield Aggregation(
                        objects=[],
                        metadata={
                            "collection_name": collection_name,
                            "hashtag": hashtag,
                            "total_items": 0,
                            "author_counts": {}
                        }
                    )
                    return

                # Aggregate by author
                author_counts = self._aggregate_by_author(tweets, author_property)

                # Sort by count (descending)
                sorted_authors = sorted(
                    author_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                if self.logger and self.logger.level <= 20:
                    # Display results in terminal for debugging
                    results_text = "\n".join([
                        f"{author}: {count} posts"
                        for author, count in sorted_authors[:10]
                    ])
                    print(
                        Panel.fit(
                            results_text,
                            title=f"Top Authors for {hashtag}",
                            border_style="green",
                            padding=(1, 1),
                        )
                    )

                yield Status(
                    f"Found {len(tweets)} posts from {len(author_counts)} authors"
                )

                # Format results for Elysia in standard aggregation format
                # Match the format from format_aggregation_response() in elysia/util/parsing.py
                # The format expects ONLY field objects, NOT metadata like ELYSIA_NUM_ITEMS
                # ELYSIA_NUM_ITEMS should be at the top level in objects, NOT inside collection data
                aggregation_results = {
                    author_property: {
                        "type": "text",
                        "values": [
                            {
                                "value": count,
                                "field": author,
                                "aggregation": "count"
                            }
                            for author, count in sorted_authors
                        ]
                    }
                }

                objects = [
                    {
                        "num_items": len(tweets),
                        "ELYSIA_NUM_ITEMS": len(tweets),  # At top level, not in collection
                        "collections": [
                            {collection_name: aggregation_results}
                        ],
                    }
                ]

                metadata = {
                    "collection_name": collection_name,
                    "hashtag": hashtag,
                    "total_items": len(tweets),
                    "unique_authors": len(author_counts),
                    "top_author": sorted_authors[0] if sorted_authors else None,
                    "author_counts": dict(sorted_authors),
                }

                # DEBUG: Log the exact structure being sent
                if self.logger:
                    import json
                    self.logger.debug("=" * 80)
                    self.logger.debug("AGGREGATION STRUCTURE BEING YIELDED:")
                    self.logger.debug(json.dumps(objects, indent=2, ensure_ascii=False))
                    self.logger.debug("=" * 80)

                yield Aggregation(objects, metadata)

                # Provide summary text response
                if sorted_authors:
                    top_author, top_count = sorted_authors[0]
                    summary = f"The author who posts most frequently with {hashtag} is **{top_author}** with {top_count} posts out of {len(tweets)} total posts containing this hashtag."
                    yield Response(text=summary)

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Error in HashtagAggregate: {str(e)}")
            yield Error(error_message=f"Failed to aggregate by hashtag: {str(e)}")
            return

        if self.logger:
            self.logger.debug("HashtagAggregate Tool finished!")
