#!/usr/bin/env python3
"""
Quick OmniMind Test (No Ollama Required)

This tests the basic memory and search functionality without needing Ollama.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧠 Quick OmniMind Test (Without LLMs)\n")

# Test 1: Basic imports
print("1️⃣ Testing imports...")
try:
    import chromadb
    import networkx as nx
    from sentence_transformers import SentenceTransformer
    print("✅ All imports successful\n")
except Exception as e:
    print(f"❌ Import failed: {e}\n")
    exit(1)

# Test 2: Initialize embedding model
print("2️⃣ Loading embedding model (first time takes ~30 seconds)...")
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Embedding model loaded\n")
except Exception as e:
    print(f"❌ Failed to load embedder: {e}\n")
    exit(1)

# Test 3: Test ChromaDB
print("3️⃣ Testing ChromaDB vector database...")
try:
    # Create client
    client = chromadb.PersistentClient(path="./data/chromadb")
    
    # Create collection
    collection = client.get_or_create_collection(
        name="test_memories",
        metadata={"description": "Test collection"}
    )
    
    # Store test memory
    test_text = "Python is a great programming language for AI"
    embedding = embedder.encode(test_text).tolist()
    
    collection.add(
        embeddings=[embedding],
        documents=[test_text],
        metadatas=[{"type": "test"}],
        ids=["test1"]
    )
    
    print("✅ Stored test memory in ChromaDB\n")
except Exception as e:
    print(f"❌ ChromaDB failed: {e}\n")
    exit(1)

# Test 4: Test semantic search
print("4️⃣ Testing semantic search...")
try:
    # Search for similar content
    query = "programming languages for machine learning"
    query_embedding = embedder.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )
    
    if results['documents']:
        print(f"✅ Search successful!")
        print(f"   Query: '{query}'")
        print(f"   Found: '{results['documents'][0][0]}'")
        print(f"   Score: {1 - results['distances'][0][0]:.2f}\n")
    else:
        print("❌ No search results\n")
except Exception as e:
    print(f"❌ Search failed: {e}\n")
    exit(1)

# Test 5: Test knowledge graph
print("5️⃣ Testing NetworkX knowledge graph...")
try:
    graph = nx.DiGraph()
    
    # Add nodes
    graph.add_node("memory1", content="First memory")
    graph.add_node("memory2", content="Second memory")
    
    # Add edge
    graph.add_edge("memory1", "memory2", relationship="leads_to")
    
    print(f"✅ Knowledge graph created")
    print(f"   Nodes: {len(graph.nodes)}")
    print(f"   Edges: {len(graph.edges)}\n")
except Exception as e:
    print(f"❌ Graph failed: {e}\n")
    exit(1)

# Test 6: Test SQLite
print("6️⃣ Testing SQLite database...")
try:
    import sqlite3
    
    # Create database
    db_path = './data/sqlite/test.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_memories (
        id INTEGER PRIMARY KEY,
        content TEXT
    )
    ''')
    
    # Insert test data
    cursor.execute("INSERT INTO test_memories (content) VALUES (?)", 
                  ("Test memory",))
    conn.commit()
    
    # Query
    cursor.execute("SELECT COUNT(*) FROM test_memories")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ SQLite working")
    print(f"   Records: {count}\n")
except Exception as e:
    print(f"❌ SQLite failed: {e}\n")
    exit(1)

print("=" * 50)
print("✨ Basic OmniMind components are working!")
print("\nNext steps to get full functionality:")
print("1. Install Ollama: https://ollama.com/download")
print("2. Start Ollama: ollama serve")
print("3. Download a model: ollama pull llama3.2:3b")
print("4. Add API keys to .env for cloud LLMs (optional)")
print("\nYou can still use OmniMind for:")
print("- Memory storage and retrieval")
print("- Semantic search")
print("- Knowledge graph building")
print("- Timeline queries")
print("\nLLM features will work once Ollama is installed.")