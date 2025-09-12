import streamlit as st
import json
import os
from datetime import datetime
import re
from langchain_groq import ChatGroq
import os
from datetime import datetime
from config.settings import settings
from services.monitoring_service import SystemMonitor

monitor = SystemMonitor()

os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
class AtlanTicketClassifier:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        
    def classify_ticket(self, ticket_text, verbose=False):
        classification_prompt = f"""
        Analyze the following customer support ticket and classify it according to the specified schema.
        
        TICKET TEXT:
        {ticket_text}
        
        CLASSIFICATION SCHEMA:
        1. Topic Tags: Choose from How-to, Product, Connector, Lineage, API/SDK, SSO, Glossary, Best practices, Sensitive data
        2. Sentiment: Choose from Frustrated, Curious, Angry, Neutral
        3. Priority: Choose from P0 (High), P1 (Medium), P2 (Low)
        
        Return your response as a valid JSON object with the following structure:
        {{
            "topic_tags": ["tag1", "tag2"],
            "sentiment": "sentiment_value",
            "priority": "priority_value"
        }}
        """
        
        verbose_logs = []
        
        try:
            if verbose:
                verbose_logs.append(f"Classification Started: {datetime.now().strftime('%H:%M:%S')}")
                verbose_logs.append(f"Ticket Length: {len(ticket_text)} characters")
                verbose_logs.append(f"Model: llama-3.3-70b-versatile")
            
            response = self.llm.invoke(classification_prompt)
            
            if verbose:
                verbose_logs.append(f"LLM Response Received: {len(response.content)} characters")
            
            # Extract JSON from response
            json_str = response.content.strip()
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                classification = json.loads(json_str)
                
                if verbose:
                    verbose_logs.append(f"Classification Complete: {classification}")
                    
                return classification, verbose_logs if verbose else classification
            else:
                # Fallback if JSON parsing fails
                fallback = {
                    "topic_tags": ["Product"],
                    "sentiment": "Neutral",
                    "priority": "P1 (Medium)"
                }
                
                if verbose:
                    verbose_logs.append("Fallback Used: JSON parsing failed")
                    
                return fallback, verbose_logs if verbose else fallback
                
        except Exception as e:
            if verbose:
                verbose_logs.append(f"Error: {str(e)}")
            
            fallback = {
                "topic_tags": ["Product"],
                "sentiment": "Neutral",
                "priority": "P1 (Medium)"
            }
            
            if not verbose:
                st.error(f"Classification error: {e}")
                
            return fallback, verbose_logs if verbose else fallback

class AtlanRAGAgent:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        
    def generate_response(self, query, classification, verbose=False):
        verbose_logs = []
        start_time = datetime.now()
        
        if verbose:
            verbose_logs.append(f"RAG Agent Started: {start_time.strftime('%H:%M:%S')}")
            verbose_logs.append(f"Classification: {classification}")
        
        # Internal analysis view
        internal_analysis = {
            "classification": classification,
            "timestamp": start_time.isoformat(),
            "query": query[:100] + "..." if len(query) > 100 else query
        }
        
        # Check if we should use RAG or just route the ticket
        rag_topics = ["How-to", "Product", "Best practices", "API/SDK", "SSO"]
        use_rag = any(topic in rag_topics for topic in classification["topic_tags"])
        
        if verbose:
            verbose_logs.append(f"RAG Decision: {'Using RAG' if use_rag else 'Routing ticket'}")
        
        if use_rag:
            # Determine which knowledge base category to use
            if any(topic in ["API/SDK"] for topic in classification["topic_tags"]):
                category_filter = "developer_hub"
            else:
                category_filter = "product_documentation"
            
            if verbose:
                verbose_logs.append(f"Knowledge Base Category: {category_filter}")
                verbose_logs.append(f"Searching Knowledge Base...")
                
            # Generate RAG response
            rag_response = self.kb.generate_rag_response(query, category_filter=category_filter)
            
            if verbose:
                verbose_logs.append(f"Sources Found: {len(rag_response.get('sources', []))}")
                verbose_logs.append(f"Answer Length: {len(rag_response.get('answer', ''))} characters")
            
            # Final response view
            final_response = {
                "answer": rag_response["answer"],
                "sources": rag_response["sources"],
                "type": "RAG Response",
                "category_used": category_filter
            }
        else:
            if verbose:
                verbose_logs.append(f"Routing: Ticket routed to appropriate team")
            
            # Route the ticket
            final_response = {
                "answer": f"This ticket has been classified as a '{classification['topic_tags'][0]}' issue and routed to the appropriate team. A specialist will review your request and respond within 24 hours.",
                "sources": [],
                "type": "Routing Response",
                "category_used": None
            }
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        if verbose:
            verbose_logs.append(f"Processing Time: {processing_time:.2f} seconds")
            verbose_logs.append(f"Response Generated: {end_time.strftime('%H:%M:%S')}")
            
        return {
            "internal_analysis": internal_analysis,
            "final_response": final_response,
            "verbose_logs": verbose_logs,
            "processing_time": processing_time
        }
