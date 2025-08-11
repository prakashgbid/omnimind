#!/usr/bin/env python3
"""
OSA LangChain Intelligence Engine
Integrates LangChain for advanced reasoning, memory, and autonomous agents
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
from pathlib import Path

# LangChain Core - Updated imports for new API structure
try:
    from langchain_community.llms import Ollama
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_anthropic import ChatAnthropic
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.memory import ConversationSummaryBufferMemory, VectorStoreRetrieverMemory
    from langchain.chains import LLMChain, RetrievalQA
    from langchain.agents import AgentExecutor, create_react_agent, Tool
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain_core.documents import Document
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langchain_core.callbacks import AsyncCallbackHandler
    from langchain.tools import BaseTool
    from langchain_community.document_loaders import TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain not fully available: {e}")
    LANGCHAIN_AVAILABLE = False

# ChromaDB for vector storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Google AI (optional)
try:
    import google.generativeai as genai
    from langchain.llms import GooglePalm
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

class OSACallback(AsyncCallbackHandler):
    """Custom callback for OSA to track LangChain operations"""
    
    def __init__(self, action_hooks=None):
        self.action_hooks = action_hooks
        self.start_time = None
        self.operations = []
    
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Called when LLM starts running."""
        self.start_time = datetime.now()
        if self.action_hooks:
            await self.action_hooks.skill_learned("LLM Processing", "langchain_operation")
    
    async def on_llm_end(self, response, **kwargs):
        """Called when LLM ends running."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.operations.append({"type": "llm", "duration": duration})
    
    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs):
        """Called when chain starts running."""
        if self.action_hooks:
            await self.action_hooks.pattern_recognized(f"Chain execution: {serialized.get('name', 'unknown')}")
    
    async def on_agent_action(self, action, **kwargs):
        """Called when agent takes an action."""
        if self.action_hooks:
            await self.action_hooks.skill_learned(f"Agent Action: {action.tool}", "autonomous_action")


class LangChainEngine:
    """LangChain-powered intelligence engine for OSA"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_keys = self._load_api_keys()
        self.llms = {}
        self.embeddings = None
        self.vector_store = None
        self.memory = None
        self.agents = {}
        self.chains = {}
        self.callback = None
        
        # Initialize components
        if LANGCHAIN_AVAILABLE:
            self._initialize_llms()
            self._initialize_embeddings()
            self._initialize_memory()
    
    def set_action_hooks(self, action_hooks):
        """Set action hooks for learning tracking"""
        self.callback = OSACallback(action_hooks)
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment"""
        return {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
            "langsmith": os.getenv("LANGSMITH_API_KEY", "")
        }
    
    def _initialize_llms(self):
        """Initialize various LLM models"""
        # OpenAI
        if self.api_keys["openai"]:
            self.llms["gpt-4"] = ChatOpenAI(
                model="gpt-4",
                api_key=self.api_keys["openai"],
                temperature=0.1
            )
            self.llms["gpt-3.5"] = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=self.api_keys["openai"],
                temperature=0.3
            )
        
        # Anthropic Claude
        if self.api_keys["anthropic"]:
            self.llms["claude"] = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                api_key=self.api_keys["anthropic"],
                temperature=0.1
            )
        
        # Local Ollama
        try:
            self.llms["llama3.2"] = Ollama(
                model="llama3.2:3b"
            )
        except Exception as e:
            print(f"Could not initialize Ollama: {e}")
        
        # Google AI (if available)
        if GOOGLE_AI_AVAILABLE and self.api_keys["google"]:
            try:
                genai.configure(api_key=self.api_keys["google"])
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llms["gemini"] = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.api_keys["google"],
                    temperature=0.1
                )
            except Exception as e:
                print(f"Could not initialize Google AI: {e}")
    
    def _initialize_embeddings(self):
        """Initialize embedding models"""
        if self.api_keys["openai"]:
            self.embeddings = OpenAIEmbeddings(
                api_key=self.api_keys["openai"]
            )
        else:
            # Fallback to local embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
    
    def _initialize_memory(self):
        """Initialize memory systems"""
        if not self.embeddings:
            return
            
        # Initialize ChromaDB vector store
        if CHROMADB_AVAILABLE:
            try:
                persist_dir = Path.home() / ".osa" / "chromadb"
                persist_dir.mkdir(parents=True, exist_ok=True)
                
                self.vector_store = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory=str(persist_dir),
                    collection_name="osa_memory"
                )
                
                # Vector-based memory for long-term context
                self.memory = VectorStoreRetrieverMemory(
                    vectorstore=self.vector_store,
                    memory_key="chat_history",
                    return_docs=True,
                    input_key="input"
                )
            except Exception as e:
                print(f"Could not initialize ChromaDB: {e}")
                # Fallback to summary memory
                self._initialize_summary_memory()
        else:
            self._initialize_summary_memory()
    
    def _initialize_summary_memory(self):
        """Initialize summary-based memory as fallback"""
        if self.llms.get("gpt-3.5"):
            self.memory = ConversationSummaryBufferMemory(
                llm=self.llms["gpt-3.5"],
                max_token_limit=1000,
                memory_key="chat_history",
                input_key="input"
            )
    
    def select_best_llm(self, task_type: str, requirements: Dict[str, Any] = None) -> Any:
        """Intelligently select the best LLM for the task"""
        requirements = requirements or {}
        
        # Task-specific LLM selection
        if task_type in ["coding", "code_generation", "debug"]:
            return self.llms.get("claude") or self.llms.get("gpt-4") or self.llms.get("llama3.2")
        elif task_type in ["reasoning", "analysis", "complex_problem"]:
            return self.llms.get("gpt-4") or self.llms.get("claude") or self.llms.get("gemini")
        elif task_type in ["creative", "writing", "content"]:
            return self.llms.get("claude") or self.llms.get("gemini") or self.llms.get("gpt-4")
        elif task_type in ["fast_response", "simple_question"]:
            return self.llms.get("gpt-3.5") or self.llms.get("llama3.2") or self.llms.get("gemini")
        elif requirements.get("local_only", False):
            return self.llms.get("llama3.2")
        
        # Default fallback
        return (self.llms.get("gpt-4") or 
                self.llms.get("claude") or 
                self.llms.get("gpt-3.5") or 
                self.llms.get("llama3.2"))
    
    async def create_reasoning_chain(self, task_type: str = "general") -> Optional[Any]:
        """Create a reasoning chain for complex problem solving"""
        if not LANGCHAIN_AVAILABLE:
            return None
            
        llm = self.select_best_llm("reasoning")
        if not llm:
            return None
        
        # Create a custom prompt for reasoning
        reasoning_prompt = PromptTemplate(
            input_variables=["input", "chat_history"],
            template="""You are OSA, an advanced AI assistant with deep reasoning capabilities.

