# import os
# import re
# from typing import Dict, Any, List
# from langchain_groq import ChatGroq
# from langchain.agents import AgentExecutor, create_react_agent
# from langchain.tools import Tool
# from langchain import hub
# from datetime import datetime
# from config.settings import settings

# class TicketClassifier:
#     """Handles ticket classification using LLM with verbose output"""
    
#     def __init__(self):
#         # Set environment variables
#         os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
        
#         self.llm = ChatGroq(
#             model="llama-3.3-70b-versatile", 
#             temperature=0,
#             verbose=True
#         )
#         print("🚀 Ticket Classifier initialized with Groq LLM")
    
#     def classify_ticket(self, ticket_text: str) -> Dict[str, Any]:
#         """Classify a ticket with verbose output"""
#         print(f"\n{'='*60}")
#         print(f"🔍 CLASSIFYING TICKET")
#         print(f"{'='*60}")
#         print(f"📝 Ticket Text: {ticket_text[:200]}...")
        
#         classification_prompt = f"""
#         You are an expert support ticket classifier for Atlan, a data catalog platform.
        
#         Classify this support ticket into the following categories:
        
#         TICKET TEXT:
#         {ticket_text}
        
#         Please provide classification in EXACTLY this format:
        
#         TOPIC: [Choose ONE from: How-to, Product, Connector, Lineage, API/SDK, SSO, Glossary, Best-practices, Sensitive-data]
#         SENTIMENT: [Choose ONE from: Frustrated, Curious, Angry, Neutral]  
#         PRIORITY: [Choose ONE from: P0-High, P1-Medium, P2-Low]
#         REASONING: [Explain why you chose these classifications]
        
#         Rules:
#         - If asking about connecting data sources → Connector
#         - If asking about API, SDK, authentication → API/SDK
#         - If asking about data flow, dependencies → Lineage
#         - If asking about Single Sign-On, SAML, OAuth → SSO
#         - If asking about metadata, business terms → Glossary
#         - If asking how to do something → How-to
#         - If about product features → Product
#         - If about security, PII → Sensitive-data
#         - If about recommendations → Best-practices
        
#         Priority based on:
#         - Business impact mentioned, urgent, blocked team → P0-High
#         - Standard request, some urgency → P1-Medium  
#         - General question, no urgency → P2-Low
#         """
        
#         try:
#             print("🤖 Sending to LLM for classification...")
#             response = self.llm.invoke(classification_prompt)
#             print(f"✅ LLM Response received")
#             print(f"📋 Raw LLM Response:\n{response.content}")
            
#             result = self._parse_classification(response.content)
            
#             print(f"\n🏷️ FINAL CLASSIFICATION:")
#             print(f"   Topic: {result['topic']}")
#             print(f"   Sentiment: {result['sentiment']}")
#             print(f"   Priority: {result['priority']}")
#             print(f"   Reasoning: {result['reasoning']}")
#             print(f"{'='*60}\n")
            
#             return result
            
#         except Exception as e:
#             print(f"❌ Classification error: {str(e)}")
#             return {
#                 "topic": "Product",
#                 "sentiment": "Neutral", 
#                 "priority": "P1-Medium",
#                 "reasoning": f"Classification failed: {str(e)}"
#             }
    
#     def _parse_classification(self, response: str) -> Dict[str, Any]:
#         """Parse LLM response into structured classification with verbose output"""
#         print("🔍 Parsing classification response...")
        
#         # Extract using regex
#         topic_match = re.search(r'TOPIC:\s*(.+)', response, re.IGNORECASE)
#         sentiment_match = re.search(r'SENTIMENT:\s*(.+)', response, re.IGNORECASE)
#         priority_match = re.search(r'PRIORITY:\s*(.+)', response, re.IGNORECASE)
#         reasoning_match = re.search(r'REASONING:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
        
#         topic = topic_match.group(1).strip() if topic_match else "Product"
#         sentiment = sentiment_match.group(1).strip() if sentiment_match else "Neutral"
#         priority = priority_match.group(1).strip() if priority_match else "P1-Medium"
#         reasoning = reasoning_match.group(1).strip() if reasoning_match else "Auto-classified"
        
