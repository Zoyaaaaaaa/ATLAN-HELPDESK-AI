import streamlit as st
import json
import os
from datetime import datetime
import uuid
import requests
import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
import os
from datetime import datetime
from typing import Dict, Any, List
from langchain import hub
from qdrant_client.http import models as rest
from services import analytics_service
from config.settings import settings
from services.ticket_classifier import AtlanRAGAgent
from services.knowledge_base import EnhancedAtlanKnowledgeBase
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
    
    # Return default tickets if file not found
    return [
        {
            "id": "T-001",
            "subject": "Database Connection Issue",
            "body": "I'm having trouble connecting my Snowflake database to Atlan. The connection test fails with a permission error.",
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "T-002", 
            "subject": "API Documentation Request",
            "body": "Where can I find the API documentation for bulk data ingestion? I need to integrate our ETL pipeline.",
            "created_at": "2024-01-15T11:45:00Z"
        }
    ]

def apply_professional_styling():
    st.markdown("""
    <style>
    /* Import Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 1400px;
    }
    
    /* Header Styles */
    .main-header {
        color: #1e293b;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 2rem 0;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        color: #334155;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .description {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Card Components */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Ticket Cards */
    .ticket-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .ticket-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    .ticket-id {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .ticket-title {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        line-height: 1.4;
    }
    
    .ticket-body {
        color: #64748b;
        font-size: 0.875rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    /* Classification Badges */
    .classification-row {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        align-items: center;
    }
    
    .classification-badge {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .topic-badge {
        background: #dbeafe;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    
    .sentiment-badge {
        background: #f0f9ff;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }
    
    .priority-badge {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    
    .priority-high {
        background: #fee2e2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    
    /* Response Containers */
    .response-section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .internal-analysis {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .final-response {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .verbose-section {
        background: #fafafa;
        border: 1px solid #e4e4e7;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.8rem;
        line-height: 1.6;
        color: #52525b;
    }
    
    /* Sources Styling */
    .source-item {
        display: flex;
        align-items: flex-start;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .source-item:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    }
    
    .source-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        background: #3b82f6;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.875rem;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    .source-content {
        flex: 1;
    }
    
    .source-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.25rem;
        font-size: 0.9rem;
    }
    
    .source-url {
        color: #64748b;
        font-size: 0.8rem;
        word-break: break-all;
    }
    
    .source-url a {
        color: #3b82f6;
        text-decoration: none;
    }
    
    .source-url a:hover {
        text-decoration: underline;
    }
    
    /* Buttons */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .stButton > button:hover {
        background: #2563eb;
        border-color: #1d4ed8;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
    }
    
    /* Secondary Buttons */
    .secondary-btn {
        background: white !important;
        color: #3b82f6 !important;
        border: 1px solid #3b82f6 !important;
    }
    
    .secondary-btn:hover {
        background: #f0f9ff !important;
        border-color: #2563eb !important;
    }
    
    /* Text Areas */
    .stTextArea textarea {
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 0.75rem;
        font-family: inherit;
        transition: border-color 0.2s ease;
    }
    
    .stTextArea textarea:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.25rem;
        gap: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #64748b;
        font-weight: 500;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #1e293b;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Progress Bars */
    .stProgress .st-bo {
        background-color: #e2e8f0;
    }
    
    .stProgress .st-bp {
        background-color: #3b82f6;
    }
    
    /* Processing Indicator */
    .processing-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 12px;
        color: #1e293b;
        margin: 1rem 0;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        color: #334155;
        font-weight: 500;
    }
    
    /* Analytics Cards */
    .analytics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .analytics-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .analytics-item h4 {
        color: #334155;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .analytics-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .analytics-change {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    /* Status Indicators */
    .status-healthy { color: #059669; }
    .status-warning { color: #d97706; }
    .status-critical { color: #dc2626; }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #64748b;
    }
    
    .empty-state h3 {
        color: #334155;
        margin-bottom: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
        color: #64748b;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .main-header {
            font-size: 2rem;
        }
        
        .classification-row {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .source-item {
            flex-direction: column;
            text-align: center;
        }
        
        .source-number {
            margin-bottom: 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Atlan AI Helpdesk",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_professional_styling()
    
    # Header
    st.markdown('<h1 class="main-header">Atlan AI Helpdesk Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="description">Intelligent ticket classification and automated response system powered by advanced AI</p>', unsafe_allow_html=True)
    
    # Initialize components
    @st.cache_resource
    def init_knowledge_base():
        return EnhancedAtlanKnowledgeBase()
    
    @st.cache_resource
    def init_classifier():
        return AtlanTicketClassifier()
    
    @st.cache_resource
    def init_rag_agent(_kb):
        return AtlanRAGAgent(_kb)
    
    with st.spinner("Initializing AI components..."):
        kb = init_knowledge_base()
        classifier = init_classifier()
        rag_agent = init_rag_agent(kb)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## Configuration")
        verbose_mode = st.toggle("Verbose Logging", value=True)
        show_internal = st.toggle("Show Internal Analysis", value=False)
        auto_classify = st.toggle("Auto-classify Tickets", value=True)
        
        st.markdown("---")
        st.markdown("### System Status")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Models", "2", "Active")
        with col2:
            st.metric("Sources", "150+", "Ready")
    
    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Ticket Classification", "🤖 AI Assistant", "📈 Analytics"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Bulk Ticket Classification</h2>', unsafe_allow_html=True)
        
        sample_tickets = load_sample_tickets()
        
        # Metrics Row
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-number">{len(sample_tickets)}</div>
                <div class="metric-label">Total Tickets</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-number">9</div>
                <div class="metric-label">Categories</div>
            </div>
            ''', unsafe_allow_html=True)
        
        
        
        # Controls
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Classify All", type="primary", use_container_width=True):
                if 'classified_tickets' in st.session_state:
                    del st.session_state.classified_tickets
                st.rerun()
        
        # Process tickets
        if auto_classify and 'classified_tickets' not in st.session_state:
            with st.spinner("Processing tickets..."):
                classified_tickets = []
                progress_bar = st.progress(0)
                
                for i, ticket in enumerate(sample_tickets):
                    ticket_text = f"Subject: {ticket['subject']}\n\nBody: {ticket['body']}"
                    
                    if verbose_mode:
                        classification, logs = classifier.classify_ticket(ticket_text, verbose=True)
                        ticket_data = {**ticket, "classification": classification, "verbose_logs": logs}
                    else:
                        classification = classifier.classify_ticket(ticket_text, verbose=False)
                        ticket_data = {**ticket, "classification": classification}
                    
                    classified_tickets.append(ticket_data)
                    progress_bar.progress((i + 1) / len(sample_tickets))
                
                st.session_state.classified_tickets = classified_tickets
                progress_bar.empty()
                st.success("All tickets classified successfully!")
        
        # Display tickets
        if 'classified_tickets' in st.session_state:
            for ticket in st.session_state.classified_tickets:
                st.markdown(f'''
                <div class="ticket-card">
                    <div class="ticket-id">{ticket['id']}</div>
                    <div class="ticket-title">{ticket['subject']}</div>
                    <div class="ticket-body">{ticket['body'][:200]}{'...' if len(ticket['body']) > 200 else ''}</div>
                    <div class="classification-row">
                        <span class="classification-badge topic-badge">
                            {', '.join(ticket['classification']['topic_tags'])}
                        </span>
                        <span class="classification-badge sentiment-badge">
                            {ticket['classification']['sentiment']}
                        </span>
                        <span class="classification-badge {'priority-badge' if 'P1' in ticket['classification']['priority'] or 'P2' in ticket['classification']['priority'] else 'priority-high'}">
                            {ticket['classification']['priority']}
                        </span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if verbose_mode and 'verbose_logs' in ticket:
                    with st.expander(f"Verbose Logs - {ticket['id']}", expanded=False):
                        st.markdown('<div class="verbose-section">', unsafe_allow_html=True)
                        for log in ticket['verbose_logs']:
                            st.text(log)
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h2 class="sub-header">Interactive AI Assistant</h2>', unsafe_allow_html=True)
        
        # Input Section
        st.markdown("### Submit New Ticket")
        new_ticket = st.text_area(
            "Describe your issue or question:",
            placeholder="Example: I'm having trouble connecting my Snowflake database to Atlan. The connection test fails with a permission error...",
            height=120
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            submit_btn = st.button("Submit Ticket", type="primary", use_container_width=True)
        with col2:
            urgent_btn = st.button("Mark Urgent", use_container_width=True, help="High priority")
        with col3:
            if st.button("Clear", use_container_width=True):
                for key in ['current_response', 'current_ticket', 'current_classification']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        if submit_btn or urgent_btn:
            if new_ticket:
                with st.spinner("Processing your request..."):
                    # Classification
                    if verbose_mode:
                        classification, class_logs = classifier.classify_ticket(new_ticket, verbose=True)
                    else:
                        classification = classifier.classify_ticket(new_ticket, verbose=False)
                        class_logs = []
                    
                    if urgent_btn:
                        classification['priority'] = 'P0 (High)'
                    
                    # RAG Response
                    response = rag_agent.generate_response(new_ticket, classification, verbose=verbose_mode)
                    
                    # Store results
                    st.session_state.update({
                        'current_response': response,
                        'current_ticket': new_ticket,
                        'current_classification': classification,
                        'classification_logs': class_logs
                    })
                    
                    st.success("Ticket processed successfully!")
            else:
                st.warning("Please enter a ticket description before submitting.")
        
        # Display Results
        if 'current_response' in st.session_state:
            st.markdown("---")
            
            # Processing Stats
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
                st.metric("Priority Level", priority.split()[0])
            
            # Classification Results
            st.markdown("### Classification Results")
            classification = st.session_state.current_classification
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'''
                <div class="response-section">
                    <h4>Topics</h4>
                    <div class="classification-badge topic-badge">
                        {', '.join(classification['topic_tags'])}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''
                <div class="response-section">
                    <h4>Sentiment</h4>
                    <div class="classification-badge sentiment-badge">
                        {classification['sentiment']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                priority_class = "priority-high" if "P0" in classification['priority'] else "priority-badge"
                st.markdown(f'''
                <div class="response-section">
                    <h4>Priority</h4>
                    <div class="classification-badge {priority_class}">
                        {classification['priority']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Verbose Classification Logs
            if verbose_mode and 'classification_logs' in st.session_state and st.session_state.classification_logs:
                with st.expander("Classification Verbose Logs", expanded=False):
                    st.markdown('<div class="verbose-section">', unsafe_allow_html=True)
                    for log in st.session_state.classification_logs:
                        st.text(log)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Internal Analysis
            if show_internal:
                st.markdown("### Internal Analysis")
                st.markdown('<div class="internal-analysis">', unsafe_allow_html=True)
                st.json(st.session_state.current_response["internal_analysis"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            # RAG Verbose Logs
            if verbose_mode and 'verbose_logs' in st.session_state.current_response:
                with st.expander("RAG Agent Verbose Logs", expanded=False):
                    st.markdown('<div class="verbose-section">', unsafe_allow_html=True)
                    for log in st.session_state.current_response["verbose_logs"]:
                        st.text(log)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # AI Response
            st.markdown("### AI Response")
            response_data = st.session_state.current_response["final_response"]
            
            st.markdown('<div class="final-response">', unsafe_allow_html=True)
            st.markdown(f"**Response:** {response_data['answer']}")
            
            if response_data.get("category_used"):
                st.markdown(f"**Knowledge Base Category:** `{response_data['category_used']}`")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sources
            sources = response_data.get("sources", [])
            if sources:
                st.markdown("### Sources & References")
                for i, source in enumerate(sources):
                    domain = urlparse(source.get('url', '')).netloc or 'Unknown Source'
                    
                    st.markdown(f'''
                    <div class="source-item">
                        <div class="source-number">{i+1}</div>
                        <div class="source-content">
                            <div class="source-title">{source.get('title', 'Untitled Document')}</div>
                            <div class="source-url">
                                {domain} • <a href="{source.get('url', '#')}" target="_blank">View Source</a>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Action Buttons
            st.markdown("### Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("👍 Helpful", use_container_width=True):
                    st.success("Thank you for your feedback!")
            
            with col2:
                if st.button("👎 Needs Improvement", use_container_width=True):
                    st.info("Feedback noted. We'll improve our responses.")
            
            with col3:
                if st.button("📧 Email Response", use_container_width=True):
                    st.info("Response would be emailed to customer")
            
            with col4:
                if st.button("🔄 Escalate to Human", use_container_width=True):
                    st.warning("Ticket escalated to human agent")
    
    with tab3:
        st.markdown('<h2 class="sub-header">Analytics Dashboard</h2>', unsafe_allow_html=True)
        
        if 'classified_tickets' in st.session_state:
            tickets = st.session_state.classified_tickets
            
            # Generate analytics
            trends = analytics_service.generate_topic_trends(tickets)
            satisfaction = analytics_service.calculate_satisfaction_metrics(tickets)
            performance = analytics_service.generate_performance_metrics(tickets)
            
            # KPI Row
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-number">{performance['total_processed']}</div>
                    <div class="metric-label">Total Processed</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-number">{satisfaction['nps_score']}%</div>
                    <div class="metric-label">NPS Score</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-number">{performance['auto_resolution_rate_percent']}%</div>
                    <div class="metric-label">Auto-Resolution</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-number">{performance['avg_processing_time_seconds']}s</div>
                    <div class="metric-label">Avg Process Time</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col5:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-number">{performance['efficiency_score']}</div>
                    <div class="metric-label">Efficiency Score</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Detailed Analytics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Topic Analysis")
                for topic, count in list(trends['topic_frequency'].items())[:6]:
                    percentage = (count / len(tickets)) * 100
                    st.markdown(f'''
                    <div class="analytics-item">
                        <h4>{topic}</h4>
                        <div class="analytics-value">{count}</div>
                        <div class="analytics-change">{percentage:.1f}% of total</div>
                        <div style="background: #e2e8f0; height: 4px; border-radius: 2px; margin-top: 0.5rem;">
                            <div style="background: #3b82f6; height: 100%; width: {percentage}%; border-radius: 2px;"></div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Sentiment Distribution")
                for sentiment, count in satisfaction['satisfaction_distribution'].items():
                    percentage = (count / len(tickets)) * 100
                    st.markdown(f'''
                    <div class="analytics-item">
                        <h4>{sentiment}</h4>
                        <div class="analytics-value">{count}</div>
                        <div class="analytics-change">{percentage:.1f}% of tickets</div>
                        <div style="background: #e2e8f0; height: 4px; border-radius: 2px; margin-top: 0.5rem;">
                            <div style="background: #3b82f6; height: 100%; width: {percentage}%; border-radius: 2px;"></div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            
        else:
            st.markdown('''
            <div class="empty-state">
                <h3>Analytics Dashboard</h3>
                <p>Analytics will be available after processing tickets. Please visit the "Ticket Classification" tab to get started.</p>
            </div>
            ''', unsafe_allow_html=True)
    
    # Footer
    st.markdown('''
    <div class="footer">
        <strong>Atlan AI Helpdesk System</strong> - Powered by Enhanced RAG & Advanced Classification<br>
        <em>Real-time processing • Intelligent responses • Source-cited answers</em>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()