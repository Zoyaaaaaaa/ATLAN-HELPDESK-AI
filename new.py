import streamlit as st
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import time
import traceback

# Import our custom modules
from services.knowledge_base import EnhancedAtlanKnowledgeBase
from services.ticket_classifier import TicketClassifier, AtlanRAGAgent

# Set page config
st.set_page_config(
    page_title="Atlan AI Helpdesk",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global reset and base styles */
    * {
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: #fafbfc;
    }
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Clean header design */
    .main-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 0;
        background: none;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0 0 1rem 0;
        line-height: 1.2;
    }
    
    .main-header p {
        font-size: 1.125rem;
        color: #666;
        margin: 0;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* Clean card design */
    .clean-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .clean-card:hover {
        border-color: #d1d5db;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f3f4f6;
    }
    
    /* Ticket cards */
    .ticket-item {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }
    
    .ticket-item:hover {
        border-color: #3b82f6;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    .ticket-id {
        font-size: 0.875rem;
        font-weight: 600;
        color: #3b82f6;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        margin-bottom: 0.5rem;
    }
    
    .ticket-subject {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.75rem;
        line-height: 1.4;
    }
    
    .ticket-body {
        color: #4b5563;
        line-height: 1.6;
        margin-bottom: 1rem;
        font-size: 0.9375rem;
    }
    
    /* Clean classification tags */
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .clean-tag {
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8125rem;
        font-weight: 500;
        border: 1px solid;
        text-transform: capitalize;
        letter-spacing: 0.025em;
    }
    
    .tag-topic { 
        background: #eff6ff; 
        border-color: #bfdbfe; 
        color: #1e40af; 
    }
    .tag-sentiment { 
        background: #f0fdf4; 
        border-color: #bbf7d0; 
        color: #166534; 
    }
    .tag-priority { 
        background: #fff7ed; 
        border-color: #fed7aa; 
        color: #c2410c; 
    }
    
    /* Priority-specific colors */
    .priority-high { 
        background: #fef2f2; 
        border-color: #fecaca; 
        color: #dc2626; 
    }
    .priority-medium { 
        background: #fffbeb; 
        border-color: #fde68a; 
        color: #d97706; 
    }
    .priority-low { 
        background: #f0fdf4; 
        border-color: #bbf7d0; 
        color: #166534; 
    }
    
    /* Response sections */
    .response-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #10b981;
    }
    
    .analysis-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #3b82f6;
    }
    
    .card-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0 0 1rem 0;
    }
    
    .response-content {
        color: #374151;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    /* Clean verbose output */
    .verbose-container {
        background: #1f2937;
        color: #e5e7eb;
        padding: 1.5rem;
        border-radius: 8px;
        font-family: 'SF Mono', Monaco, 'Inconsolata', 'Roboto Mono', Consolas, monospace;
        font-size: 0.875rem;
        line-height: 1.6;
        max-height: 400px;
        overflow-y: auto;
        margin: 1rem 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .verbose-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .verbose-container::-webkit-scrollbar-track {
        background: #374151;
        border-radius: 4px;
    }
    
    .verbose-container::-webkit-scrollbar-thumb {
        background: #6b7280;
        border-radius: 4px;
    }
    
    /* Status indicators */
    .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .status-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .status-ready { background: #10b981; }
    .status-error { background: #ef4444; }
    .status-waiting { background: #f59e0b; }
    
    .status-text {
        font-size: 0.875rem;
        font-weight: 500;
        color: #374151;
    }
    
    /* Metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-item {
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.875rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.8125rem;
        font-weight: 500;
        color: #6b7280;
        margin: 0.25rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        transition: all 0.2s ease !important;
        font-size: 0.9375rem !important;
        padding: 0.75rem !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    
    .stButton > button:hover {
        background: #2563eb !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: white !important;
        border-right: 1px solid #e5e7eb !important;
    }
    
    .css-1d391kg .css-10trblm {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 8px !important;
        border: 1px solid #e5e7eb !important;
        font-weight: 500 !important;
        color: #374151 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border-radius: 0 0 8px 8px !important;
        border: 1px solid #e5e7eb !important;
        border-top: none !important;
        padding: 1rem !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #1d4ed8) !important;
        border-radius: 4px !important;
    }
    
    /* Remove default margins and padding */
    .element-container {
        margin: 0 !important;
    }
    
    /* Clean up spacing */
    .block-container > div {
        gap: 1rem !important;
    }
    
    /* Source citations */
    .source-item {
        background: #f8fafc;
        border-radius: 6px;
        padding: 1rem;
        border-left: 3px solid #3b82f6;
        margin: 0.5rem 0;
        font-size: 0.875rem;
    }
    
    .source-title {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }
    
    .source-url {
        color: #3b82f6;
        text-decoration: none;
        font-size: 0.8125rem;
    }
    
    .source-url:hover {
        text-decoration: underline;
    }
    
    .source-meta {
        color: #6b7280;
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    /* Reasoning text */
    .reasoning-text {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 6px;
        color: #4b5563;
        font-style: italic;
        font-size: 0.9375rem;
        line-height: 1.5;
        margin: 0.75rem 0;
        border-left: 3px solid #e5e7eb;
    }
    
    /* Input labels */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {
        font-weight: 500 !important;
        color: #374151 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 500 !important;
        color: #374151 !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        border-radius: 8px !important;
        color: #166534 !important;
    }
    
    .stError {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        border-radius: 8px !important;
        color: #dc2626 !important;
    }
    
    .stWarning {
        background: #fffbeb !important;
        border: 1px solid #fde68a !important;
        border-radius: 8px !important;
        color: #d97706 !important;
    }
    
    /* Clean up default streamlit styling */
    .row-widget.stRadio > div {
        flex-direction: column !important;
        gap: 0.5rem !important;
    }
    
    .row-widget.stRadio > div > label {
        background: transparent !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
    }
    
    .row-widget.stRadio > div > label:hover {
        border-color: #3b82f6 !important;
        background: #f8fafc !important;
    }
    
    .row-widget.stRadio > div > label[data-checked="true"] {
        border-color: #3b82f6 !important;
        background: #eff6ff !important;
        color: #1e40af !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

from utils.data_loader import load_sample_tickets
load_sample_tickets()

# Sample tickets data
SAMPLE_TICKETS = [
    {
        "id": "TICKET-245",
        "subject": "Connecting Snowflake to Atlan - required permissions?",
        "body": "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing. We've tried using our standard service account, but it's not working. Our entire BI team is blocked on this integration for a major upcoming project, so it's quite urgent. Could you please provide a definitive list of the exact permissions and credentials needed on the Snowflake side to get this working? Thanks."
    },
    {
        "id": "TICKET-246", 
        "subject": "Data lineage not showing downstream impacts",
        "body": "Our data lineage view isn't capturing all the downstream transformations in our dbt models. We have a complex data pipeline and need to understand the full impact of changes. Can you help us troubleshoot why some lineage connections are missing?"
    },
    {
        "id": "TICKET-247",
        "subject": "API authentication failing with 401 errors", 
        "body": "I'm trying to use the Atlan Python SDK to automate some metadata updates, but I keep getting 401 authentication errors. I've double-checked my API token. What could be wrong?"
    },
    {
        "id": "TICKET-248",
        "subject": "How to implement SSO with Okta?",
        "body": "We need to set up Single Sign-On integration with our Okta identity provider. What are the configuration steps and requirements for SAML SSO setup in Atlan?"
    },
    {
        "id": "TICKET-249",
        "subject": "Best practices for data governance policies",
        "body": "We're looking for recommendations on how to structure our data governance framework in Atlan. What are the best practices for setting up policies, classifications, and ownership?"
    }
]

class VerboseCapture:
    """Enhanced verbose output capture with better formatting"""
    def __init__(self):
        self.output = []

    def write(self, text):
        if text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_text = f"[{timestamp}] {text.strip()}"
            self.output.append(formatted_text)
            return len(text)

    def get_output(self):
        if not self.output:
            return "No verbose output available."
        return '\n'.join(self.output)

    def clear(self):
        self.output = []

def initialize_session_state():
    """Initialize all session state variables"""
    # Verbose capture
    if 'verbose_capture' not in st.session_state:
        st.session_state.verbose_capture = VerboseCapture()

    # Initialize knowledge base
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None
        st.session_state.kb_status = "initializing"

        with st.spinner("Initializing Atlan Knowledge Base..."):
            try:
                import sys
                original_stdout = sys.stdout
                sys.stdout = st.session_state.verbose_capture

                st.session_state.knowledge_base = EnhancedAtlanKnowledgeBase()
                st.session_state.kb_status = "ready"

                sys.stdout = original_stdout
                st.success("Knowledge Base initialized successfully")

            except Exception as e:
                sys.stdout = original_stdout
                st.error(f"Failed to initialize Knowledge Base: {str(e)}")
                st.session_state.kb_status = "error"
                st.session_state.kb_error = str(e)

    # Initialize classifier
    if 'classifier' not in st.session_state:
        if st.session_state.knowledge_base:
            try:
                st.session_state.classifier = TicketClassifier()
                st.session_state.classifier_status = "ready"
            except Exception as e:
                st.error(f"Failed to initialize Classifier: {str(e)}")
                st.session_state.classifier_status = "error"
                st.session_state.classifier = None
        else:
            st.session_state.classifier_status = "waiting"
            st.session_state.classifier = None

    # Initialize RAG agent
    if 'rag_agent' not in st.session_state:
        if st.session_state.knowledge_base:
            try:
                st.session_state.rag_agent = AtlanRAGAgent(st.session_state.knowledge_base)
                st.session_state.agent_status = "ready"
            except Exception as e:
                st.error(f"Failed to initialize RAG Agent: {str(e)}")
                st.session_state.agent_status = "error"
                st.session_state.rag_agent = None
        else:
            st.session_state.agent_status = "waiting"
            st.session_state.rag_agent = None

    # Sample tickets
    if 'sample_tickets' not in st.session_state:
        st.session_state.sample_tickets = SAMPLE_TICKETS

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>Atlan AI Helpdesk</h1>
        <p>Intelligent ticket classification with RAG-powered responses</p>
    </div>
    """, unsafe_allow_html=True)

def get_priority_class(priority: str) -> str:
    """Get CSS class for priority tag"""
    if 'high' in priority.lower() or 'p0' in priority.lower():
        return 'priority-high'
    elif 'medium' in priority.lower() or 'p1' in priority.lower():
        return 'priority-medium'
    else:
        return 'priority-low'

def render_classification_tags(classification: Dict[str, Any]) -> str:
    """Render clean classification tags"""
    priority_class = get_priority_class(classification.get('priority', ''))
    
    return f"""
    <div class="tag-container">
        <span class="clean-tag tag-topic">{classification.get('topic', 'Unknown')}</span>
        <span class="clean-tag tag-sentiment">{classification.get('sentiment', 'Neutral')}</span>
        <span class="clean-tag {priority_class}">{classification.get('priority', 'Low')}</span>
    </div>
    """

def display_verbose_output():
    """Display verbose output in a clean way"""
    if st.session_state.verbose_capture.output:
        with st.expander("View Processing Details", expanded=False):
            verbose_html = st.session_state.verbose_capture.get_output()
            st.markdown(f'<div class="verbose-container">{verbose_html}</div>', unsafe_allow_html=True)

def render_bulk_classification():
    """Render bulk ticket classification dashboard"""
    st.markdown('<h2 class="section-header">Bulk Ticket Classification</h2>', unsafe_allow_html=True)

    if not st.session_state.classifier:
        st.error("Classifier not available")
        return

    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    
    if st.button("Classify All Tickets", type="primary", use_container_width=True):
        st.session_state.classified_tickets = []
        st.session_state.verbose_capture.clear()

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, ticket in enumerate(st.session_state.sample_tickets):
            status_text.text(f'Processing ticket {i+1} of {len(st.session_state.sample_tickets)}...')

            st.session_state.verbose_capture.clear()
            ticket_text = f"Subject: {ticket['subject']}\nBody: {ticket['body']}"
            classification = st.session_state.classifier.classify_ticket(ticket_text)

            classified_ticket = {
                **ticket,
                "classification": classification,
                "classified_at": datetime.now().isoformat()
            }
            st.session_state.classified_tickets.append(classified_ticket)

            progress_bar.progress((i + 1) / len(st.session_state.sample_tickets))
            time.sleep(0.3)

        status_text.text('All tickets classified successfully')
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Display classified tickets
    if hasattr(st.session_state, 'classified_tickets'):
        st.markdown(f'<h3 class="section-header">Classification Results ({len(st.session_state.classified_tickets)} tickets)</h3>', unsafe_allow_html=True)

        for ticket in st.session_state.classified_tickets:
            st.markdown(f"""
            <div class="ticket-item">
                <div class="ticket-id">{ticket['id']}</div>
                <div class="ticket-subject">{ticket['subject']}</div>
                <div class="ticket-body">{ticket['body'][:200]}{'...' if len(ticket['body']) > 200 else ''}</div>
                {render_classification_tags(ticket['classification'])}
                <div class="reasoning-text">{ticket['classification'].get('reasoning', 'No reasoning provided')}</div>
            </div>
            """, unsafe_allow_html=True)

def render_interactive_agent():
    """Render interactive AI agent interface"""
    st.markdown('<h2 class="section-header">Interactive AI Agent</h2>', unsafe_allow_html=True)

    if not st.session_state.classifier or not st.session_state.rag_agent:
        st.error("AI Agent not available - System initialization incomplete")
        return

    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    
    with st.form("query_form", clear_on_submit=False):
        user_query = st.text_area(
            "Enter your question or support ticket:",
            placeholder="How do I set up SSO with Okta in Atlan?\nWhat permissions are needed for Snowflake connector?\nHow to troubleshoot API authentication issues?",
            height=100,
            help="Ask about Atlan products, APIs, connectors, lineage, SSO, or technical questions"
        )

        col1, col2 = st.columns([4, 1])
        with col1:
            submit_button = st.form_submit_button("Process Query", type="primary", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("Clear", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    if clear_button:
        st.session_state.verbose_capture.clear()
        st.rerun()

    if submit_button and user_query.strip():
        st.session_state.verbose_capture.clear()

        # Classification
        with st.spinner("Analyzing query..."):
            classification = st.session_state.classifier.classify_ticket(user_query)

                # Show classification
            st.markdown(render_classification_tags(classification), unsafe_allow_html=True)

        display_verbose_output()
        st.session_state.verbose_capture.clear()

        # Generate response
        with st.spinner("Generating response..."):
            try:
                import sys
                original_stdout = sys.stdout
                sys.stdout = st.session_state.verbose_capture

                response_data = st.session_state.rag_agent.generate_response(user_query, classification)
                sys.stdout = original_stdout

                # Display response
                response_title = {
                    "rag_generated": "AI Response",
                    "routed": "Ticket Routed",
                    "rag_error": "Response (Fallback)"
                }.get(response_data["response_type"], "Response")

                st.markdown(f"""
                <div class="response-card">
                    <div class="card-title">{response_title}</div>
                    <div class="response-content">{response_data['answer']}</div>
                </div>
                """, unsafe_allow_html=True)

                # Show sources if available
                if response_data.get("sources_included") and 'sources' in response_data:
                    st.markdown('<div class="card-title" style="margin-top: 1.5rem;">Sources</div>', unsafe_allow_html=True)
                    for i, source in enumerate(response_data.get('sources', []), 1):
                        st.markdown(f"""
                        <div class="source-item">
                            <div class="source-title">{i}. {source.get('title', 'Unknown Source')}</div>
                            <a href="{source.get('url', '#')}" class="source-url" target="_blank">{source.get('url', 'No URL')}</a>
                            <div class="source-meta">Category: {source.get('category', 'Unknown')} • Tags: {', '.join(source.get('tags', []))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                display_verbose_output()

            except Exception as e:
                sys.stdout = original_stdout
                st.error(f"Error generating response: {str(e)}")

def render_knowledge_base_info():
    """Render knowledge base information"""
    st.markdown('<h2 class="section-header">Knowledge Base Information</h2>', unsafe_allow_html=True)

    if not st.session_state.knowledge_base:
        st.error("Knowledge Base not available")
        return

    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    
    # Knowledge base stats
    with st.spinner("Loading knowledge base statistics..."):
        try:
            stats = st.session_state.knowledge_base.get_knowledge_base_stats()

            if "error" not in stats:
                # Display metrics
                st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-item">
                    <div class="metric-value">{stats['total_vectors']:,}</div>
                    <div class="metric-label">Total Vectors</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-item">
                    <div class="metric-value">{len(stats['categories'])}</div>
                    <div class="metric-label">Categories</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-item">
                    <div class="metric-value">{len(stats['source_types'])}</div>
                    <div class="metric-label">Source Types</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-item">
                    <div class="metric-value">Ready</div>
                    <div class="metric-label">Status</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

                # Detailed breakdown
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Categories:**")
                    for category, count in stats['categories'].items():
                        st.write(f"• {category}: {count:,} vectors")

                with col2:
                    st.write("**Source Types:**")
                    for source_type, count in stats['source_types'].items():
                        st.write(f"• {source_type}: {count:,} vectors")

                st.write(f"**Last Updated:** {stats['last_updated']}")
            else:
                st.error(f"Error loading stats: {stats['error']}")

        except Exception as e:
            st.error(f"Error displaying knowledge base info: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Testing interface
    st.markdown('<div class="clean-card" style="margin-top: 2rem;">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">Test Knowledge Base Search</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        test_query = st.text_input(
            "Enter a test query:",
            placeholder="How to authenticate with Atlan API?"
        )

    with col2:
        category_filter = st.selectbox(
            "Category Filter:",
            ["None", "product_documentation", "developer_hub"],
            index=0
        )

    if st.button("Search Knowledge Base", type="primary", use_container_width=True) and test_query:
        st.session_state.verbose_capture.clear()

        with st.spinner("Searching knowledge base..."):
            try:
                filter_category = None if category_filter == "None" else category_filter
                results = st.session_state.knowledge_base.search_knowledge_base(
                    test_query, 
                    limit=5, 
                    category_filter=filter_category
                )

                if results:
                    st.success(f"Found {len(results)} results")

                    # Display results
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Result {i} - Similarity: {result.score:.1%}"):
                            payload = result.payload

                            col1, col2 = st.columns([2, 1])

                            with col1:
                                st.write(f"**Title:** {payload['title']}")
                                st.write(f"**URL:** {payload['url']}")
                                st.write(f"**Category:** {payload['main_category']} / {payload['subcategory']}")

                            with col2:
                                st.metric("Confidence", f"{result.score:.1%}")
                                st.write(f"**Chunk:** {payload['chunk_index']}/{payload['total_chunks']}")

                            st.write("**Content Preview:**")
                            content_preview = payload['content'][:400] + "..." if len(payload['content']) > 400 else payload['content']
                            st.write(content_preview)

                    # Generate RAG response
                    if st.button("Generate RAG Response", use_container_width=True):
                        with st.spinner("Generating RAG response..."):
                            rag_response = st.session_state.knowledge_base.generate_rag_response(
                                test_query,
                                limit=3,
                                category_filter=filter_category
                            )

                            st.markdown(f"""
                            <div class="response-card">
                                <div class="card-title">RAG Response (Confidence: {rag_response['confidence']:.1%})</div>
                                <div class="response-content">{rag_response['answer']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            if rag_response['sources']:
                                st.markdown('<div class="card-title" style="margin-top: 1.5rem;">Sources Used</div>', unsafe_allow_html=True)
                                for i, source in enumerate(rag_response['sources'], 1):
                                    st.markdown(f"""
                                    <div class="source-item">
                                        <div class="source-title">{i}. {source['title']}</div>
                                        <a href="{source['url']}" class="source-url" target="_blank">{source['url']}</a>
                                        <div class="source-meta">Category: {source['category']} / {source['subcategory']} • Tags: {', '.join(source['tags'])}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.warning("No results found for your query")

            except Exception as e:
                st.error(f"Search error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_system_status():
    """Render system status in sidebar"""
    st.sidebar.markdown("### System Status")

    # Status grid
    status_items = []
    
    # Knowledge Base status
    kb_status = st.session_state.kb_status
    kb_class = "status-ready" if kb_status == "ready" else ("status-error" if kb_status == "error" else "status-waiting")
    status_items.append(f'<div class="status-item"><div class="status-dot {kb_class}"></div><span class="status-text">Knowledge Base: {kb_status.title()}</span></div>')

    # Classifier status
    classifier_status = getattr(st.session_state, 'classifier_status', 'waiting')
    classifier_class = "status-ready" if classifier_status == "ready" else ("status-error" if classifier_status == "error" else "status-waiting")
    status_items.append(f'<div class="status-item"><div class="status-dot {classifier_class}"></div><span class="status-text">Classifier: {classifier_status.title()}</span></div>')

    # RAG Agent status
    agent_status = getattr(st.session_state, 'agent_status', 'waiting')
    agent_class = "status-ready" if agent_status == "ready" else ("status-error" if agent_status == "error" else "status-waiting")
    status_items.append(f'<div class="status-item"><div class="status-dot {agent_class}"></div><span class="status-text">RAG Agent: {agent_status.title()}</span></div>')

    status_html = '<div class="status-grid">' + ''.join(status_items) + '</div>'
    st.sidebar.markdown(status_html, unsafe_allow_html=True)

    # Quick stats
    if st.session_state.knowledge_base:
        st.sidebar.markdown("### Quick Stats")
        try:
            stats = st.session_state.knowledge_base.get_knowledge_base_stats()
            if "error" not in stats:
                st.sidebar.metric("Total Vectors", f"{stats['total_vectors']:,}")
                st.sidebar.metric("Categories", len(stats['categories']))
        except:
            st.sidebar.write("Stats loading...")

def main():
    """Main Streamlit application"""
    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")

        # Navigation options
        page = st.radio(
            "Select View:",
            [
                "Bulk Classification", 
                "Interactive Agent", 
                "Knowledge Base Info"
            ],
            index=1  # Default to Interactive Agent
        )

        st.markdown("---")

        # System status
        render_system_status()

        st.markdown("---")

        # Tips
        with st.expander("Tips"):
            st.write("""
            **For best results:**
            - Be specific in your questions
            - Use technical terms when relevant
            - Ask about Atlan features, APIs, connectors
            - Questions about setup, configuration, troubleshooting work well
            """)

        # Clear verbose output button
        if st.button("Clear Verbose Output"):
            st.session_state.verbose_capture.clear()
            st.success("Verbose output cleared")

    # Main content based on page selection
    if page == "Bulk Classification":
        render_bulk_classification()
    elif page == "Interactive Agent":
        render_interactive_agent()
    else:  # Knowledge Base Info
        render_knowledge_base_info()

    # Simple footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem 0;">
        <strong>Atlan AI Helpdesk System</strong> - Powered by Enhanced RAG & LangChain Agents
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()