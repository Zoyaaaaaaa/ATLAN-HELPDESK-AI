from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Priority(str, Enum):
    """Ticket priority levels"""
    P0_HIGH = "P0 (High)"
    P1_MEDIUM = "P1 (Medium)"
    P2_LOW = "P2 (Low)"

class Sentiment(str, Enum):
    """Customer sentiment analysis"""
    FRUSTRATED = "Frustrated"
    CURIOUS = "Curious"
    ANGRY = "Angry"
    NEUTRAL = "Neutral"

class TopicTag(str, Enum):
    """Available topic tags for classification"""
    HOW_TO = "How-to"
    PRODUCT = "Product"
    CONNECTOR = "Connector"
    LINEAGE = "Lineage"
    API_SDK = "API/SDK"
    SSO = "SSO"
    GLOSSARY = "Glossary"
    BEST_PRACTICES = "Best practices"
    SENSITIVE_DATA = "Sensitive data"

class TicketClassification(BaseModel):
    """Classification result for a support ticket"""
    topic_tags: List[str] = Field(description="Relevant topic tags")
    sentiment: Sentiment = Field(description="Customer sentiment")
    priority: Priority = Field(description="Ticket priority level")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    reasoning: Optional[str] = Field(description="AI reasoning for classification")

class TicketData(BaseModel):
    """Raw ticket data"""
    id: Optional[str] = Field(description="Ticket ID")
    subject: str = Field(description="Ticket subject")
    description: str = Field(description="Ticket description")
    customer_id: Optional[str] = Field(description="Customer identifier")
    created_at: Optional[str] = Field(description="Creation timestamp")

class Document(BaseModel):
    """Document model for knowledge base"""
    id: str = Field(description="Unique document identifier")
    title: str = Field(description="Document title")
    content: str = Field(description="Document content")
    url: str = Field(description="Source URL")
    source_type: str = Field(description="Type of source (docs/developer)")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

class RAGResponse(BaseModel):
    """Response from RAG pipeline"""
    answer: str = Field(description="Generated answer")
    sources: List[str] = Field(default_factory=list, description="Source URLs")
    retrieved_docs: List[Document] = Field(default_factory=list, description="Retrieved documents")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Response confidence")

class TicketResponse(BaseModel):
    """Complete ticket response"""
    ticket_id: str = Field(description="Ticket identifier")
    classification: TicketClassification = Field(description="Ticket classification")
    response: str = Field(description="AI-generated response")
    sources: List[str] = Field(default_factory=list, description="Reference sources")
    processing_time: float = Field(description="Processing time in seconds")
    needs_human_review: bool = Field(default=False, description="Requires human intervention")

class SearchResult(BaseModel):
    """Search result from vector store"""
    document: Document = Field(description="Retrieved document")
    score: float = Field(description="Similarity score")
    
class KnowledgeBaseStats(BaseModel):
    """Statistics about the knowledge base"""
    total_documents: int = Field(description="Total number of documents")
    sources: dict = Field(description="Documents by source type")
    last_updated: str = Field(description="Last update timestamp")