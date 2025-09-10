# import streamlit as st
# import json
# import os
# from datetime import datetime
# import uuid
# import requests
# import re
# from urllib.parse import urlparse
# from typing import List, Dict, Any, Optional
# import time

# # Import your existing components
# from langchain import hub
# from langchain.agents import AgentExecutor, create_structured_chat_agent
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_groq import ChatGroq
# from sentence_transformers import SentenceTransformer
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from qdrant_client import QdrantClient
# from qdrant_client.http import models as rest

# # Set environment variables
# os.environ["TAVILY_API_KEY"] = "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"
# os.environ["GOOGLE_API_KEY"] = "AIzaSyCsw7V4iXwPOdXRDAO1BwZOhM9WbJ-gR_U"
# os.environ["GROQ_API_KEY"] = "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"

# # Initialize the enhanced knowledge base (your existing code)
# from services.knowledge_base import EnhancedAtlanKnowledgeBase


# # Initialize the AI classifier
# class AtlanTicketClassifier:
#     def __init__(self):
#         self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        
#     def classify_ticket(self, ticket_text):
#         classification_prompt = f"""
#         Analyze the following customer support ticket and classify it according to the specified schema.
        
#         TICKET TEXT:
#         {ticket_text}
        
#         CLASSIFICATION SCHEMA:
#         1. Topic Tags: Choose from How-to, Product, Connector, Lineage, API/SDK, SSO, Glossary, Best practices, Sensitive data
#         2. Sentiment: Choose from Frustrated, Curious, Angry, Neutral
#         3. Priority: Choose from P0 (High), P1 (Medium), P2 (Low)
        
#         Return your response as a valid JSON object with the following structure:
#         {{
#             "topic_tags": ["tag1", "tag2"],
#             "sentiment": "sentiment_value",
#             "priority": "priority_value"
#         }}
#         """
        
#         try:
#             response = self.llm.invoke(classification_prompt)
#             # Extract JSON from response
#             json_str = response.content.strip()
#             # Clean up the response to extract just the JSON
#             json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
#             if json_match:
#                 json_str = json_match.group(0)
#                 classification = json.loads(json_str)
#                 return classification
#             else:
#                 # Fallback if JSON parsing fails
#                 return {
#                     "topic_tags": ["Product"],
#                     "sentiment": "Neutral",
#                     "priority": "P1 (Medium)"
#                 }
#         except Exception as e:
#             st.error(f"Classification error: {e}")
#             return {
#                 "topic_tags": ["Product"],
#                 "sentiment": "Neutral",
#                 "priority": "P1 (Medium)"
#             }

# # Initialize the RAG agent
# class AtlanRAGAgent:
#     def __init__(self, knowledge_base):
#         self.kb = knowledge_base
#         self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        
#     def generate_response(self, query, classification):
#         # Internal analysis view
#         internal_analysis = {
#             "classification": classification,
#             "timestamp": datetime.now().isoformat(),
#             "query": query
#         }
        
#         # Check if we should use RAG or just route the ticket
#         rag_topics = ["How-to", "Product", "Best practices", "API/SDK", "SSO"]
#         use_rag = any(topic in rag_topics for topic in classification["topic_tags"])
        
#         if use_rag:
#             # Determine which knowledge base category to use
#             if any(topic in ["API/SDK"] for topic in classification["topic_tags"]):
#                 category_filter = "developer_hub"
#             else:
#                 category_filter = "product_documentation"
                
#             # Generate RAG response
#             rag_response = self.kb.generate_rag_response(query, category_filter=category_filter)
            
#             # Final response view
#             final_response = {
#                 "answer": rag_response["answer"],
#                 "sources": rag_response["sources"],
#                 "type": "RAG Response"
#             }
#         else:
#             # Route the ticket
#             final_response = {
#                 "answer": f"This ticket has been classified as a '{classification['topic_tags'][0]}' issue and routed to the appropriate team.",
#                 "sources": [],
#                 "type": "Routing Response"
#             }
            
#         return {
#             "internal_analysis": internal_analysis,
#             "final_response": final_response
#         }

