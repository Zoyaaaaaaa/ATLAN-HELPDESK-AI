# #!/usr/bin/env python3
# """
# Atlan Helpdesk Application
# Main application file that demonstrates bulk ticket classification and interactive AI agent
# """

# import json
# import time
# from typing import Dict, Any, List, Optional
# from datetime import datetime

# from services.memory_store import MemoryStore
# from services.ticket_classifier import TicketClassifier
# from services.rag_service import RAGService
# from config.settings import Settings

# class AtlanHelpdeskApp:
#     """Main Atlan Helpdesk Application"""
    
#     def __init__(self):
#         print("🚀 Initializing Atlan Helpdesk Application")
#         print("=" * 80)
        
#         # Initialize components
#         self.settings = Settings()
#         self.memory_store = MemoryStore()
#         self.classifier = TicketClassifier()
        
#         # Initialize RAG service with knowledge base
#         try:
#             from services.knowledge_base import EnhancedAtlanKnowledgeBase
#             knowledge_base = EnhancedAtlanKnowledgeBase()
#             self.rag_service = RAGService(knowledge_base)
#             print("✅ RAG Service initialized with Knowledge Base")
#         except Exception as e:
#             print(f"⚠️ Could not initialize Enhanced Knowledge Base: {e}")
#             self.rag_service = RAGService()
#             print("✅ RAG Service initialized without Knowledge Base")
        
#         print("✅ All components initialized successfully!")
        
#         # Perform bulk classification on startup
#         self._perform_bulk_classification()
    
#     def _perform_bulk_classification(self):
#         """Perform bulk classification of all loaded tickets"""
#         print("\n🔄 Performing bulk ticket classification...")
#         print("-" * 60)
        
#         tickets = self.memory_store.get_tickets()
        
#         if not tickets:
#             print("⚠️ No tickets found to classify")
#             return
        
#         print(f"📋 Classifying {len(tickets)} tickets...")
        
#         # Classify all tickets
#         classified_tickets = self.classifier.classify_bulk_tickets(tickets)
        
#         # Store classified tickets
#         self.memory_store.store_classified_tickets(classified_tickets)
        
#         print(f"✅ Classified {len(classified_tickets)} tickets successfully!")
        
#         # Display classification summary
#         self._display_classification_summary()
    
#     def _display_classification_summary(self):
#         """Display summary of ticket classifications"""
#         print("\n📊 CLASSIFICATION SUMMARY")
#         print("=" * 50)
        
#         stats = self.memory_store.get_app_stats()
#         classification_stats = stats.get("classification_stats", {})
        
#         # Topic distribution
#         print("🏷️  TOPIC DISTRIBUTION:")
#         topics = classification_stats.get("topics", {})
#         for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
#             percentage = (count / stats["total_tickets_classified"]) * 100
#             print(f"   • {topic}: {count} tickets ({percentage:.1f}%)")
        
#         # Sentiment distribution  
#         print("\n😊 SENTIMENT DISTRIBUTION:")
#         sentiments = classification_stats.get("sentiments", {})
#         for sentiment, count in sorted(sentiments.items(), key=lambda x: x[1], reverse=True):
#             percentage = (count / stats["total_tickets_classified"]) * 100
#             print(f"   • {sentiment}: {count} tickets ({percentage:.1f}%)")
        
#         # Priority distribution
#         print("\n⚡ PRIORITY DISTRIBUTION:")
#         priorities = classification_stats.get("priorities", {})
#         for priority, count in sorted(priorities.items(), key=lambda x: x[1], reverse=True):
#             percentage = (count / stats["total_tickets_classified"]) * 100 
#             print(f"   • {priority}: {count} tickets ({percentage:.1f}%)")
    
#     def display_bulk_classification_dashboard(self):
#         """Display the bulk ticket classification dashboard"""
#         print("\n" + "=" * 80)
#         print("📋 BULK TICKET CLASSIFICATION DASHBOARD")
#         print("=" * 80)
        
#         classified_tickets = self.memory_store.get_classified_tickets()
        
