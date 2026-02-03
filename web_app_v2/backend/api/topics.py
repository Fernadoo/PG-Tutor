"""
API Router for Topic Management
"""

from fastapi import APIRouter, HTTPException
from typing import List

from models.schemas import TopicResponse, KnowledgeGraphResponse, KnowledgeGraphNode, KnowledgeGraphEdge
from services.knowledge_graph_service import KnowledgeGraphService

router = APIRouter()
kg_service = KnowledgeGraphService()


@router.get("/list", response_model=List[TopicResponse])
async def list_topics(level: int = None):
    """List all topics, optionally filtered by level."""
    topics = kg_service.get_topics(level)
    return [TopicResponse(**t) for t in topics]


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str):
    """Get a specific topic by ID."""
    topic = kg_service.get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return TopicResponse(**topic)


@router.get("/graph/visualization", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph():
    """Get knowledge graph structure for visualization."""
    graph_data = kg_service.get_graph_structure()
    
    nodes = [
        KnowledgeGraphNode(
            id=n["id"],
            name=n["name"],
            level=n["level"],
            difficulty=n["difficulty"],
            x=n.get("x", 0),
            y=n.get("y", 0)
        )
        for n in graph_data["nodes"]
    ]
    
    edges = [
        KnowledgeGraphEdge(source=e["source"], target=e["target"])
        for e in graph_data["edges"]
    ]
    
    return KnowledgeGraphResponse(nodes=nodes, edges=edges)
