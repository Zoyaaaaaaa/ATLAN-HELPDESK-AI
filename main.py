import streamlit as st
import json
import os
from datetime import datetime
import uuid
import requests
import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional
import time
import logging
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from services import analytics_service,monitoring_service
from config.settings import settings
# from services.ticket_classifier import TicketClassifier as AtlanTicketClassifier,AtlanRAGAgent
from services.ticket_classifier import AtlanRAGAgent
from services.knowledge_base import EnhancedAtlanKnowledgeBase
monitor=monitoring_service.SystemMonitor

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
                verbose_logs.append(f"🔍 **Classification Started**: {datetime.now().strftime('%H:%M:%S')}")
                verbose_logs.append(f"📝 **Ticket Length**: {len(ticket_text)} characters")
                verbose_logs.append(f"🤖 **Model**: llama-3.3-70b-versatile")
            
            response = self.llm.invoke(classification_prompt)
            
            if verbose:
                verbose_logs.append(f"✅ **LLM Response Received**: {len(response.content)} characters")
            
            # Extract JSON from response
            json_str = response.content.strip()
            # Clean up the response to extract just the JSON
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                classification = json.loads(json_str)
                
                if verbose:
                    verbose_logs.append(f"🎯 **Classification Complete**: {classification}")
                    
                return classification, verbose_logs if verbose else classification
            else:
                # Fallback if JSON parsing fails
                fallback = {
                    "topic_tags": ["Product"],
                    "sentiment": "Neutral",
                    "priority": "P1 (Medium)"
                }
                
                if verbose:
                    verbose_logs.append("⚠️ **Fallback Used**: JSON parsing failed")
                    
                return fallback, verbose_logs if verbose else fallback
                
        except Exception as e:
            if verbose:
                verbose_logs.append(f"❌ **Error**: {str(e)}")
            
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
            verbose_logs.append(f"🚀 **RAG Agent Started**: {start_time.strftime('%H:%M:%S')}")
            verbose_logs.append(f"📊 **Classification**: {classification}")
        
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
            verbose_logs.append(f"🔄 **RAG Decision**: {'Using RAG' if use_rag else 'Routing ticket'}")
        
        if use_rag:
            # Determine which knowledge base category to use
            if any(topic in ["API/SDK"] for topic in classification["topic_tags"]):
                category_filter = "developer_hub"
            else:
                category_filter = "product_documentation"
            
            if verbose:
                verbose_logs.append(f"📚 **Knowledge Base Category**: {category_filter}")
                verbose_logs.append(f"🔍 **Searching Knowledge Base**...")
                
            # Generate RAG response
            rag_response = self.kb.generate_rag_response(query, category_filter=category_filter)
            
            if verbose:
                verbose_logs.append(f"📄 **Sources Found**: {len(rag_response.get('sources', []))}")
                verbose_logs.append(f"📝 **Answer Length**: {len(rag_response.get('answer', ''))} characters")
            
            # Final response view
            final_response = {
                "answer": rag_response["answer"],
                "sources": rag_response["sources"],
                "type": "RAG Response",
                "category_used": category_filter
            }
        else:
            if verbose:
                verbose_logs.append(f"📮 **Routing**: Ticket routed to appropriate team")
            
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
            verbose_logs.append(f"⏱️ **Processing Time**: {processing_time:.2f} seconds")
            verbose_logs.append(f"✅ **Response Generated**: {end_time.strftime('%H:%M:%S')}")
            
        return {
            "internal_analysis": internal_analysis,
            "final_response": final_response,
            "verbose_logs": verbose_logs,
            "processing_time": processing_time
        }

def load_sample_tickets() -> List[Dict[str, Any]]:
    """Load sample tickets from JSON file or return default data"""
    try:
        print("Loading from json file!")
        json_path = "data/sample_tickets.json"
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
    except Exception:
        pass