#         if not classified_tickets:
#             print("⚠️ No classified tickets available")
#             return
        
#         for i, ticket in enumerate(classified_tickets, 1):
#             print(f"\n🎫 TICKET {i}: {ticket['id']}")
#             print("-" * 50)
#             print(f"📝 Subject: {ticket['subject']}")
#             print(f"💬 Body: {ticket['body'][:200]}{'...' if len(ticket['body']) > 200 else ''}")
            
#             classification = ticket['classification']
#             print(f"\n🔍 CLASSIFICATION:")
#             print(f"   🏷️  Topic Tags: {', '.join(classification['topic_tags'])}")
#             print(f"   😊 Sentiment: {classification['sentiment']}")
#             print(f"   ⚡ Priority: {classification['priority']}")
#             print(f"   🎯 Confidence Scores:")
#             for metric, score in classification['confidence_scores'].items():
#                 print(f"      • {metric.title()}: {score:.3f}")
#             print(f"   🧠 Reasoning: {classification['reasoning']}")
        
#         # Display summary statistics
#         self._display_classification_summary()
    
#     def process_new_ticket(self, subject: str, body: str) -> Dict[str, Any]:
#         """Process a new ticket through the complete AI pipeline"""
#         print(f"\n🆕 Processing new ticket: '{subject[:50]}...'")
#         print("-" * 60)
        
#         # Create ticket object
#         new_ticket = {
#             "subject": subject,
#             "body": body,
#             "created_at": datetime.utcnow().isoformat()
#         }
        
#         # Add to memory store
#         ticket_id = self.memory_store.add_ticket(new_ticket)
#         new_ticket["id"] = ticket_id
        
#         # Classify the ticket
#         classification = self.classifier.classify_ticket(new_ticket)
        
#         # Process with RAG or routing based on topic
#         rag_topics = ["How-to", "Product", "Best practices", "API/SDK", "SSO"]
#         use_rag = any(topic in rag_topics for topic in classification.topic_tags)
        
#         if use_rag:
#             # Use RAG for response
#             rag_response = self.rag_service.get_response(
#                 f"{subject} {body}", 
#                 classification
#             )
            
#             processed_result = {
#                 "ticket": new_ticket,
#                 "classification": {
#                     "topic_tags": classification.topic_tags,
#                     "sentiment": classification.sentiment,
#                     "priority": classification.priority,
#                     "confidence_scores": classification.confidence_scores,
#                     "reasoning": classification.reasoning
#                 },
#                 "processing_strategy": "RAG_RESPONSE",
#                 "response": {
#                     "type": "RAG_RESPONSE",
#                     "answer": rag_response.answer,
#                     "confidence": rag_response.confidence_score,
#                     "sources": rag_response.sources,
#                     "context_chunks": [
#                         {
#                             "title": doc.title,
#                             "url": doc.url,
#                             "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
#                         }
#                         for doc in rag_response.retrieved_docs
#                     ]
#                 },
#                 "processed_at": datetime.utcnow().isoformat()
#             }
#         else:
#             # Route to appropriate team
#             primary_topic = classification.topic_tags[0] if classification.topic_tags else "General"
            
#             routing_map = {
#                 "Connector": "Data Engineering Team",
#                 "Lineage": "Data Governance Team", 
#                 "Glossary": "Business Metadata Team",
#                 "Sensitive data": "Security & Compliance Team",
#                 "Data Products": "Product Management",
#                 "Governance": "Governance Council",
#                 "Workflows": "Automation Team"
#             }
            
#             routed_to = routing_map.get(primary_topic, "General Support Team")
            
#             processed_result = {
#                 "ticket": new_ticket,
#                 "classification": {
#                     "topic_tags": classification.topic_tags,
#                     "sentiment": classification.sentiment,
#                     "priority": classification.priority,
#                     "confidence_scores": classification.confidence_scores,
#                     "reasoning": classification.reasoning
#                 },
#                 "processing_strategy": "ROUTING_RESPONSE",
#                 "response": {
#                     "type": "ROUTING_RESPONSE",
#                     "topic": primary_topic,
#                     "priority": classification.priority,
#                     "routed_to": routed_to,
#                     "answer": f"This ticket has been classified as a '{primary_topic}' issue with {classification.priority} priority and has been routed to the {routed_to} for further handling."
#                 },
#                 "processed_at": datetime.utcnow().isoformat()
#             }
        
