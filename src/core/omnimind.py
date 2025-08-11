"""
OmniMind Core - The Brain of the System

This is the main class that coordinates everything:
- Memory storage and retrieval
- Multi-model consensus
- Knowledge graph connections
- Decision tracking
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib

import chromadb
from chromadb.config import Settings
import networkx as nx
import ollama
from sentence_transformers import SentenceTransformer


class OmniMind:
    """
    The core OmniMind system that remembers everything and provides
    intelligent responses using local LLMs with full context.
    """
    
    def __init__(self, config_path: str = ".env"):
        """
        Initialize OmniMind with all its components.
        
        What happens here:
        1. Load configuration
        2. Initialize vector database (ChromaDB) for semantic search
        3. Connect to SQLite for structured data
        4. Create knowledge graph for relationships
        5. Set up local LLM connections
        6. Load embedding model for converting text to vectors
        """
        print("🧠 Initializing OmniMind...")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize vector database for semantic search
        # ChromaDB stores text as vectors so we can search by meaning
        self.chroma_client = chromadb.PersistentClient(
            path=self.config.get('CHROMADB_PATH', './data/chromadb'),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create the main collection for memories
        self.memory_collection = self.chroma_client.get_or_create_collection(
            name="memories",
            metadata={"description": "All OmniMind memories and thoughts"}
        )
        
        # Initialize SQLite for structured data
        # This stores the actual text and metadata
        self.db_path = self.config.get('SQLITE_PATH', './data/sqlite/omnimind.db')
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row  # This lets us access columns by name
        
        # Initialize knowledge graph
        # This tracks how thoughts and decisions connect to each other
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.graph_path = self.config.get('GRAPH_PATH', './data/graphs/knowledge.gpickle')
        self._load_graph()
        
        # Initialize Ollama client for local LLMs
        self.ollama = ollama.Client()
        
        # Initialize embedding model for converting text to vectors
        # This runs locally, no API needed!
        print("   Loading embedding model (first time takes a minute)...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✅ OmniMind initialized and ready!")
    
    def remember(self, thought: str, context: Optional[Dict] = None) -> str:
        """
        Store a thought/memory in the system.
        
        This method:
        1. Creates an embedding (vector) of the thought
        2. Stores it in ChromaDB for semantic search
        3. Saves to SQLite for structured queries
        4. Updates the knowledge graph
        
        Args:
            thought: The text to remember
            context: Optional metadata (project, tags, etc.)
        
        Returns:
            memory_id: Unique ID for this memory
        """
        print(f"💭 Remembering: {thought[:50]}...")
        
        # Generate unique ID for this memory
        memory_id = self._generate_id(thought)
        
        # Create embedding (convert text to vector)
        embedding = self.embedder.encode(thought).tolist()
        
        # Prepare metadata
        metadata = {
            "timestamp": str(datetime.now()),
            "type": "memory",
            **(context or {})
        }
        
        # Store in ChromaDB for semantic search
        self.memory_collection.add(
            embeddings=[embedding],
            documents=[thought],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        # Store in SQLite for structured queries
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO memories (thought, context, embedding_id, tags, project)
            VALUES (?, ?, ?, ?, ?)
        """, (
            thought,
            json.dumps(context) if context else None,
            memory_id,
            context.get('tags') if context else None,
            context.get('project') if context else None
        ))
        self.db.commit()
        
        # Add to knowledge graph
        self.graph.add_node(memory_id, 
                           content=thought[:100], 
                           timestamp=datetime.now(),
                           type='memory')
        
        # Save graph
        self._save_graph()
        
        print(f"✅ Remembered with ID: {memory_id}")
        return memory_id
    
    def think(self, prompt: str, use_consensus: bool = True) -> str:
        """
        Process a thought with full context from memories.
        
        This is the main method you'll use. It:
        1. Searches for relevant memories
        2. Builds context from past thoughts
        3. Queries local LLM(s)
        4. Returns a contextual response
        5. Remembers this interaction
        
        Args:
            prompt: Your question or thought
            use_consensus: Whether to use multiple models
        
        Returns:
            response: The AI's contextual response
        """
        print(f"\n🤔 Thinking about: {prompt[:50]}...")
        
        # Step 1: Find relevant memories
        print("   📚 Searching memories...")
        memories = self.search_memories(prompt, limit=10)
        
        # Step 2: Build context from memories
        context = self._build_context(memories)
        
        # Step 3: Create enhanced prompt with context
        enhanced_prompt = f"""
You are OmniMind, an AI with perfect memory. Use the following context from past conversations and decisions to provide a comprehensive answer.

RELEVANT MEMORIES:
{context}

CURRENT QUESTION:
{prompt}

Provide a thoughtful response that:
1. References relevant past decisions or discussions
2. Maintains consistency with previous thoughts
3. Builds upon past insights
4. Highlights any contradictions with past positions

RESPONSE:
"""
        
        # Step 4: Get response(s) from LLM(s)
        if use_consensus and len(self._get_available_models()) > 1:
            print("   🤝 Building consensus from multiple models...")
            response = self._get_consensus_response(enhanced_prompt)
        else:
            print("   💬 Querying local LLM...")
            response = self._query_single_model(enhanced_prompt)
        
        # Step 5: Remember this interaction
        self.remember(
            thought=f"Q: {prompt}\nA: {response}",
            context={
                "type": "qa_pair",
                "question": prompt,
                "memories_used": len(memories)
            }
        )
        
        # Step 6: Update knowledge graph connections
        # Connect this thought to related memories
        new_id = self._generate_id(f"Q: {prompt}")
        for memory in memories[:3]:  # Connect to top 3 related memories
            if 'id' in memory:
                self.graph.add_edge(memory['id'], new_id, 
                                  weight=memory.get('score', 0.5))
        
        return response
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search memories using semantic similarity.
        
        This uses vector search to find memories that are
        semantically similar to your query, not just keyword matches.
        
        Args:
            query: What to search for
            limit: Maximum results to return
        
        Returns:
            List of relevant memories with scores
        """
        # Create embedding for the query
        query_embedding = self.embedder.encode(query).tolist()
        
        # Search in ChromaDB
        results = self.memory_collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        # Format results
        memories = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                memory = {
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'score': 1 - results['distances'][0][i] if results['distances'] else 0,
                    'id': results['ids'][0][i] if results['ids'] else None
                }
                memories.append(memory)
        
        return memories
    
    def get_timeline(self, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> List[Dict]:
        """
        Get memories from a specific time period.
        
        Useful for questions like "What did I decide last month?"
        
        Args:
            start_date: Beginning of time range (YYYY-MM-DD)
            end_date: End of time range (YYYY-MM-DD)
        
        Returns:
            List of memories in chronological order
        """
        cursor = self.db.cursor()
        
        query = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        
        memories = []
        for row in cursor.fetchall():
            memories.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'thought': row['thought'],
                'context': json.loads(row['context']) if row['context'] else {},
                'project': row['project'],
                'tags': row['tags']
            })
        
        return memories
    
    def _get_consensus_response(self, prompt: str) -> str:
        """
        Get responses from multiple models and build consensus.
        
        This queries several local models and synthesizes their
        responses into a single, high-quality answer.
        """
        models = self._get_available_models()
        responses = []
        
        # Query each model
        for model in models[:3]:  # Use up to 3 models
            try:
                response = self.ollama.generate(
                    model=model,
                    prompt=prompt
                )
                responses.append({
                    'model': model,
                    'response': response['response']
                })
                print(f"      ✓ Got response from {model}")
            except Exception as e:
                print(f"      ✗ Failed to query {model}: {e}")
        
        if not responses:
            return "Unable to generate response from local models."
        
        if len(responses) == 1:
            return responses[0]['response']
        
        # Build consensus
        consensus_prompt = f"""