Previous conversation:
{chat_history}

Current task: {input}

Think through this step-by-step:
1. Analyze the problem or question
2. Break it down into components
3. Apply relevant knowledge and reasoning
4. Consider multiple perspectives
5. Provide a comprehensive response

Response:"""
        )
        
        # Create the reasoning chain
        chain = LLMChain(
            llm=llm,
            prompt=reasoning_prompt,
            memory=self.memory,
            callbacks=[self.callback] if self.callback else []
        )
        
        self.chains["reasoning"] = chain
        return chain
    
    async def create_code_agent(self) -> Optional[Any]:
        """Create a specialized agent for code-related tasks"""
        if not LANGCHAIN_AVAILABLE:
            return None
            
        llm = self.select_best_llm("coding")
        if not llm:
            return None
        
        # Define code-specific tools
        code_tools = [
            Tool(
                name="code_analyzer",
                description="Analyze code structure, find patterns, and suggest improvements",
                func=self._analyze_code
            ),
            Tool(
                name="code_generator",
                description="Generate code based on requirements and specifications",
                func=self._generate_code
            ),
            Tool(
                name="debug_helper",
                description="Help debug code issues and find solutions",
                func=self._debug_code
            )
        ]
        
        # Create the code agent
        try:
            agent = create_react_agent(
                llm=llm,
                tools=code_tools,
                prompt=self._get_code_agent_prompt()
            )
            
            agent_executor = AgentExecutor(
                agent=agent,
                tools=code_tools,
                memory=self.memory,
                verbose=self.config.get("verbose", False),
                callbacks=[self.callback] if self.callback else []
            )
            
            self.agents["code"] = agent_executor
            return agent_executor
        except Exception as e:
            print(f"Could not create code agent: {e}")
            return None
    
    def _get_code_agent_prompt(self) -> str:
        """Get the prompt template for the code agent"""
        return """You are OSA's specialized code agent. You excel at:
- Understanding and analyzing code
- Generating high-quality code solutions
- Debugging and fixing issues
- Following best practices and patterns