#         # Store processed result
#         self.memory_store.store_processed_ticket(processed_result)
        
#         print(f"✅ Ticket {ticket_id} processed successfully!")
        
#         return processed_result
    
#     def display_ticket_analysis(self, processed_result: Dict[str, Any]):
#         """Display the internal analysis (back-end view) of a ticket"""
#         print("\n🔍 INTERNAL ANALYSIS (Back-end View)")
#         print("=" * 60)
        
#         ticket = processed_result["ticket"]
#         classification = processed_result["classification"]
        
#         print(f"🎫 Ticket ID: {ticket['id']}")
#         print(f"📝 Subject: {ticket['subject']}")
#         print(f"💬 Body: {ticket['body'][:300]}{'...' if len(ticket['body']) > 300 else ''}")
        
#         print(f"\n🏷️  TOPIC CLASSIFICATION:")
#         print(f"   Tags: {', '.join(classification['topic_tags'])}")
#         print(f"   Confidence: {classification['confidence_scores']['topic']:.3f}")
        
#         print(f"\n😊 SENTIMENT ANALYSIS:")
#         print(f"   Sentiment: {classification['sentiment']}")
#         print(f"   Confidence: {classification['confidence_scores']['sentiment']:.3f}")
        
#         print(f"\n⚡ PRIORITY ASSESSMENT:")
#         print(f"   Priority: {classification['priority']}")
#         print(f"   Confidence: {classification['confidence_scores']['priority']:.3f}")
        
#         print(f"\n🧠 REASONING:")
#         print(f"   {classification['reasoning']}")
        
#         print(f"\n⚙️  PROCESSING STRATEGY: {processed_result['processing_strategy']}")
    
#     def display_ticket_response(self, processed_result: Dict[str, Any]):
#         """Display the final response (front-end view) for a ticket"""
#         print("\n💬 FINAL RESPONSE (Front-end View)")
#         print("=" * 60)
        
#         response = processed_result["response"]
        
#         if response["type"] == "RAG_RESPONSE":
#             print("🤖 AI-Generated Response with Knowledge Base:")
#             print(f"   Confidence: {response['confidence']:.3f}")
#             print(f"   Context Chunks Used: {len(response['context_chunks'])}")
#             print()
#             print(response["answer"])
            
#             if response.get("sources"):
#                 print(f"\n📚 Sources ({len(response['sources'])}):")
#                 for i, source in enumerate(response["sources"], 1):
#                     if isinstance(source, str):
#                         print(f"   {i}. {source}")
#                     else:
#                         print(f"   {i}. {source}")
        
#         elif response["type"] == "ROUTING_RESPONSE":
#             print("🎯 Routing Response:")
#             print(f"   Topic: {response['topic']}")
#             print(f"   Priority: {response['priority']}")
#             print(f"   Routed To: {response['routed_to']}")
#             print()
#             print(response["answer"])
        
#         else:
#             print("❓ Unknown response type")
#             print(response.get("answer", "No response available"))
    
#     def interactive_mode(self):
#         """Run the application in interactive mode"""
#         print("\n" + "=" * 80)
#         print("🤖 INTERACTIVE AI AGENT MODE")
#         print("=" * 80)
#         print("Enter ticket details to see AI classification and response")
#         print("Type 'quit' to exit, 'dashboard' to see bulk classification, 'stats' for statistics")
#         print("-" * 80)
        
#         while True:
#             try:
#                 print("\n" + "=" * 50)
#                 command = input("Enter command (new ticket/dashboard/stats/quit): ").strip().lower()
                
#                 if command == 'quit':
#                     print("👋 Goodbye!")
#                     break
                
