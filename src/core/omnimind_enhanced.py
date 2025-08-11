"""
Enhanced OmniMind Core with Cloud LLM Support

This enhanced version supports both local and cloud LLMs,
making it suitable for use as a Claude Code agent.
"""

import os
import json
import sqlite3
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import hashlib

import chromadb
from chromadb.config import Settings
import networkx as nx
from sentence_transformers import SentenceTransformer

# Import providers
from ..providers import (
    ProviderManager,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider
)

# Import premium providers and router
try:
    from ..providers.chatgpt5_provider import ChatGPT5Provider
    from ..providers.claude_opus_provider import ClaudeOpusProvider
    from ..providers.intelligent_router import IntelligentRouter
    PREMIUM_AVAILABLE = True
except:
    PREMIUM_AVAILABLE = False


class OmniMindEnhanced:
    """
    Enhanced OmniMind with support for both local and cloud LLMs.
    
    This version can:
    - Use local models via Ollama
    - Use cloud models (OpenAI, Anthropic, Google)
    - Work as a Claude Code agent
    - Switch between providers dynamically
    - Build consensus across different provider types
    """
    
    def __init__(self, config_path: str = ".env", use_intelligent_routing: bool = True):
        """Initialize Enhanced OmniMind."""
        print("🧠 Initializing Enhanced OmniMind...")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize provider manager
        self.provider_manager = ProviderManager()
        self._setup_providers()
        
        # Initialize intelligent router if available
        self.intelligent_router = None
        if use_intelligent_routing and PREMIUM_AVAILABLE:
            try:
                self.intelligent_router = IntelligentRouter({
                    'monthly_budget': float(self.config.get('MONTHLY_BUDGET_USD', '10')),
                    'prefer_local': self.config.get('PREFER_LOCAL_MODELS', 'true').lower() == 'true'
                })
                print("   ✅ Intelligent routing enabled (Local + Premium)")
            except Exception as e:
                print(f"   ⚠️ Intelligent routing not available: {e}")
        
        # Initialize vector database
        self.chroma_client = chromadb.PersistentClient(
            path=self.config.get('CHROMADB_PATH', './data/chromadb'),
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.memory_collection = self.chroma_client.get_or_create_collection(
            name="memories",
            metadata={"description": "All OmniMind memories and thoughts"}
        )
        
        # Initialize SQLite
        self.db_path = self.config.get('SQLITE_PATH', './data/sqlite/omnimind.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row
        self._init_database()
        
        # Initialize knowledge graph
        self.graph = nx.DiGraph()
        self.graph_path = self.config.get('GRAPH_PATH', './data/graphs/knowledge.gpickle')
        self._load_graph()
        
        # Initialize embedding model
        print("   Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✅ Enhanced OmniMind ready with cloud LLM support!")
    
    def _setup_providers(self):
        """Setup all configured providers."""
        # Local provider (Ollama)
        if self.config.get('USE_LOCAL_MODELS', 'true').lower() == 'true':
            try:
                ollama_provider = OllamaProvider({})
                self.provider_manager.add_provider('ollama', ollama_provider)
                print("   ✅ Local models (Ollama) configured")
            except Exception as e:
                print(f"   ⚠️  Ollama not available: {e}")
        
        # OpenAI provider
        if self.config.get('OPENAI_API_KEY'):
            # Use ChatGPT5Provider if available for better routing
            if PREMIUM_AVAILABLE:
                try:
                    chatgpt5_provider = ChatGPT5Provider({
                        'api_key': self.config['OPENAI_API_KEY'],
                        'smart_routing': True,
                        'max_cost_per_query': float(self.config.get('MAX_COST_PER_QUERY', '0.50'))
                    })
                    self.provider_manager.add_provider('openai', chatgpt5_provider)
                    print("   ✅ ChatGPT 5.0/GPT-4 configured with smart routing")
                except:
                    # Fallback to standard OpenAI provider
                    openai_provider = OpenAIProvider({
                        'api_key': self.config['OPENAI_API_KEY'],
                        'default_model': self.config.get('OPENAI_MODEL', 'gpt-4-turbo-preview')
                    })
                    self.provider_manager.add_provider('openai', openai_provider)
                    print("   ✅ OpenAI configured")
            else:
                openai_provider = OpenAIProvider({
                    'api_key': self.config['OPENAI_API_KEY'],
                    'default_model': self.config.get('OPENAI_MODEL', 'gpt-4-turbo-preview')
                })
                self.provider_manager.add_provider('openai', openai_provider)
                print("   ✅ OpenAI configured")
        
        # Anthropic provider
        if self.config.get('ANTHROPIC_API_KEY'):
            # Use ClaudeOpusProvider if available for better routing
            if PREMIUM_AVAILABLE:
                try:
                    opus_provider = ClaudeOpusProvider({
                        'api_key': self.config['ANTHROPIC_API_KEY'],
                        'smart_routing': True,
                        'prefer_opus': self.config.get('PREFER_OPUS', 'false').lower() == 'true'
                    })
                    self.provider_manager.add_provider('anthropic', opus_provider)
                    print("   ✅ Claude 3 Opus configured with smart routing")
                except:
                    # Fallback to standard Anthropic provider
                    anthropic_provider = AnthropicProvider({
                        'api_key': self.config['ANTHROPIC_API_KEY'],
                        'default_model': self.config.get('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
                    })
                    self.provider_manager.add_provider('anthropic', anthropic_provider)
                    print("   ✅ Anthropic configured")
            else:
                anthropic_provider = AnthropicProvider({
                    'api_key': self.config['ANTHROPIC_API_KEY'],
                    'default_model': self.config.get('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
                })
                self.provider_manager.add_provider('anthropic', anthropic_provider)
                print("   ✅ Anthropic configured")
        
        # Google provider
        if self.config.get('GOOGLE_API_KEY'):
            google_provider = GoogleProvider({
                'api_key': self.config['GOOGLE_API_KEY'],
                'default_model': self.config.get('GOOGLE_MODEL', 'gemini-pro')
            })
            self.provider_manager.add_provider('google', google_provider)
            print("   ✅ Google configured")
    
    async def think_async(self, 
                         prompt: str, 
                         providers: Optional[List[str]] = None,
                         use_consensus: bool = True,
                         prefer_cloud: bool = False,
                         model: Optional[str] = None) -> str:
        """
        Async version of think that supports both local and cloud providers.
        
        Args:
            prompt: The question or thought
            providers: Specific providers to use (e.g., ['openai', 'anthropic'])
            use_consensus: Whether to use multiple models
            prefer_cloud: Prefer cloud models over local
        
        Returns:
            The response with full context
        """
        print(f"\n🤔 Thinking about: {prompt[:50]}...")
        
        # Find relevant memories
        print("   📚 Searching memories...")
        memories = self.search_memories(prompt, limit=10)
        
        # Build context
        context = self._build_context(memories)
        
        # Create enhanced prompt
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
        
        # Determine which providers to use
        if providers:
            selected_providers = providers
        elif prefer_cloud:
            # Prefer cloud providers if available
            selected_providers = self.provider_manager.get_cloud_providers()
            if not selected_providers:
                selected_providers = self.provider_manager.get_local_providers()
        else:
            # Use all available providers
            selected_providers = self.provider_manager.list_providers()
        
        # Get response(s)
        if use_consensus and len(selected_providers) > 1:
            print(f"   🤝 Building consensus from {len(selected_providers)} models...")
            response = await self._get_consensus_response_async(enhanced_prompt, selected_providers)
        else:
            provider_name = selected_providers[0]
            if model:
                print(f"   💬 Querying {provider_name} with model {model}...")
            else:
                print(f"   💬 Querying {provider_name}...")
            response = await self._query_single_provider_async(enhanced_prompt, provider_name, model=model)
        
        # Remember this interaction
        self.remember(
            thought=f"Q: {prompt}\nA: {response}",
            context={
                "type": "qa_pair",
                "question": prompt,
                "providers_used": selected_providers,
                "memories_used": len(memories)
            }
        )
        
        return response
    
    def think(self, prompt: str, **kwargs) -> str:
        """Synchronous wrapper for think_async."""
        return asyncio.run(self.think_async(prompt, **kwargs))
    
    async def _get_consensus_response_async(self, prompt: str, providers: List[str]) -> str:
        """Get consensus from multiple providers (async)."""
        responses = []
        
        # Query each provider concurrently
        tasks = []
        for provider_name in providers[:3]:  # Limit to 3 for speed
            provider = self.provider_manager.get_provider(provider_name)
            if provider:
                tasks.append(self._query_provider_async(provider, prompt, provider_name))
        
        # Wait for all responses
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful responses
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                responses.append(result)
        
        if not responses:
            return "Unable to generate response from selected models."
        
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
        
        # Use the first available provider for synthesis
        synthesizer = self.provider_manager.get_provider(providers[0])
        synthesis_response = await synthesizer.complete(consensus_prompt)
        
        return synthesis_response.content
    
    async def _query_provider_async(self, provider, prompt: str, provider_name: str, model: Optional[str] = None) -> Dict:
        """Query a single provider asynchronously."""
        try:
            response = await provider.complete(prompt, model=model)
            print(f"      ✓ Got response from {provider_name}")
            return {
                'provider': provider_name,
                'response': response.content,
                'model': response.model,
                'cost': response.cost
            }
        except Exception as e:
            print(f"      ✗ Failed to query {provider_name}: {e}")
            return {'provider': provider_name, 'error': str(e)}
    
    async def _query_single_provider_async(self, prompt: str, provider_name: str, model: Optional[str] = None) -> str:
        """Query a single provider."""
        provider = self.provider_manager.get_provider(provider_name)
        if not provider:
            return f"Provider {provider_name} not available."
        
        try:
            response = await provider.complete(prompt, model=model)
            return response.content
        except Exception as e:
            return f"Error querying {provider_name}: {e}"
    
    def remember(self, thought: str, context: Optional[Dict] = None) -> str:
        """Store a memory (same as original)."""
        print(f"💭 Remembering: {thought[:50]}...")
        
        memory_id = self._generate_id(thought)
        embedding = self.embedder.encode(thought).tolist()
        
        metadata = {
            "timestamp": str(datetime.now()),
            "type": "memory",
            **(context or {})
        }
        
        # Store in ChromaDB
        self.memory_collection.add(
            embeddings=[embedding],
            documents=[thought],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        # Store in SQLite
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
        
        self._save_graph()
        
        print(f"✅ Remembered with ID: {memory_id}")
        return memory_id
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """Search memories using semantic similarity."""
        query_embedding = self.embedder.encode(query).tolist()
        
        results = self.memory_collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
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
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about configured providers."""
        info = {
            'available_providers': self.provider_manager.list_providers(),
            'cloud_providers': self.provider_manager.get_cloud_providers(),
            'local_providers': self.provider_manager.get_local_providers(),
            'provider_details': {}
        }
        
        for provider_name in info['available_providers']:
            provider = self.provider_manager.get_provider(provider_name)
            if provider:
                info['provider_details'][provider_name] = provider.get_info()
        
        return info
    
    def set_preferred_providers(self, providers: List[str]):
        """Set preferred providers for queries."""
        self.config['PREFERRED_PROVIDERS'] = ','.join(providers)
    
    # Include all other methods from original OmniMind...
    def _init_database(self):
        """Initialize database tables."""
        cursor = self.db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            thought TEXT NOT NULL,
            response TEXT,
            context TEXT,
            embedding_id TEXT,
            tags TEXT,
            project TEXT,
            importance INTEGER DEFAULT 5
        )
        ''')
        self.db.commit()
    
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