# Enhanced styling and layout
def apply_custom_styling():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Headers */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #4F46E5;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 0.5rem;
    }
    
    /* Stats cards */
    .stats-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .stat-card {
        flex: 1;
        min-width: 200px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Ticket cards */
    .ticket-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .ticket-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.1);
    }
    
    .ticket-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .ticket-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .ticket-id {
        background: #F3F4F6;
        color: #6B7280;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .ticket-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1F2937;
        margin: 0.5rem 0;
        line-height: 1.4;
    }
    
    .ticket-body {
        color: #6B7280;
        line-height: 1.6;
        margin: 1rem 0;
    }
    
    .ticket-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #F3F4F6;
    }
    
    /* Classification badges */
    .classification-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .classification-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 500;
        transition: transform 0.2s ease;
    }
    
    .classification-badge:hover {
        transform: scale(1.05);
    }
    
    .topic-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .sentiment-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .priority-badge {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    /* Response containers */
    .response-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .internal-analysis {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #f39c12;
    }
    
    .final-response {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #16a085;
    }
    
    .verbose-logs {
        background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #8e44ad;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.8;
    }
    
    /* Sources styling */
    .sources-container {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .source-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        text-decoration: none;
        color: inherit;
    }
    
    .source-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    .source-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    .source-content {
        flex: 1;
    }
    
    .source-title {
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 0.25rem;
    }
    
    .source-url {
        font-size: 0.8rem;
        color: #6B7280;
        word-break: break-all;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 1rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Text input styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Progress indicators */
    .processing-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Expandable sections */
    .stExpander {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .stExpander > div:first-child {
        background: #f8fafc;
    }
    
    /* Animation classes */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .stats-container {
            flex-direction: column;
        }
        
        .ticket-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        
        .classification-badges {
            flex-direction: column;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit application
def main():
    st.set_page_config(
        page_title="Atlan Helpdesk AI Assistant",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styling
    apply_custom_styling()
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Atlan Helpdesk AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #6B7280; margin-bottom: 3rem;">Intelligent ticket classification and automated response system</p>', unsafe_allow_html=True)
    
    # Initialize components (with caching to avoid reinitialization)
    @st.cache_resource
    def init_knowledge_base():
        return EnhancedAtlanKnowledgeBase()
    
    @st.cache_resource
    def init_classifier():
        return AtlanTicketClassifier()
    
    @st.cache_resource
    def init_rag_agent(_kb):
        return AtlanRAGAgent(_kb)
    
    # Initialize components with progress
    with st.spinner("🔄 Initializing AI components..."):
        kb = init_knowledge_base()
        classifier = init_classifier()
        rag_agent = init_rag_agent(kb)
    
    # Sidebar configuration
    st.sidebar.markdown("## ⚙️ Configuration")
    verbose_mode = st.sidebar.toggle("Verbose Logging", value=True, help="Show detailed processing logs")
    show_internal_analysis = st.sidebar.toggle("Show Internal Analysis", value=True, help="Display internal analysis details")
    auto_classify = st.sidebar.toggle("Auto-classify on Load", value=True, help="Automatically classify sample tickets")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Stats")
    st.sidebar.metric("Active Models", "2")
    st.sidebar.metric("Knowledge Base Sources", "150+")
    st.sidebar.metric("Classification Categories", "9")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["📋 Bulk Classification", "🤖 Interactive Agent", "📈 Analytics"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">📋 Bulk Ticket Classification Dashboard</h2>', unsafe_allow_html=True)
        
        # Load sample tickets
        sample_tickets = load_sample_tickets()
        
        # Stats display
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(sample_tickets)}</div>
                <div class="stat-label">Total Tickets</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Classification controls
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Classification Controls")
        with col2:
            if st.button("🔄 Re-classify All", key="reclassify"):
                if 'classified_tickets' in st.session_state:
                    del st.session_state.classified_tickets
                st.rerun()
        
        # Classify all tickets
        if auto_classify and ('classified_tickets' not in st.session_state):
            with st.spinner("🔍 Classifying tickets..."):
                classified_tickets = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, ticket in enumerate(sample_tickets):
                    status_text.text(f"Processing ticket {i+1}/{len(sample_tickets)}: {ticket['id']}")
                    
                    # Combine subject and body for classification
                    ticket_text = f"Subject: {ticket['subject']}\n\nBody: {ticket['body']}"
                    
                    if verbose_mode:
                        classification, logs = classifier.classify_ticket(ticket_text, verbose=True)
                        ticket_data = {
                            **ticket,
                            "classification": classification,
                            "verbose_logs": logs
                        }
                    else:
                        classification = classifier.classify_ticket(ticket_text, verbose=False)
                        ticket_data = {
                            **ticket,
                            "classification": classification
                        }
                    
                    classified_tickets.append(ticket_data)
                    progress_bar.progress((i + 1) / len(sample_tickets))
                
                st.session_state.classified_tickets = classified_tickets
                progress_bar.empty()
                status_text.empty()
                st.success("✅ All tickets classified successfully!")
        
        # Display classified tickets
        if 'classified_tickets' in st.session_state:
            for ticket in st.session_state.classified_tickets:
                with st.container():
                    st.markdown(f"""
                    <div class="ticket-card animate-fade-in-up">
                        <div class="ticket-header">
                            <div>
                                <div class="ticket-id">{ticket['id']}</div>
                                <div class="ticket-title">{ticket['subject']}</div>
                            </div>
                        </div>
                        <div class="ticket-body">{ticket['body'][:300]}{'...' if len(ticket['body']) > 300 else ''}</div>
                        <div class="classification-badges">
                            <div class="classification-badge topic-badge">
                                📚 Topics: {', '.join(ticket['classification']['topic_tags'])}
                            </div>
                            <div class="classification-badge sentiment-badge">
                                😊 Sentiment: {ticket['classification']['sentiment']}
                            </div>
                            <div class="classification-badge priority-badge">
                                ⚡ Priority: {ticket['classification']['priority']}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show verbose logs if enabled
                    if verbose_mode and 'verbose_logs' in ticket:
                        with st.expander(f"🔍 Verbose Logs - {ticket['id']}", expanded=False):
                            st.markdown('<div class="verbose-logs">', unsafe_allow_html=True)
                            for log in ticket['verbose_logs']:
                                st.markdown(log)
                            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h2 class="sub-header">🤖 Interactive AI Agent</h2>', unsafe_allow_html=True)
        
        # Input section
        st.markdown("### 📝 Submit New Ticket")
        new_ticket = st.text_area(
            "Describe your issue or question:",
            placeholder="Example: I'm having trouble connecting my Snowflake database to Atlan. The connection test fails with a permission error...",
            height=120,
            help="Provide as much detail as possible for better classification and response"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            submit_btn = st.button("🚀 Submit Ticket", type="primary", use_container_width=True)
        with col2:
            priority_urgent = st.button("⚡ Mark Urgent", use_container_width=True)
        with col3:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_btn:
            st.session_state.current_response = None
            st.session_state.current_ticket = None
            st.session_state.current_classification = None
            st.rerun()
        
        if submit_btn or priority_urgent:
            if new_ticket:
                with st.spinner("🔄 Processing your ticket..."):
                    # Create progress indicators
                    progress_container = st.empty()
                    progress_container.markdown("""
                    <div class="processing-indicator">
                        <div style="margin-right: 1rem;">🔍</div>
                        <div>Analyzing your ticket...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Classify the ticket
                    if verbose_mode:
                        classification, class_logs = classifier.classify_ticket(new_ticket, verbose=True)
                    else:
                        classification = classifier.classify_ticket(new_ticket, verbose=False)
                        class_logs = []
                    
                    # Override priority if urgent button was clicked
                    if priority_urgent:
                        classification['priority'] = 'P0 (High)'
                    
                    progress_container.markdown("""
                    <div class="processing-indicator">
                        <div style="margin-right: 1rem;">🤖</div>
                        <div>Generating intelligent response...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Generate response
                    response = rag_agent.generate_response(new_ticket, classification, verbose=verbose_mode)
                    
                    # Store in session state
                    st.session_state.current_response = response
                    st.session_state.current_ticket = new_ticket
                    st.session_state.current_classification = classification
                    st.session_state.classification_logs = class_logs
                    
                    progress_container.empty()
                    st.success("✅ Ticket processed successfully!")
            else:
                st.warning("⚠️ Please enter a ticket description before submitting.")
        
        # Display results if available
        if 'current_response' in st.session_state:
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")
            
            # Processing time and stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Processing Time", f"{st.session_state.current_response.get('processing_time', 0):.2f}s")
            with col2:
                st.metric("Response Type", st.session_state.current_response["final_response"]["type"])
            with col3:
                sources_count = len(st.session_state.current_response["final_response"].get("sources", []))
                st.metric("Sources Found", sources_count)
            with col4:
                priority = st.session_state.current_classification["priority"]
                st.metric("Priority", priority)
            
            # Classification results
            st.markdown("### 🏷️ Classification Results")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="classification-badge topic-badge" style="width: 100%; text-align: center; padding: 1rem;">
                    <strong>📚 Topics</strong><br>
                    {', '.join(st.session_state.current_classification['topic_tags'])}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                sentiment_emoji = {
                    'Frustrated': '😤',
                    'Curious': '🤔',
                    'Angry': '😠',
                    'Neutral': '😐'
                }.get(st.session_state.current_classification['sentiment'], '😐')
                
                st.markdown(f"""
                <div class="classification-badge sentiment-badge" style="width: 100%; text-align: center; padding: 1rem;">
                    <strong>{sentiment_emoji} Sentiment</strong><br>
                    {st.session_state.current_classification['sentiment']}
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                priority_emoji = {
                    'P0 (High)': '🔴',
                    'P1 (Medium)': '🟡',
                    'P2 (Low)': '🟢'
                }.get(st.session_state.current_classification['priority'], '🟡')
                
                st.markdown(f"""
                <div class="classification-badge priority-badge" style="width: 100%; text-align: center; padding: 1rem;">
                    <strong>{priority_emoji} Priority</strong><br>
                    {st.session_state.current_classification['priority']}
                </div>
                """, unsafe_allow_html=True)
            
            # Show classification verbose logs if enabled
            if verbose_mode and 'classification_logs' in st.session_state and st.session_state.classification_logs:
                with st.expander("🔍 Classification Verbose Logs", expanded=False):
                    st.markdown('<div class="verbose-logs">', unsafe_allow_html=True)
                    for log in st.session_state.classification_logs:
                        st.markdown(log)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Internal analysis view
            if show_internal_analysis:
                st.markdown("### 🔧 Internal Analysis")
                st.markdown('<div class="internal-analysis">', unsafe_allow_html=True)
                st.json(st.session_state.current_response["internal_analysis"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            # RAG verbose logs
            if verbose_mode and 'verbose_logs' in st.session_state.current_response:
                with st.expander("🤖 RAG Agent Verbose Logs", expanded=True):
                    st.markdown('<div class="verbose-logs">', unsafe_allow_html=True)
                    for log in st.session_state.current_response["verbose_logs"]:
                        st.markdown(log)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Final response view
            st.markdown("### 💬 AI Response")
            st.markdown('<div class="final-response">', unsafe_allow_html=True)
            
            # Response text with better formatting
            response_text = st.session_state.current_response["final_response"]["answer"]
            st.markdown(f"**Response:** {response_text}")
            
            # Display category used if available
            category_used = st.session_state.current_response["final_response"].get("category_used")
            if category_used:
                st.markdown(f"**📚 Knowledge Base Category:** `{category_used}`")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display sources with enhanced styling
            sources = st.session_state.current_response["final_response"].get("sources", [])
            if sources:
                st.markdown("### 📖 Sources & References")
                st.markdown('<div class="sources-container">', unsafe_allow_html=True)
                
                for i, source in enumerate(sources):
                    # Extract domain from URL for display
                    try:
                        domain = urlparse(source.get('url', '')).netloc or 'Unknown Source'
                    except:
                        domain = 'Unknown Source'
                    
                    st.markdown(f"""
                    <div class="source-item">
                        <div class="source-icon">{i+1}</div>
                        <div class="source-content">
                            <div class="source-title">{source.get('title', 'Untitled Document')}</div>
                            <div class="source-url">
                                🌐 {domain} • 
                                <a href="{source.get('url', '#')}" target="_blank" style="color: #667eea; text-decoration: none;">
                                    View Source ↗
                                </a>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("### 🎯 Next Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("👍 Helpful", use_container_width=True):
                    st.success("Thank you for your feedback! 🎉")
            
            with col2:
                if st.button("👎 Not Helpful", use_container_width=True):
                    st.info("We'll improve our responses. Thank you for the feedback! 📝")
            
            with col3:
                if st.button("📧 Email Response", use_container_width=True):
                    st.info("Response would be emailed to ticket submitter 📨")
            
            with col4:
                if st.button("🔄 Escalate", use_container_width=True):
                    st.warning("Ticket escalated to human agent 👨‍💻")
    
    with tab3:
        st.markdown('<h2 class="sub-header">📈 Advanced Analytics Dashboard</h2>', unsafe_allow_html=True)
        
        if 'classified_tickets' in st.session_state:
            tickets = st.session_state.classified_tickets
            
            # Generate analytics
            trends = analytics_service.generate_topic_trends(tickets)
            satisfaction = analytics_service.calculate_satisfaction_metrics(tickets)
            workload = analytics_service.generate_workload_distribution(tickets)
            performance = analytics_service.generate_performance_metrics(tickets)
            
            # Key Metrics Overview
            st.markdown("### 🎯 Key Performance Indicators")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px;">
                    <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{performance['total_processed']}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Total Tickets</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 12px;">
                    <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{satisfaction['nps_score']}%</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">NPS Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 12px;">
                    <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{performance['auto_resolution_rate_percent']}%</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Auto-Resolution</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; border-radius: 12px;">
                    <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{performance['avg_processing_time_seconds']}s</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Avg Process Time</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; border-radius: 12px;">
                    <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{performance['efficiency_score']}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Efficiency Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Advanced Analytics Sections
            col1, col2 = st.columns(2)
            
            with col1:
                # Topic Trends
                st.markdown("### 📚 Topic Analysis")
                st.markdown('<div class="analytics-container">', unsafe_allow_html=True)
                
                for topic, count in list(trends['topic_frequency'].items())[:7]:
                    percentage = (count / len(tickets)) * 100
                    st.markdown(f"""
                    <div style="margin: 1rem 0; padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: 500; color: #333;">{topic}</span>
                            <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.8rem;">
                                {count} tickets
                            </span>
                        </div>
                        <div style="background: #f0f0f0; border-radius: 8px; height: 8px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: {percentage}%; border-radius: 8px; transition: width 0.5s ease;"></div>
                        </div>
                        <div style="font-size: 0.8rem; color: #666; margin-top: 0.3rem;">{percentage:.1f}% of total volume</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                # Sentiment Deep Dive
                st.markdown("### 😊 Sentiment Analysis")
                
                sentiment_colors = {
                    'Frustrated': '#ff6b6b',
                    'Curious': '#4facfe',
                    'Angry': '#e55555',
                    'Neutral': '#95a5a6'
                }
                
                for sentiment, count in satisfaction['satisfaction_distribution'].items():
                    percentage = (count / len(tickets)) * 100
                    color = sentiment_colors.get(sentiment, '#95a5a6')
                    emoji = {'Frustrated': '😤', 'Curious': '🤔', 'Angry': '😠', 'Neutral': '😐'}.get(sentiment, '😐')
                    
                    st.markdown(f"""
                    <div style="margin: 1rem 0; padding: 1.2rem; background: white; border-radius: 12px; border-left: 5px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{emoji}</span>
                                <span style="font-weight: 600; color: #333;">{sentiment}</span>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.3rem; font-weight: bold; color: {color};">{count}</div>
                                <div style="font-size: 0.8rem; color: #666;">{percentage:.1f}%</div>
                            </div>
                        </div>
                        <div style="margin-top: 0.8rem; background: #f8f9fa; border-radius: 6px; height: 6px; overflow: hidden;">
                            <div style="background: {color}; height: 100%; width: {percentage}%; border-radius: 6px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Performance Metrics
                st.markdown("### 🎯 AI Performance")
                st.markdown(f"""
                <div style="padding: 1.5rem; background: linear-gradient(135deg, #d1f2eb 0%, #a3e4d7 100%); border-radius: 12px; margin: 1rem 0;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.8rem; font-weight: bold; color: #16a085;">{performance['avg_classification_confidence']:.1%}</div>
                            <div style="color: #2c3e50; font-size: 0.9rem;">Classification Accuracy</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.8rem; font-weight: bold; color: #16a085;">{performance['efficiency_score']}</div>
                            <div style="color: #2c3e50; font-size: 0.9rem;">Overall Efficiency</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 4rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 16px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                <h3 style="color: #495057; margin-bottom: 1rem;">Analytics Dashboard</h3>
                <p style="color: #6c757d; font-size: 1.1rem; max-width: 500px; margin: 0 auto;">
                    Advanced analytics will appear after tickets are classified. Visit the 'Bulk Classification' tab to get started!
                </p>
                <div style="margin-top: 2rem;">
                    <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.8rem 2rem; border-radius: 25px; font-weight: 500; text-decoration: none; display: inline-block;">
                        ⚡ Start Classification
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    with tab4:
        st.markdown('<h2 class="sub-header">🔧 System Monitoring</h2>', unsafe_allow_html=True)
        
        # System Health Overview
        health_status = monitor.get_health_status()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_color = {
                'healthy': '#48dbfb',
                'warning': '#feca57',
                'critical': '#ff6b6b'
            }.get(health_status['status'], '#95a5a6')
            
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: {status_color}; color: white; border-radius: 12px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{'🟢' if health_status['status'] == 'healthy' else '🟡' if health_status['status'] == 'warning' else '🔴'}</div>
                <div style="font-size: 1.2rem; font-weight: bold;">System Status</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">{health_status['status'].title()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Health Score", f"{health_status['health_score']}/100")
        
        with col3:
            st.metric("Uptime", health_status['uptime'])
        
        with col4:
            st.metric("Active Issues", len(health_status['issues']))
        
        # System Metrics
        system_metrics = monitor.get_system_metrics()
        app_metrics = monitor.get_application_metrics()
        
        if 'error' not in system_metrics:
            st.markdown("### 📊 Real-time Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### System Resources")
                
                # CPU Usage
                cpu_color = '#ff6b6b' if system_metrics['cpu_percent'] > 80 else '#feca57' if system_metrics['cpu_percent'] > 60 else '#48dbfb'
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>CPU Usage</span>
                        <span>{system_metrics['cpu_percent']:.1f}%</span>
                    </div>
                    <div style="background: #e0e0e0; border-radius: 10px; height: 10px;">
                        <div style="background: {cpu_color}; width: {system_metrics['cpu_percent']}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Memory Usage
                mem_color = '#ff6b6b' if system_metrics['memory_percent'] > 80 else '#feca57' if system_metrics['memory_percent'] > 60 else '#48dbfb'
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Memory Usage</span>
                        <span>{system_metrics['memory_percent']:.1f}%</span>
                    </div>
                    <div style="background: #e0e0e0; border-radius: 10px; height: 10px;">
                        <div style="background: {mem_color}; width: {system_metrics['memory_percent']}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.metric("Available Memory", f"{system_metrics['memory_available_gb']} GB")
                st.metric("Disk Usage", f"{system_metrics['disk_usage_percent']:.1f}%")
            
            with col2:
                st.markdown("#### Application Performance")
                st.metric("Total Requests", app_metrics['total_requests'])
                st.metric("Avg Response Time", f"{app_metrics['avg_response_time']}s")
                st.metric("Error Rate", f"{app_metrics['error_rate']}%")
                st.metric("Cache Hit Rate", f"{app_metrics['cache_hit_rate']*100:.1f}%")
        
        # Recent Alerts
        recent_alerts = monitor.get_recent_alerts(5)
        if recent_alerts:
            st.markdown("### 🚨 Recent Alerts")
            for alert in recent_alerts:
                alert_color = {
                    'critical': '#ff6b6b',
                    'warning': '#feca57',
                    'info': '#48dbfb'
                }.get(alert['type'], '#95a5a6')
                
                st.markdown(f"""
                <div style="padding: 1rem; margin: 0.5rem 0; background: {alert_color}20; border-left: 4px solid {alert_color}; border-radius: 8px;">
                    <div style="font-weight: bold; color: {alert_color};">{alert['title']}</div>
                    <div style="color: #666; margin-top: 0.25rem;">{alert['message']}</div>
                    <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">{alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Performance Report
        with st.expander("📈 Performance Report", expanded=False):
            performance_report = monitor.generate_performance_report()
            if 'message' not in performance_report:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Requests", performance_report['total_requests'])
                    st.metric("Success Rate", f"{performance_report['success_rate']}%")
                    st.metric("Avg Response Time", f"{performance_report['avg_response_time']}s")
                
                with col2:
                    st.metric("Min Response Time", f"{performance_report['min_response_time']}s")
                    st.metric("Max Response Time", f"{performance_report['max_response_time']}s")
                
                if performance_report['endpoint_statistics']:
                    st.markdown("#### Endpoint Statistics")
                    for endpoint, stats in performance_report['endpoint_statistics'].items():
                        st.markdown(f"**{endpoint}**: {stats['request_count']} requests, {stats['avg_response_time']}s avg, {stats['error_rate']}% error rate")
            else:
                st.info(performance_report['message'])
        
        # Clear alerts button
        if st.button("🗑️ Clear All Alerts"):
            monitor.clear_alerts()
            st.success("All alerts cleared!")
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎯 <strong>Atlan AI Helpdesk System</strong> - Powered by Enhanced RAG & LangChain Agents</p>
        <p><em>Real-time verbose processing • Intelligent classification • Source-cited responses</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


# #improve below abhi




# import streamlit as st
# import json
# import os
# from datetime import datetime
# from typing import Dict, List, Any
# import time
# import traceback
# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd
# import numpy as np

# # Import our custom modules
# from services.knowledge_base import EnhancedAtlanKnowledgeBase
# from services.ticket_classifier import TicketClassifier, AtlanRAGAgent

# # Set page config
# st.set_page_config(
#     page_title="Atlan AI Helpdesk System",
#     page_icon="🎯",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Enhanced CSS styling
# st.markdown("""
# <style>
#     :root {
#         --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#         --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
#         --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
#         --info-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
#         --dark-bg: #1a1a2e;
#         --card-bg: #ffffff;
#         --text-dark: #2d3436;
#         --text-light: #636e72;
#         --shadow: 0 10px 30px rgba(0,0,0,0.1);
#         --radius: 16px;
#     }
    
#     .stApp {
#         background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
#     }
    
#     .main > div {
#         background: var(--card-bg);
#         border-radius: var(--radius);
#         margin: 1rem;
#         padding: 2rem;
#         box-shadow: var(--shadow);
#     }
    
#     .main-header {
#         background: var(--primary-gradient);
#         padding: 2.5rem;
#         border-radius: var(--radius);
#         color: white;
#         text-align: center;
#         margin-bottom: 2rem;
#         box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
#         position: relative;
#         overflow: hidden;
#     }
    
#     .main-header::before {
#         content: '';
#         position: absolute;
#         top: -50%;
#         left: -50%;
#         width: 200%;
#         height: 200%;
#         background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
#         transform: rotate(30deg);
#     }
    
#     .main-header h1 {
#         margin: 0 0 0.5rem 0;
#         font-size: 2.8rem;
#         font-weight: 800;
#         position: relative;
#         z-index: 2;
#     }
    
#     .main-header p {
#         font-size: 1.2rem;
#         opacity: 0.9;
#         position: relative;
#         z-index: 2;
#     }
    
#     .ticket-card {
#         background: linear-gradient(145deg, #f8f9ff, #f1f3ff);
#         padding: 1.8rem;
#         border-radius: 12px;
#         border-left: 5px solid #667eea;
#         margin-bottom: 1.2rem;
#         transition: all 0.3s ease;
#         box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
#     }
    
#     .ticket-card:hover {
#         transform: translateY(-5px);
#         box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
#     }
    
#     .classification-row {
#         display: flex;
#         flex-wrap: wrap;
#         gap: 0.75rem;
#         margin: 1rem 0;
#     }
    
#     .classification-tag {
#         padding: 0.6rem 1.2rem;
#         border-radius: 25px;
#         font-size: 0.85rem;
#         font-weight: 600;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#         color: white;
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#     }
    
#     .tag-topic { background: var(--primary-gradient); }
#     .tag-frustrated { background: var(--secondary-gradient); }
#     .tag-angry { background: linear-gradient(135deg, #ff8a80, #ff5722); }
#     .tag-curious { background: var(--success-gradient); }
#     .tag-neutral { background: linear-gradient(135deg, #9c27b0, #673ab7); }
#     .tag-satisfied { background: linear-gradient(135deg, #66bb6a, #43a047); }
#     .tag-high { background: linear-gradient(135deg, #f44336, #d32f2f); }
#     .tag-medium { background: linear-gradient(135deg, #ff9800, #f57c00); }
#     .tag-low { background: linear-gradient(135deg, #4caf50, #388e3c); }
    
#     .response-section {
#         background: linear-gradient(145deg, #e8f5e8, #f1f8e9);
#         padding: 1.8rem;
#         border-radius: 12px;
#         border: 2px solid #4caf50;
#         margin: 1.2rem 0;
#         box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);
#     }
    
#     .analysis-section {
#         background: linear-gradient(145deg, #e3f2fd, #f3f9ff);
#         padding: 1.8rem;
#         border-radius: 12px;
#         border: 2px solid #2196f3;
#         margin: 1.2rem 0;
#         box-shadow: 0 4px 15px rgba(33, 150, 243, 0.1);
#     }
    
#     .confidence-indicator {
#         display: inline-flex;
#         align-items: center;
#         padding: 0.6rem 1.2rem;
#         border-radius: 25px;
#         font-weight: 600;
#         margin-left: 1rem;
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#     }
    
#     .confidence-high { background: #d4edda; color: #155724; }
#     .confidence-medium { background: #fff3cd; color: #856404; }
#     .confidence-low { background: #f8d7da; color: #721c24; }
    
#     .metric-card {
#         background: white;
#         padding: 1.8rem;
#         border-radius: var(--radius);
#         text-align: center;
#         box-shadow: 0 8px 20px rgba(0,0,0,0.08);
#         border-top: 5px solid #667eea;
#         transition: all 0.3s ease;
#         height: 100%;
#     }
    
#     .metric-card:hover {
#         transform: translateY(-5px);
#         box-shadow: 0 15px 30px rgba(0,0,0,0.12);
#     }
    
#     .metric-value {
#         font-size: 2.5rem;
#         font-weight: 800;
#         color: #667eea;
#         margin: 0;
#         text-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
    
#     .metric-label {
#         font-size: 0.95rem;
#         color: var(--text-light);
#         margin-top: 0.5rem;
#         font-weight: 500;
#     }
    
#     .source-card {
#         background: linear-gradient(145deg, #fff8f0, #fff4e6);
#         padding: 1.2rem;
#         border-radius: 10px;
#         border-left: 4px solid #ff9800;
#         margin: 0.8rem 0;
#         box-shadow: 0 4px 10px rgba(255, 152, 0, 0.1);
#         transition: all 0.3s ease;
#     }
    
#     .source-card:hover {
#         transform: translateX(5px);
#         box-shadow: 0 8px 20px rgba(255, 152, 0, 0.15);
#     }
    
#     .status-indicator {
#         display: inline-flex;
#         align-items: center;
#         padding: 0.4rem 1rem;
#         border-radius: 20px;
#         font-size: 0.85rem;
#         font-weight: 600;
#         margin: 0.3rem 0;
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#     }
    
#     .status-ready { background: #d4edda; color: #155724; }
#     .status-error { background: #f8d7da; color: #721c24; }
#     .status-warning { background: #fff3cd; color: #856404; }
    
#     .analytics-container {
#         background: white;
#         border-radius: var(--radius);
#         padding: 1.5rem;
#         margin: 1rem 0;
#         box-shadow: var(--shadow);
#     }
    
#     .sub-header {
#         font-size: 1.8rem;
#         font-weight: 700;
#         color: var(--text-dark);
#         margin-bottom: 1.5rem;
#         padding-bottom: 0.5rem;
#         border-bottom: 3px solid #667eea;
#         display: inline-block;
#     }
    
#     .chart-container {
#         background: white;
#         border-radius: var(--radius);
#         padding: 1.5rem;
#         margin: 1rem 0;
#         box-shadow: var(--shadow);
#     }
    
#     .empty-state {
#         text-align: center;
#         padding: 4rem;
#         background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
#         border-radius: var(--radius);
#         margin: 2rem 0;
#         box-shadow: var(--shadow);
#     }
    
#     .empty-state-icon {
#         font-size: 5rem;
#         margin-bottom: 1.5rem;
#         opacity: 0.7;
#     }
    
#     .cta-button {
#         background: var(--primary-gradient);
#         color: white;
#         padding: 1rem 2.5rem;
#         border-radius: 30px;
#         font-weight: 600;
#         text-decoration: none;
#         display: inline-block;
#         margin-top: 1.5rem;
#         box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
#         transition: all 0.3s ease;
#         border: none;
#         cursor: pointer;
#     }
    
#     .cta-button:hover {
#         transform: translateY(-3px);
#         box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
#         color: white;
#     }
    
#     .progress-bar {
#         height: 10px;
#         border-radius: 5px;
#         background: #f0f0f0;
#         overflow: hidden;
#         margin: 0.5rem 0;
#     }
    
#     .progress-fill {
#         height: 100%;
#         border-radius: 5px;
#         transition: width 0.5s ease;
#     }
    
#     .sentiment-card {
#         padding: 1.5rem;
#         border-radius: 12px;
#         margin: 1rem 0;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.08);
#         border-left: 5px solid;
#         transition: all 0.3s ease;
#     }
    
#     .sentiment-card:hover {
#         transform: translateY(-3px);
#         box-shadow: 0 8px 25px rgba(0,0,0,0.12);
#     }
# </style>
# """, unsafe_allow_html=True)

# # Analytics service (mock implementation)
# class AnalyticsService:
#     def generate_topic_trends(self, tickets):
#         topics = {}
#         for ticket in tickets:
#             topic = ticket['classification']['topic']
#             topics[topic] = topics.get(topic, 0) + 1
        
#         return {
#             'topic_frequency': dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)),
#             'total_tickets': len(tickets)
#         }
    
#     def calculate_satisfaction_metrics(self, tickets):
#         sentiments = {}
#         for ticket in tickets:
#             sentiment = ticket['classification']['sentiment']
#             sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
#         nps_score = 75  # Mock NPS calculation
#         return {
#             'satisfaction_distribution': sentiments,
#             'nps_score': nps_score
#         }
    
#     def generate_workload_distribution(self, tickets):
#         # Mock workload distribution
#         return {
#             'by_priority': {'High': 25, 'Medium': 50, 'Low': 25},
#             'by_complexity': {'Simple': 40, 'Moderate': 45, 'Complex': 15}
#         }
    
#     def generate_performance_metrics(self, tickets):
#         # Mock performance metrics
#         return {
#             'total_processed': len(tickets),
#             'auto_resolution_rate_percent': 65,
#             'avg_processing_time_seconds': 124,
#             'avg_classification_confidence': 0.87,
#             'efficiency_score': 8.7
#         }

# analytics_service = AnalyticsService()

# def load_sample_tickets() -> List[Dict[str, Any]]:
#     """Load sample tickets from JSON file or return default data"""
#     try:
#         json_path = "data/sample_tickets.json"
#         if os.path.exists(json_path):
#             with open(json_path, 'r') as f:
#                 return json.load(f)
#     except Exception:
#         pass

#     return [
#         {
#             "id": "TICKET-245",
#             "subject": "Connecting Snowflake to Atlan - required permissions?",
#             "body": "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing. We've tried using our standard service account, but it's not working. Our entire BI team is blocked on this integration for a major upcoming project, so it's quite urgent. Could you please provide a definitive list of the exact permissions and credentials needed on the Snowflake side to get this working? Thanks."
#         },
#         {
#             "id": "TICKET-246", 
#             "subject": "Data lineage not showing downstream impacts",
#             "body": "Our data lineage view isn't capturing all the downstream transformations in our dbt models. We have a complex data pipeline and need to understand the full impact of changes. Can you help us troubleshoot why some lineage connections are missing?"
#         },
#         {
#             "id": "TICKET-247",
#             "subject": "API authentication failing with 401 errors", 
#             "body": "I'm trying to use the Atlan Python SDK to automate some metadata updates, but I keep getting 401 authentication errors. I've double-checked my API token. What could be wrong?"
#         },
#         {
#             "id": "TICKET-248",
#             "subject": "How to implement SSO with Okta?",
#             "body": "We need to set up Single Sign-On integration with our Okta identity provider. What are the configuration steps and requirements for SAML SSO setup in Atlan?"
#         },
#         {
#             "id": "TICKET-249",
#             "subject": "Best practices for data governance policies",
#             "body": "We're looking for recommendations on how to structure our data governance framework in Atlan. What are the best practices for setting up policies, classifications, and ownership?"
#         }
#     ]

# def initialize_session_state():
#     """Initialize all session state variables"""
    
#     if 'sample_tickets' not in st.session_state:
#         st.session_state.sample_tickets = load_sample_tickets()
    
#     if 'knowledge_base' not in st.session_state:
#         st.session_state.knowledge_base = None
#         st.session_state.kb_status = "initializing"
        
#         with st.spinner("Initializing Atlan Knowledge Base..."):
#             try:
#                 st.session_state.knowledge_base = EnhancedAtlanKnowledgeBase()
#                 st.session_state.kb_status = "ready"
#                 st.success("Knowledge Base initialized successfully!")
#             except Exception as e:
#                 st.error(f"Failed to initialize Knowledge Base: {str(e)}")
#                 st.session_state.kb_status = "error"
#                 if "429" in str(e):
#                     st.info("Rate limit detected. Please wait and refresh the page.")
    
#     if 'classifier' not in st.session_state:
#         if st.session_state.knowledge_base and st.session_state.kb_status == "ready":
#             try:
#                 st.session_state.classifier = TicketClassifier()
#                 st.session_state.classifier_status = "ready"
#             except Exception as e:
#                 st.session_state.classifier_status = "error"
#                 st.session_state.classifier = None
#         else:
#             st.session_state.classifier_status = "waiting"
#             st.session_state.classifier = None
    
#     if 'rag_agent' not in st.session_state:
#         if st.session_state.knowledge_base and st.session_state.kb_status == "ready":
#             try:
#                 st.session_state.rag_agent = AtlanRAGAgent(st.session_state.knowledge_base)
#                 st.session_state.agent_status = "ready"
#             except Exception as e:
#                 st.session_state.agent_status = "error"
#                 st.session_state.rag_agent = None
#         else:
#             st.session_state.agent_status = "waiting"
#             st.session_state.rag_agent = None

# def render_header():
#     """Render the main header"""
#     st.markdown("""
#     <div class="main-header">
#         <h1>Atlan AI Helpdesk System</h1>
#         <p>Intelligent ticket classification with RAG-powered responses</p>
#     </div>
#     """, unsafe_allow_html=True)

# def get_confidence_class(confidence: float) -> str:
#     """Get CSS class for confidence level"""
#     if confidence >= 0.8:
#         return "confidence-high"
#     elif confidence >= 0.5:
#         return "confidence-medium"
#     else:
#         return "confidence-low"

# def render_classification_tags(classification: Dict[str, Any]) -> str:
#     """Render classification tags with proper styling"""
#     topic = classification.get('topic', 'unknown')
#     sentiment = classification.get('sentiment', 'neutral').lower()
#     priority = classification.get('priority', 'medium').lower().replace(' ', '').replace('(', '').replace(')', '')
    
#     return f"""
#     <div class="classification-row">
#         <span class="classification-tag tag-topic">{topic}</span>
#         <span class="classification-tag tag-{sentiment}">{classification.get('sentiment', 'Neutral')}</span>
#         <span class="classification-tag tag-{priority}">{classification.get('priority', 'Medium')}</span>
#     </div>
#     """

# def render_bulk_classification():
#     """Render bulk ticket classification dashboard"""
#     st.header("Bulk Ticket Classification Dashboard")
    
#     if not st.session_state.classifier or st.session_state.classifier_status != "ready":
#         st.error("Classifier not available - please check system status")
#         return
    
#     col1, col2 = st.columns([3, 1])
    
#     with col1:
#         if st.button("Classify All Tickets", type="primary", use_container_width=True):
#             classify_all_tickets()
    
#     with col2:
#         if st.button("Clear Results", use_container_width=True):
#             if 'classified_tickets' in st.session_state:
#                 del st.session_state.classified_tickets
#             st.rerun()
    
#     if hasattr(st.session_state, 'classified_tickets'):
#         st.subheader(f"Classification Results ({len(st.session_state.classified_tickets)} tickets)")
        
#         for ticket in st.session_state.classified_tickets:
#             st.markdown(f"""
#             <div class="ticket-card">
#                 <h4>{ticket['id']}: {ticket['subject']}</h4>
#                 <p><strong>Description:</strong> {ticket['body'][:200]}{'...' if len(ticket['body']) > 200 else ''}</p>
#                 {render_classification_tags(ticket['classification'])}
#                 <p><em><strong>Reasoning:</strong> {ticket['classification']['reasoning']}</em></p>
#                 <small>Classified at: {ticket['classified_at']}</small>
#             </div>
#             """, unsafe_allow_html=True)

# def classify_all_tickets():
#     """Classify all tickets with rate limiting"""
#     st.session_state.classified_tickets = []
#     progress_bar = st.progress(0)
#     status_text = st.empty()
    
#     for i, ticket in enumerate(st.session_state.sample_tickets):
#         status_text.text(f'Classifying ticket {i+1}/{len(st.session_state.sample_tickets)}: {ticket["subject"]}')
        
#         try:
#             if i > 0:
#                 time.sleep(2)
                
#             ticket_text = f"Subject: {ticket['subject']}\nBody: {ticket['body']}"
#             classification = st.session_state.classifier.classify_ticket(ticket_text)
            
#             classified_ticket = {
#                 **ticket,
#                 "classification": classification,
#                 "classified_at": datetime.now().isoformat()
#             }
#             st.session_state.classified_tickets.append(classified_ticket)
            
#         except Exception as e:
#             st.error(f"Error classifying ticket {ticket['id']}: {str(e)}")
#             if "429" in str(e):
#                 st.warning("Rate limit hit - please wait before retrying")
#                 break
        
#         progress_bar.progress((i + 1) / len(st.session_state.sample_tickets))
    
#     status_text.text('Classification completed!')
#     time.sleep(1)
#     status_text.empty()
#     progress_bar.empty()

# def render_interactive_agent():
#     """Render interactive AI agent interface"""
#     st.header("Interactive AI Agent with RAG System")
    
#     if not all([
#         st.session_state.classifier and st.session_state.classifier_status == "ready",
#         st.session_state.rag_agent and st.session_state.agent_status == "ready",
#         st.session_state.knowledge_base and st.session_state.kb_status == "ready"
#     ]):
#         st.error("AI Agent not available - System initialization incomplete")
#         return
    
#     with st.form("query_form", clear_on_submit=False):
#         user_query = st.text_area(
#             "Submit your question or support ticket:",
#             placeholder="e.g., How do I set up SSO with Okta in Atlan?\ne.g., What permissions are needed for Snowflake connector?",
#             height=120
#         )
        
#         col1, col2 = st.columns([3, 1])
#         with col1:
#             submit_button = st.form_submit_button("Process Query", type="primary", use_container_width=True)
#         with col2:
#             clear_button = st.form_submit_button("Clear", use_container_width=True)
    
#     if submit_button and user_query.strip():
#         st.markdown("---")
        
#         # Step 1: Classification
#         st.markdown("### Analysis")
#         with st.spinner("Analyzing query..."):
#             try:
#                 classification = st.session_state.classifier.classify_ticket(user_query)
                
#                 st.markdown(f"""
#                 <div class="analysis-section">
#                     <h4>Classification Results:</h4>
#                     {render_classification_tags(classification)}
#                     <p><strong>AI Reasoning:</strong> {classification['reasoning']}</p>
#                 </div>
#                 """, unsafe_allow_html=True)
                
#             except Exception as e:
#                 st.error(f"Classification error: {str(e)}")
#                 return
        
#         # Step 2: Generate RAG response using existing knowledge base method
#         st.markdown("### AI Response")
        
#         with st.spinner("Generating intelligent response using RAG system..."):
#             try:
#                 # Use existing generate_rag_response method from knowledge base
#                 rag_response = st.session_state.knowledge_base.generate_rag_response(
#                     user_query,
#                     limit=3
#                 )
                
#                 # Get confidence from the response
#                 confidence = rag_response.get('confidence', 0.0)
#                 confidence_class = get_confidence_class(confidence)
                
#                 # Generate agent response with RAG context
#                 response_data = st.session_state.rag_agent.generate_response(
#                     user_query, 
#                     classification
#                 )
                
#                 # Display response with confidence
#                 st.markdown(f"""
#                 <div class="response-section">
#                     <h4>Generated Response
#                         <span class="confidence-indicator {confidence_class}">
#                             Confidence: {confidence:.1%}
#                         </span>
#                     </h4>
#                     <div style="white-space: pre-wrap;">{rag_response.get('answer', 'No response generated')}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
                
#                 # Display sources if available
#                 if rag_response.get('sources'):
#                     st.markdown("### Sources")
#                     for i, source in enumerate(rag_response['sources'], 1):
#                         st.markdown(f"""
#                         <div class="source-card">
#                             <strong>{i}. {source['title']}</strong><br>
#                             <a href="{source['url']}" target="_blank">{source['url']}</a><br>
#                             <small>Category: {source['category']} / {source['subcategory']} | Tags: {', '.join(source['tags'])}</small>
#                         </div>
#                         """, unsafe_allow_html=True)
                
#             except Exception as e:
#                 st.error(f"Error generating response: {str(e)}")
#                 if "429" in str(e):
#                     st.info("Rate limit detected. Please wait before trying again.")

# import streamlit as st

# def render_knowledge_base_info():
#     """Render knowledge base information and testing interface"""
#     st.header("📚 Knowledge Base Information & Testing")

#     if not st.session_state.knowledge_base or st.session_state.kb_status != "ready":
#         st.error("Knowledge Base not available")
#         return

#     # Stats section
#     with st.spinner("Loading knowledge base statistics..."):
#         try:
#             stats = st.session_state.knowledge_base.get_knowledge_base_stats()

#             if "error" not in stats:
#                 st.markdown("### 📊 Knowledge Base Stats")

#                 col1, col2 = st.columns(2)


#                 with col1:
#                     st.markdown(f"""
#                     <div class="metric-card">
#                         <div class="metric-value">{len(stats['source_types'])}</div>
#                         <p class="metric-label">Source Types</p>
#                     </div>
#                     """, unsafe_allow_html=True)

#                 with col2:
#                     st.markdown(f"""
#                     <div class="metric-card success">
#                         <div class="metric-value">✓</div>
#                         <p class="metric-label">Status</p>
#                     </div>
#                     """, unsafe_allow_html=True)

#                 # Breakdown of source types
#                 st.markdown("#### 🔎 Source Type Breakdown")
#                 for source_type, count in stats['source_types'].items():
#                     st.write(f"- **{source_type}**: {count:,} chunks")

#             else:
#                 st.error(f"Error loading stats: {stats['error']}")

#         except Exception as e:
#             st.error(f"Error displaying knowledge base info: {str(e)}")

#     st.markdown("---")

#     # Testing interface
#     st.subheader("🧪 Test Knowledge Base Search")

#     col1, col2 = st.columns([3, 1])

#     with col1:
#         test_query = st.text_input(
#             "Enter a test query:",
#             placeholder="e.g., How to authenticate with Atlan API?"
#         )

#     with col2:
#         category_filter = st.selectbox(
#             "Category Filter:",
#             ["None", "product_documentation", "developer_hub"],
#             index=0
#         )

#     if st.button("🔍 Search Knowledge Base", type="primary", use_container_width=True) and test_query:
#         with st.spinner("Searching knowledge base..."):
#             try:
#                 filter_category = None if category_filter == "None" else category_filter

#                 results = st.session_state.knowledge_base.search_knowledge_base(
#                     test_query,
#                     limit=5,
#                     category_filter=filter_category
#                 )

#                 if results:
#                     st.success(f"Found {len(results)} results")

#                     for i, result in enumerate(results, 1):
#                         with st.expander(f"Result {i} • Similarity Score: {result.score:.3f}"):
#                             payload = result.payload

#                             st.markdown(f"""
#                             **📌 Title:** {payload['title']}  
#                             **🔗 URL:** [{payload['url']}]({payload['url']})  
#                             **📂 Category:** {payload['main_category']} / {payload['subcategory']}  
#                             **🏷️ Tags:** {', '.join(payload['tags'])}  
#                             """)
#                             st.metric("Confidence", f"{result.score:.1%}")
#                             st.write(f"**Chunk:** {payload['chunk_index']}/{payload['total_chunks']}")

#                             st.markdown("**📝 Content Preview:**")
#                             st.info(payload['content'][:500] + "..." if len(payload['content']) > 500 else payload['content'])

#             except Exception as e:
#                 st.error(f"Search error: {str(e)}")

# def render_system_status():
#     """Render system status in sidebar"""
#     st.sidebar.markdown("### System Status")
    
#     # Knowledge Base status
#     if st.session_state.kb_status == "ready":
#         st.sidebar.markdown('<div class="status-indicator status-ready">Knowledge Base: Ready</div>', unsafe_allow_html=True)
#     elif st.session_state.kb_status == "error":
#         st.sidebar.markdown('<div class="status-indicator status-error">Knowledge Base: Error</div>', unsafe_allow_html=True)
#     else:
#         st.sidebar.markdown('<div class="status-indicator status-warning">Knowledge Base: Initializing</div>', unsafe_allow_html=True)
    
#     # Classifier status
#     classifier_status = getattr(st.session_state, 'classifier_status', 'waiting')
#     if classifier_status == "ready":
#         st.sidebar.markdown('<div class="status-indicator status-ready">Classifier: Ready</div>', unsafe_allow_html=True)
#     elif classifier_status == "error":
#         st.sidebar.markdown('<div class="status-indicator status-error">Classifier: Error</div>', unsafe_allow_html=True)
#     else:
#         st.sidebar.markdown('<div class="status-indicator status-warning">Classifier: Waiting</div>', unsafe_allow_html=True)
    
#     # RAG Agent status
#     agent_status = getattr(st.session_state, 'agent_status', 'waiting')
#     if agent_status == "ready":
#         st.sidebar.markdown('<div class="status-indicator status-ready">RAG Agent: Ready</div>', unsafe_allow_html=True)
#     elif agent_status == "error":
#         st.sidebar.markdown('<div class="status-indicator status-error">RAG Agent: Error</div>', unsafe_allow_html=True)
#     else:
#         st.sidebar.markdown('<div class="status-indicator status-warning">RAG Agent: Waiting</div>', unsafe_allow_html=True)

# def main():
#     """Main Streamlit application"""
#     initialize_session_state()
#     render_header()
    
#     # Sidebar navigation
#     with st.sidebar:
#         st.title("Navigation")
        
#         page = st.radio(
#             "Select View:",
#             [
#                 "Bulk Classification", 
#                 "Interactive Agent", 
#                 "Knowledge Base Info",
#                 "Analytics Dashboard"
#             ],
#             index=3
#         )
        
#         st.markdown("---")
#         render_system_status()
    
#     # Main content based on page selection
#     if page == "Bulk Classification":
#         render_bulk_classification()
#     elif page == "Interactive Agent":
#         render_interactive_agent()
#     elif page == "Knowledge Base Info":
#         render_knowledge_base_info()
#     # else:
#     #     render_analytics_dashboard()

# if __name__ == "__main__":
#     main()