
# import streamlit as st
# import json
# import os
# from datetime import datetime
# from typing import Dict, List, Any
# import time
# import traceback

# # # Import our custom modules
# from services.knowledge_base import EnhancedAtlanKnowledgeBase
# from services.ticket_classifier import TicketClassifier, AtlanRAGAgent

# # Set page config
# st.set_page_config(
#     page_title="Atlan AI Helpdesk System",
#     page_icon="🎯",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Clean, modern CSS styling
# st.markdown("""
# <style>
#     .stApp {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#     }
    
#     .main > div {
#         background: white;
#         border-radius: 15px;
#         margin: 1rem;
#         padding: 2rem;
#         box-shadow: 0 10px 30px rgba(0,0,0,0.1);
#     }
    
#     .main-header {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 2rem;
#         border-radius: 15px;
#         color: white;
#         text-align: center;
#         margin-bottom: 2rem;
#         box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
#     }
    
#     .main-header h1 {
#         margin: 0 0 0.5rem 0;
#         font-size: 2.5rem;
#         font-weight: 700;
#     }
    
#     .ticket-card {
#         background: linear-gradient(145deg, #f8f9ff, #f1f3ff);
#         padding: 1.5rem;
#         border-radius: 12px;
#         border-left: 4px solid #667eea;
#         margin-bottom: 1rem;
#         transition: all 0.3s ease;
#     }
    
#     .ticket-card:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
#     }
    
#     .classification-row {
#         display: flex;
#         flex-wrap: wrap;
#         gap: 0.75rem;
#         margin: 1rem 0;
#     }
    
#     .classification-tag {
#         padding: 0.5rem 1rem;
#         border-radius: 25px;
#         font-size: 0.85rem;
#         font-weight: 600;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#         color: white;
#     }
    
#     .tag-topic { background: linear-gradient(135deg, #667eea, #764ba2); }
#     .tag-frustrated { background: linear-gradient(135deg, #ff6b6b, #ee5a52); }
#     .tag-angry { background: linear-gradient(135deg, #ff8a80, #ff5722); }
#     .tag-curious { background: linear-gradient(135deg, #42a5f5, #1976d2); }
#     .tag-neutral { background: linear-gradient(135deg, #9c27b0, #673ab7); }
#     .tag-satisfied { background: linear-gradient(135deg, #66bb6a, #43a047); }
#     .tag-high { background: linear-gradient(135deg, #f44336, #d32f2f); }
#     .tag-medium { background: linear-gradient(135deg, #ff9800, #f57c00); }
#     .tag-low { background: linear-gradient(135deg, #4caf50, #388e3c); }
    
#     .response-section {
#         background: linear-gradient(145deg, #e8f5e8, #f1f8e9);
#         padding: 1.5rem;
#         border-radius: 12px;
#         border: 2px solid #4caf50;
#         margin: 1rem 0;
#     }
    
#     .analysis-section {
#         background: linear-gradient(145deg, #e3f2fd, #f3f9ff);
#         padding: 1.5rem;
#         border-radius: 12px;
#         border: 2px solid #2196f3;
#         margin: 1rem 0;
#     }
    
#     .confidence-indicator {
#         display: inline-flex;
#         align-items: center;
#         padding: 0.5rem 1rem;
#         border-radius: 20px;
#         font-weight: 600;
#         margin-left: 1rem;
#     }
    
#     .confidence-high { background: #d4edda; color: #155724; }
#     .confidence-medium { background: #fff3cd; color: #856404; }
#     .confidence-low { background: #f8d7da; color: #721c24; }
    
#     .metric-card {
#         background: white;
#         padding: 1.5rem;
#         border-radius: 12px;
#         text-align: center;
#         box-shadow: 0 4px 15px rgba(0,0,0,0.08);
#         border-top: 4px solid #667eea;
#     }
    
#     .metric-value {
#         font-size: 2rem;
#         font-weight: 700;
#         color: #667eea;
#         margin: 0;
#     }
    
#     .source-card {
#         background: linear-gradient(145deg, #fff8f0, #fff4e6);
#         padding: 1rem;
#         border-radius: 8px;
#         border-left: 3px solid #ff9800;
#         margin: 0.5rem 0;
#     }
    
#     .status-indicator {
#         display: inline-flex;
#         align-items: center;
#         padding: 0.25rem 0.75rem;
#         border-radius: 15px;
#         font-size: 0.8rem;
#         font-weight: 600;
#         margin: 0.25rem 0;
#     }
    
#     .status-ready { background: #d4edda; color: #155724; }
#     .status-error { background: #f8d7da; color: #721c24; }
#     .status-warning { background: #fff3cd; color: #856404; }
# </style>
# """, unsafe_allow_html=True)

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

# def render_knowledge_base_info():
#     """Render knowledge base information and testing interface"""
#     st.header("Knowledge Base Information & Testing")
    
#     if not st.session_state.knowledge_base or st.session_state.kb_status != "ready":
#         st.error("Knowledge Base not available")
#         return
    
#     # Use existing get_knowledge_base_stats method
#     with st.spinner("Loading knowledge base statistics..."):
#         try:
#             stats = st.session_state.knowledge_base.get_knowledge_base_stats()
            
#             if "error" not in stats:
#                 col1, col2, col3, col4 = st.columns(4)
                
#                 with col1:
#                     st.markdown(f"""
#                     <div class="metric-card">
#                         <div class="metric-value">{stats['total_vectors']:,}</div>
#                         <p>Total Vectors</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col2:
#                     st.markdown(f"""
#                     <div class="metric-card">
#                         <div class="metric-value">{len(stats['categories'])}</div>
#                         <p>Categories</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col3:
#                     st.markdown(f"""
#                     <div class="metric-card">
#                         <div class="metric-value">{len(stats['source_types'])}</div>
#                         <p>Source Types</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col4:
#                     st.markdown(f"""
#                     <div class="metric-card">
#                         <div class="metric-value">✓</div>
#                         <p>Status</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Detailed breakdown
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.write("**Categories:**")
#                     for category, count in stats['categories'].items():
#                         st.write(f"• {category}: {count:,} vectors")
                
#                 with col2:
#                     st.write("**Source Types:**")
#                     for source_type, count in stats['source_types'].items():
#                         st.write(f"• {source_type}: {count:,} vectors")
#             else:
#                 st.error(f"Error loading stats: {stats['error']}")
                
#         except Exception as e:
#             st.error(f"Error displaying knowledge base info: {str(e)}")
    
#     st.markdown("---")
    
#     # Testing interface using existing search_knowledge_base method
#     st.subheader("Test Knowledge Base Search")
    
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
    
#     if st.button("Search Knowledge Base", type="primary", use_container_width=True) and test_query:
#         with st.spinner("Searching knowledge base..."):
#             try:
#                 filter_category = None if category_filter == "None" else category_filter
                
#                 # Use existing search_knowledge_base method
#                 results = st.session_state.knowledge_base.search_knowledge_base(
#                     test_query, 
#                     limit=5, 
#                     category_filter=filter_category
#                 )
                
#                 if results:
#                     st.success(f"Found {len(results)} results")
                    
#                     for i, result in enumerate(results, 1):
#                         with st.expander(f"Result {i} - Similarity Score: {result.score:.3f}"):
#                             payload = result.payload
                            
#                             col1, col2 = st.columns([2, 1])
                            
#                             with col1:
#                                 st.write(f"**Title:** {payload['title']}")
#                                 st.write(f"**URL:** {payload['url']}")
#                                 st.write(f"**Category:** {payload['main_category']} / {payload['subcategory']}")
#                                 st.write(f"**Tags:** {', '.join(payload['tags'])}")
                            
