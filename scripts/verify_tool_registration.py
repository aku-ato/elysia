#!/usr/bin/env python3
"""
Verification script to confirm HashtagAggregate is registered by default.

This script tests that the HashtagAggregate tool is automatically available
when creating a new Tree without manual registration.

Usage:
    python scripts/verify_tool_registration.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_default_registration():
    """Test that HashtagAggregate is available by default"""

    print("=" * 70)
    print("HASHTAG AGGREGATE TOOL - DEFAULT REGISTRATION TEST")
    print("=" * 70)

    # Import Tree
    print("\n1. Importing Elysia Tree...")
    try:
        from elysia import Tree
        print("   ✓ Tree imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import Tree: {str(e)}")
        return False

    # Create tree with default initialization (multi_branch)
    print("\n2. Creating Tree with default (multi_branch) initialization...")
    try:
        tree = Tree()
        print("   ✓ Tree created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create Tree: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # List available tools
    print("\n3. Checking available tools...")
    available_tools = list(tree.tools.keys())
    print(f"   Available tools: {', '.join(available_tools)}")

    # Verify HashtagAggregate is present
    print("\n4. Verifying HashtagAggregate registration...")
    if "hashtag_aggregate" in tree.tools:
        print("   ✓ hashtag_aggregate found in tools!")
    else:
        print("   ✗ hashtag_aggregate NOT found in tools")
        print("   Expected tools to include: hashtag_aggregate")
        print(f"   Actual tools: {available_tools}")
        return False

    # Verify tool type
    print("\n5. Verifying tool type...")
    try:
        from elysia.tools.retrieval.hashtag_aggregate import HashtagAggregate
        tool_instance = tree.tools["hashtag_aggregate"]

        if isinstance(tool_instance, HashtagAggregate):
            print("   ✓ Tool is correct type (HashtagAggregate)")
        else:
            print(f"   ✗ Tool is wrong type: {type(tool_instance)}")
            return False
    except Exception as e:
        print(f"   ✗ Error verifying tool type: {str(e)}")
        return False

    # Test with one_branch initialization
    print("\n6. Testing with one_branch initialization...")
    try:
        tree_one_branch = Tree(branch_initialisation="one_branch")
        if "hashtag_aggregate" in tree_one_branch.tools:
            print("   ✓ hashtag_aggregate found in one_branch tree!")
        else:
            print("   ⚠ hashtag_aggregate NOT in one_branch tree (may be expected)")
    except Exception as e:
        print(f"   ✗ Error testing one_branch: {str(e)}")

    # Verify tool properties
    print("\n7. Verifying tool properties...")
    tool = tree.tools["hashtag_aggregate"]
    print(f"   - Name: {tool.name}")
    print(f"   - Description: {tool.description[:80]}...")
    print(f"   - Inputs: {list(tool.inputs.keys())}")
    print(f"   - End: {tool.end}")

    expected_inputs = ["hashtag", "collection_name", "author_property", "text_property", "limit"]
    actual_inputs = list(tool.inputs.keys())

    if all(inp in actual_inputs for inp in ["hashtag", "collection_name"]):
        print("   ✓ Required inputs present")
    else:
        print("   ✗ Required inputs missing")
        return False

    # Final summary
    print("\n" + "=" * 70)
    print("TEST RESULT: ✅ SUCCESS")
    print("=" * 70)
    print("\nHashtagAggregate tool is successfully registered by default!")
    print("Users can now use it without manual registration:")
    print("\n  tree = Tree()")
    print('  tree("Who tweets most with #hashtag?", collection_names=[...])')
    print("\n" + "=" * 70)

    return True


def main():
    """Main entry point"""
    try:
        success = test_default_registration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
