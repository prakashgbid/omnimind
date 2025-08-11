#!/usr/bin/env python3
"""
OmniMind Demo (No LLM Required)

This demonstrates OmniMind's memory and search capabilities without needing Ollama.
Perfect for testing the system before setting up LLMs.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create a simplified OmniMind that works without LLMs
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
import json

class OmniMindLite:
    """Simplified OmniMind for testing without LLMs."""
    
    def __init__(self):
        print("🧠 Initializing OmniMind Lite (No LLM mode)...")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./data/chromadb")
        self.collection = self.client.get_or_create_collection("memories")
        
        # Initialize embedder
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize SQLite
        self.db_path = './data/sqlite/omnimind.db'
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.db = sqlite3.connect(self.db_path)
        self._init_db()
        
        print("✅ OmniMind Lite ready!\n")
    
    def _init_db(self):
        cursor = self.db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            thought TEXT NOT NULL,
            project TEXT,
            tags TEXT
        )
        ''')
        self.db.commit()
    
    def remember(self, thought, project=None, tags=None):
        """Store a memory."""
        # Generate embedding
        embedding = self.embedder.encode(thought).tolist()
        
        # Store in ChromaDB
        memory_id = f"mem_{datetime.now().timestamp()}"
        self.collection.add(
            embeddings=[embedding],
            documents=[thought],
            metadatas=[{
                "timestamp": str(datetime.now()),
                "project": project or "",
                "tags": tags or ""
            }],
            ids=[memory_id]
        )
        
        # Store in SQLite
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO memories (thought, project, tags) VALUES (?, ?, ?)",
            (thought, project, tags)
        )
        self.db.commit()
        
        return memory_id
    
    def search(self, query, limit=5):
        """Search memories semantically."""
        query_embedding = self.embedder.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        memories = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                memories.append({
                    'content': results['documents'][0][i],
                    'score': 1 - results['distances'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })
        
        return memories
    
    def get_recent(self, hours=24):
        """Get recent memories."""
        cursor = self.db.cursor()
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute(
            "SELECT * FROM memories WHERE timestamp > ? ORDER BY timestamp DESC",
            (since,)
        )
        
        return cursor.fetchall()


def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║      🧠 OmniMind Demo (No LLM) 🧠       ║
    ╚══════════════════════════════════════════╝
    
    This demo shows OmniMind's memory capabilities
    without requiring Ollama or cloud LLMs.
    """)
    
    om = OmniMindLite()
    
    # Demo 1: Store memories
    print("📝 Demo 1: Storing Memories")
    print("-" * 40)
    
    memories_to_store = [
        ("Decided to use React for the frontend because of team expertise", "webapp", "decision,frontend"),
        ("PostgreSQL chosen over MySQL for better JSON support", "webapp", "decision,database"),
        ("Implementing JWT authentication with refresh tokens", "webapp", "implementation,security"),
        ("TypeScript will be used for type safety across the project", "webapp", "decision,language"),
        ("Tailwind CSS for styling to speed up development", "webapp", "decision,styling"),
        ("Redis for caching and session management", "webapp", "infrastructure,cache"),
        ("Docker containers for consistent deployment", "webapp", "deployment,infrastructure"),
        ("GitHub Actions for CI/CD pipeline", "webapp", "deployment,automation")
    ]
    
    for thought, project, tags in memories_to_store:
        memory_id = om.remember(thought, project, tags)
        print(f"✅ Stored: {thought[:50]}...")
    
    print(f"\n📊 Total memories stored: {len(memories_to_store)}")
    
    # Demo 2: Semantic search
    print("\n🔍 Demo 2: Semantic Search")
    print("-" * 40)
    
    searches = [
        "What database are we using?",
        "Frontend framework decision",
        "How are we handling authentication?",
        "Deployment strategy",
        "Programming language choice"
    ]
    
    for query in searches:
        print(f"\n❓ Query: '{query}'")
        results = om.search(query, limit=2)
        
        for i, result in enumerate(results, 1):
            score = result['score']
            content = result['content']
            print(f"   {i}. [Score: {score:.2f}] {content[:60]}...")
    
    # Demo 3: Timeline
    print("\n\n📅 Demo 3: Recent Memories")
    print("-" * 40)
    
    recent = om.get_recent(hours=1)
    print(f"Memories from the last hour: {len(recent)}")
    
    for memory in recent[:3]:
        print(f"- {memory[2][:60]}...")  # memory[2] is the thought column
    
    # Demo 4: Project filtering
    print("\n\n🏗️ Demo 4: Project-Specific Search")
    print("-" * 40)
    
    print("Searching for 'webapp' project decisions...")
    results = om.search("decisions made for the webapp project", limit=3)
    
    for result in results:
        if result['metadata'].get('project') == 'webapp':
            print(f"- {result['content'][:60]}...")
    
    # Summary
    print("\n\n" + "=" * 50)
    print("✨ Demo Complete!")
    print("=" * 50)
    print("""
    OmniMind is working! You can:
    ✅ Store memories with context
    ✅ Search semantically (finds meaning, not just keywords)
    ✅ Track project decisions
    ✅ Query timeline of thoughts
    
    To enable AI responses:
    1. Install Ollama: https://ollama.com/download
    2. Or add API keys to .env:
       - OPENAI_API_KEY=sk-...
       - ANTHROPIC_API_KEY=sk-ant-...
    
    Try the full version:
    - python src/main.py cli
    - python src/main.py web
    """)


if __name__ == "__main__":
    main()