# # Load sample tickets
# def load_sample_tickets():
#     # In a real application, you would load from a file
#     # For now, using the provided example and some additional ones
#     return [
#         {
#             "id": "TICKET-245",
#             "subject": "Connecting Snowflake to Atlan - required permissions?",
#             "body": "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing. We've tried using our standard service account, but it's not working. Our entire BI team is blocked on this integration for a major upcoming project, so it's quite urgent. Could you please provide a definitive list of the exact permissions and credentials needed on the Snowflake side to get this working? Thanks."
#         },
#         {
#             "id": "TICKET-301",
#             "subject": "How to create custom lineage in Atlan?",
#             "body": "I need to create custom lineage for our ETL processes that aren't automatically captured. The documentation seems sparse on this topic. Can you provide a step-by-step guide?"
#         },
#         {
#             "id": "TICKET-422",
#             "subject": "API authentication issues",
#             "body": "I'm getting a 401 error when trying to authenticate with the Atlan API using my service account credentials. The same credentials work in the UI. What could be causing this?"
#         }
#     ]

# # Streamlit application
# def main():
#     st.set_page_config(
#         page_title="Atlan Helpdesk AI",
#         page_icon="🔍",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
    
#     # Custom CSS
#     st.markdown("""
#     <style>
#     .main-header {
#         font-size: 3rem;
#         color: #1E3A8A;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .sub-header {
#         font-size: 1.5rem;
#         color: #3B82F6;
#         margin-top: 1.5rem;
#         margin-bottom: 1rem;
#     }
#     .ticket-card {
#         padding: 1rem;
#         border-radius: 0.5rem;
#         border-left: 4px solid #3B82F6;
#         background-color: #F3F4F6;
#         margin-bottom: 1rem;
#     }
#     .classification-badge {
#         display: inline-block;
#         padding: 0.25rem 0.5rem;
#         border-radius: 0.25rem;
#         font-size: 0.8rem;
#         margin-right: 0.5rem;
#         margin-bottom: 0.5rem;
#     }
#     .topic-badge {
#         background-color: #DBEAFE;
#         color: #1E40AF;
#     }
#     .sentiment-badge {
#         background-color: #FCE7F3;
#         color: #9D174D;
#     }
#     .priority-badge {
#         background-color: #FEF3C7;
#         color: #92400E;
#     }
#     .internal-analysis {
#         background-color: #FEF3C7;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         margin-bottom: 1rem;
#     }
#     .final-response {
#         background-color: #D1FAE5;
#         padding: 1rem;
#         border-radius: 0.5rem;
#     }
#     </style>
#     """, unsafe_allow_html=True)
    
#     st.markdown('<h1 class="main-header">🔍 Atlan Helpdesk AI Assistant</h1>', unsafe_allow_html=True)
    
#     # Initialize components (with caching to avoid reinitialization)
#     @st.cache_resource
#     def init_knowledge_base():
#         return EnhancedAtlanKnowledgeBase()
    
#     @st.cache_resource
#     def init_classifier():
#         return AtlanTicketClassifier()
    
#     @st.cache_resource
#     def init_rag_agent(_kb):
#         return AtlanRAGAgent(_kb)
    
#     # Initialize components
#     with st.spinner("Initializing AI components..."):
#         kb = init_knowledge_base()
#         classifier = init_classifier()
#         rag_agent = init_rag_agent(kb)
    
#     # Create tabs for different functionalities
#     tab1, tab2 = st.tabs(["Bulk Ticket Classification", "Interactive AI Agent"])
    
#     with tab1:
#         st.markdown('<h2 class="sub-header">Bulk Ticket Classification Dashboard</h2>', unsafe_allow_html=True)
        
#         # Load sample tickets
#         sample_tickets = load_sample_tickets()
        
#         # Classify all tickets
#         if 'classified_tickets' not in st.session_state:
#             with st.spinner("Classifying tickets..."):
#                 classified_tickets = []
#                 for ticket in sample_tickets:
#                     # Combine subject and body for classification
#                     ticket_text = f"Subject: {ticket['subject']}\n\nBody: {ticket['body']}"
#                     classification = classifier.classify_ticket(ticket_text)
#                     classified_tickets.append({
#                         **ticket,
#                         "classification": classification
#                     })
#                 st.session_state.classified_tickets = classified_tickets
        
#         # Display classified tickets
#         for ticket in st.session_state.classified_tickets:
#             with st.container():
#                 st.markdown(f"""
#                 <div class="ticket-card">
#                     <h3>{ticket['subject']} <span style="font-size: 0.8rem; color: #6B7280;">({ticket['id']})</span></h3>
#                     <p>{ticket['body'][:200]}...</p>
#                     <div>
#                         <strong>Classification:</strong><br>
#                         <span class="classification-badge topic-badge">Topics: {', '.join(ticket['classification']['topic_tags'])}</span>
#                         <span class="classification-badge sentiment-badge">Sentiment: {ticket['classification']['sentiment']}</span>
#                         <span class="classification-badge priority-badge">Priority: {ticket['classification']['priority']}</span>
#                     </div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
#     with tab2:
#         st.markdown('<h2 class="sub-header">Interactive AI Agent</h2>', unsafe_allow_html=True)
        