#                 elif command == 'dashboard':
#                     self.display_bulk_classification_dashboard()
#                     continue
                
#                 elif command == 'stats':
#                     self.display_system_statistics()
#                     continue
                
#                 elif command in ['new', 'ticket', 'new ticket', '']:
#                     # Get new ticket details
#                     print("\n📝 Enter new ticket details:")
#                     subject = input("Subject: ").strip()
#                     if not subject:
#                         print("❌ Subject is required")
#                         continue
                    
#                     print("Body (press Enter twice to finish):")
#                     body_lines = []
#                     while True:
#                         line = input()
#                         if line == "" and body_lines and body_lines[-1] == "":
#                             body_lines.pop()  # Remove the last empty line
#                             break
#                         body_lines.append(line)
                    
#                     body = "\n".join(body_lines).strip()
#                     if not body:
#                         print("❌ Body is required")
#                         continue
                    
#                     # Process the ticket
#                     processed_result = self.process_new_ticket(subject, body)
                    
#                     # Display both views
#                     self.display_ticket_analysis(processed_result)
#                     self.display_ticket_response(processed_result)
                
#                 else:
#                     print("❌ Unknown command. Use: new ticket, dashboard, stats, or quit")
            
#             except KeyboardInterrupt:
#                 print("\n👋 Goodbye!")
#                 break
#             except Exception as e:
#                 print(f"❌ Error: {e}")
    
#     def display_system_statistics(self):
#         """Display comprehensive system statistics"""
#         print("\n📊 SYSTEM STATISTICS")
#         print("=" * 60)
        
#         # Memory store stats
#         app_stats = self.memory_store.get_app_stats()
#         print("📈 APPLICATION STATS:")
#         print(f"   • Total Tickets Loaded: {app_stats['total_tickets_loaded']}")
#         print(f"   • Total Tickets Classified: {app_stats['total_tickets_classified']}")
#         print(f"   • Total Tickets Processed: {app_stats['total_tickets_processed']}")
#         print(f"   • Last Loaded: {app_stats['last_loaded_at']}")
        
#         # Processing stats
#         if "processing_stats" in app_stats:
#             processing_stats = app_stats["processing_stats"]
            
#             if "strategies" in processing_stats:
#                 print(f"\n⚙️  PROCESSING STRATEGIES:")
#                 for strategy, count in processing_stats["strategies"].items():
#                     print(f"   • {strategy}: {count} tickets")
            
#             if "response_types" in processing_stats:
#                 print(f"\n💬 RESPONSE TYPES:")
#                 for response_type, count in processing_stats["response_types"].items():
#                     print(f"   • {response_type}: {count} tickets")
            
#             if "rag_confidence" in processing_stats:
#                 print(f"\n🎯 RAG CONFIDENCE DISTRIBUTION:")
#                 for confidence_level, count in processing_stats["rag_confidence"].items():
#                     print(f"   • {confidence_level.title()}: {count} responses")
        
#         # Knowledge base stats if available
#         try:
#             kb_stats = self.rag_service.get_collection_stats()
#             if "error" not in kb_stats:
#                 print(f"\n📚 KNOWLEDGE BASE STATS:")
#                 print(f"   • Total Vectors: {kb_stats.get('total_vectors', 0)}")
#                 print(f"   • Categories: {', '.join(kb_stats.get('categories', {}).keys())}")
#         except:
#             print(f"\n📚 KNOWLEDGE BASE: Not available")

# def main():
#     """Main entry point for the application"""
#     try:
#         app = AtlanHelpdeskApp()
#         app.interactive_mode()
#     except Exception as e:
#         print(f"❌ Failed to start application: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()