#         print(f"   ✅ Extracted Topic: {topic}")
#         print(f"   ✅ Extracted Sentiment: {sentiment}")
#         print(f"   ✅ Extracted Priority: {priority}")
        
#         return {
#             "topic": topic,
#             "sentiment": sentiment,
#             "priority": priority,
#             "reasoning": reasoning
#         }

# class AtlanRAGAgent:
#     """RAG-powered agent using only the Atlan knowledge base"""
    
#     def __init__(self, knowledge_base):
#         self.knowledge_base = knowledge_base
        
#         # Set environment variables
#         os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
        
#         self.llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             temperature=0,
#             verbose=True
#         )
        
#         # Create RAG tool
#         self.rag_tool = Tool(
#             name="search_atlan_knowledge",
#             description="Search Atlan documentation for answers about products, APIs, how-tos, connectors, lineage, SSO, and best practices. Always use this tool for any Atlan-related questions.",
#             func=self._search_knowledge_base
#         )
        
#         # Create agent with only RAG tool
#         tools = [self.rag_tool]
#         prompt = hub.pull("hwchase17/react")
#         agent = create_react_agent(self.llm, tools, prompt)
        
#         # Remove the problematic early_stopping_method parameter
#         self.agent_executor = AgentExecutor(
#             agent=agent,
#             tools=tools,
#             verbose=True,
#             max_iterations=5,
#             # early_stopping_method="generate",  # Remove this line
#             handle_parsing_errors=True,
#             return_intermediate_steps=True
#         )
        
#         print("🤖 RAG Agent initialized with Atlan knowledge base")
    
#     def _search_knowledge_base(self, query: str) -> str:
#         """Search knowledge base with verbose output"""
#         print(f"\n🔍 SEARCHING ATLAN KNOWLEDGE BASE")
#         print(f"Query: {query}")
#         print("-" * 50)
        
#         try:
#             # Determine category based on query keywords
#             category_filter = self._determine_category(query)
#             print(f"📂 Category Filter: {category_filter}")
            
#             # Search with RAG
#             response = self.knowledge_base.generate_rag_response(
#                 query, 
#                 limit=5, 
#                 category_filter=category_filter
#             )
            
#             print(f"📊 Confidence Score: {response['confidence']:.3f}")
#             print(f"📚 Sources Found: {len(response['sources'])}")
            
#             if response['sources']:
#                 # Format response with sources
#                 result = f"Based on Atlan documentation:\n\n{response['answer']}\n\n"
#                 result += "📖 SOURCES:\n"
                
#                 for i, source in enumerate(response['sources'], 1):
#                     result += f"{i}. {source['title']}\n"
#                     result += f"   URL: {source['url']}\n"
#                     result += f"   Category: {source['category']}/{source['subcategory']}\n"
#                     result += f"   Tags: {', '.join(source['tags'])}\n\n"
                
#                 print("✅ Knowledge base search successful")
#                 return result
#             else:
#                 print("⚠️ No sources found in knowledge base")
#                 return "I couldn't find specific information in the Atlan documentation for your query. Please contact support for detailed assistance."
                
#         except Exception as e:
#             print(f"❌ Knowledge base search error: {str(e)}")
#             return f"Error searching Atlan documentation: {str(e)}"
    
#     def _determine_category(self, query: str) -> str:
#         """Determine search category based on query"""
#         query_lower = query.lower()
        
#         # Developer/API related keywords
#         if any(keyword in query_lower for keyword in [
#             'api', 'sdk', 'authenticate', 'token', 'python', 'java', 'javascript', 'rest',
#             'endpoint', 'curl', 'postman', 'developer', 'code', 'script', 'programmatic'
#         ]):
#             return "developer_hub"
        
#         # Product documentation keywords
#         elif any(keyword in query_lower for keyword in [
#             'product', 'feature', 'how to', 'guide', 'tutorial', 'setup', 'configure',
#             'ui', 'interface', 'dashboard', 'catalog', 'discovery', 'governance'
#         ]):
#             return "product_documentation"
        
#         # Default to product documentation
#         return "product_documentation"
    
#     def generate_response(self, query: str, classification: Dict[str, Any]) -> Dict[str, Any]:
#         """Generate response using RAG agent with verbose output"""
#         print(f"\n{'='*80}")
#         print(f"🚀 GENERATING RAG RESPONSE")
#         print(f"{'='*80}")
#         print(f"📝 Query: {query}")
#         print(f"🏷️ Classification: {classification['topic']} | {classification['sentiment']} | {classification['priority']}")
        