#         # Input for new ticket
#         new_ticket = st.text_area(
#             "Enter a new ticket or question:",
#             placeholder="Describe your issue or question here...",
#             height=150
#         )
        
#         if st.button("Submit Ticket", type="primary"):
#             if new_ticket:
#                 with st.spinner("Analyzing ticket..."):
#                     # Classify the ticket
#                     classification = classifier.classify_ticket(new_ticket)
                    
#                     # Generate response
#                     response = rag_agent.generate_response(new_ticket, classification)
                    
#                     # Store in session state
#                     st.session_state.current_response = response
#                     st.session_state.current_ticket = new_ticket
#                     st.session_state.current_classification = classification
#             else:
#                 st.warning("Please enter a ticket or question before submitting.")
        
#         # Display results if available
#         if 'current_response' in st.session_state:
#             st.markdown("---")
#             st.markdown("### Analysis Results")
            
#             # Internal analysis view
#             st.markdown("#### Internal Analysis View")
#             st.markdown('<div class="internal-analysis">', unsafe_allow_html=True)
#             st.json(st.session_state.current_response["internal_analysis"])
#             st.markdown('</div>', unsafe_allow_html=True)
            
#             # Final response view
#             st.markdown("#### Final Response View")
#             st.markdown('<div class="final-response">', unsafe_allow_html=True)
#             st.write(st.session_state.current_response["final_response"]["answer"])
            
#             # Display sources if available
#             if st.session_state.current_response["final_response"]["sources"]:
#                 st.markdown("##### Sources:")
#                 for i, source in enumerate(st.session_state.current_response["final_response"]["sources"]):
#                     st.markdown(f"{i+1}. [{source['title']}]({source['url']})")
            
#             st.markdown('</div>', unsafe_allow_html=True)

# if __name__ == "__main__":
#     main()



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

# Import your existing components
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