#                             with col2:
#                                 st.metric("Confidence", f"{result.score:.1%}")
#                                 st.write(f"**Chunk:** {payload['chunk_index']}/{payload['total_chunks']}")
                            
#                             st.write("**Content Preview:**")
#                             st.write(payload['content'][:500] + "..." if len(payload['content']) > 500 else payload['content'])
                    
#                     # Test RAG response using existing method
#                     st.markdown("---")
#                     st.subheader("Generated RAG Response")
                    
#                     if st.button("Generate RAG Response", use_container_width=True):
#                         with st.spinner("Generating RAG response..."):
#                             rag_response = st.session_state.knowledge_base.generate_rag_response(
#                                 test_query,
#                                 limit=3,
#                                 category_filter=filter_category
#                             )
                            
#                             confidence_class = get_confidence_class(rag_response['confidence'])
                            
#                             st.markdown(f"""
#                             <div class="response-section">
#                                 <h4>RAG Response
#                                     <span class="confidence-indicator {confidence_class}">
#                                         Confidence: {rag_response['confidence']:.1%}
#                                     </span>
#                                 </h4>
#                                 <div style="white-space: pre-wrap;">{rag_response['answer']}</div>
#                             </div>
#                             """, unsafe_allow_html=True)
                            
#                             if rag_response['sources']:
#                                 st.write("**Sources Used:**")
#                                 for i, source in enumerate(rag_response['sources'], 1):
#                                     st.markdown(f"""
#                                     <div class="source-card">
#                                         <strong>{i}. {source['title']}</strong><br>
#                                         <a href="{source['url']}" target="_blank">{source['url']}</a><br>
#                                         Category: {source['category']} / {source['subcategory']} | Tags: {', '.join(source['tags'])}
#                                     </div>
#                                     """, unsafe_allow_html=True)
#                 else:
#                     st.warning("No results found for your query")
                    
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
#                 "Knowledge Base Info"
#             ],
#             index=1
#         )
        
#         st.markdown("---")
#         render_system_status()
    
#     # Main content based on page selection
#     if page == "Bulk Classification":
#         render_bulk_classification()
#     elif page == "Interactive Agent":
#         render_interactive_agent()
#     else:
#         render_knowledge_base_info()

# if __name__ == "__main__":
#     main()

# # import streamlit as st
# # import json
# # import time
# # import traceback
# # from datetime import datetime
# # from typing import Dict, List, Any
# # import plotly.express as px
# # import plotly.graph_objects as go
# # import pandas as pd
# # import numpy as np
# # import sys
# # import io
# # from contextlib import redirect_stdout, redirect_stderr

# # # Import our services
# # from services.knowledge_base import EnhancedAtlanKnowledgeBase
# # from services.ticket_classifier import TicketClassifier, AtlanRAGAgent
# # from config.settings import settings

# # # Set page config
# # st.set_page_config(
# #     page_title="Verbose Backend Analysis Dashboard",
# #     page_icon="🔍",
# #     layout="wide",
# #     initial_sidebar_state="expanded"
# # )

# # # Enhanced CSS for verbose display
# # st.markdown("""
# # <style>
# #     :root {
# #         --primary-color: #2E8B57;
# #         --secondary-color: #4682B4;
# #         --accent-color: #FF6B35;
# #         --success-color: #28A745;
# #         --warning-color: #FFC107;
# #         --error-color: #DC3545;
# #         --info-color: #17A2B8;
# #         --dark-bg: #1E1E1E;
# #         --light-bg: #F8F9FA;
# #         --card-bg: #FFFFFF;
# #         --text-primary: #212529;
# #         --text-secondary: #6C757D;
# #         --border-color: #DEE2E6;
# #         --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
# #         --radius: 12px;
# #     }

# #     .stApp {
# #         background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
# #     }

# #     .main-header {
# #         background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
# #         padding: 2rem;
# #         border-radius: var(--radius);
# #         color: white;
# #         text-align: center;
# #         margin-bottom: 2rem;
# #         box-shadow: var(--shadow);
# #     }

# #     .main-header h1 {
# #         margin: 0;
# #         font-size: 2.5rem;
# #         font-weight: 700;
# #     }

# #     .main-header p {
# #         margin: 0.5rem 0 0 0;
# #         font-size: 1.1rem;
# #         opacity: 0.9;
# #     }

# #     .verbose-section {
# #         background: var(--card-bg);
# #         border-radius: var(--radius);
# #         padding: 1.5rem;
# #         margin: 1rem 0;
# #         box-shadow: var(--shadow);
# #         border-left: 4px solid var(--primary-color);
# #     }

# #     .verbose-header {
# #         font-size: 1.3rem;
# #         font-weight: 600;
# #         color: var(--primary-color);
# #         margin-bottom: 1rem;
# #         display: flex;
# #         align-items: center;
# #         gap: 0.5rem;
# #     }

# #     .thought-process {
# #         background: linear-gradient(145deg, #e8f5e8, #f0f8f0);
# #         border: 2px solid var(--success-color);
# #         border-radius: var(--radius);
# #         padding: 1.5rem;
# #         margin: 1rem 0;
# #         font-family: 'Courier New', monospace;
# #         white-space: pre-wrap;
# #         line-height: 1.6;
# #     }

# #     .processing-step {
# #         background: var(--light-bg);
# #         border-left: 4px solid var(--info-color);
# #         padding: 1rem;
# #         margin: 0.5rem 0;
# #         border-radius: 0 var(--radius) var(--radius) 0;
# #     }

# #     .step-title {
# #         font-weight: 600;
# #         color: var(--info-color);
# #         margin-bottom: 0.5rem;
# #     }

# #     .console-output {
# #         background: var(--dark-bg);
# #         color: #00FF00;
# #         font-family: 'Courier New', monospace;
# #         padding: 1rem;
# #         border-radius: var(--radius);
# #         margin: 1rem 0;
# #         white-space: pre-wrap;
# #         font-size: 0.9rem;
# #         line-height: 1.4;
# #         max-height: 400px;
# #         overflow-y: auto;
# #     }

# #     .analysis-card {
# #         background: var(--card-bg);
# #         border-radius: var(--radius);
# #         padding: 1.5rem;
# #         margin: 1rem 0;
# #         box-shadow: var(--shadow);
# #         border-top: 4px solid var(--accent-color);
# #     }

# #     .metric-row {
# #         display: flex;
# #         gap: 1rem;
# #         margin: 1rem 0;
# #         flex-wrap: wrap;
# #     }

# #     .metric-card {
# #         background: var(--card-bg);
# #         border-radius: var(--radius);
# #         padding: 1rem;
# #         text-align: center;
# #         box-shadow: var(--shadow);
# #         flex: 1;
# #         min-width: 150px;
# #         border-top: 3px solid var(--primary-color);
# #     }

# #     .metric-value {
# #         font-size: 2rem;
# #         font-weight: 700;
# #         color: var(--primary-color);
# #         margin: 0;
# #     }

# #     .metric-label {
# #         font-size: 0.9rem;
# #         color: var(--text-secondary);
# #         margin-top: 0.5rem;
# #     }

# #     .status-indicator {
# #         display: inline-flex;
# #         align-items: center;
# #         padding: 0.5rem 1rem;
# #         border-radius: 20px;
# #         font-size: 0.85rem;
# #         font-weight: 600;
# #         margin: 0.25rem;
# #     }

# #     .status-success { background: #d4edda; color: #155724; }
# #     .status-warning { background: #fff3cd; color: #856404; }
# #     .status-error { background: #f8d7da; color: #721c24; }
# #     .status-info { background: #d1ecf1; color: #0c5460; }

# #     .verbose-log {
# #         background: #f8f9fa;
# #         border: 1px solid var(--border-color);
# #         border-radius: var(--radius);
# #         padding: 1rem;
# #         margin: 0.5rem 0;
# #         font-family: 'Courier New', monospace;
# #         font-size: 0.85rem;
# #         white-space: pre-wrap;
# #     }

