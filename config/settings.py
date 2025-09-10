# import os
# from typing import Dict, List
# from dotenv import load_dotenv
# load_dotenv()
# class Settings:
#     """Application settings and configuration"""
    
#     # API Keys
#     GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
#     TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
    
#     # Qdrant Configuration
#     QDRANT_URL = os.getenv("QDRANT_URL", "https://2926feae-a2ea-4ce3-bafb-b4a47075e39a.eu-central-1-0.aws.cloud.qdrant.io:6333")
#     QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ySsf9zVCNaQqrirLbX-pc8oBJUDbOmzU5xfdLNHgR8Q")
    
#     # Use in-memory mode if Qdrant is not available
#     USE_MEMORY_STORE = os.getenv("USE_MEMORY_STORE", "true").lower() == "true"
    
#     # Model Configuration
#     LLM_MODEL = "llama-3.3-70b-versatile"
#     EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
#     EMBEDDING_DIMENSION = 384
#     QDRANT_COLLECTION_NAME = "atlan_documentation"


#     # Chunking settings
#     CHUNK_SIZE = 1000
#     CHUNK_OVERLAP = 200

#     # Similarity threshold
#     SIMILARITY_THRESHOLD = 0.7
        
#     # Knowledge Base URLs
#     DOCUMENTATION_URLS = [
#         "https://docs.atlan.com/",
#         "https://docs.atlan.com/getting-started",
#         "https://docs.atlan.com/lineage",
#         "https://docs.atlan.com/governance",
#         "https://docs.atlan.com/connectors",
#         "https://docs.atlan.com/sso",
#         "https://docs.atlan.com/glossary",
#         "https://docs.atlan.com/security",
#         "https://docs.atlan.com/best-practices"
#     ]
    
#     DEVELOPER_URLS = [
#         "https://developer.atlan.com/",
#         "https://developer.atlan.com/api",
#         "https://developer.atlan.com/sdk",
#         "https://developer.atlan.com/authentication",
#         "https://developer.atlan.com/examples"
#     ]
    
#     # Classification Configuration
#     TOPIC_KEYWORDS = {
#         "How-to": ["how", "tutorial", "guide", "step", "instructions", "setup", "configure"],
#         "Product": ["feature", "functionality", "product", "tool", "dashboard", "interface"],
#         "Connector": ["connector", "connection", "sync", "integration", "source", "database"],
#         "Lineage": ["lineage", "dependency", "upstream", "downstream", "relationship", "trace"],
#         "API/SDK": ["api", "sdk", "endpoint", "authentication", "token", "request", "response"],
#         "SSO": ["sso", "single sign-on", "saml", "oauth", "authentication", "login", "azure", "okta"],
#         "Glossary": ["glossary", "term", "definition", "vocabulary", "business term"],
#         "Best practices": ["best practice", "recommendation", "standard", "guideline", "approach"],
#         "Sensitive data": ["pii", "sensitive", "privacy", "gdpr", "compliance", "encryption"]
#     }
    
#     SENTIMENT_KEYWORDS = {
#         "Angry": ["angry", "furious", "outraged", "terrible", "awful", "hate", "worst"],
#         "Frustrated": ["frustrated", "annoying", "stuck", "difficult", "confusing", "problem"],
#         "Curious": ["curious", "wondering", "interested", "explore", "learn", "understand"],
#         "Neutral": []  # Default fallback
#     }
    
#     PRIORITY_RULES = {
#         "P0 (High)": {
#             "keywords": ["urgent", "critical", "down", "error", "broken", "not working"],
#             "sentiment": ["Angry", "Frustrated"]
#         },
#         "P1 (Medium)": {
#             "keywords": ["help", "issue", "problem", "question"],
#             "sentiment": ["Curious"]
#         },
#         "P2 (Low)": {
#             "keywords": ["how", "guide", "tutorial", "best practice"],
#             "sentiment": ["Neutral"]
#         }
#     }
    
#     # SLA Configuration (hours)
#     SLA_HOURS = {
#         "P0 (High)": 2,
#         "P1 (Medium)": 8,
#         "P2 (Low)": 24
#     }
    
#     # RAG Configuration
#     MAX_SEARCH_RESULTS = 5
#     CHUNK_SIZE = 1000
#     CHUNK_OVERLAP = 100
#     SIMILARITY_THRESHOLD = 0.7
    
#     # System Prompts
#     # config/settings.py
#     CLASSIFICATION_PROMPT = """
#     Analyze this support ticket and provide classification:

#     Subject: {subject}
#     Description: {description}

#     Return response in exact JSON format with these fields:
#     - topic_tags: array of relevant topics
#     - sentiment: one of "Angry", "Frustrated", "Curious", "Neutral" 
#     - priority: one of "P0 (High)", "P1 (Medium)", "P2 (Low)"
#     - confidence_score: float between 0-1
#     - reasoning: brief explanation
#     """
    
#     RAG_SYSTEM_PROMPT = """
#     You are Atlan's AI support assistant. Use the provided context from Atlan's documentation 
#     to answer the customer's question accurately and helpfully.

#     Guidelines:
#     - Provide clear, step-by-step instructions when applicable
#     - Include relevant links and references
#     - Be concise but comprehensive
#     - If the context doesn't contain enough information, say so
#     - Always maintain a helpful and professional tone

#     Context: {context}
    
#     Question: {question}
    
#     Provide a detailed answer based on the context above.
#     """

# # Create global settings instance
# settings = Settings()
import os
from typing import Dict, List

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