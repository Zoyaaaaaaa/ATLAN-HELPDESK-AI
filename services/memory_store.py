import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import Settings

class MemoryStore:
    """In-memory data store for tickets and application state"""
    
    def __init__(self):
        self.settings = Settings()
        self.tickets: List[Dict[str, Any]] = []
        self.classified_tickets: List[Dict[str, Any]] = []
        self.processed_tickets: List[Dict[str, Any]] = []
        self.app_stats = {
            "total_tickets_loaded": 0,
            "total_tickets_classified": 0,
            "total_tickets_processed": 0,
            "last_loaded_at": None,
            "classification_stats": {},
            "processing_stats": {}
        }
        
        # Load sample tickets on initialization
        self._load_sample_tickets()
    
    def _load_sample_tickets(self):
        """Load sample tickets from JSON file"""
        try:
            if not os.path.exists(self.settings.SAMPLE_TICKETS_FILE):
                print(f"⚠️ Sample tickets file not found: {self.settings.SAMPLE_TICKETS_FILE}")
                self._create_default_tickets()
                return
            
            print(f"📂 Loading tickets from: {self.settings.SAMPLE_TICKETS_FILE}")
            
            with open(self.settings.SAMPLE_TICKETS_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    self.tickets = data
                elif isinstance(data, dict) and 'tickets' in data:
                    self.tickets = data['tickets']
                else:
                    print("❌ Invalid ticket data format")
                    self._create_default_tickets()
                    return
            
            self.app_stats["total_tickets_loaded"] = len(self.tickets)
            self.app_stats["last_loaded_at"] = datetime.utcnow().isoformat()
            
            print(f"✅ Loaded {len(self.tickets)} tickets successfully")
            
        except Exception as e:
            print(f"❌ Error loading tickets: {e}")
            self._create_default_tickets()
    
    def _create_default_tickets(self):
        """Create default sample tickets if file doesn't exist"""
        print("📝 Creating default sample tickets...")
        
        default_tickets = [
            {
                "id": "TICKET-001",
                "subject": "How to set up Snowflake connector permissions?",
                "body": "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing. We've tried using our standard service account, but it's not working. Our entire BI team is blocked on this integration for a major upcoming project, so it's quite urgent. Could you please provide a definitive list of the exact permissions and credentials needed on the Snowflake side to get this working? Thanks."
            },
            {
                "id": "TICKET-002", 
                "subject": "API authentication not working",
                "body": "I'm trying to use the Python SDK to authenticate with our Atlan instance, but I keep getting 401 errors. I've generated an API token from the admin panel, but the authentication still fails. Can someone help me understand what I'm doing wrong? Here's the code I'm using: atlan.client.configure(api_key='my-token', base_url='https://company.atlan.com')"
            },
            {
                "id": "TICKET-003",
                "subject": "Question about data lineage visualization", 
                "body": "Hi, I'm curious about how Atlan's lineage feature works. We have a complex data pipeline with multiple transformations, and I want to understand how lineage is automatically detected vs manually configured. Is there documentation on best practices for lineage mapping? Also, can we customize the lineage graph appearance?"
            },
            {
                "id": "TICKET-004",
                "subject": "SSO integration with Okta",
                "body": "We need to set up single sign-on integration with our Okta identity provider. Our security team requires all applications to use SSO, and we're getting pushback about Atlan not being properly integrated. This is blocking our rollout to the wider organization. Can you provide step-by-step instructions for Okta SAML configuration?"
            },
            {
                "id": "TICKET-005",
                "subject": "Business glossary terms not syncing",
                "body": "Our business glossary terms that we've defined in Atlan don't seem to be syncing properly with our connected data sources. We've created comprehensive definitions for our key business metrics, but they're not appearing when users browse the data catalog. Is there a sync process we need to trigger manually? This is affecting user adoption as people can't find the context they need."
            },
            {
                "id": "TICKET-006",
                "subject": "Data classification and PII tagging",
                "body": "We need to implement automated PII detection and classification in our data catalog. Our compliance team requires that all personally identifiable information is properly tagged and classified. Does Atlan have built-in capabilities for this, or do we need to configure custom classification rules? We're particularly concerned about GDPR compliance."
            },
            {
                "id": "TICKET-007", 
                "subject": "Performance issues with large datasets",
                "body": "We're experiencing slow loading times when browsing assets from our largest data warehouse. Some tables have millions of rows and hundreds of columns, and the asset profile pages are taking 30+ seconds to load. Is this expected behavior, or are there optimization settings we should configure? Our users are getting frustrated with the performance."
            },
            {
                "id": "TICKET-008",
                "subject": "Workflow automation for data quality",
                "body": "I'm wondering if we can set up automated workflows to run data quality checks and send notifications when issues are detected. We want to create playbooks that trigger when data freshness drops below certain thresholds or when schema changes are detected. What are the capabilities of Atlan's workflow system?"
            }
        ]
        
        self.tickets = default_tickets
        self.app_stats["total_tickets_loaded"] = len(default_tickets)
        self.app_stats["last_loaded_at"] = datetime.utcnow().isoformat()
        
        print(f"✅ Created {len(default_tickets)} default tickets")
    
    def get_tickets(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all tickets with optional limit"""
        if limit:
            return self.tickets[:limit]
        return self.tickets.copy()
    
    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific ticket by ID"""
        for ticket in self.tickets:
            if ticket.get("id") == ticket_id:
                return ticket.copy()
        return None
    
    def add_ticket(self, ticket: Dict[str, Any]) -> str:
        """Add a new ticket and return its ID"""
        if "id" not in ticket:
            # Generate ID if not provided
            ticket_count = len(self.tickets) + 1
            ticket["id"] = f"TICKET-{ticket_count:03d}"
        
        # Add timestamp
        ticket["created_at"] = datetime.utcnow().isoformat()
        
        self.tickets.append(ticket)
        self.app_stats["total_tickets_loaded"] += 1
        
        return ticket["id"]
    
    def store_classified_tickets(self, classified_tickets: List[Dict[str, Any]]):
        """Store classified tickets"""
        self.classified_tickets = classified_tickets
        self.app_stats["total_tickets_classified"] = len(classified_tickets)
        
        # Update classification stats
        classification_stats = {
            "topics": {},
            "sentiments": {},
            "priorities": {}
        }
        
        for ticket in classified_tickets:
            classification = ticket.get("classification", {})
            
            # Count topics
            for topic in classification.get("topic_tags", []):
                classification_stats["topics"][topic] = classification_stats["topics"].get(topic, 0) + 1
            
            # Count sentiments
            sentiment = classification.get("sentiment", "Unknown")
            classification_stats["sentiments"][sentiment] = classification_stats["sentiments"].get(sentiment, 0) + 1
            
            # Count priorities
            priority = classification.get("priority", "Unknown")
            classification_stats["priorities"][priority] = classification_stats["priorities"].get(priority, 0) + 1
        
        self.app_stats["classification_stats"] = classification_stats
    
    def get_classified_tickets(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get classified tickets with optional limit"""
        if limit:
            return self.classified_tickets[:limit]
        return self.classified_tickets.copy()
    
    def store_processed_ticket(self, processed_ticket: Dict[str, Any]):
        """Store a single processed ticket"""
        # Check if ticket already exists (update) or is new
        existing_index = -1
        ticket_id = processed_ticket.get("ticket", {}).get("id")
        
        for i, ticket in enumerate(self.processed_tickets):
            if ticket.get("ticket", {}).get("id") == ticket_id:
                existing_index = i
                break
        
        # Add processing timestamp
        processed_ticket["processed_at"] = datetime.utcnow().isoformat()
        
        if existing_index >= 0:
            # Update existing
            self.processed_tickets[existing_index] = processed_ticket
        else:
            # Add new
            self.processed_tickets.append(processed_ticket)
            self.app_stats["total_tickets_processed"] += 1
        
        # Update processing stats
        self._update_processing_stats(processed_ticket)
    
    def _update_processing_stats(self, processed_ticket: Dict[str, Any]):
        """Update processing statistics"""
        strategy = processed_ticket.get("processing_strategy", "Unknown")
        response_type = processed_ticket.get("response", {}).get("type", "Unknown")
        
        if "processing_stats" not in self.app_stats:
            self.app_stats["processing_stats"] = {}
        
        stats = self.app_stats["processing_stats"]
        
        # Count by strategy
        stats["strategies"] = stats.get("strategies", {})
        stats["strategies"][strategy] = stats["strategies"].get(strategy, 0) + 1
        
        # Count by response type
        stats["response_types"] = stats.get("response_types", {})
        stats["response_types"][response_type] = stats["response_types"].get(response_type, 0) + 1
        
        # Count by confidence (for RAG responses)
        if response_type == "RAG_RESPONSE":
            confidence = processed_ticket.get("response", {}).get("confidence", 0)
            confidence_bucket = "low" if confidence < 0.3 else "medium" if confidence < 0.7 else "high"
            
            stats["rag_confidence"] = stats.get("rag_confidence", {})
            stats["rag_confidence"][confidence_bucket] = stats["rag_confidence"].get(confidence_bucket, 0) + 1
    
    def get_processed_tickets(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get processed tickets with optional limit"""
        if limit:
            return self.processed_tickets[:limit]
        return self.processed_tickets.copy()
    
    def get_processed_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get a processed ticket by ID"""
        for ticket in self.processed_tickets:
            if ticket.get("ticket", {}).get("id") == ticket_id:
                return ticket.copy()
        return None
    
    def get_app_stats(self) -> Dict[str, Any]:
        """Get application statistics"""
        return self.app_stats.copy()
    
    def filter_classified_tickets(self, 
                                topic: Optional[str] = None,
                                sentiment: Optional[str] = None, 
                                priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter classified tickets by classification criteria"""
        filtered = self.classified_tickets
        
        if topic:
            filtered = [t for t in filtered if topic in t.get("classification", {}).get("topic_tags", [])]
        
        if sentiment:
            filtered = [t for t in filtered if t.get("classification", {}).get("sentiment") == sentiment]
        
        if priority:
            filtered = [t for t in filtered if t.get("classification", {}).get("priority") == priority]
        
        return filtered
    
    def search_tickets(self, search_term: str) -> List[Dict[str, Any]]:
        """Search tickets by subject or body content"""
        search_term = search_term.lower()
        results = []
        
        for ticket in self.tickets:
            subject = ticket.get("subject", "").lower()
            body = ticket.get("body", "").lower()
            
            if search_term in subject or search_term in body:
                results.append(ticket.copy())
        
        return results
    
    def clear_all_data(self):
        """Clear all stored data (useful for testing)"""
        self.tickets.clear()
        self.classified_tickets.clear()
        self.processed_tickets.clear()
        self.app_stats = {
            "total_tickets_loaded": 0,
            "total_tickets_classified": 0,
            "total_tickets_processed": 0,
            "last_loaded_at": None,
            "classification_stats": {},
            "processing_stats": {}
        }
        print("🗑️ All data cleared from memory store")