# #     .classification-result {
# #         background: linear-gradient(145deg, #e3f2fd, #f3f9ff);
# #         border: 2px solid var(--info-color);
# #         border-radius: var(--radius);
# #         padding: 1.5rem;
# #         margin: 1rem 0;
# #     }

# #     .rag-response {
# #         background: linear-gradient(145deg, #fff8e1, #fffde7);
# #         border: 2px solid var(--warning-color);
# #         border-radius: var(--radius);
# #         padding: 1.5rem;
# #         margin: 1rem 0;
# #     }

# #     .source-item {
# #         background: var(--light-bg);
# #         border-left: 4px solid var(--accent-color);
# #         padding: 1rem;
# #         margin: 0.5rem 0;
# #         border-radius: 0 var(--radius) var(--radius) 0;
# #     }

# #     .expandable-section {
# #         border: 1px solid var(--border-color);
# #         border-radius: var(--radius);
# #         margin: 1rem 0;
# #         overflow: hidden;
# #     }

# #     .section-header {
# #         background: var(--light-bg);
# #         padding: 1rem;
# #         font-weight: 600;
# #         cursor: pointer;
# #         border-bottom: 1px solid var(--border-color);
# #     }

# #     .section-content {
# #         padding: 1rem;
# #         background: var(--card-bg);
# #     }
# # </style>
# # """, unsafe_allow_html=True)

# # class VerboseLogger:
# #     """Captures and displays verbose output from backend processes"""
    
# #     def __init__(self):
# #         self.logs = []
# #         self.current_step = None
    
# #     def log_step(self, step_name: str, details: str = ""):
# #         """Log a processing step"""
# #         timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
# #         self.logs.append({
# #             'timestamp': timestamp,
# #             'type': 'step',
# #             'step': step_name,
# #             'details': details
# #         })
    
# #     def log_thought(self, thought: str):
# #         """Log AI thought process"""
# #         timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
# #         self.logs.append({
# #             'timestamp': timestamp,
# #             'type': 'thought',
# #             'content': thought
# #         })
    
# #     def log_output(self, output: str, output_type: str = 'info'):
# #         """Log system output"""
# #         timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
# #         self.logs.append({
# #             'timestamp': timestamp,
# #             'type': 'output',
# #             'output_type': output_type,
# #             'content': output
# #         })
    
# #     def get_logs(self) -> List[Dict]:
# #         """Get all logs"""
# #         return self.logs
    
# #     def clear_logs(self):
# #         """Clear all logs"""
# #         self.logs = []

# # def initialize_session_state():
# #     """Initialize session state with verbose logging"""
# #     if 'verbose_logger' not in st.session_state:
# #         st.session_state.verbose_logger = VerboseLogger()
    
# #     if 'knowledge_base' not in st.session_state:
# #         st.session_state.verbose_logger.log_step("Initializing Knowledge Base")
# #         try:
# #             st.session_state.knowledge_base = EnhancedAtlanKnowledgeBase()
# #             st.session_state.kb_status = "ready"
# #             st.session_state.verbose_logger.log_output("✅ Knowledge Base initialized successfully", "success")
# #         except Exception as e:
# #             st.session_state.kb_status = "error"
# #             st.session_state.verbose_logger.log_output(f"❌ Knowledge Base initialization failed: {str(e)}", "error")
    
# #     if 'classifier' not in st.session_state:
# #         st.session_state.verbose_logger.log_step("Initializing Ticket Classifier")
# #         try:
# #             st.session_state.classifier = TicketClassifier()
# #             st.session_state.classifier_status = "ready"
# #             st.session_state.verbose_logger.log_output("✅ Ticket Classifier initialized successfully", "success")
# #         except Exception as e:
# #             st.session_state.classifier_status = "error"
# #             st.session_state.verbose_logger.log_output(f"❌ Classifier initialization failed: {str(e)}", "error")
    
# #     if 'rag_agent' not in st.session_state and st.session_state.get('knowledge_base'):
# #         st.session_state.verbose_logger.log_step("Initializing RAG Agent")
# #         try:
# #             st.session_state.rag_agent = AtlanRAGAgent(st.session_state.knowledge_base)
# #             st.session_state.agent_status = "ready"
# #             st.session_state.verbose_logger.log_output("✅ RAG Agent initialized successfully", "success")
# #         except Exception as e:
# #             st.session_state.agent_status = "error"
# #             st.session_state.verbose_logger.log_output(f"❌ RAG Agent initialization failed: {str(e)}", "error")

# # def render_header():
# #     """Render the main header"""
# #     st.markdown("""
# #     <div class="main-header">
# #         <h1>🔍 Verbose Backend Analysis Dashboard</h1>
# #         <p>Comprehensive AI Processing with Detailed Thought Analysis & System Monitoring</p>
# #     </div>
# #     """, unsafe_allow_html=True)

# # def render_system_status():
# #     """Render detailed system status"""
# #     st.markdown("### 🖥️ System Status & Health")
    
# #     col1, col2, col3 = st.columns(3)
    
# #     with col1:
# #         kb_status = st.session_state.get('kb_status', 'unknown')
# #         status_class = 'status-success' if kb_status == 'ready' else 'status-error' if kb_status == 'error' else 'status-warning'
# #         st.markdown(f'<div class="{status_class}">Knowledge Base: {kb_status.title()}</div>', unsafe_allow_html=True)
    
# #     with col2:
# #         classifier_status = st.session_state.get('classifier_status', 'unknown')
# #         status_class = 'status-success' if classifier_status == 'ready' else 'status-error' if classifier_status == 'error' else 'status-warning'
# #         st.markdown(f'<div class="{status_class}">Classifier: {classifier_status.title()}</div>', unsafe_allow_html=True)
    
# #     with col3:
# #         agent_status = st.session_state.get('agent_status', 'unknown')
# #         status_class = 'status-success' if agent_status == 'ready' else 'status-error' if agent_status == 'error' else 'status-warning'
# #         st.markdown(f'<div class="{status_class}">RAG Agent: {agent_status.title()}</div>', unsafe_allow_html=True)

# # def capture_verbose_output(func, *args, **kwargs):
# #     """Capture verbose output from function execution"""
# #     # Capture stdout and stderr
# #     old_stdout = sys.stdout
# #     old_stderr = sys.stderr
    
# #     stdout_capture = io.StringIO()
# #     stderr_capture = io.StringIO()
    
# #     try:
# #         sys.stdout = stdout_capture
# #         sys.stderr = stderr_capture
        
# #         result = func(*args, **kwargs)
        
# #         stdout_content = stdout_capture.getvalue()
# #         stderr_content = stderr_capture.getvalue()
        
# #         return result, stdout_content, stderr_content
        
# #     finally:
# #         sys.stdout = old_stdout
# #         sys.stderr = old_stderr

# # def render_verbose_classification():
# #     """Render verbose ticket classification interface"""
# #     st.markdown("## 🎯 Verbose Ticket Classification Analysis")
    
# #     # Sample tickets for testing
# #     sample_tickets = [
# #         "Connecting Snowflake to Atlan - required permissions? Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing.",
# #         "Data lineage not showing downstream impacts. Our data lineage view isn't capturing all the downstream transformations in our dbt models.",
# #         "API authentication failing with 401 errors. I'm trying to use the Atlan Python SDK to automate some metadata updates, but I keep getting 401 authentication errors.",
# #         "How to implement SSO with Okta? We need to set up Single Sign-On integration with our Okta identity provider.",
# #         "Best practices for data governance policies. We're looking for recommendations on how to structure our data governance framework in Atlan."
# #     ]
    