#         topic = classification['topic']
        
#         # Check if topic should use RAG
#         rag_topics = ['How-to', 'Product', 'Best-practices', 'API/SDK', 'SSO', 'Connector', 'Lineage', 'Glossary']
        
#         if topic in rag_topics:
#             print(f"✅ Topic '{topic}' will use RAG system")
            
#             # Enhanced query for agent
#             enhanced_query = f"""
#             User Question: {query}
            
#             Topic Classification: {topic}
            
#             Please search the Atlan knowledge base to provide a comprehensive answer with source citations.
#             Focus on practical, actionable information from the official documentation.
#             """
            
#             try:
#                 print("🔄 Invoking RAG agent...")
#                 result = self.agent_executor.invoke({"input": enhanced_query})
                
#                 print("✅ RAG agent completed successfully")
                
#                 return {
#                     "response_type": "rag_generated",
#                     "answer": result["output"],
#                     "intermediate_steps": result.get("intermediate_steps", []),
#                     "sources_included": True
#                 }
                
#             except Exception as e:
#                 print(f"❌ RAG agent error: {str(e)}")
#                 return {
#                     "response_type": "rag_error",
#                     "answer": f"I encountered an error while searching the Atlan documentation: {str(e)}. Please contact support for assistance.",
#                     "sources_included": False,
#                     "error": str(e)
#                 }
#         else:
#             print(f"📤 Topic '{topic}' will be routed (no RAG needed)")
#             ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
#             return {
#                 "response_type": "routed",
#                 "answer": f"This ticket has been classified as a '{topic}' issue with {classification['priority']} priority and routed to the appropriate team. Ticket ID: {ticket_id}",
#                 "sources_included": False,
#                 "ticket_id": ticket_id
#             }
        

# # class AtlanRAGAgent:
# #     """RAG-powered agent using only the Atlan knowledge base"""
    
# #     def __init__(self, knowledge_base):
# #         self.knowledge_base = knowledge_base
        
# #         # Set environment variables
# #         os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
        
# #         self.llm = ChatGroq(
# #             model="llama-3.3-70b-versatile",
# #             temperature=0,
# #             verbose=True
# #         )
        
# #         # Create RAG tool
# #         self.rag_tool = Tool(
# #             name="search_atlan_knowledge",
# #             description="Search Atlan documentation for answers about products, APIs, how-tos, connectors, lineage, SSO, and best practices. Always use this tool for any Atlan-related questions.",
# #             func=self._search_knowledge_base
# #         )
        
# #         # Create agent with only RAG tool
# #         tools = [self.rag_tool]
# #         prompt = hub.pull("hwchase17/react")
# #         agent = create_react_agent(self.llm, tools, prompt)
        
# #         self.agent_executor = AgentExecutor(
# #             agent=agent,
# #             tools=tools,
# #             verbose=True,
# #             max_iterations=5,
# #             early_stopping_method="generate",
# #             return_intermediate_steps=True
# #         )
        
# #         print("🤖 RAG Agent initialized with Atlan knowledge base")
    
# #     def _search_knowledge_base(self, query: str) -> str:
# #         """Search knowledge base with verbose output"""
# #         print(f"\n🔍 SEARCHING ATLAN KNOWLEDGE BASE")
# #         print(f"Query: {query}")
# #         print("-" * 50)
        
# #         try:
# #             # Determine category based on query keywords
# #             category_filter = self._determine_category(query)
# #             print(f"📂 Category Filter: {category_filter}")
            
# #             # Search with RAG
# #             response = self.knowledge_base.generate_rag_response(
# #                 query, 
# #                 limit=5, 
# #                 category_filter=category_filter
# #             )
            
# #             print(f"📊 Confidence Score: {response['confidence']:.3f}")
# #             print(f"📚 Sources Found: {len(response['sources'])}")
            
# #             if response['sources']:
# #                 # Format response with sources
# #                 result = f"Based on Atlan documentation:\n\n{response['answer']}\n\n"
# #                 result += "📖 SOURCES:\n"
                
