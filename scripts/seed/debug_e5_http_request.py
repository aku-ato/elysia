#!/usr/bin/env python3
"""
Debug script to inspect the actual HTTP request sent to Weaviate server.
This will help determine if the Python client is adding unexpected parameters.
"""

import asyncio
import logging
from weaviate.classes.config import Configure, Property, DataType
import weaviate
import httpx

# Monkey-patch httpx to log requests
original_request = httpx.AsyncClient.request

async def logging_request(self, method, url, **kwargs):
    """Log all HTTP requests with their full details."""
    logger = logging.getLogger("HTTP_DEBUG")
    logger.info(f"\n{'='*60}")
    logger.info(f"HTTP {method} {url}")
    logger.info(f"Headers: {kwargs.get('headers', {})}")
    if 'json' in kwargs:
        import json
        logger.info(f"JSON Body:\n{json.dumps(kwargs['json'], indent=2)}")
    elif 'content' in kwargs:
        logger.info(f"Content: {kwargs['content'][:500]}...")
    logger.info(f"{'='*60}\n")

    # Call original request
    return await original_request(self, method, url, **kwargs)

httpx.AsyncClient.request = logging_request

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
logger = logging.getLogger(__name__)


async def test_e5_request_inspection():
    """Inspect the actual HTTP request for E5 model configuration."""

    client = weaviate.use_async_with_local(
        port=8080,
        grpc_port=50051
    )

    try:
        async with client:
            test_collection_name = "DebugE5Request"

            # Delete if exists
            if await client.collections.exists(test_collection_name):
                await client.collections.delete(test_collection_name)

            logger.info("Creating collection with E5 model using passage_model/query_model...")
            logger.info("This should show the EXACT HTTP request sent to Weaviate server")

            # Configure E5 with passage_model/query_model
            vectorizer_config = Configure.Vectorizer.text2vec_huggingface(
                passage_model="intfloat/multilingual-e5-large",
                query_model="intfloat/multilingual-e5-large"
            )

            logger.info(f"\nPython config object:")
            logger.info(f"  model: {vectorizer_config.model}")
            logger.info(f"  passageModel: {vectorizer_config.passageModel}")
            logger.info(f"  queryModel: {vectorizer_config.queryModel}")
            logger.info(f"\nSerialized (_to_dict):")
            import json
            logger.info(json.dumps(vectorizer_config._to_dict(), indent=2))

            try:
                collection = await client.collections.create(
                    name=test_collection_name,
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                    ],
                    vectorizer_config=vectorizer_config
                )
                logger.info("✓ SUCCESS: Collection created")
                await client.collections.delete(test_collection_name)
            except Exception as e:
                logger.error(f"✗ FAILED: {str(e)}")
                logger.error("Check the HTTP request body above to see what was actually sent")

    except Exception as e:
        logger.exception(f"Error: {e}")


async def main():
    logger.info("\n" + "="*70)
    logger.info("E5 MODEL HTTP REQUEST DEBUGGING")
    logger.info("="*70 + "\n")

    await test_e5_request_inspection()


if __name__ == "__main__":
    asyncio.run(main())