# #     # Ticket selection
# #     selected_ticket = st.selectbox(
# #         "Select a ticket to analyze:",
# #         sample_tickets,
# #         format_func=lambda x: x[:80] + "..." if len(x) > 80 else x
# #     )
    
# #     # Custom ticket input
# #     custom_ticket = st.text_area(
# #         "Or enter your own ticket:",
# #         placeholder="Enter ticket description here...",
# #         height=100
# #     )
    
# #     ticket_to_analyze = custom_ticket if custom_ticket.strip() else selected_ticket
    
# #     col1, col2 = st.columns([3, 1])
# #     with col1:
# #         if st.button("🔍 Analyze Ticket with Verbose Output", type="primary", use_container_width=True):
# #             analyze_ticket_verbose(ticket_to_analyze)
    
# #     with col2:
# #         if st.button("🧹 Clear Logs", use_container_width=True):
# #             st.session_state.verbose_logger.clear_logs()
# #             st.rerun()

# # def analyze_ticket_verbose(ticket_text: str):
# #     """Analyze ticket with comprehensive verbose output"""
# #     if not st.session_state.get('classifier') or st.session_state.get('classifier_status') != 'ready':
# #         st.error("❌ Classifier not available")
# #         return
    
# #     st.session_state.verbose_logger.clear_logs()
# #     st.session_state.verbose_logger.log_step("Starting Ticket Analysis", f"Analyzing: {ticket_text[:100]}...")
    
# #     # Create containers for real-time updates
# #     status_container = st.container()
# #     thought_container = st.container()
# #     classification_container = st.container()
# #     rag_container = st.container()
# #     logs_container = st.container()
    
# #     with status_container:
# #         st.markdown("### 🔄 Processing Status")
# #         progress_bar = st.progress(0)
# #         status_text = st.empty()
    
# #     # Step 1: Classification
# #     status_text.text("🤖 Classifying ticket...")
# #     progress_bar.progress(25)
    
# #     try:
# #         # Capture classification output
# #         st.session_state.verbose_logger.log_step("Ticket Classification", "Sending to LLM for analysis")
        
# #         classification_result, stdout_output, stderr_output = capture_verbose_output(
# #             st.session_state.classifier.classify_ticket, 
# #             ticket_text
# #         )
        
# #         # Log the captured output
# #         if stdout_output:
# #             st.session_state.verbose_logger.log_output(stdout_output, "classification")
# #         if stderr_output:
# #             st.session_state.verbose_logger.log_output(stderr_output, "error")
        
# #         progress_bar.progress(50)
# #         status_text.text("✅ Classification completed")
        
# #         # Display classification results
# #         with classification_container:
# #             st.markdown("### 🏷️ Classification Results")
            
# #             col1, col2, col3 = st.columns(3)
# #             with col1:
# #                 st.markdown(f"""
# #                 <div class="metric-card">
# #                     <div class="metric-value">{classification_result['topic']}</div>
# #                     <div class="metric-label">Topic</div>
# #                 </div>
# #                 """, unsafe_allow_html=True)
            
# #             with col2:
# #                 st.markdown(f"""
# #                 <div class="metric-card">
# #                     <div class="metric-value">{classification_result['sentiment']}</div>
# #                     <div class="metric-label">Sentiment</div>
# #                 </div>
# #                 """, unsafe_allow_html=True)
            
# #             with col3:
# #                 st.markdown(f"""
# #                 <div class="metric-card">
# #                     <div class="metric-value">{classification_result['priority']}</div>
# #                     <div class="metric-label">Priority</div>
# #                 </div>
# #                 """, unsafe_allow_html=True)
            
# #             st.markdown(f"""
# #             <div class="classification-result">
# #                 <h4>🧠 AI Reasoning Process:</h4>
# #                 <div class="thought-process">{classification_result['reasoning']}</div>
# #             </div>
# #             """, unsafe_allow_html=True)
        
# #         # Step 2: RAG Response Generation
# #         if st.session_state.get('rag_agent') and st.session_state.get('agent_status') == 'ready':
# #             status_text.text("🔍 Generating RAG response...")
# #             progress_bar.progress(75)
            
# #             st.session_state.verbose_logger.log_step("RAG Response Generation", "Searching knowledge base and generating response")
            
# #             try:
# #                 rag_result, rag_stdout, rag_stderr = capture_verbose_output(
# #                     st.session_state.rag_agent.generate_response,
# #                     ticket_text,
# #                     classification_result
# #                 )
                
# #                 # Log RAG output
# #                 if rag_stdout:
# #                     st.session_state.verbose_logger.log_output(rag_stdout, "rag")
# #                 if rag_stderr:
# #                     st.session_state.verbose_logger.log_output(rag_stderr, "error")
                
# #                 progress_bar.progress(100)
# #                 status_text.text("✅ Analysis completed successfully")
                
# #                 # Display RAG results
# #                 with rag_container:
# #                     st.markdown("### 🤖 RAG System Response")
                    
# #                     st.markdown(f"""
# #                     <div class="rag-response">
# #                         <h4>📝 Generated Response:</h4>
# #                         <div style="white-space: pre-wrap; line-height: 1.6;">{rag_result.get('answer', 'No response generated')}</div>
# #                         <br>
# #                         <small><strong>Response Type:</strong> {rag_result.get('response_type', 'unknown')}</small>
# #                     </div>
# #                     """, unsafe_allow_html=True)
                    
# #                     # Show intermediate steps if available
# #                     if rag_result.get('intermediate_steps'):
# #                         with st.expander("🔍 View RAG Processing Steps"):
# #                             for i, step in enumerate(rag_result['intermediate_steps'], 1):
# #                                 st.markdown(f"""
# #                                 <div class="processing-step">
# #                                     <div class="step-title">Step {i}</div>
# #                                     <div>{step}</div>
# #                                 </div>
# #                                 """, unsafe_allow_html=True)
                
# #             except Exception as e:
# #                 st.session_state.verbose_logger.log_output(f"❌ RAG generation error: {str(e)}", "error")
# #                 st.error(f"RAG generation failed: {str(e)}")
        
# #     except Exception as e:
# #         st.session_state.verbose_logger.log_output(f"❌ Classification error: {str(e)}", "error")
# #         st.error(f"Classification failed: {str(e)}")
    
# #     # Display comprehensive logs
# #     with logs_container:
# #         render_verbose_logs()

# # def render_verbose_logs():
# #     """Render comprehensive verbose logs"""
# #     st.markdown("### 📋 Comprehensive System Logs")
    
# #     logs = st.session_state.verbose_logger.get_logs()
    
# #     if not logs:
# #         st.info("No logs available. Run an analysis to see verbose output.")
# #         return
    
# #     # Log filtering
# #     col1, col2 = st.columns([3, 1])
# #     with col1:
# #         log_filter = st.selectbox(
# #             "Filter logs by type:",
# #             ["All", "Steps", "Thoughts", "Classification", "RAG", "Errors"],
# #             index=0
# #         )
    
# #     with col2:
# #         if st.button("📥 Export Logs"):
# #             log_text = "\n".join([f"[{log['timestamp']}] {log.get('content', log.get('step', 'Unknown'))}" for log in logs])
# #             st.download_button(
# #                 "Download Logs",
# #                 log_text,
# #                 file_name=f"verbose_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
# #                 mime="text/plain"
# #             )
    
# #     # Display filtered logs
# #     filtered_logs = logs
# #     if log_filter != "All":
# #         filter_map = {
# #             "Steps": "step",
# #             "Thoughts": "thought", 
# #             "Classification": "output",
# #             "RAG": "output",
# #             "Errors": "output"
# #         }
# #         log_type = filter_map.get(log_filter, "step")
        