Synthesize these AI responses into a single, high-quality answer:

{json.dumps(responses, indent=2)}

Create a unified response that:
1. Combines the best insights from all responses
2. Resolves any contradictions
3. Maintains clarity and coherence

SYNTHESIZED RESPONSE:
"""
        
        # Use the first model to synthesize
        final_response = self.ollama.generate(
            model=models[0],
            prompt=consensus_prompt
        )
        
        return final_response['response']
    
    def _query_single_model(self, prompt: str) -> str:
        """Query a single local model."""
        models = self._get_available_models()
        if not models:
            return "No local models available. Please run 'ollama pull llama3.2:3b'"
        
        response = self.ollama.generate(
            model=models[0],
            prompt=prompt
        )
        return response['response']
    
    def _get_available_models(self) -> List[str]:
        """Get list of available local models."""
        try:
            models = self.ollama.list()
            return [m['name'] for m in models['models']]
        except:
            return []
    
    def _build_context(self, memories: List[Dict]) -> str:
        """Build context string from memories."""
        if not memories:
            return "No relevant past memories found."
        
        context_parts = []
        for i, memory in enumerate(memories[:5], 1):
            context_parts.append(
                f"{i}. [{memory['metadata'].get('timestamp', 'Unknown date')}] "
                f"(Relevance: {memory['score']:.2f})\n"
                f"   {memory['content'][:200]}..."
            )
        
        return "\n".join(context_parts)
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content."""
        return hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:16]
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from .env file."""
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        return config
    
    def _load_graph(self):
        """Load knowledge graph from disk."""
        if os.path.exists(self.graph_path):
            try:
                self.graph = nx.read_gpickle(self.graph_path)
                print(f"   📊 Loaded knowledge graph with {len(self.graph.nodes)} nodes")
            except:
                self.graph = nx.DiGraph()
    
    def _save_graph(self):
        """Save knowledge graph to disk."""
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        nx.write_gpickle(self.graph, self.graph_path)