#!/usr/bin/env python3
"""Test E5 model collection creation directly"""

import weaviate
from weaviate.classes.config import Configure, Property, DataType
import asyncio

async def main():
    print("Connecting to Weaviate...")
    client = weaviate.WeaviateClient(
        connection_params=weaviate.connect.ConnectionParams.from_url("http://localhost:8080", 50051)
    )

    try:
        await client.connect()
        print("✓ Connected")

        # Delete if exists
        if await client.collections.exists("TestE5Direct"):
            print("Deleting existing collection...")
            await client.collections.delete("TestE5Direct")

        # Try E5-specific config
        print("\nCreating collection with E5 passage_model/query_model...")
        collection = await client.collections.create(
            name="TestE5Direct",
            properties=[Property(name="text", data_type=DataType.TEXT)],
            vectorizer_config=Configure.Vectorizer.text2vec_huggingface(
                passage_model="intfloat/multilingual-e5-large",
                query_model="intfloat/multilingual-e5-large"
            )
        )
        print("✓ Collection created successfully!")

        # Cleanup
        print("\nCleaning up...")
        await client.collections.delete("TestE5Direct")
        print("✓ Done")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