# #         if log_filter == "Classification":
# #             filtered_logs = [log for log in logs if log.get('type') == 'output' and log.get('output_type') == 'classification']
# #         elif log_filter == "RAG":
# #             filtered_logs = [log for log in logs if log.get('type') == 'output' and log.get('output_type') == 'rag']
# #         elif log_filter == "Errors":
# #             filtered_logs = [log for log in logs if log.get('type') == 'output' and log.get('output_type') == 'error']
# #         else:
# #             filtered_logs = [log for log in logs if log.get('type') == log_type]
    
# #     # Display logs in console-style format
# #     if filtered_logs:
# #         console_output = ""
# #         for log in filtered_logs:
# #             timestamp = log['timestamp']
            
# #             if log['type'] == 'step':
# #                 console_output += f"[{timestamp}] 🔄 STEP: {log['step']}\n"
# #                 if log.get('details'):
# #                     console_output += f"    Details: {log['details']}\n"
            
# #             elif log['type'] == 'thought':
# #                 console_output += f"[{timestamp}] 🧠 THOUGHT: {log['content']}\n"
            
# #             elif log['type'] == 'output':
# #                 output_type = log.get('output_type', 'info')
# #                 emoji = {'success': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(output_type, 'ℹ️')
# #                 console_output += f"[{timestamp}] {emoji} OUTPUT ({output_type.upper()}): {log['content']}\n"
            
# #             console_output += "\n"
        
# #         st.markdown(f"""
# #         <div class="console-output">{console_output}</div>
# #         """, unsafe_allow_html=True)
# #     else:
# #         st.info(f"No logs found for filter: {log_filter}")

# # def render_knowledge_base_testing():
# #     """Render knowledge base testing interface"""
# #     st.markdown("## 📚 Knowledge Base Verbose Testing")
    
# #     if not st.session_state.get('knowledge_base') or st.session_state.get('kb_status') != 'ready':
# #         st.error("❌ Knowledge Base not available")
# #         return
    
# #     # Test query input
# #     test_query = st.text_input(
# #         "Enter test query:",
# #         placeholder="e.g., How to authenticate with Atlan API?",
# #         value="How to set up lineage in Atlan?"
# #     )
    
# #     col1, col2 = st.columns([2, 1])
# #     with col1:
# #         search_limit = st.slider("Number of results:", 1, 10, 3)
    
# #     with col2:
# #         category_filter = st.selectbox(
# #             "Category filter:",
# #             ["None", "product_documentation", "developer_hub"],
# #             index=0
# #         )
    
# #     if st.button("🔍 Test Knowledge Base Search", type="primary", use_container_width=True) and test_query:
# #         st.session_state.verbose_logger.log_step("Knowledge Base Search", f"Query: {test_query}")
        
# #         try:
# #             # Test search
# #             filter_cat = None if category_filter == "None" else category_filter
            
# #             search_results = st.session_state.knowledge_base.search_knowledge_base(
# #                 test_query,
# #                 limit=search_limit,
# #                 category_filter=filter_cat
# #             )
            
# #             st.session_state.verbose_logger.log_output(f"✅ Found {len(search_results)} search results", "success")
            
# #             # Display search results
# #             st.markdown("### 🔍 Search Results")
            
# #             for i, result in enumerate(search_results, 1):
# #                 with st.expander(f"Result {i} • Confidence: {result.score:.1%}"):
# #                     payload = result.payload
                    
# #                     col1, col2 = st.columns([2, 1])
                    
# #                     with col1:
# #                         st.markdown(f"**📌 Title:** {payload['title']}")
# #                         st.markdown(f"**🔗 URL:** [{payload['url']}]({payload['url']})")
# #                         st.markdown(f"**📂 Category:** {payload['main_category']} / {payload['subcategory']}")
# #                         st.markdown(f"**🏷️ Tags:** {', '.join(payload['tags'])}")
                    
# #                     with col2:
# #                         st.metric("Confidence Score", f"{result.score:.1%}")
# #                         st.metric("Chunk", f"{payload['chunk_index']}/{payload['total_chunks']}")
                    
# #                     st.markdown("**📝 Content Preview:**")
# #                     st.info(payload['content'][:300] + "..." if len(payload['content']) > 300 else payload['content'])
            
# #             # Test RAG response
# #             st.markdown("### 🤖 RAG Response Generation")
            
# #             if st.button("Generate RAG Response", use_container_width=True):
# #                 st.session_state.verbose_logger.log_step("RAG Response Generation", "Generating comprehensive response")
                
# #                 rag_response = st.session_state.knowledge_base.generate_rag_response(
# #                     test_query,
# #                     limit=search_limit,
# #                     category_filter=filter_cat
# #                 )
                
# #                 st.session_state.verbose_logger.log_output(f"✅ RAG response generated with {rag_response['confidence']:.1%} confidence", "success")
                
# #                 # Display RAG response
# #                 st.markdown(f"""
# #                 <div class="rag-response">
# #                     <h4>🤖 Generated Response (Confidence: {rag_response['confidence']:.1%})</h4>
# #                     <div style="white-space: pre-wrap; line-height: 1.6;">{rag_response['answer']}</div>
# #                 </div>
# #                 """, unsafe_allow_html=True)
                
# #                 # Display sources
# #                 if rag_response.get('sources'):
# #                     st.markdown("### 📖 Sources Used")
# #                     for i, source in enumerate(rag_response['sources'], 1):
# #                         st.markdown(f"""
# #                         <div class="source-item">
# #                             <strong>{i}. {source['title']}</strong><br>
# #                             <a href="{source['url']}" target="_blank">{source['url']}</a><br>
# #                             <small>Category: {source['category']}/{source['subcategory']} | Tags: {', '.join(source['tags'])}</small>
# #                         </div>
# #                         """, unsafe_allow_html=True)
        
# #         except Exception as e:
# #             st.session_state.verbose_logger.log_output(f"❌ Knowledge base test error: {str(e)}", "error")
# #             st.error(f"Test failed: {str(e)}")

# # def main():
# #     """Main Streamlit application"""
# #     initialize_session_state()
# #     render_header()
    
# #     # Sidebar navigation
# #     with st.sidebar:
# #         st.title("🔍 Navigation")
        
# #         page = st.radio(
# #             "Select Analysis View:",
# #             [
# #                 "🎯 Verbose Classification",
# #                 "📚 Knowledge Base Testing", 
# #                 "📋 System Logs",
# #                 "🖥️ System Status"
# #             ],
# #             index=0
# #         )
        
# #         st.markdown("---")
# #         st.markdown("### ⚙️ System Health")
# #         render_system_status()
        
# #         st.markdown("---")
# #         st.markdown("### 📊 Quick Stats")
        
# #         logs = st.session_state.verbose_logger.get_logs()
# #         st.metric("Total Log Entries", len(logs))
        
# #         error_logs = [log for log in logs if log.get('output_type') == 'error']
# #         st.metric("Error Count", len(error_logs))
        
# #         success_logs = [log for log in logs if log.get('output_type') == 'success']
# #         st.metric("Success Count", len(success_logs))
    
# #     # Main content
# #     if page == "🎯 Verbose Classification":
# #         render_verbose_classification()
# #     elif page == "📚 Knowledge Base Testing":
# #         render_knowledge_base_testing()
# #     elif page == "📋 System Logs":
# #         st.markdown("## 📋 Complete System Logs")
# #         render_verbose_logs()
# #     elif page == "🖥️ System Status":
# #         st.markdown("## 🖥️ Detailed System Status")
# #         render_system_status()
        
# #         # Additional system information
# #         st.markdown("### 📈 System Performance Metrics")
        
# #         col1, col2, col3, col4 = st.columns(4)
        
# #         with col1:
# #             st.markdown("""
# #             <div class="metric-card">
# #                 <div class="metric-value">98.5%</div>
# #                 <div class="metric-label">Uptime</div>
# #             </div>
# #             """, unsafe_allow_html=True)
        
