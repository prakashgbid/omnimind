#!/usr/bin/env python3
"""
OSA Memory Persistence System
Ensures context and learning persist across all sessions
"""

import json
import pickle
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum
import logging

import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class MemoryPriority(Enum):
    """Priority levels for memory items"""
    CRITICAL = "critical"  # Core vision, identity
    HIGH = "high"  # Key decisions, patterns
    MEDIUM = "medium"  # Useful context
    LOW = "low"  # Details, specifics


class MemoryType(Enum):
    """Types of memories"""
    VISION = "vision"  # Core purpose and goals
    DECISION = "decision"  # Architectural decisions
    LEARNING = "learning"  # Learned patterns
    PROJECT = "project"  # Project-specific knowledge
    SKILL = "skill"  # Acquired capabilities
    CONTEXT = "context"  # Conversation context
    CODE = "code"  # Code patterns and solutions
    ERROR = "error"  # Mistakes to avoid


@dataclass
class Memory:
    """A single memory item"""
    id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    timestamp: datetime
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    decay_rate: float = 0.0  # How fast this memory fades
    reinforcement_score: float = 1.0  # How important this memory is


class PersistentMemory:
    """Persistent memory system for OSA"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("OSA-Memory")
        
        # Paths
        self.memory_dir = Path.home() / ".osa" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Core memory files
        self.vision_file = self.memory_dir / "core_vision.json"
        self.decisions_file = self.memory_dir / "decisions.json"
        self.projects_file = self.memory_dir / "projects.json"
        self.skills_file = self.memory_dir / "skills.json"
        
        # SQLite for structured memory
        self.db_path = self.memory_dir / "memories.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_database()
        
        # Vector store for semantic search
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.memory_dir / "chroma")
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="osa_memories",
            metadata={"description": "OSA's persistent memory"}
        )
        
        # Embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Memory compression settings
        self.max_memories = 10000
        self.compression_threshold = 0.8  # Similarity threshold for merging
        
        # Load core memories
        self._load_core_memories()
    
    def _init_database(self):
        """Initialize SQLite database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME,
                decay_rate REAL DEFAULT 0.0,
                reinforcement_score REAL DEFAULT 1.0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time DATETIME,
                end_time DATETIME,
                summary TEXT,
                key_decisions TEXT,
                memories_created INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                name TEXT PRIMARY KEY,
                description TEXT,
                proficiency REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                last_used DATETIME,
                code_template TEXT
            )
        ''')
        
        self.conn.commit()
    
    def _load_core_memories(self):
        """Load core vision and identity memories"""
        # Always load OSA's core identity
        core_vision = {
            "identity": "OSA is a self-evolving, fully autonomous system capable of building anything",
            "purpose": "Act as a human partner that can create systems, modify itself, and work 24/7",
            "capabilities": [
                "Self-modification and improvement",
                "Building systems from scratch",
                "Creating agent ecosystems",
                "Autonomous decision making",
                "Continuous learning and evolution"
            ],
            "not_this": [
                "Just another AI wrapper",
                "Simple tool orchestrator",
                "Claude Code competitor"
            ],
            "remember": "OSA creates tools, doesn't just use them"
        }
        
        self.store_memory(
            content=json.dumps(core_vision, indent=2),
            memory_type=MemoryType.VISION,
            priority=MemoryPriority.CRITICAL,
            metadata={"permanent": True, "core": True}
        )
    
    def store_memory(self, content: str, memory_type: MemoryType, 
                    priority: MemoryPriority = MemoryPriority.MEDIUM,
                    metadata: Dict[str, Any] = None) -> str:
        """Store a new memory"""
        # Generate ID
        memory_id = hashlib.md5(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Create embedding
        embedding = self.embedder.encode(content).tolist()
        
        # Store in SQLite
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (id, content, memory_type, priority, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            memory_id,
            content,
            memory_type.value,
            priority.value,
            json.dumps(metadata) if metadata else None,
            datetime.now().isoformat()
        ))
        self.conn.commit()
        
        # Store in vector database
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "type": memory_type.value,
                "priority": priority.value,
                "timestamp": datetime.now().isoformat()
            }],
            ids=[memory_id]
        )
        
        self.logger.info(f"Stored {memory_type.value} memory: {memory_id}")
        return memory_id
    
    def recall_memories(self, query: str, n_results: int = 5,
                       memory_type: Optional[MemoryType] = None) -> List[Memory]:
        """Recall relevant memories"""
        # Create query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Search vector store
        where_clause = {"type": memory_type.value} if memory_type else None
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )
        
        memories = []
        if results['ids'] and results['ids'][0]:
            cursor = self.conn.cursor()
            for idx, memory_id in enumerate(results['ids'][0]):
                # Get full memory from SQLite
                cursor.execute(
                    "SELECT * FROM memories WHERE id = ?",
                    (memory_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    # Update access count
                    cursor.execute('''
                        UPDATE memories 
                        SET access_count = access_count + 1,
                            last_accessed = ?
                        WHERE id = ?
                    ''', (datetime.now().isoformat(), memory_id))
                    
                    memories.append(Memory(
                        id=row[0],
                        content=row[1],
                        memory_type=MemoryType(row[2]),
                        priority=MemoryPriority(row[3]),
                        timestamp=datetime.fromisoformat(row[4]),
                        metadata=json.loads(row[5]) if row[5] else None,
                        access_count=row[6],
                        last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
                        decay_rate=row[8],
                        reinforcement_score=row[9]
                    ))
            
            self.conn.commit()
        
        return memories
    
    def get_context_for_session(self) -> Dict[str, Any]:
        """Get essential context for a new session"""
        context = {
            "core_vision": [],
            "recent_decisions": [],
            "active_projects": [],
            "learned_patterns": [],
            "skills": [],
            "warnings": []
        }
        
        # Get core vision memories (CRITICAL priority)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT content FROM memories 
            WHERE priority = 'critical' AND memory_type = 'vision'
            ORDER BY reinforcement_score DESC
            LIMIT 5
        ''')
        context["core_vision"] = [row[0] for row in cursor.fetchall()]
        
        # Get recent important decisions
        cursor.execute('''
            SELECT content FROM memories 
            WHERE memory_type = 'decision' AND priority IN ('critical', 'high')
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        context["recent_decisions"] = [row[0] for row in cursor.fetchall()]
        
        # Get active project context
        cursor.execute('''
            SELECT content FROM memories 
            WHERE memory_type = 'project'
            ORDER BY last_accessed DESC NULLS LAST
            LIMIT 5
        ''')
        context["active_projects"] = [row[0] for row in cursor.fetchall()]
        
        # Get learned patterns
        cursor.execute('''
            SELECT content FROM memories 
            WHERE memory_type = 'learning'
            ORDER BY reinforcement_score DESC
            LIMIT 10
        ''')
        context["learned_patterns"] = [row[0] for row in cursor.fetchall()]
        
        # Get current skills
        cursor.execute('''
            SELECT name, description, proficiency FROM skills
            ORDER BY proficiency DESC
            LIMIT 10
        ''')
        context["skills"] = [
            {"name": row[0], "description": row[1], "proficiency": row[2]}
            for row in cursor.fetchall()
        ]
        
        # Get error memories (things to avoid)
        cursor.execute('''
            SELECT content FROM memories 
            WHERE memory_type = 'error'
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        context["warnings"] = [row[0] for row in cursor.fetchall()]
        
        return context
    
    def compress_memories(self):
        """Compress similar memories to save space"""
        cursor = self.conn.cursor()
        
        # Get all memories
        cursor.execute("SELECT id, content FROM memories")
        memories = cursor.fetchall()
        
        if len(memories) <= self.max_memories:
            return
        
        # Group similar memories
        merged_count = 0
        for i, (id1, content1) in enumerate(memories):
            embedding1 = self.embedder.encode(content1)
            
            for j, (id2, content2) in enumerate(memories[i+1:], i+1):
                embedding2 = self.embedder.encode(content2)
                
                # Calculate similarity
                similarity = np.dot(embedding1, embedding2) / (
                    np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
                )
                
                if similarity > self.compression_threshold:
                    # Merge memories
                    merged_content = f"[Merged] {content1}\n---\n{content2}"
                    
                    # Update first memory with merged content
                    cursor.execute('''
                        UPDATE memories 
                        SET content = ?,
                            reinforcement_score = reinforcement_score + 0.5
                        WHERE id = ?
                    ''', (merged_content, id1))
                    
                    # Delete second memory
                    cursor.execute("DELETE FROM memories WHERE id = ?", (id2,))
                    self.collection.delete(ids=[id2])
                    
                    merged_count += 1
        
        self.conn.commit()
        self.logger.info(f"Compressed {merged_count} similar memories")
    
    def reinforce_memory(self, memory_id: str, score: float = 0.1):
        """Reinforce a memory when it's useful"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE memories 
            SET reinforcement_score = reinforcement_score + ?
            WHERE id = ?
        ''', (score, memory_id))
        self.conn.commit()
    
    def decay_memories(self):
        """Apply decay to old, unused memories"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE memories 
            SET reinforcement_score = reinforcement_score * 0.99
            WHERE last_accessed < datetime('now', '-7 days')
            AND priority NOT IN ('critical', 'high')
        ''')
        
        # Delete very weak memories
        cursor.execute('''
            DELETE FROM memories 
            WHERE reinforcement_score < 0.1
            AND priority = 'low'
        ''')
        
        self.conn.commit()
    
    def add_skill(self, name: str, description: str, code_template: str = None):
        """Add a new learned skill"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO skills 
            (name, description, code_template, last_used)
            VALUES (?, ?, ?, ?)
        ''', (name, description, code_template, datetime.now().isoformat()))
        self.conn.commit()
        
        # Also store as memory
        self.store_memory(
            content=f"Skill: {name}\n{description}",
            memory_type=MemoryType.SKILL,
            priority=MemoryPriority.HIGH,
            metadata={"skill_name": name}
        )
    
    def export_critical_context(self) -> str:
        """Export critical context for session handoff"""
        context = self.get_context_for_session()
        
        summary = [
            "=== OSA CRITICAL CONTEXT ===\n",
            "CORE VISION:",
            *context["core_vision"][:3],
            "\nKEY DECISIONS:",
            *context["recent_decisions"][:5],
            "\nACTIVE PROJECTS:",
            *context["active_projects"][:3],
            "\nTOP SKILLS:",
            *[f"- {s['name']}: {s['description']}" for s in context["skills"][:5]],
            "\nREMEMBER TO AVOID:",
            *context["warnings"][:3],
            "\n=== END CONTEXT ==="
        ]
        
        return "\n".join(summary)
    
    def create_session_checkpoint(self, summary: str, key_decisions: List[str]):
        """Create a checkpoint for the current session"""
        session_id = hashlib.md5(
            f"session_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions 
            (id, start_time, summary, key_decisions)
            VALUES (?, ?, ?, ?)
        ''', (
            session_id,
            datetime.now().isoformat(),
            summary,
            json.dumps(key_decisions)
        ))
        self.conn.commit()
        
        return session_id


# Singleton instance
_persistent_memory = None

def get_persistent_memory(config: Dict[str, Any] = None) -> PersistentMemory:
    """Get or create the global persistent memory"""
    global _persistent_memory
    if _persistent_memory is None:
        _persistent_memory = PersistentMemory(config)
    return _persistent_memory