# #                 for i, source in enumerate(response['sources'], 1):
# #                     result += f"{i}. {source['title']}\n"
# #                     result += f"   URL: {source['url']}\n"
# #                     result += f"   Category: {source['category']}/{source['subcategory']}\n"
# #                     result += f"   Tags: {', '.join(source['tags'])}\n\n"
                
# #                 print("✅ Knowledge base search successful")
# #                 return result
# #             else:
# #                 print("⚠️ No sources found in knowledge base")
# #                 return "I couldn't find specific information in the Atlan documentation for your query. Please contact support for detailed assistance."
                
# #         except Exception as e:
# #             print(f"❌ Knowledge base search error: {str(e)}")
# #             return f"Error searching Atlan documentation: {str(e)}"
    
# #     def _determine_category(self, query: str) -> str:
# #         """Determine search category based on query"""
# #         query_lower = query.lower()
        
# #         # Developer/API related keywords
# #         if any(keyword in query_lower for keyword in [
# #             'api', 'sdk', 'authenticate', 'token', 'python', 'java', 'javascript', 'rest',
# #             'endpoint', 'curl', 'postman', 'developer', 'code', 'script', 'programmatic'
# #         ]):
# #             return "developer_hub"
        
# #         # Product documentation keywords
# #         elif any(keyword in query_lower for keyword in [
# #             'product', 'feature', 'how to', 'guide', 'tutorial', 'setup', 'configure',
# #             'ui', 'interface', 'dashboard', 'catalog', 'discovery', 'governance'
# #         ]):
# #             return "product_documentation"
        
# #         # Default to product documentation
# #         return "product_documentation"
    
# #     def generate_response(self, query: str, classification: Dict[str, Any]) -> Dict[str, Any]:
# #         """Generate response using RAG agent with verbose output"""
# #         print(f"\n{'='*80}")
# #         print(f"🚀 GENERATING RAG RESPONSE")
# #         print(f"{'='*80}")
# #         print(f"📝 Query: {query}")
# #         print(f"🏷️ Classification: {classification['topic']} | {classification['sentiment']} | {classification['priority']}")
        
# #         topic = classification['topic']
        
# #         # Check if topic should use RAG
# #         rag_topics = ['How-to', 'Product', 'Best-practices', 'API/SDK', 'SSO', 'Connector', 'Lineage', 'Glossary']
        
# #         if topic in rag_topics:
# #             print(f"✅ Topic '{topic}' will use RAG system")
            
# #             # Enhanced query for agent
# #             enhanced_query = f"""
# #             User Question: {query}
            
# #             Topic Classification: {topic}
            
# #             Please search the Atlan knowledge base to provide a comprehensive answer with source citations.
# #             Focus on practical, actionable information from the official documentation.
# #             """
            
# #             try:
# #                 print("🔄 Invoking RAG agent...")
# #                 result = self.agent_executor.invoke({"input": enhanced_query})
                
# #                 print("✅ RAG agent completed successfully")
                
# #                 return {
# #                     "response_type": "rag_generated",
# #                     "answer": result["output"],
# #                     "intermediate_steps": result.get("intermediate_steps", []),
# #                     "sources_included": True
# #                 }
                
# #             except Exception as e:
# #                 print(f"❌ RAG agent error: {str(e)}")
# #                 return {
# #                     "response_type": "rag_error",
# #                     "answer": f"I encountered an error while searching the Atlan documentation: {str(e)}. Please contact support for assistance.",
# #                     "sources_included": False,
# #                     "error": str(e)
# #                 }
# #         else:
# #             print(f"📤 Topic '{topic}' will be routed (no RAG needed)")
# #             ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
# #             return {
# #                 "response_type": "routed",
# #                 "answer": f"This ticket has been classified as a '{topic}' issue with {classification['priority']} priority and routed to the appropriate team. Ticket ID: {ticket_id}",
# #                 "sources_included": False,
# #                 "ticket_id": ticket_id
# #             }
import os
import re
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain import hub
from datetime import datetime
from config.settings import settings

