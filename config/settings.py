import os
from typing import Dict, List
from dotenv import load_dotenv
load_dotenv()

class Settings:
    """Configuration settings for the helpdesk application"""
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_CLASS = "services.knowledge_base_service.EnhancedAtlanKnowledgeBase"
    
    # Classification Configuration
    TOPIC_TAGS = [
        "How-to",
        "Product", 
        "Connector",
        "Lineage",
        "API/SDK",
        "SSO",
        "Glossary",
        "Best practices",
        "Sensitive data",
        "Authentication",
        "Data Products",
        "Workflows",
        "Governance",
        "Insights",
        "Other"
    ]
    
    SENTIMENT_CATEGORIES = [
        "Frustrated",
        "Curious", 
        "Angry",
        "Neutral",
        "Positive",
        "Confused",
        "Urgent"
    ]
    
    PRIORITY_LEVELS = [
        "P0",  # High/Critical
        "P1",  # Medium  
        "P2"   # Low
    ]
    
    # RAG Configuration
    RAG_ENABLED_TOPICS = [
        "How-to",
        "Product", 
        "Best practices",
        "API/SDK",
        "SSO",
        "Authentication",
        "Data Products",
        "Lineage",
        "Glossary"
    ]
    
    RAG_SEARCH_LIMIT = 5
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY")
    JINA_API_KEY: str = os.getenv("JINA_API_KEY")
    
    # Category Mapping for Knowledge Base Filtering
    TOPIC_TO_CATEGORY_MAP = {
        "API/SDK": "developer_hub",
        "Authentication": "product_documentation", 
        "SSO": "product_documentation",
        "Product": "product_documentation",
        "Data Products": "product_documentation",
        "Lineage": "product_documentation",
        "Glossary": "product_documentation",
        "How-to": None,  # Search all categories
        "Best practices": "product_documentation"
    }
    
    # File Paths
    DATA_DIR = "data"
    SAMPLE_TICKETS_FILE = os.path.join(DATA_DIR, "sample_tickets.json")
    
    # Response Templates
    ROUTING_MESSAGE_TEMPLATE = "This ticket has been classified as a '{topic}' issue with {priority} priority and routed to the appropriate team."
    
    # UI Configuration
    TICKETS_PER_PAGE = 10
    MAX_RESPONSE_LENGTH = 2000
    
    @classmethod
    def get_category_filter(cls, topic: str) -> str:
        """Get knowledge base category filter for a topic"""
        return cls.TOPIC_TO_CATEGORY_MAP.get(topic)
    
    @classmethod
    def should_use_rag(cls, topic: str) -> bool:
        """Check if topic should use RAG for response generation"""
        return topic in cls.RAG_ENABLED_TOPICS
settings = Settings()