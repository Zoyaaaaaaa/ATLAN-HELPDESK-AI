import streamlit as st
from typing import Dict, Any, List
from datetime import datetime

def render_main_header():
    """Render the main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Atlan AI Helpdesk System</h1>
        <p>Intelligent ticket classification with RAG-powered responses</p>
        <p><em>Powered by Enhanced Knowledge Base & LangChain Agents</em></p>
    </div>
    """, unsafe_allow_html=True)

def get_tag_classes(classification: Dict[str, Any]) -> Dict[str, str]:
    """Get CSS classes for classification tags"""
    topic = classification.get('topic', '').lower().replace('-', '').replace(' ', '')
    sentiment = classification.get('sentiment', '').lower().replace('-', '').replace(' ', '')
    priority = classification.get('priority', '').lower().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    return {
        'topic': 'topic-tag',
        'sentiment': f'sentiment-{sentiment}',
        'priority': f'priority-{priority}'
    }

def render_classification_tags(classification: Dict[str, Any]) -> str:
    """Render classification tags with proper styling"""
    classes = get_tag_classes(classification)
    
    return f"""
    <div class="classification-tags">
        <span class="tag {classes['topic']}">{classification.get('topic', 'Unknown')}</span>
        <span class="tag {classes['sentiment']}">{classification.get('sentiment', 'Unknown')}</span>
        <span class="tag {classes['priority']}">{classification.get('priority', 'Unknown')}</span>
    </div>
    """

def render_ticket_card(ticket: Dict[str, Any], show_classification: bool = False):
    """Render a ticket card with optional classification"""
    classification_html = ""
    if show_classification and 'classification' in ticket:
        classification_html = render_classification_tags(ticket['classification'])
        reasoning = ticket['classification'].get('reasoning', 'No reasoning provided')
        classification_html += f'<p><em><strong>Reasoning:</strong> {reasoning}</em></p>'
    
    # Truncate body for display
    body_preview = ticket['body'][:300] + '...' if len(ticket['body']) > 300 else ticket['body']
    
    # Format timestamp if available
    timestamp_html = ""
    if 'classified_at' in ticket:
        timestamp_html = f'<small>Classified at: {ticket["classified_at"]}</small>'
    elif 'created_at' in ticket:
        timestamp_html = f'<small>Created at: {ticket["created_at"]}</small>'
    
    st.markdown(f"""
    <div class="ticket-card">
        <h4>🎫 {ticket['id']}: {ticket['subject']}</h4>
        <p><strong>Description:</strong> {body_preview}</p>
        {classification_html}
        {timestamp_html}
    </div>
    """, unsafe_allow_html=True)

def render_status_indicator(status: str, label: str):
    """Render a status indicator with label"""
    status_class = {
        "ready": "status-success",
        "error": "status-error",
        "initializing": "status-warning",
        "waiting": "status-warning"
    }.get(status, "status-warning")
    
    st.sidebar.markdown(
        f'<span class="status-indicator {status_class}"></span>**{label}:** {status.title()}', 
        unsafe_allow_html=True
    )

def render_metric_card(title: str, value: str, description: str = ""):
    """Render a metric card"""
    desc_html = f"<p>{description}</p>" if description else ""
    
    return f"""
    <div class="metric-card">
        <h3>{value}</h3>
        <p>{title}</p>
        {desc_html}
    </div>
    """

def render_response_section(response_data: Dict[str, Any]):
    """Render response section based on response type"""
    response_type = response_data.get("response_type", "unknown")
    answer = response_data.get("answer", "No response generated")
    
    if response_type == "rag_generated":
        st.markdown(f"""
        <div class="response-section">
            <h4>✅ RAG-Generated Response:</h4>
            <div style="white-space: pre-wrap;">{answer}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if response_data.get("sources_included"):
            st.success("📚 Response includes source citations from Atlan documentation")
    
    elif response_type == "routed":
        st.markdown(f"""
        <div class="response-section">
            <h4>📤 Ticket Routed:</h4>
            <p>{answer}</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:  # rag_error or unknown
        st.markdown(f"""
        <div class="response-section">
            <h4>⚠️ Response with Fallback:</h4>
            <p>{answer}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if "error" in response_data:
            st.error(f"Technical details: {response_data['error']}")

def display_verbose_output(verbose_capture):
    """Display verbose output in a formatted expandable section"""
    if not verbose_capture.is_empty():
        with st.expander("🔍 Verbose Output (Agent Thinking Process)", expanded=False):
            verbose_text = verbose_capture.get_output()
            st.markdown(f"""
            <div class="verbose-output">
{verbose_text}
            </div>
            """, unsafe_allow_html=True)