class TicketClassifier:
    """Handles ticket classification using LLM with verbose output"""
    
    def __init__(self):
        # Set environment variables
        os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0,
            verbose=True
        )
        print("🚀 Ticket Classifier initialized with Groq LLM")
    
    def classify_ticket(self, ticket_text: str) -> Dict[str, Any]:
        """Classify a ticket with verbose output"""
        print(f"\n{'='*60}")
        print(f"🔍 CLASSIFYING TICKET")
        print(f"{'='*60}")
        print(f"📝 Ticket Text: {ticket_text[:200]}...")
        
        classification_prompt = f"""
        You are an expert support ticket classifier for Atlan, a data catalog platform.
        
        Classify this support ticket into the following categories:
        
        TICKET TEXT:
        {ticket_text}
        
        Please provide classification in EXACTLY this format:
        
        TOPIC: [Choose ONE from: How-to, Product, Connector, Lineage, API/SDK, SSO, Glossary, Best-practices, Sensitive-data]
        SENTIMENT: [Choose ONE from: Frustrated, Curious, Angry, Neutral]  
        PRIORITY: [Choose ONE from: P0-High, P1-Medium, P2-Low]
        REASONING: [Explain why you chose these classifications]
        
        Rules:
        - If asking about connecting data sources → Connector
        - If asking about API, SDK, authentication → API/SDK
        - If asking about data flow, dependencies → Lineage
        - If asking about Single Sign-On, SAML, OAuth → SSO
        - If asking about metadata, business terms → Glossary
        - If asking how to do something → How-to
        - If about product features → Product
        - If about security, PII → Sensitive-data
        - If about recommendations → Best-practices
        
        Priority based on:
        - Business impact mentioned, urgent, blocked team → P0-High
        - Standard request, some urgency → P1-Medium  
        - General question, no urgency → P2-Low
        """
        
        try:
            print("🤖 Sending to LLM for classification...")
            response = self.llm.invoke(classification_prompt)
            print(f"✅ LLM Response received")
            print(f"📋 Raw LLM Response:\n{response.content}")
            
            result = self._parse_classification(response.content)
            
            print(f"\n🏷️ FINAL CLASSIFICATION:")
            print(f"   Topic: {result['topic']}")
            print(f"   Sentiment: {result['sentiment']}")
            print(f"   Priority: {result['priority']}")
            print(f"   Reasoning: {result['reasoning']}")
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Classification error: {str(e)}")
            return {
                "topic": "Product",
                "sentiment": "Neutral", 
                "priority": "P1-Medium",
                "reasoning": f"Classification failed: {str(e)}"
            }
    
    def _parse_classification(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured classification with verbose output"""
        print("🔍 Parsing classification response...")
        
        # Extract using regex
        topic_match = re.search(r'TOPIC:\s*(.+)', response, re.IGNORECASE)
        sentiment_match = re.search(r'SENTIMENT:\s*(.+)', response, re.IGNORECASE)
        priority_match = re.search(r'PRIORITY:\s*(.+)', response, re.IGNORECASE)
        reasoning_match = re.search(r'REASONING:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
        
        topic = topic_match.group(1).strip() if topic_match else "Product"
        sentiment = sentiment_match.group(1).strip() if sentiment_match else "Neutral"
        priority = priority_match.group(1).strip() if priority_match else "P1-Medium"
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "Auto-classified"
        
        print(f"   ✅ Extracted Topic: {topic}")
        print(f"   ✅ Extracted Sentiment: {sentiment}")
        print(f"   ✅ Extracted Priority: {priority}")
        
        return {
            "topic": topic,
            "sentiment": sentiment,
            "priority": priority,
            "reasoning": reasoning
        }

class AtlanRAGAgent:
    """RAG-powered agent using only the Atlan knowledge base"""
    
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        
        # Set environment variables
        os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            verbose=True
        )
        
        # Create RAG tool
        self.rag_tool = Tool(
            name="search_atlan_knowledge",
            description="Search Atlan documentation for answers about products, APIs, how-tos, connectors, lineage, SSO, and best practices. Always use this tool for any Atlan-related questions.",
            func=self._search_knowledge_base
        )
        
        # Create agent with only RAG tool
        tools = [self.rag_tool]
        prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(self.llm, tools, prompt)
        
        # Remove the problematic early_stopping_method parameter
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        print("🤖 RAG Agent initialized with Atlan knowledge base")
    
    def _search_knowledge_base(self, query: str) -> str:
        """Search knowledge base with verbose output"""
        print(f"\n🔍 SEARCHING ATLAN KNOWLEDGE BASE")
        print(f"Query: {query}")
        print("-" * 50)
        
        try:
            # Determine category based on query keywords
            category_filter = self._determine_category(query)
            print(f"📂 Category Filter: {category_filter}")
            
            # Search with RAG
            response = self.knowledge_base.generate_rag_response(
                query, 
                limit=5, 
                category_filter=category_filter
            )
            
            print(f"📊 Confidence Score: {response['confidence']:.3f}")
            print(f"📚 Sources Found: {len(response['sources'])}")
            
            if response['sources']:
                # Format response with sources
                result = f"Based on Atlan documentation:\n\n{response['answer']}\n\n"
                result += "📖 SOURCES:\n"
                
                for i, source in enumerate(response['sources'], 1):
                    result += f"{i}. {source['title']}\n"
                    result += f"   URL: {source['url']}\n"
                    result += f"   Category: {source['category']}/{source['subcategory']}\n"
                    result += f"   Tags: {', '.join(source['tags'])}\n\n"
                
                print("✅ Knowledge base search successful")
                return result
            else:
                print("⚠️ No sources found in knowledge base")
                return "I couldn't find specific information in the Atlan documentation for your query. Please contact support for detailed assistance."
                
        except Exception as e:
            print(f"❌ Knowledge base search error: {str(e)}")
            return f"Error searching Atlan documentation: {str(e)}"
    
    def _determine_category(self, query: str) -> str:
        """Determine search category based on query"""
        query_lower = query.lower()
        
        # Developer/API related keywords
        if any(keyword in query_lower for keyword in [
            'api', 'sdk', 'authenticate', 'token', 'python', 'java', 'javascript', 'rest',
            'endpoint', 'curl', 'postman', 'developer', 'code', 'script', 'programmatic'
        ]):
            return "developer_hub"
        
        # Product documentation keywords
        elif any(keyword in query_lower for keyword in [
            'product', 'feature', 'how to', 'guide', 'tutorial', 'setup', 'configure',
            'ui', 'interface', 'dashboard', 'catalog', 'discovery', 'governance'
        ]):
            return "product_documentation"
        
        # Default to product documentation
        return "product_documentation"
    
    def generate_response(self, query: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using RAG agent with verbose output"""
        print(f"\n{'='*80}")
        print(f"🚀 GENERATING RAG RESPONSE")
        print(f"{'='*80}")
        print(f"📝 Query: {query}")
        print(f"🏷️ Classification: {classification['topic']} | {classification['sentiment']} | {classification['priority']}")
        
        topic = classification['topic']
        
        # Check if topic should use RAG
        rag_topics = ['How-to', 'Product', 'Best-practices', 'API/SDK', 'SSO', 'Connector', 'Lineage', 'Glossary']
        
        if topic in rag_topics:
            print(f"✅ Topic '{topic}' will use RAG system")
            
            # Enhanced query for agent
            enhanced_query = f"""
            User Question: {query}
            
            Topic Classification: {topic}
            
            Please search the Atlan knowledge base to provide a comprehensive answer with source citations.
            Focus on practical, actionable information from the official documentation.
            """
            
            try:
                print("🔄 Invoking RAG agent...")
                result = self.agent_executor.invoke({"input": enhanced_query})
                
                print("✅ RAG agent completed successfully")
                
                return {
                    "response_type": "rag_generated",
                    "answer": result["output"],
                    "intermediate_steps": result.get("intermediate_steps", []),
                    "sources_included": True
                }
                
            except Exception as e:
                print(f"❌ RAG agent error: {str(e)}")
                return {
                    "response_type": "rag_error",
                    "answer": f"I encountered an error while searching the Atlan documentation: {str(e)}. Please contact support for assistance.",
                    "sources_included": False,
                    "error": str(e)
                }
        else:
            print(f"📤 Topic '{topic}' will be routed (no RAG needed)")
            ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "response_type": "routed",
                "answer": f"This ticket has been classified as a '{topic}' issue with {classification['priority']} priority and routed to the appropriate team. Ticket ID: {ticket_id}",
                "sources_included": False,
                "ticket_id": ticket_id
            }
