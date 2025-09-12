import logging
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer
from models.ticket_models import RAGResponse, TicketClassification, Document

logger = logging.getLogger(__name__)

class RAGService:
    """RAG service for answering support queries"""
    
    def __init__(self, knowledge_base: Any = None):
        """
        Initialize the RAG service
        
        Args:
            knowledge_base: Instance of EnhancedAtlanKnowledgeBase (optional)
        """
        self.kb_manager = knowledge_base
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded embedding model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            self.embedding_model = None
        
        logger.info("RAG Service initialized")
    
    def get_response(self, query: str, classification: Optional[TicketClassification] = None) -> RAGResponse:
        """Get a RAG response for a query"""
        # If we have a knowledge base, use it
        if self.kb_manager:
            try:
                # Extract topic context for enhanced search
                topic_context = classification.topic_tags if classification else None
                
                # Determine search strategy based on topics
                category_filter = None
                if topic_context:
                    # Map topics to knowledge base categories
                    topic_to_category = {
                        "How-to": "product_documentation",
                        "Product": "product_documentation", 
                        "Best practices": "product_documentation",
                        "API/SDK": "developer_hub",
                        "SSO": "product_documentation"
                    }
                    for topic in topic_context:
                        if topic in topic_to_category:
                            category_filter = topic_to_category[topic]
                            break
                
                # Generate RAG response
                rag_result = self.kb_manager.generate_rag_response(
                    query, 
                    limit=5, 
                    category_filter=category_filter
                )
                
                # Convert to Document objects
                documents = []
                for chunk in rag_result.get("context_chunks", []):
                    documents.append(Document(
                        id=str(hash(chunk.get("title", ""))),
                        title=chunk.get("title", ""),
                        content=chunk.get("content", ""),
                        url=chunk.get("url", ""),
                        source_type="knowledge_base",
                        metadata={
                            "category": chunk.get("category", ""),
                            "score": chunk.get("score", 0.0),
                            "tags": chunk.get("tags", [])
                        }
                    ))
                
                return RAGResponse(
                    answer=rag_result["answer"],
                    sources=[source["url"] for source in rag_result.get("sources", [])],
                    retrieved_docs=documents,
                    confidence_score=rag_result.get("confidence", 0.0),
                    metadata={
                        "category_filter": category_filter,
                        "query": query
                    }
                )
                
            except Exception as e:
                logger.error(f"Error generating RAG response: {str(e)}")
                # Fall through to default response
        
        # Fallback response when knowledge base is not available or fails
        answer = f"""Based on Atlan documentation, here's information about your query:

{query}

This appears to be related to {', '.join(classification.topic_tags) if classification else 'general'} topics.

For detailed information, please refer to:
- Atlan Documentation: https://docs.atlan.com/
- Developer Hub: https://developer.atlan.com/

If you need further assistance, please contact support."""

        return RAGResponse(
            answer=answer,
            sources=[
                "https://docs.atlan.com/",
                "https://developer.atlan.com/"
            ],
            retrieved_docs=[],
            confidence_score=0.5,
            metadata={"fallback": True}
        )
    
    def get_collection_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if self.kb_manager:
            try:
                return self.kb_manager.get_knowledge_base_stats()
            except Exception as e:
                return {"error": f"Failed to get knowledge base stats: {str(e)}"}
        return {"error": "Knowledge base not available"}