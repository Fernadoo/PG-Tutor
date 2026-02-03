"""
Knowledge Graph Service

Provides knowledge graph operations for the API.
"""

import sys
import os
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from knowledge_graph import KnowledgeGraph


class KnowledgeGraphService:
    """Service for knowledge graph operations."""
    
    def __init__(self):
        self._kg = KnowledgeGraph()
    
    def get_topics(self, level: Optional[int] = None) -> List[Dict]:
        """Get all topics, optionally filtered by level."""
        topics = []
        
        if level is not None:
            level_topics = self._kg.get_topics_at_level(level)
            topics.extend(level_topics)
        else:
            for lvl in self._kg.get_all_levels():
                topics.extend(self._kg.get_topics_at_level(lvl))
        
        return [self._topic_to_dict(t) for t in topics]
    
    def get_topic_by_id(self, topic_id: str) -> Optional[Dict]:
        """Get topic by ID."""
        # ID format: name in lowercase with underscores
        for level in self._kg.get_all_levels():
            for topic in self._kg.get_topics_at_level(level):
                if topic.name.lower().replace(" ", "_") == topic_id:
                    return self._topic_to_dict(topic)
        return None
    
    def get_topic_by_name(self, name: str) -> Optional[object]:
        """Get topic object by name (for internal use)."""
        return self._kg.get_topic_by_name(name)
    
    def get_graph_structure(self) -> Dict:
        """Get graph structure for visualization."""
        import networkx as nx
        
        G = nx.DiGraph()
        
        # Add nodes and edges
        for level in self._kg.get_all_levels():
            topics = self._kg.get_topics_at_level(level)
            for topic in topics:
                G.add_node(
                    topic.name,
                    level=topic.level,
                    difficulty=topic.difficulty
                )
                for prereq in topic.prerequisites:
                    G.add_edge(prereq, topic.name)
        
        # Calculate layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        nodes = []
        for node in G.nodes():
            data = G.nodes[node]
            x, y = pos[node]
            nodes.append({
                "id": node.lower().replace(" ", "_"),
                "name": node,
                "level": data["level"],
                "difficulty": data["difficulty"],
                "x": float(x),
                "y": float(y)
            })
        
        edges = []
        for edge in G.edges():
            edges.append({
                "source": edge[0].lower().replace(" ", "_"),
                "target": edge[1].lower().replace(" ", "_")
            })
        
        return {"nodes": nodes, "edges": edges}
    
    def get_topic_prerequisites(self, topic_name: str) -> List[str]:
        """Get prerequisites for a topic."""
        topic = self._kg.get_topic_by_name(topic_name)
        if topic:
            return topic.prerequisites
        return []
    
    def get_random_topic_at_level(self, level: int):
        """Get random topic at level."""
        return self._kg.get_random_topic_at_level(level)
    
    def _topic_to_dict(self, topic) -> Dict:
        """Convert Topic object to dictionary."""
        return {
            "id": topic.name.lower().replace(" ", "_"),
            "name": topic.name,
            "level": topic.level,
            "difficulty": topic.difficulty,
            "content": topic.content,
            "prerequisites": topic.prerequisites
        }