# Set environment variables
os.environ["TAVILY_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyCsw7V4iXwPOdXRDAO1BwZOhM9WbJ-gR_U"
os.environ["GROQ_API_KEY"] = "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"

# Initialize the enhanced knowledge base (your existing code)
from services.knowledge_base import EnhancedAtlanKnowledgeBase

# Enhanced AI classifier with verbose logging
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

# Enhanced RAG agent with verbose logging
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

# Load sample tickets with more examples
def load_sample_tickets():
    return [
 {
   "id": "TICKET-245",
   "subject": "Connecting Snowflake to Atlan - required permissions?",
   "body": "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing. We've tried using our standard service account, but it's not working. Our entire BI team is blocked on this integration for a major upcoming project, so it's quite urgent. Could you please provide a definitive list of the exact permissions and credentials needed on the Snowflake side to get this working? Thanks."
 },
 {
   "id": "TICKET-246",
   "subject": "Which connectors automatically capture lineage?",
   "body": "Hello, I'm new to Atlan and trying to understand the lineage capabilities. The documentation mentions automatic lineage, but it's not clear which of our connectors (we use Fivetran, dbt, and Tableau) support this out-of-the-box. We need to present a clear picture of our data flow to leadership next week. Can you explain how lineage capture differs for these tools?"
 },
 {
   "id": "TICKET-247",
   "subject": "Deployment of Atlan agent for private data lake",
   "body": "Our primary data lake is hosted on-premise within a secure VPC and is not exposed to the internet. We understand we need to use the Atlan agent for this, but the setup instructions are a bit confusing for our security team. This is a critical source for us, and we can't proceed with our rollout until we get this connected. Can you provide a detailed deployment guide or connect us with a technical expert?"
 },
 {
   "id": "TICKET-248",
   "subject": "How to surface sample rows and schema changes?",
   "body": "Hi, we've successfully connected our Redshift cluster, and the assets are showing up. However, my data analysts are asking how they can see sample data or recent schema changes directly within Atlan without having to go back to Redshift. Is this feature available? I feel like I'm missing something obvious."
 },
 {
   "id": "TICKET-249",
   "subject": "Exporting lineage view for a specific table",
   "body": "For our quarterly audit, I need to provide a complete upstream and downstream lineage diagram for our core `fact_orders` table. I can see the lineage perfectly in the UI, but I can't find an option to export this view as an image or PDF. This is a hard requirement from our compliance team and the deadline is approaching fast. Please help!"
 },
 {
   "id": "TICKET-250",
   "subject": "Importing lineage from Airflow jobs",
   "body": "We run hundreds of ETL jobs in Airflow, and we need to see that lineage reflected in Atlan. I've read that Atlan can integrate with Airflow, but how do we configure it to correctly map our DAGs to the specific datasets they are transforming? The current documentation is a bit high-level."
 },
 {
   "id": "TICKET-251",
   "subject": "Using the Visual Query Builder",
   "body": "I'm a business analyst and not very comfortable with writing complex SQL. I was excited to see the Visual Query Builder in Atlan, but I'm having trouble figuring out how to join multiple tables and save my query for later use. Is there a tutorial or a quick guide you can point me to?"
 },
 {
   "id": "TICKET-252",
   "subject": "Programmatic extraction of lineage",
   "body": "Our internal data science team wants to build a custom application that analyzes metadata propagation delays. To do this, we need to programmatically extract lineage data from Atlan via an API. Does the API expose lineage information, and if so, could you provide an example of the endpoint and the structure of the response?"
 },
 {
   "id": "TICKET-253",
   "subject": "Upstream lineage to Snowflake view not working",
   "body": "This is infuriating. We have a critical Snowflake view, `finance.daily_revenue`, that is built from three upstream tables. Atlan is correctly showing the downstream dependencies, but the upstream lineage is completely missing. This makes the view untrustworthy for our analysts. We've re-run the crawler multiple times. What could be causing this? This is a huge problem for us."
 },
 {
   "id": "TICKET-254",
   "subject": "How to create a business glossary and link terms in bulk?",
   "body": "We are migrating our existing business glossary from a spreadsheet into Atlan. We have over 500 terms. Manually creating each one and linking them to thousands of assets seems impossible. Is there a bulk import feature using CSV or an API to create terms and link them to assets? This is blocking our entire governance initiative."
 },
 {
   "id": "TICKET-255",
   "subject": "Creating a custom role for data stewards",
   "body": "I'm trying to set up a custom role for our data stewards. They need permission to edit descriptions and link glossary terms, but they should NOT have permission to run queries or change connection settings. I'm looking at the default roles, but none of them fit perfectly. How can I create a new role with this specific set of permissions?"
 },
 {
   "id": "TICKET-256",
   "subject": "Mapping Active Directory groups to Atlan teams",
   "body": "Our company policy requires us to manage all user access through Active Directory groups. We need to map our existing AD groups (e.g., 'data-analyst-finance', 'data-engineer-core') to teams within Atlan to automatically grant the correct permissions. I can't find the settings for this. How is this configured?"
 },
 {
   "id": "TICKET-257",
   "subject": "RBAC for assets vs. glossaries",
   "body": "I need clarification on how Atlan's role-based access control works. If a user is denied access to a specific Snowflake schema, can they still see the glossary terms that are linked to the tables in that schema? I need to ensure our PII governance is airtight."
 },
 {
   "id": "TICKET-258",
   "subject": "Process for onboarding asset owners",
   "body": "We've started identifying owners for our key data assets. What is the recommended workflow in Atlan to assign these owners and automatically notify them? We want to make sure they are aware of their responsibilities without us having to send manual emails for every assignment."
 },
 {
   "id": "TICKET-259",
   "subject": "How does Atlan surface sensitive fields like PII?",
   "body": "Our security team is evaluating Atlan and their main question is around PII and sensitive data. How does Atlan automatically identify fields containing PII? What are our options to apply tags or masks to these fields once they are identified to prevent unauthorized access?"
 },
 {
   "id": "TICKET-260",
   "subject": "Authentication methods for APIs and SDKs",
   "body": "We are planning to build several automations using the Atlan API and Python SDK. What authentication methods are supported? Is it just API keys, or can we use something like OAuth? We have a strict policy that requires key rotation every 90 days, so we need to understand how to manage this programmatically."
 },
 {
   "id": "TICKET-261",
   "subject": "Enabling and testing SAML SSO",
   "body": "We are ready to enable SAML SSO with our Okta instance. However, we are very concerned about disrupting our active users if the configuration is wrong. Is there a way to test the SSO configuration for a specific user or group before we enable it for the entire workspace?"
 },
 {
   "id": "TICKET-262",
   "subject": "SSO login not assigning user to correct group",
   "body": "I've just had a new user, 'test.user@company.com', log in via our newly configured SSO. They were authenticated successfully, but they were not added to the 'Data Analysts' group as expected based on our SAML assertions. This is preventing them from accessing any assets. What could be the reason for this mis-assignment?"
 },
 {
   "id": "TICKET-263",
   "subject": "Integration with existing DLP or secrets manager",
   "body": "Does Atlan have the capability to integrate with third-party tools like a DLP (Data Loss Prevention) solution or a secrets manager like HashiCorp Vault? We need to ensure that connection credentials and sensitive metadata classifications are handled by our central security systems."
 },
 {
   "id": "TICKET-264",
   "subject": "Accessing audit logs for compliance reviews",
   "body": "Our compliance team needs to perform a quarterly review of all activities within Atlan. They need to know who accessed what data, who made permission changes, etc. Where can we find these audit logs, and is there a way to export them or pull them via an API for our records?"
 },
 {
   "id": "TICKET-265",
   "subject": "How to programmatically create an asset using the REST API?",
   "body": "I'm trying to create a new custom asset (a 'Report') using the REST API, but my requests keep failing with a 400 error. The API documentation is a bit sparse on the required payload structure for creating new entities. Could you provide a basic cURL or Python `requests` example of what a successful request body should look like?"
 },
 {
   "id": "TICKET-266",
   "subject": "SDK availability and Python example",
   "body": "I'm a data engineer and prefer using SDKs over raw API calls. Which languages do you provide SDKs for? I'm particularly interested in Python. Where can I find the installation instructions (e.g., PyPI package name) and a short code snippet for a common task, like creating a new glossary term?"
 },
 {
   "id": "TICKET-267",
   "subject": "How do webhooks work in Atlan?",
   "body": "I'm exploring using webhooks to send real-time notifications from Atlan to our internal Slack channel. I need to understand what types of events (e.g., asset updated, term created) can trigger a webhook. Also, how do we validate that the incoming payloads are genuinely from Atlan? Do you support payload signing?"
 },
 {
   "id": "TICKET-268",
   "subject": "Triggering an AWS Lambda from Atlan events",
   "body": "We have a workflow where we want to trigger a custom AWS Lambda function whenever a specific Atlan tag (e.g., 'PII-Confirmed') is added to an asset. What is the recommended and most secure way to set this up? Should we use webhooks pointing to an API Gateway, or is there a more direct integration?"
 },
 {
   "id": "TICKET-269",
   "subject": "When to use Atlan automations vs. external services?",
   "body": "I see that Atlan has a built-in 'Automations' feature. I'm trying to decide if I should use this to manage a workflow or if I should use an external service like Zapier or our own Airflow instance. Could you provide some guidance or examples on what types of workflows are best suited for the native automations versus an external tool?"
 },
 {
   "id": "TICKET-270",
   "subject": "Connector failed to crawl - where to check logs?",
   "body": "URGENT: Our nightly Snowflake crawler failed last night and no new metadata was ingested. This is a critical failure as our morning reports are now missing lineage information. Where can I find the detailed error logs for the crawler run to understand what went wrong? I need to fix this ASAP."
 },
 {
   "id": "TICKET-271",
   "subject": "Asset extracted but not published to Atlan",
   "body": "This is very strange. I'm looking at the crawler logs, and I can see that the asset 'schema.my_table' was successfully extracted from the source. However, when I search for this table in the Atlan UI, it doesn't appear. It seems like it's getting stuck somewhere between extraction and publishing. Can you please investigate the root cause?"
 },
 {
   "id": "TICKET-272",
   "subject": "How to measure adoption and generate reports?",
   "body": "My manager is asking for metrics on our Atlan usage to justify the investment. I need to generate a report showing things like the number of active users, most frequently queried tables, and the number of assets with assigned owners. Does Atlan have a reporting or dashboarding feature for this?"
 },
 {
   "id": "TICKET-273",
   "subject": "Best practices for catalog hygiene",
   "body": "We've been using Atlan for six months, and our catalog is already starting to get a bit messy with duplicate assets and stale metadata from old tests. As we roll this out to more teams, what are some common best practices or features within Atlan that can help us maintain good catalog hygiene and prevent this problem from getting worse?"
 },
 {
   "id": "TICKET-274",
   "subject": "How to scale Atlan across multiple business units?",
   "body": "We are planning a global rollout of Atlan to multiple business units, each with its own data sources and governance teams. We're looking for advice on the best way to structure our Atlan instance. Should we use separate workspaces, or can we achieve isolation using teams and permissions within a single workspace while maintaining a consistent governance model?"
 }
]


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
        st.markdown('<h2 class="sub-header">📈 Analytics Dashboard</h2>', unsafe_allow_html=True)
        
        if 'classified_tickets' in st.session_state:
            tickets = st.session_state.classified_tickets
            
            # Analytics overview
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Topic Distribution")
                
                # Count topics
                topic_counts = {}
                for ticket in tickets:
                    for topic in ticket['classification']['topic_tags']:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
                # Create a simple bar chart representation
                st.markdown('<div class="analytics-container">', unsafe_allow_html=True)
                for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(tickets)) * 100
                    st.markdown(f"""
                    <div style="margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                            <span style="font-weight: 500;">{topic}</span>
                            <span style="font-size: 0.9rem; color: #6B7280;">{count} ({percentage:.1f}%)</span>
                        </div>
                        <div style="background: #E5E7EB; border-radius: 4px; height: 8px;">
                            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; border-radius: 4px; width: {percentage}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 😊 Sentiment Analysis")
                
                # Count sentiments
                sentiment_counts = {}
                for ticket in tickets:
                    sentiment = ticket['classification']['sentiment']
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                # Display sentiment distribution
                sentiment_colors = {
                    'Frustrated': '#f5576c',
                    'Curious': '#4facfe',
                    'Angry': '#ff6b6b',
                    'Neutral': '#95a5a6'
                }
                
                for sentiment, count in sentiment_counts.items():
                    percentage = (count / len(tickets)) * 100
                    color = sentiment_colors.get(sentiment, '#95a5a6')
                    
                    st.markdown(f"""
                    <div style="margin: 1rem 0; padding: 1rem; background: white; border-radius: 8px; border-left: 4px solid {color};">
                        <div style="display: flex; justify-content: between; align-items: center;">
                            <span style="font-weight: 500; font-size: 1.1rem;">{sentiment}</span>
                            <span style="margin-left: auto; background: {color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.9rem;">
                                {count} tickets ({percentage:.1f}%)
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Priority analysis
            st.markdown("### ⚡ Priority Distribution")
            col1, col2, col3 = st.columns(3)
            
            priority_counts = {}
            for ticket in tickets:
                priority = ticket['classification']['priority']
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            priority_colors = {
                'P0 (High)': '#ff6b6b',
                'P1 (Medium)': '#feca57',
                'P2 (Low)': '#48dbfb'
            }
            
            for i, (priority, count) in enumerate(priority_counts.items()):
                percentage = (count / len(tickets)) * 100
                color = priority_colors.get(priority, '#95a5a6')
                
                cols = [col1, col2, col3]
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 2rem; background: {color}; color: white; border-radius: 12px; margin: 0.5rem 0;">
                        <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">{count}</div>
                        <div style="font-size: 1rem; opacity: 0.9;">{priority}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">({percentage:.1f}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recent activity timeline
            st.markdown("### 📅 Recent Activity")
            st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
            
            # Sort tickets by creation time (simulated)
            sorted_tickets = sorted(tickets, key=lambda x: x.get('created_at', ''), reverse=True)
            
            for ticket in sorted_tickets[:5]:  # Show last 5 tickets
                priority_color = priority_colors.get(ticket['classification']['priority'], '#95a5a6')
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 1rem; margin: 0.5rem 0; background: white; border-radius: 8px; border-left: 4px solid {priority_color};">
                    <div style="flex: 1;">
                        <div style="font-weight: 500; margin-bottom: 0.25rem;">{ticket['subject']}</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">
                            {ticket['id']} • {ticket.get('created_at', 'N/A')} • 
                            <span style="background: {priority_color}; color: white; padding: 0.1rem 0.5rem; border-radius: 8px; font-size: 0.8rem;">
                                {ticket['classification']['priority']}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.info("📊 Analytics will appear after tickets are classified. Please visit the 'Bulk Classification' tab first.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #6B7280;">
        <p>🎯 <strong>Atlan Helpdesk AI Assistant</strong> - Powered by Advanced Language Models</p>
        <p style="font-size: 0.9rem;">Built with ❤️ using Streamlit, LangChain, and Groq</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()