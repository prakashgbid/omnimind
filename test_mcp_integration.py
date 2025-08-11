#!/usr/bin/env python3
"""
Test MCP Integration with OSA
Tests the Model Context Protocol servers
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mcp_integration():
    """Test MCP server integration with OSA"""
    
    print("=" * 60)
    print("OSA MCP Integration Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Import OSA components
        from core.osa_autonomous import OSAAutonomous
        from core.mcp_client import get_mcp_client
        
        # Initialize OSA with MCP
        print("🚀 Initializing OSA with MCP integration...")
        osa = OSAAutonomous({
            "verbose": True,
            "mcp": {
                "enabled": True,
                "auto_start": True
            }
        })
        
        # Initialize systems
        await osa.initialize()
        print("✓ OSA initialized successfully")
        print()
        
        # Get status
        status = osa.get_status()
        
        # Display MCP status
        print("📊 MCP Server Status:")
        print("-" * 40)
        if 'mcp' in status and status['mcp'] != {'available': False}:
            mcp_status = status['mcp']
            print(f"  Total Configured: {mcp_status.get('total_configured', 0)}")
            print(f"  Total Running: {mcp_status.get('total_running', 0)}")
            print()
            
            if 'servers' in mcp_status:
                for server_name, server_info in mcp_status['servers'].items():
                    status_icon = "🟢" if server_info.get('running') else "🔴"
                    enabled_icon = "✓" if server_info.get('enabled') else "✗"
                    print(f"  {status_icon} {server_name}:")
                    print(f"     Enabled: {enabled_icon}")
                    print(f"     Type: {server_info.get('type', 'unknown')}")
                    if server_info.get('config'):
                        print(f"     Config: {server_info['config']}")
                    print()
        else:
            print("  ❌ MCP not available or not configured")
        
        print()
        
        # Test individual MCP servers
        print("🧪 Testing MCP Server Operations:")
        print("-" * 40)
        
        # Test memory server
        print("\n1. Memory Server Test:")
        response = await osa.process_autonomously("Remember that the test value is 42")
        print(f"   Store: {response[:100]}...")
        
        response = await osa.process_autonomously("What is the test value I asked you to remember?")
        print(f"   Recall: {response[:100]}...")
        
        # Test filesystem operations (simulated through OSA)
        print("\n2. Filesystem Server Test:")
        response = await osa.process_autonomously("List the Python files in the current directory")
        print(f"   Result: {response[:150]}...")
        
        # Test git operations (simulated)
        print("\n3. Git Server Test:")
        response = await osa.process_autonomously("Check the git status of this repository")
        print(f"   Result: {response[:150]}...")
        
        print("\n" + "=" * 60)
        print("✅ MCP Integration Test Complete!")
        print("=" * 60)
        
        # Shutdown cleanly
        await osa.shutdown()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()


async def test_mcp_direct():
    """Test MCP client directly without OSA"""
    
    print("\n" + "=" * 60)
    print("Direct MCP Client Test")
    print("=" * 60)
    print()
    
    try:
        from core.mcp_client import get_mcp_client
        
        mcp = get_mcp_client()
        print("✓ MCP Client initialized")
        
        # Test server operations
        print("\n🔌 Testing server operations:")
        
        # Memory server
        print("\n- Memory Server:")
        success = await mcp.start_server("memory")
        if success:
            print("  ✓ Started successfully")
            # Store and retrieve
            stored = await mcp.store_memory("test_key", {"value": 42, "type": "test"})
            print(f"  ✓ Stored data: {stored}")
            
            retrieved = await mcp.retrieve_memory("test_key")
            print(f"  ✓ Retrieved data: {retrieved}")
        else:
            print("  ✗ Failed to start")
        
        # Filesystem server
        print("\n- Filesystem Server:")
        success = await mcp.start_server("filesystem")
        if success:
            print("  ✓ Started successfully")
            files = await mcp.list_files(".")
            if files:
                print(f"  ✓ Found {len(files)} files")
        else:
            print("  ✗ Failed to start")
        
        # Stop all servers
        print("\n🛑 Stopping all servers...")
        await mcp.stop_all_servers()
        print("✓ All servers stopped")
        
    except Exception as e:
        print(f"❌ Direct test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("OSA MCP Integration Test Suite")
    print("==============================\n")
    
    # Run both test suites
    asyncio.run(test_mcp_integration())
    asyncio.run(test_mcp_direct())