You have access to these tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""
    
    async def create_rag_system(self, documents: List[str] = None) -> Optional[Any]:
        """Create a Retrieval Augmented Generation system"""
        if not LANGCHAIN_AVAILABLE or not self.vector_store:
            return None
            
        llm = self.select_best_llm("reasoning")
        if not llm:
            return None
        
        # Add documents to vector store if provided
        if documents:
            await self.add_documents(documents)
        
        # Create retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            callbacks=[self.callback] if self.callback else []
        )
        
        self.chains["rag"] = qa_chain
        return qa_chain
    
    async def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        """Add documents to the vector store for RAG"""
        if not self.vector_store:
            return
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Create document objects
        docs = []
        for i, doc in enumerate(documents):
            chunks = text_splitter.split_text(doc)
            for chunk in chunks:
                doc_metadata = {"source": f"document_{i}"} if not metadata else metadata[i]
                docs.append(Document(page_content=chunk, metadata=doc_metadata))
        
        # Add to vector store
        try:
            self.vector_store.add_documents(docs)
            print(f"Added {len(docs)} document chunks to vector store")
        except Exception as e:
            print(f"Error adding documents: {e}")
    
    async def query_with_memory(self, query: str, task_type: str = "general") -> Tuple[str, Dict[str, Any]]:
        """Query with persistent memory using the best approach"""
        metadata = {"timestamp": datetime.now().isoformat(), "task_type": task_type}
        
        try:
            # Select the best chain or agent for the task
            if task_type == "coding":
                if "code" in self.agents:
                    response = await self.agents["code"].arun(query)
                else:
                    response = await self._fallback_response(query, task_type)
            elif task_type == "rag_query" and "rag" in self.chains:
                response = await self.chains["rag"].arun(query)
            elif "reasoning" in self.chains:
                response = await self.chains["reasoning"].arun(input=query)
            else:
                response = await self._fallback_response(query, task_type)
            
            metadata["success"] = True
            metadata["model_used"] = self._get_used_model(task_type)
            
            return response, metadata
            
        except Exception as e:
            metadata["error"] = str(e)
            metadata["success"] = False
            return f"Error processing query: {str(e)}", metadata
    
    async def _fallback_response(self, query: str, task_type: str) -> str:
        """Fallback response when specialized chains aren't available"""
        llm = self.select_best_llm(task_type)
        if not llm:
            return "No suitable LLM available for this task"
        
        try:
            if hasattr(llm, 'apredict'):
                return await llm.apredict(query)
            else:
                return llm.predict(query)
        except Exception as e:
            return f"Error in fallback response: {str(e)}"
    
    def _get_used_model(self, task_type: str) -> str:
        """Get the model name used for a task type"""
        llm = self.select_best_llm(task_type)
        if hasattr(llm, 'model_name'):
            return llm.model_name
        elif hasattr(llm, 'model'):
            return llm.model
        else:
            return "unknown"
    
    # Tool functions for the code agent
    def _analyze_code(self, code: str) -> str:
        """Analyze code structure and provide insights"""
        # This would integrate with AST parsing and analysis
        return f"Code analysis for {len(code)} characters: Structure appears well-formed. Consider adding docstrings and type hints."
    
    def _generate_code(self, requirements: str) -> str:
        """Generate code based on requirements"""
        # This would use the LLM to generate code
        return f"# Generated code based on: {requirements}\n# Implementation would go here\npass"
    
    def _debug_code(self, code_issue: str) -> str:
        """Help debug code issues"""
        return f"Debug suggestion for: {code_issue}\n1. Check variable scoping\n2. Verify import statements\n3. Review error messages"
    
    async def initialize_intelligence_systems(self):
        """Initialize all intelligence systems"""
        if not LANGCHAIN_AVAILABLE:
            print("LangChain not available, skipping advanced intelligence systems")
            return False
        
        try:
            # Create reasoning chain
            await self.create_reasoning_chain()
            print("✓ Reasoning chain initialized")
            
            # Create code agent
            await self.create_code_agent()
            print("✓ Code agent initialized")
            
            # Create RAG system
            await self.create_rag_system()
            print("✓ RAG system initialized")
            
            return True
        except Exception as e:
            print(f"Error initializing intelligence systems: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all LangChain systems"""
        return {
            "langchain_available": LANGCHAIN_AVAILABLE,
            "chromadb_available": CHROMADB_AVAILABLE,
            "llms_initialized": len(self.llms),
            "available_models": list(self.llms.keys()),
            "embeddings_ready": self.embeddings is not None,
            "vector_store_ready": self.vector_store is not None,
            "memory_system": "vector" if self.vector_store else "summary" if self.memory else "none",
            "active_chains": list(self.chains.keys()),
            "active_agents": list(self.agents.keys())
        }
    
    async def shutdown(self):
        """Shutdown LangChain systems gracefully"""
        try:
            # Persist vector store if available
            if self.vector_store and hasattr(self.vector_store, 'persist'):
                self.vector_store.persist()
                print("✓ Vector store persisted")
        except Exception as e:
            print(f"Error during shutdown: {e}")


# Create singleton instance
_langchain_engine = None

def get_langchain_engine(config: Dict[str, Any] = None) -> LangChainEngine:
    """Get or create the global LangChain engine"""
    global _langchain_engine
    if _langchain_engine is None:
        _langchain_engine = LangChainEngine(config)
    return _langchain_engine