# #         with col2:
# #             st.markdown("""
# #             <div class="metric-card">
# #                 <div class="metric-value">1.2s</div>
# #                 <div class="metric-label">Avg Response</div>
# #             </div>
# #             """, unsafe_allow_html=True)
        
# #         with col3:
# #             st.markdown("""
# #             <div class="metric-card">
# #                 <div class="metric-value">87%</div>
# #                 <div class="metric-label">Classification Accuracy</div>
# #             </div>
# #             """, unsafe_allow_html=True)
        
# #         with col4:
# #             st.markdown("""
# #             <div class="metric-card">
# #                 <div class="metric-value">2.7K</div>
# #                 <div class="metric-label">KB Documents</div>
# #             </div>
# #             """, unsafe_allow_html=True)

# # if __name__ == "__main__":
# #     main()

import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import time
import traceback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Import our custom modules
from services.knowledge_base import EnhancedAtlanKnowledgeBase
from services.ticket_classifier import TicketClassifier, AtlanRAGAgent

# Set page config
st.set_page_config(
    page_title="Atlan AI Helpdesk System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling with cleaner, more modern approach
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Headers */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        transform: rotate(30deg);
    }
    
    .main-header h1 {
        margin: 0 0 1rem 0;
        font-size: 3.5rem;
        font-weight: 700;
        position: relative;
        z-index: 2;
        line-height: 1.2;
    }
    
    .main-header p {
        font-size: 1.3rem;
        opacity: 0.95;
        position: relative;
        z-index: 2;
        font-weight: 400;
    }
    
    .sub-header {
        font-size: 2rem;
        font-weight: 600;
        color: #4F46E5;
        margin: 2.5rem 0 1.5rem 0;
        border-bottom: 3px solid #E5E7EB;
        padding-bottom: 0.75rem;
        display: inline-block;
    }
    
    /* Stats cards container */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border-top: 5px solid transparent;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    }
    
    .stat-card.primary { border-top-color: #667eea; }
    .stat-card.success { border-top-color: #4ade80; }
    .stat-card.warning { border-top-color: #fbbf24; }
    .stat-card.info { border-top-color: #06b6d4; }
    
    .stat-number {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #6B7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Ticket cards */
    .ticket-card {
        background: white;
        border-radius: 18px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .ticket-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
    }
    
    .ticket-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .ticket-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .ticket-id {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: #475569;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .ticket-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0.75rem 0;
        line-height: 1.4;
        flex: 1;
    }
    
    .ticket-body {
        color: #64748b;
        line-height: 1.7;
        margin: 1.5rem 0;
        font-size: 1rem;
    }
    
    .ticket-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #f1f5f9;
        font-size: 0.9rem;
        color: #64748b;
    }
    
    /* Classification badges */
    .classification-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin: 1.5rem 0;
    }
    
    .classification-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .classification-badge:hover {
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
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
    
    .priority-high { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    .priority-medium { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .priority-low { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    
    /* Response containers */
    .response-container {
        background: white;
        border-radius: 18px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 1px solid #f1f5f9;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        position: relative;
    }
    
    .response-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4ade80 0%, #22c55e 100%);
        border-radius: 18px 18px 0 0;
    }
    
    .analysis-container {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #f59e0b;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    
    .analysis-container h4 {
        color: #92400e;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    .rag-response-container {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    .rag-response-container h4 {
        color: #1e40af;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .verbose-logs {
        background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #8b5cf6;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);
        position: relative;
    }
    
    .verbose-logs h4 {
        color: #6b21a8;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    .verbose-logs pre {
        background: rgba(255, 255, 255, 0.7);
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        border: 1px solid rgba(139, 92, 246, 0.2);
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    /* Sources styling */
    .sources-container {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .sources-container h4 {
        color: #334155;
        font-weight: 600;
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .source-item {
        display: flex;
        align-items: flex-start;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        text-decoration: none;
        color: inherit;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .source-item:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
        background: #fafbff;
    }
    
    .source-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        margin-right: 1.5rem;
        flex-shrink: 0;
    }
    
    .source-content {
        flex: 1;
    }
    
    .source-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        line-height: 1.4;
    }
    
    .source-url {
        font-size: 0.85rem;
        color: #64748b;
        word-break: break-all;
        margin-bottom: 0.5rem;
    }
    
    .source-meta {
        font-size: 0.8rem;
        color: #94a3b8;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    /* Confidence indicators */
    .confidence-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-left: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .confidence-high { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    .confidence-medium { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    .confidence-low { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
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
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Form styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        padding: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.3rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .status-ready { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    .status-error { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    .status-warning { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    /* Empty states */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 20px;
        margin: 2rem 0;
        border: 2px dashed #cbd5e1;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        opacity: 0.6;
    }
    
    .empty-state h3 {
        color: #475569;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    .empty-state p {
        color: #64748b;
        margin-bottom: 2rem;
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
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .animate-fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .animate-slide-in-right {
        animation: slideInRight 0.5s ease-out;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .stats-container {
            grid-template-columns: 1fr;
        }
        
        .ticket-header {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .classification-badges {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .source-item {
            flex-direction: column;
            text-align: center;
        }
        
        .source-icon {
            margin: 0 0 1rem 0;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
</style>
""", unsafe_allow_html=True)

# Analytics service (mock implementation)
class AnalyticsService:
    def generate_topic_trends(self, tickets):
        topics = {}
        for ticket in tickets:
            topic = ticket['classification']['topic']
            topics[topic] = topics.get(topic, 0) + 1
        
        return {
            'topic_frequency': dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)),
            'total_tickets': len(tickets)
        }
    
    def calculate_satisfaction_metrics(self, tickets):
        sentiments = {}
        for ticket in tickets:
            sentiment = ticket['classification']['sentiment']
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        nps_score = 75  # Mock NPS calculation
        return {
            'satisfaction_distribution': sentiments,
            'nps_score': nps_score
        }
    
    def generate_workload_distribution(self, tickets):
        # Mock workload distribution
        return {
            'by_priority': {'High': 25, 'Medium': 50, 'Low': 25},
            'by_complexity': {'Simple': 40, 'Moderate': 45, 'Complex': 15}
        }
    
    def generate_performance_metrics(self, tickets):
        # Mock performance metrics
        return {
            'total_processed': len(tickets),
            'auto_resolution_rate_percent': 65,
            'avg_processing_time_seconds': 124,
            'avg_classification_confidence': 0.87,
            'efficiency_score': 8.7
        }

analytics_service = AnalyticsService()

def load_sample_tickets() -> List[Dict[str, Any]]:
    """Load sample tickets from JSON file or return default data"""
    try:
        json_path = "data/sample_tickets.json"
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
    except Exception:
        pass

    return [
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

def initialize_session_state():
    """Initialize all session state variables"""
    
    if 'sample_tickets' not in st.session_state:
        st.session_state.sample_tickets = load_sample_tickets()
    
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None
        st.session_state.kb_status = "initializing"
        
        with st.spinner("Initializing Atlan Knowledge Base..."):
            try:
                st.session_state.knowledge_base = EnhancedAtlanKnowledgeBase()
                st.session_state.kb_status = "ready"
                st.success("Knowledge Base initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize Knowledge Base: {str(e)}")
                st.session_state.kb_status = "error"
                if "429" in str(e):
                    st.info("Rate limit detected. Please wait and refresh the page.")
    
    if 'classifier' not in st.session_state:
        if st.session_state.knowledge_base and st.session_state.kb_status == "ready":
            try:
                st.session_state.classifier = TicketClassifier()
                st.session_state.classifier_status = "ready"
            except Exception as e:
                st.session_state.classifier_status = "error"
                st.session_state.classifier = None
        else:
            st.session_state.classifier_status = "waiting"
            st.session_state.classifier = None
    
    if 'rag_agent' not in st.session_state:
        if st.session_state.knowledge_base and st.session_state.kb_status == "ready":
            try:
                st.session_state.rag_agent = AtlanRAGAgent(st.session_state.knowledge_base)
                st.session_state.agent_status = "ready"
            except Exception as e:
                st.session_state.agent_status = "error"
                st.session_state.rag_agent = None
        else:
            st.session_state.agent_status = "waiting"
            st.session_state.rag_agent = None

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header animate-fade-in-up">
        <h1>Atlan AI Helpdesk System</h1>
        <p>Intelligent ticket classification with RAG-powered responses</p>
    </div>
    """, unsafe_allow_html=True)

def get_confidence_class(confidence: float) -> str:
    """Get CSS class for confidence level"""
    if confidence >= 0.8:
        return "confidence-high"
    elif confidence >= 0.5:
        return "confidence-medium"
    else:
        return "confidence-low"

def render_classification_badges(classification: Dict[str, Any]) -> str:
    """Render classification badges with proper styling"""
    topic = classification.get('topic', 'Unknown')
    sentiment = classification.get('sentiment', 'Neutral')
    priority = classification.get('priority', 'Medium')
    
    return f"""
    <div class="classification-badges">
        <span class="classification-badge topic-badge">📂 {topic}</span>
        <span class="classification-badge sentiment-badge">😊 {sentiment}</span>
        <span class="classification-badge priority-badge priority-{priority.lower().replace(' ', '')}">⚡ {priority}</span>
    </div>
    """

def render_bulk_classification():
    """Render bulk ticket classification dashboard"""
    st.markdown('<h2 class="sub-header">Bulk Ticket Classification Dashboard</h2>', unsafe_allow_html=True)
    
    if not st.session_state.classifier or st.session_state.classifier_status != "ready":
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <h3>Classifier Not Available</h3>
            <p>Please check system status and try again</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🚀 Classify All Tickets", type="primary", use_container_width=True):
            classify_all_tickets()
    
    with col2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            if 'classified_tickets' in st.session_state:
                del st.session_state.classified_tickets
            st.rerun()
    
    if hasattr(st.session_state, 'classified_tickets'):
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-card primary">
                <div class="stat-number">{len(st.session_state.classified_tickets)}</div>
                <div class="stat-label">Classified Tickets</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 class="sub-header">Classification Results</h3>', unsafe_allow_html=True)
        
        for ticket in st.session_state.classified_tickets:
            st.markdown(f"""
            <div class="ticket-card animate-fade-in-up">
                <div class="ticket-header">
                    <div class="ticket-id">{ticket['id']}</div>
                    <div class="ticket-title">{ticket['subject']}</div>
                </div>
                
                <div class="ticket-body">
                    {ticket['body'][:300]}{'...' if len(ticket['body']) > 300 else ''}
                </div>
                
                {render_classification_badges(ticket['classification'])}
                
                <div class="analysis-container">
                    <h4>AI Analysis</h4>
                    <p><strong>Reasoning:</strong> {ticket['classification']['reasoning']}</p>
                </div>
                
                <div class="ticket-meta">
                    <span>Classified: {ticket['classified_at'][:19].replace('T', ' ')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <h3>No Classifications Yet</h3>
            <p>Click "Classify All Tickets" to begin automated classification</p>
        </div>
        """, unsafe_allow_html=True)

def classify_all_tickets():
    """Classify all tickets with rate limiting"""
    st.session_state.classified_tickets = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticket in enumerate(st.session_state.sample_tickets):
        status_text.text(f'Classifying ticket {i+1}/{len(st.session_state.sample_tickets)}: {ticket["subject"]}')
        
        try:
            if i > 0:
                time.sleep(2)
                
            ticket_text = f"Subject: {ticket['subject']}\nBody: {ticket['body']}"
            classification = st.session_state.classifier.classify_ticket(ticket_text)
            
            classified_ticket = {
                **ticket,
                "classification": classification,
                "classified_at": datetime.now().isoformat()
            }
            st.session_state.classified_tickets.append(classified_ticket)
            
        except Exception as e:
            st.error(f"Error classifying ticket {ticket['id']}: {str(e)}")
            if "429" in str(e):
                st.warning("Rate limit hit - please wait before retrying")
                break
        
        progress_bar.progress((i + 1) / len(st.session_state.sample_tickets))
    
    status_text.text('Classification completed!')
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

def render_interactive_agent():
    """Render interactive AI agent interface"""
    st.markdown('<h2 class="sub-header">Interactive AI Agent with RAG System</h2>', unsafe_allow_html=True)
    
    if not all([
        st.session_state.classifier and st.session_state.classifier_status == "ready",
        st.session_state.rag_agent and st.session_state.agent_status == "ready",
        st.session_state.knowledge_base and st.session_state.kb_status == "ready"
    ]):
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🤖</div>
            <h3>AI Agent Not Available</h3>
            <p>System initialization incomplete - please check system status</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    with st.form("query_form", clear_on_submit=False):
        user_query = st.text_area(
            "Submit your question or support ticket:",
            placeholder="e.g., How do I set up SSO with Okta in Atlan?\ne.g., What permissions are needed for Snowflake connector?",
            height=120,
            help="Enter your technical question or support request for intelligent analysis and response"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submit_button = st.form_submit_button("Process Query", type="primary", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("Clear", use_container_width=True)
    
    if submit_button and user_query.strip():
        st.markdown("---")
        
        # Step 1: Classification
        st.markdown("### Query Analysis")
        with st.spinner("Analyzing query..."):
            try:
                classification = st.session_state.classifier.classify_ticket(user_query)
                
                st.markdown(f"""
                <div class="analysis-container animate-slide-in-right">
                    <h4>🔍 Classification Results</h4>
                    {render_classification_badges(classification)}
                    <div style="margin-top: 1rem;">
                        <strong>AI Reasoning:</strong><br>
                        <em>{classification['reasoning']}</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Classification error: {str(e)}")
                return
        
        # Step 2: Generate RAG response
        st.markdown("### AI Response")
        
        with st.spinner("Generating intelligent response using RAG system..."):
            try:
                # Use existing generate_rag_response method from knowledge base
                rag_response = st.session_state.knowledge_base.generate_rag_response(
                    user_query,
                    limit=3
                )
                
                # Get confidence from the response
                confidence = rag_response.get('confidence', 0.0)
                confidence_class = get_confidence_class(confidence)
                
                # Generate agent response with RAG context
                response_data = st.session_state.rag_agent.generate_response(
                    user_query, 
                    classification
                )
                
                # Display response with confidence
                st.markdown(f"""
                <div class="rag-response-container animate-fade-in-up">
                    <h4>🤖 Generated Response
                        <span class="confidence-indicator {confidence_class}">
                            Confidence: {confidence:.1%}
                        </span>
                    </h4>
                    <div style="white-space: pre-wrap; line-height: 1.6; font-size: 1rem;">
                        {rag_response.get('answer', 'No response generated')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display verbose logs if available
                if response_data and 'verbose_log' in response_data:
                    st.markdown(f"""
                    <div class="verbose-logs animate-fade-in-up">
                        <h4>🔧 Processing Details</h4>
                        <pre>{response_data['verbose_log']}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display sources if available
                if rag_response.get('sources'):
                    st.markdown(f"""
                    <div class="sources-container animate-slide-in-right">
                        <h4>📚 Knowledge Sources ({len(rag_response['sources'])} found)</h4>
                    """, unsafe_allow_html=True)
                    
                    for i, source in enumerate(rag_response['sources'], 1):
                        st.markdown(f"""
                        <div class="source-item">
                            <div class="source-icon">{i}</div>
                            <div class="source-content">
                                <div class="source-title">{source['title']}</div>
                                <div class="source-url">
                                    <a href="{source['url']}" target="_blank">{source['url']}</a>
                                </div>
                                <div class="source-meta">
                                    <span>Category: {source['category']} / {source['subcategory']}</span>
                                    <span>Tags: {', '.join(source['tags'])}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                if "429" in str(e):
                    st.info("Rate limit detected. Please wait before trying again.")

def render_knowledge_base_info():
    """Render knowledge base information and testing interface"""
    st.markdown('<h2 class="sub-header">Knowledge Base Information & Testing</h2>', unsafe_allow_html=True)

    if not st.session_state.knowledge_base or st.session_state.kb_status != "ready":
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📚</div>
            <h3>Knowledge Base Not Available</h3>
            <p>Please check system initialization status</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Stats section
    with st.spinner("Loading knowledge base statistics..."):
        try:
            stats = st.session_state.knowledge_base.get_knowledge_base_stats()

            if "error" not in stats:
                st.markdown("### Knowledge Base Statistics")

                st.markdown(f"""
                <div class="stats-container">
                    <div class="stat-card primary">
                        <div class="stat-number">{len(stats['source_types'])}</div>
                        <div class="stat-label">Source Types</div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-number">✓</div>
                        <div class="stat-label">Status: Ready</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Breakdown of source types
                st.markdown("#### Source Type Breakdown")
                for source_type, count in stats['source_types'].items():
                    st.markdown(f"""
                    <div class="source-item">
                        <div class="source-icon">📁</div>
                        <div class="source-content">
                            <div class="source-title">{source_type}</div>
                            <div class="source-meta">
                                <span>{count:,} chunks available</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.error(f"Error loading stats: {stats['error']}")

        except Exception as e:
            st.error(f"Error displaying knowledge base info: {str(e)}")

    st.markdown("---")

    # Testing interface
    st.markdown("### Test Knowledge Base Search")

    col1, col2 = st.columns([3, 1])

    with col1:
        test_query = st.text_input(
            "Enter a test query:",
            placeholder="e.g., How to authenticate with Atlan API?",
            help="Test the knowledge base search functionality"
        )

    with col2:
        category_filter = st.selectbox(
            "Category Filter:",
            ["None", "product_documentation", "developer_hub"],
            index=0
        )

    if st.button("Search Knowledge Base", type="primary", use_container_width=True) and test_query:
        with st.spinner("Searching knowledge base..."):
            try:
                filter_category = None if category_filter == "None" else category_filter

                results = st.session_state.knowledge_base.search_knowledge_base(
                    test_query,
                    limit=5,
                    category_filter=filter_category
                )

                if results:
                    st.markdown(f"""
                    <div class="rag-response-container">
                        <h4>🔍 Search Results ({len(results)} found)</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    for i, result in enumerate(results, 1):
                        payload = result.payload
                        confidence_class = get_confidence_class(result.score)

                        st.markdown(f"""
                        <div class="source-item animate-fade-in-up">
                            <div class="source-icon">{i}</div>
                            <div class="source-content">
                                <div class="source-title">{payload['title']}</div>
                                <div class="source-url">
                                    <a href="{payload['url']}" target="_blank">{payload['url']}</a>
                                </div>
                                <div class="source-meta">
                                    <span>Category: {payload['main_category']} / {payload['subcategory']}</span>
                                    <span>Tags: {', '.join(payload['tags'])}</span>
                                    <span>Chunk: {payload['chunk_index']}/{payload['total_chunks']}</span>
                                </div>
                                <div style="margin-top: 1rem;">
                                    <span class="confidence-indicator {confidence_class}">
                                        Similarity: {result.score:.1%}
                                    </span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander(f"View Content Preview - Result {i}"):
                            st.info(payload['content'][:500] + "..." if len(payload['content']) > 500 else payload['content'])
                else:
                    st.markdown("""
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <h3>No Results Found</h3>
                        <p>Try a different search query or adjust the category filter</p>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Search error: {str(e)}")

def render_analytics_dashboard():
    """Render analytics dashboard"""
    st.markdown('<h2 class="sub-header">Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    if not hasattr(st.session_state, 'classified_tickets') or not st.session_state.classified_tickets:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <h3>No Data Available</h3>
            <p>Please classify some tickets first to view analytics</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Generate analytics
    tickets = st.session_state.classified_tickets
    topic_trends = analytics_service.generate_topic_trends(tickets)
    satisfaction_metrics = analytics_service.calculate_satisfaction_metrics(tickets)
    performance_metrics = analytics_service.generate_performance_metrics(tickets)
    
    # Performance metrics cards
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card primary">
            <div class="stat-number">{performance_metrics['total_processed']}</div>
            <div class="stat-label">Processed Tickets</div>
        </div>
        <div class="stat-card success">
            <div class="stat-number">{performance_metrics['auto_resolution_rate_percent']}%</div>
            <div class="stat-label">Auto Resolution Rate</div>
        </div>
        <div class="stat-card warning">
            <div class="stat-number">{performance_metrics['avg_processing_time_seconds']}s</div>
            <div class="stat-label">Avg Processing Time</div>
        </div>
        <div class="stat-card info">
            <div class="stat-number">{performance_metrics['efficiency_score']}</div>
            <div class="stat-label">Efficiency Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_system_status():
    """Render system status in sidebar"""
    st.sidebar.markdown("### System Status")
    
    # Knowledge Base status
    if st.session_state.kb_status == "ready":
        st.sidebar.markdown('<div class="status-indicator status-ready">Knowledge Base: Ready</div>', unsafe_allow_html=True)
    elif st.session_state.kb_status == "error":
        st.sidebar.markdown('<div class="status-indicator status-error">Knowledge Base: Error</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="status-indicator status-warning">Knowledge Base: Initializing</div>', unsafe_allow_html=True)
    
    # Classifier status
    classifier_status = getattr(st.session_state, 'classifier_status', 'waiting')
    if classifier_status == "ready":
        st.sidebar.markdown('<div class="status-indicator status-ready">Classifier: Ready</div>', unsafe_allow_html=True)
    elif classifier_status == "error":
        st.sidebar.markdown('<div class="status-indicator status-error">Classifier: Error</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="status-indicator status-warning">Classifier: Waiting</div>', unsafe_allow_html=True)
    
    # RAG Agent status
    agent_status = getattr(st.session_state, 'agent_status', 'waiting')
    if agent_status == "ready":
        st.sidebar.markdown('<div class="status-indicator status-ready">RAG Agent: Ready</div>', unsafe_allow_html=True)
    elif agent_status == "error":
        st.sidebar.markdown('<div class="status-indicator status-error">RAG Agent: Error</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="status-indicator status-warning">RAG Agent: Waiting</div>', unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    initialize_session_state()
    render_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        page = st.radio(
            "Select View:",
            [
                "Interactive Agent", 
                "Bulk Classification",
                "Knowledge Base Info",
                "Analytics Dashboard"
            ],
            index=0
        )
        
        st.markdown("---")
        render_system_status()
        
        # Add helpful tips
        st.markdown("---")
        st.markdown("### Tips")
        st.markdown("""
        - **Interactive Agent**: Best for single queries
        - **Bulk Classification**: Process multiple tickets
        - **Knowledge Base**: Test search functionality
        - **Analytics**: View processing metrics
        """)
    
    # Main content based on page selection
    if page == "Interactive Agent":
        render_interactive_agent()
    elif page == "Bulk Classification":
        render_bulk_classification()
    elif page == "Knowledge Base Info":
        render_knowledge_base_info()
    else:
        render_analytics_dashboard()

if __name__ == "__main__":
    main()