# app.py (Streamlit Version)
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
    page_title="🎯 Atlan AI Helpdesk System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .ticket-card {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .ticket-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .classification-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .tag {
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .topic-tag { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .sentiment-frustrated { background: linear-gradient(135deg, #ff6b6b, #ee5a52); color: white; }
    .sentiment-angry { background: linear-gradient(135deg, #ff8a80, #ff5722); color: white; }
    .sentiment-curious { background: linear-gradient(135deg, #42a5f5, #1976d2); color: white; }
    .sentiment-neutral { background: linear-gradient(135deg, #9c27b0, #673ab7); color: white; }
    .priority-p0-high { background: linear-gradient(135deg, #f44336, #d32f2f); color: white; }
    .priority-p1-medium { background: linear-gradient(135deg, #ff9800, #f57c00); color: white; }
    .priority-p2-low { background: linear-gradient(135deg, #4caf50, #388e3c); color: white; }
    
    .analysis-section {
        background: linear-gradient(145deg, #e3f2fd, #bbdefb);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #2196f3;
        margin: 1rem 0;
    }
    
    .response-section {
        background: linear-gradient(145deg, #e8f5e8, #c8e6c9);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #4caf50;
        margin: 1rem 0;
    }
    
    .verbose-output {
        background: #263238;
        color: #00e676;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
        margin: 1rem 0;
        border: 1px solid #37474f;
    }
    
    .source-citation {
        background: linear-gradient(145deg, #fff3e0, #ffe0b2);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-success { background: #4caf50; }
    .status-error { background: #f44336; }
    .status-warning { background: #ff9800; }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-top: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

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
    """Capture verbose output from operations"""
    def __init__(self):
        self.output = []
    
    def write(self, text):
        if text.strip():
            self.output.append(text)
            return len(text)
    
    def get_output(self):
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
        
        with st.spinner("🚀 Initializing Atlan Knowledge Base..."):
            try:
                # Redirect stdout to capture verbose output
                import sys
                original_stdout = sys.stdout
                sys.stdout = st.session_state.verbose_capture
                
                st.session_state.knowledge_base = EnhancedAtlanKnowledgeBase()
                st.session_state.kb_status = "ready"
                
                # Restore stdout
                sys.stdout = original_stdout
                
                st.success("✅ Knowledge Base initialized successfully!")
                
            except Exception as e:
                sys.stdout = original_stdout
                st.error(f"❌ Failed to initialize Knowledge Base: {str(e)}")
                st.session_state.kb_status = "error"
                st.session_state.kb_error = str(e)
    
    # Initialize classifier
    if 'classifier' not in st.session_state:
        if st.session_state.knowledge_base:
            try:
                st.session_state.classifier = TicketClassifier()
                st.session_state.classifier_status = "ready"
            except Exception as e:
                st.error(f"❌ Failed to initialize Classifier: {str(e)}")
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
                st.error(f"❌ Failed to initialize RAG Agent: {str(e)}")
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
        <span class="tag {classes['topic']}">{classification['topic']}</span>
        <span class="tag {classes['sentiment']}">{classification['sentiment']}</span>
        <span class="tag {classes['priority']}">{classification['priority']}</span>
    </div>
    """

def display_verbose_output():
    """Display verbose output in a formatted way"""
    if st.session_state.verbose_capture.output:
        with st.expander("🔍 Verbose Output (Agent Thinking Process)", expanded=True):
            verbose_text = st.session_state.verbose_capture.get_output()
            st.markdown(f"""
            <div class="verbose-output">
{verbose_text}
            </div>
            """, unsafe_allow_html=True)

def render_bulk_classification():
    """Render bulk ticket classification dashboard"""
    st.header("📊 Bulk Ticket Classification Dashboard")
    
    if not st.session_state.classifier:
        st.error("❌ Classifier not available")
        return
    
    # Classify all tickets button
    if st.button("🚀 Classify All Tickets", type="primary", use_container_width=True):
        st.session_state.classified_tickets = []
        st.session_state.verbose_capture.clear()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        verbose_container = st.empty()
        
        for i, ticket in enumerate(st.session_state.sample_tickets):
            status_text.text(f'🔍 Classifying ticket {i+1}/{len(st.session_state.sample_tickets)}: {ticket["subject"]}')
            
            # Clear previous verbose output
            st.session_state.verbose_capture.clear()
            
            # Classify ticket
            ticket_text = f"Subject: {ticket['subject']}\nBody: {ticket['body']}"
            classification = st.session_state.classifier.classify_ticket(ticket_text)
            
            # Store classified ticket
            classified_ticket = {
                **ticket,
                "classification": classification,
                "classified_at": datetime.now().isoformat()
            }
            st.session_state.classified_tickets.append(classified_ticket)
            
            # Show verbose output for current classification
            with verbose_container.container():
                display_verbose_output()
            
            progress_bar.progress((i + 1) / len(st.session_state.sample_tickets))
            time.sleep(0.5)  # Small delay to show progress
        
        status_text.text('✅ All tickets classified successfully!')
        time.sleep(2)
        status_text.empty()
        progress_bar.empty()
        verbose_container.empty()
    
    # Display classified tickets if available
    if hasattr(st.session_state, 'classified_tickets'):
        st.subheader(f"📋 Classification Results ({len(st.session_state.classified_tickets)} tickets)")
        
        for i, ticket in enumerate(st.session_state.classified_tickets, 1):
            st.markdown(f"""
            <div class="ticket-card">
                <h4>🎫 {ticket['id']}: {ticket['subject']}</h4>
                <p><strong>Description:</strong> {ticket['body'][:300]}{'...' if len(ticket['body']) > 300 else ''}</p>
                {render_classification_tags(ticket['classification'])}
                <p><em><strong>Reasoning:</strong> {ticket['classification']['reasoning']}</em></p>
                <small>Classified at: {ticket['classified_at']}</small>
            </div>
            """, unsafe_allow_html=True)

def render_interactive_agent():
    """Render interactive AI agent interface"""
    st.header("🤖 Interactive AI Agent with RAG System")
    
    if not st.session_state.classifier or not st.session_state.rag_agent:
        st.error("❌ AI Agent not available - System initialization incomplete")
        return
    
    # Input form
    with st.form("query_form", clear_on_submit=False):
        user_query = st.text_area(
            "💬 Submit your question or support ticket:",
            placeholder="e.g., How do I set up SSO with Okta in Atlan?\ne.g., What permissions are needed for Snowflake connector?\ne.g., How to troubleshoot API authentication issues?",
            height=120,
            help="Ask about Atlan products, APIs, connectors, lineage, SSO, or any technical questions"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submit_button = st.form_submit_button("🚀 Process Query", type="primary", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("🧹 Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.verbose_capture.clear()
        st.rerun()
    
    if submit_button and user_query.strip():
        # Clear previous verbose output
        st.session_state.verbose_capture.clear()
        
        st.markdown("---")
        
        # Step 1: Classification
        st.markdown("### 🔬 Internal Analysis (Backend View)")
        with st.spinner("🔍 Analyzing query..."):
            classification = st.session_state.classifier.classify_ticket(user_query)
        
        # Show classification results
        st.markdown(f"""
        <div class="analysis-section">
            <h4>📊 Classification Results:</h4>
            {render_classification_tags(classification)}
            <p><strong>🧠 AI Reasoning:</strong> {classification['reasoning']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show verbose classification output
        display_verbose_output()
        st.session_state.verbose_capture.clear()
        
        # Step 2: Generate response
        st.markdown("### 💬 AI Response (Frontend View)")
        
        with st.spinner("🔄 Generating intelligent response using RAG system..."):
            try:
                # Capture verbose output for agent
                import sys
                original_stdout = sys.stdout
                sys.stdout = st.session_state.verbose_capture
                
                response_data = st.session_state.rag_agent.generate_response(user_query, classification)
                
                # Restore stdout
                sys.stdout = original_stdout
                
                # Display response based on type
                if response_data["response_type"] == "rag_generated":
                    st.markdown(f"""
                    <div class="response-section">
                        <h4>✅ RAG-Generated Response:</h4>
                        <div style="white-space: pre-wrap;">{response_data['answer']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if response_data.get("sources_included"):
                        st.success("📚 Response includes source citations from Atlan documentation")
                
                elif response_data["response_type"] == "routed":
                    st.markdown(f"""
                    <div class="response-section">
                        <h4>📤 Ticket Routed:</h4>
                        <p>{response_data['answer']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                else:  # rag_error
                    st.markdown(f"""
                    <div class="response-section">
                        <h4>⚠️ Response with Fallback:</h4>
                        <p>{response_data['answer']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if "error" in response_data:
                        st.error(f"Technical details: {response_data['error']}")
                
                # Show verbose agent output
                display_verbose_output()
                
            except Exception as e:
                sys.stdout = original_stdout
                st.error(f"❌ Error generating response: {str(e)}")
                st.code(traceback.format_exc())

def render_knowledge_base_info():
    """Render knowledge base information and testing interface"""
    st.header("📚 Knowledge Base Information & Testing")
    
    if not st.session_state.knowledge_base:
        st.error("❌ Knowledge Base not available")
        return
    
    # Knowledge base stats
    with st.spinner("📊 Loading knowledge base statistics..."):
        try:
            stats = st.session_state.knowledge_base.get_knowledge_base_stats()
            
            if "error" not in stats:
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{stats['total_vectors']:,}</h3>
                        <p>Total Vectors</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{len(stats['categories'])}</h3>
                        <p>Categories</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{len(stats['source_types'])}</h3>
                        <p>Source Types</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>✅</h3>
                        <p>Status</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed breakdown
                st.subheader("📊 Detailed Breakdown")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📂 Categories:**")
                    for category, count in stats['categories'].items():
                        st.write(f"• {category}: {count:,} vectors")
                    
                    st.write(f"\n**⏰ Last Updated:** {stats['last_updated']}")
                
                with col2:
                    st.write("**🔧 Source Types:**")
                    for source_type, count in stats['source_types'].items():
                        st.write(f"• {source_type}: {count:,} vectors")
            else:
                st.error(f"Error loading stats: {stats['error']}")
                
        except Exception as e:
            st.error(f"Error displaying knowledge base info: {str(e)}")
    
    st.markdown("---")
    
    # Testing interface
    st.subheader("🧪 Test Knowledge Base Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        test_query = st.text_input(
            "Enter a test query:",
            placeholder="e.g., How to authenticate with Atlan API?"
        )
    
    with col2:
        category_filter = st.selectbox(
            "Category Filter:",
            ["None", "product_documentation", "developer_hub"],
            index=0
        )
    
    if st.button("🔍 Search Knowledge Base", type="primary", use_container_width=True) and test_query:
        st.session_state.verbose_capture.clear()
        
        with st.spinner("🔍 Searching knowledge base..."):
            try:
                # Determine category filter
                filter_category = None if category_filter == "None" else category_filter
                
                # Search knowledge base
                results = st.session_state.knowledge_base.search_knowledge_base(
                    test_query, 
                    limit=5, 
                    category_filter=filter_category
                )
                
                if results:
                    st.success(f"✅ Found {len(results)} results")
                    
                    # Display results
                    for i, result in enumerate(results, 1):
                        with st.expander(f"📄 Result {i} - Similarity Score: {result.score:.3f}"):
                            payload = result.payload
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**📋 Title:** {payload['title']}")
                                st.write(f"**🔗 URL:** {payload['url']}")
                                st.write(f"**📂 Category:** {payload['main_category']} / {payload['subcategory']}")
                                st.write(f"**🏷️ Tags:** {', '.join(payload['tags'])}")
                            
                            with col2:
                                st.metric("Confidence", f"{result.score:.1%}")
                                st.write(f"**📊 Chunk:** {payload['chunk_index']}/{payload['total_chunks']}")
                                st.write(f"**📝 Length:** {payload['chunk_length']} chars")
                            
                            st.write("**📖 Content Preview:**")
                            st.write(payload['content'][:500] + "..." if len(payload['content']) > 500 else payload['content'])
                    
                    # Test RAG response
                    st.markdown("---")
                    st.subheader("🤖 Generated RAG Response")
                    
                    if st.button("🚀 Generate RAG Response", use_container_width=True):
                        with st.spinner("🔄 Generating RAG response..."):
                            rag_response = st.session_state.knowledge_base.generate_rag_response(
                                test_query,
                                limit=3,
                                category_filter=filter_category
                            )
                            
                            st.markdown(f"""
                            <div class="response-section">
                                <h4>🎯 RAG Response (Confidence: {rag_response['confidence']:.1%})</h4>
                                <div style="white-space: pre-wrap;">{rag_response['answer']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if rag_response['sources']:
                                st.write("**📚 Sources Used:**")
                                for i, source in enumerate(rag_response['sources'], 1):
                                    st.markdown(f"""
                                    <div class="source-citation">
                                        <strong>{i}. {source['title']}</strong><br>
                                        🔗 <a href="{source['url']}" target="_blank">{source['url']}</a><br>
                                        📂 Category: {source['category']} / {source['subcategory']}<br>
                                        🏷️ Tags: {', '.join(source['tags'])}
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No results found for your query")
                    
            except Exception as e:
                st.error(f"❌ Search error: {str(e)}")
                st.code(traceback.format_exc())

def render_system_status():
    """Render system status in sidebar"""
    st.sidebar.markdown("### 🔧 System Status")
    
    # Knowledge Base status
    if st.session_state.kb_status == "ready":
        st.sidebar.markdown('<span class="status-indicator status-success"></span>**Knowledge Base:** Ready', unsafe_allow_html=True)
    elif st.session_state.kb_status == "error":
        st.sidebar.markdown('<span class="status-indicator status-error"></span>**Knowledge Base:** Error', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="status-indicator status-warning"></span>**Knowledge Base:** Initializing', unsafe_allow_html=True)
    
    # Classifier status
    classifier_status = getattr(st.session_state, 'classifier_status', 'waiting')
    if classifier_status == "ready":
        st.sidebar.markdown('<span class="status-indicator status-success"></span>**Classifier:** Ready', unsafe_allow_html=True)
    elif classifier_status == "error":
        st.sidebar.markdown('<span class="status-indicator status-error"></span>**Classifier:** Error', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="status-indicator status-warning"></span>**Classifier:** Waiting', unsafe_allow_html=True)
    
    # RAG Agent status
    agent_status = getattr(st.session_state, 'agent_status', 'waiting')
    if agent_status == "ready":
        st.sidebar.markdown('<span class="status-indicator status-success"></span>**RAG Agent:** Ready', unsafe_allow_html=True)
    elif agent_status == "error":
        st.sidebar.markdown('<span class="status-indicator status-error"></span>**RAG Agent:** Error', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="status-indicator status-warning"></span>**RAG Agent:** Waiting', unsafe_allow_html=True)
    
    # Quick stats
    if st.session_state.knowledge_base:
        st.sidebar.markdown("### 📊 Quick Stats")
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
        st.title("🎯 Navigation")
        
        # Navigation options
        page = st.radio(
            "Select View:",
            [
                "📊 Bulk Classification", 
                "🤖 Interactive Agent", 
                "📚 Knowledge Base Info"
            ],
            index=1  # Default to Interactive Agent
        )
        
        st.markdown("---")
        
        # System status
        render_system_status()
        
        st.markdown("---")
        
        # Tips
        with st.expander("💡 Tips"):
            st.write("""
            **For best results:**
            - Be specific in your questions
            - Use technical terms when relevant
            - Ask about Atlan features, APIs, connectors
            - Questions about setup, configuration, troubleshooting work great
            """)
        
        # Clear verbose output button
        if st.button("🧹 Clear Verbose Output"):
            st.session_state.verbose_capture.clear()
            st.success("Verbose output cleared!")
    
    # Main content based on page selection
    if page == "📊 Bulk Classification":
        render_bulk_classification()
    elif page == "🤖 Interactive Agent":
        render_interactive_agent()
    else:  # Knowledge Base Info
        render_knowledge_base_info()
    
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