# import uuid
# from datetime import datetime
# from firecrawl import Firecrawl
# from sentence_transformers import SentenceTransformer
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from qdrant_client import QdrantClient
# from qdrant_client.http import models as rest
# import time

# class KnowledgeBaseManager:
#     def __init__(self):
#         print("=" * 60)
#         print("🚀 Initializing Knowledge Base Manager...")
#         print("=" * 60)

#         # ---- Embedding Model ----
#         print("📚 Initializing embedding model...")
#         self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
#         print("✅ Loaded embedding model: all-MiniLM-L6-v2")

#         # ---- Text Splitter ----
#         print("📝 Initializing text splitter...")
#         self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         print("✅ Text splitter configured (chunk_size=1000, overlap=200)")

#         # ---- Firecrawl ----
#         print("🌐 Initializing Firecrawl scraper...")
#         self.scraper = Firecrawl(api_key="fc-0f0bca73568742ed9c8a11e488ce3b07")
#         print("✅ Firecrawl initialized")

#         # ---- Qdrant ----
#         print("\n🔌 Connecting to Qdrant database...")
#         try:
#             self.qdrant = QdrantClient(
#                 url="https://2926feae-a2ea-4ce3-bafb-b4a47075e39a.eu-central-1-0.aws.cloud.qdrant.io:6333",
#                 api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ySsf9zVCNaQqrirLbX-pc8oBJUDbOmzU5xfdLNHgR8Q",
#                 timeout=30.0  # Increase timeout
#             )
#             print("✅ Connected to Qdrant")
#         except Exception as e:
#             print(f"❌ Failed to connect to Qdrant: {e}")
#             raise

#         self.collection_name = "atlan_documentation"

#         # Check if collection exists first
#         try:
#             collections = self.qdrant.get_collections()
#             collection_names = [col.name for col in collections.collections]
            
#             if self.collection_name in collection_names:
#                 print(f"✅ Collection '{self.collection_name}' already exists")
#                 # Just get the collection info to verify it's working
#                 collection_info = self.qdrant.get_collection(collection_name=self.collection_name)
#                 print(f"📊 Collection vectors: {collection_info.vectors_count}")
#             else:
#                 print(f"📝 Creating new collection: {self.collection_name}")
#                 self._create_collection()
                
#         except Exception as e:
#             print(f"❌ Error checking collections: {e}")
#             print("📝 Creating collection...")
#             self._create_collection()

#         # Check if collection is empty and build knowledge base
#         try:
#             count = self.qdrant.count(collection_name=self.collection_name).count
#             if count == 0:
#                 print("📝 Knowledge base empty → building now...")
#                 self.build_knowledge_base()
#             else:
#                 print(f"📊 Knowledge base already has {count} vectors")
#         except Exception as e:
#             print(f"❌ Error checking collection count: {e}")
#             print("📝 Proceeding with building knowledge base...")
#             self.build_knowledge_base()

#         print("✅ Initialization complete!")

#     def _create_collection(self):
#         """Create collection with proper error handling"""
#         try:
#             self.qdrant.create_collection(
#                 collection_name=self.collection_name,
#                 vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
#             )
#             print("✅ Qdrant collection created successfully")
#         except Exception as e:
#             print(f"❌ Error creating collection: {e}")
#             # Check if collection might already exist
#             try:
#                 collections = self.qdrant.get_collections()
#                 collection_names = [col.name for col in collections.collections]
#                 if self.collection_name in collection_names:
#                     print(f"✅ Collection '{self.collection_name}' exists despite error")
#                 else:
#                     raise e
#             except:
#                 raise e

#     def scrape_all_documentation(self):
#         """Scrape docs using Firecrawl with detailed progress tracking"""
#         urls = [
#             "https://docs.atlan.com/",
#             "https://docs.atlan.com/getting-started",
#             "https://docs.atlan.com/lineage",
#             "https://docs.atlan.com/governance",
#             "https://docs.atlan.com/connectors",
#             "https://docs.atlan.com/sso",
#             "https://docs.atlan.com/glossary",
#             "https://docs.atlan.com/security",
#             "https://docs.atlan.com/best-practices",
#         ]

#         documents = []
#         print(f"\n🌐 Starting documentation scraping for {len(urls)} URLs...")
#         print("-" * 50)

#         for i, url in enumerate(urls, 1):
#             try:
#                 print(f"🔍 [{i}/{len(urls)}] Scraping: {url}")
                
#                 # Add delay to avoid rate limiting
#                 time.sleep(2)  # Increased delay
                
#                 # FIXED: Use the correct method name 'scrape' instead of 'scrape_url'
#                 # and pass formats as a list parameter
#                 data = self.scraper.scrape(url, formats=["markdown"])
                
#                 # FIXED: Access the data differently based on the new API structure
#                 if isinstance(data, dict):
#                     # Check different possible keys for content
#                     text = ""
#                     if "markdown" in data:
#                         text = data["markdown"]
#                     elif "content" in data:
#                         text = data["content"]
#                     elif "data" in data and isinstance(data["data"], dict):
#                         text = data["data"].get("markdown", data["data"].get("content", ""))
                    
#                     # Get metadata
#                     metadata = data.get("metadata", {})
#                     title = metadata.get("title", url.split('/')[-1] or "Homepage")
#                 else:
#                     # If data is not a dict, try to access it as an object
#                     text = getattr(data, 'markdown', '') or getattr(data, 'content', '')
#                     title = getattr(data, 'title', url.split('/')[-1] or "Homepage")
                
#                 if not text or not text.strip():
#                     print(f"   ⚠️  Empty content from {url}")
#                     continue

#                 char_count = len(text)
#                 print(f"   ✅ Success! Title: '{title}', Characters: {char_count}")
                
#                 documents.append({
#                     "url": url,
#                     "title": title,
#                     "content": text,
#                     "scraped_at": datetime.utcnow().isoformat()
#                 })

#             except Exception as e:
#                 print(f"   ❌ Failed scraping {url}: {str(e)}")
#                 # Add more detailed error info for debugging
#                 print(f"   🔧 Error type: {type(e).__name__}")
#                 continue

#         print("-" * 50)
#         print(f"📄 Total successfully scraped documents: {len(documents)}/{len(urls)}")
#         return documents

#     def build_knowledge_base(self):
#         """Scrape, chunk, embed, and store docs in Qdrant with progress tracking"""
#         print("\n🏗️  Building knowledge base...")
        
#         # Scrape documents
#         docs = self.scrape_all_documentation()
#         if not docs:
#             print("⚠️ No documents scraped, skipping indexing")
#             return

#         total_chunks = 0
#         points = []
        
#         print(f"\n🔨 Processing {len(docs)} documents for embedding...")
#         print("-" * 50)

#         for doc_idx, doc in enumerate(docs, 1):
#             try:
#                 print(f"📄 [{doc_idx}/{len(docs)}] Processing: {doc['title']}")
                
#                 # Split into chunks
#                 chunks = self.splitter.split_text(doc["content"])
#                 print(f"   🧩 Created {len(chunks)} chunks")
#                 total_chunks += len(chunks)

#                 # Process each chunk
#                 for chunk_idx, chunk in enumerate(chunks, 1):
#                     try:
#                         # Embed the chunk
#                         vector = self.embedder.encode(chunk).tolist()
                        
#                         points.append(
#                             rest.PointStruct(
#                                 id=str(uuid.uuid4()),
#                                 vector=vector,
#                                 payload={
#                                     "url": doc["url"],
#                                     "title": doc["title"],
#                                     "content": chunk,
#                                     "scraped_at": doc["scraped_at"],
#                                     "chunk_index": chunk_idx,
#                                     "total_chunks": len(chunks)
#                                 },
#                             )
#                         )
                        
#                         # Print progress every 10 chunks
#                         if chunk_idx % 10 == 0:
#                             print(f"   📊 Embedded {chunk_idx}/{len(chunks)} chunks")
                            
#                     except Exception as e:
#                         print(f"   ❌ Error embedding chunk {chunk_idx}: {str(e)}")
#                         continue
                        
#                 print(f"   ✅ Finished processing: {doc['title']}")
                
#             except Exception as e:
#                 print(f"❌ Error processing document {doc['title']}: {str(e)}")
#                 continue

#         # Insert into Qdrant
#         if points:
#             print(f"\n📥 Inserting {len(points)} chunks into Qdrant...")
#             try:
#                 # Insert in smaller batches to avoid timeouts
#                 batch_size = 50  # Reduced batch size
#                 for i in range(0, len(points), batch_size):
#                     batch = points[i:i + batch_size]
#                     try:
#                         self.qdrant.upsert(
#                             collection_name=self.collection_name, 
#                             points=batch,
#                             wait=True
#                         )
#                         print(f"   ✅ Inserted batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
#                     except Exception as batch_error:
#                         print(f"   ⚠️ Batch {i//batch_size + 1} failed: {batch_error}")
#                         # Try individual points
#                         for j, point in enumerate(batch):
#                             try:
#                                 self.qdrant.upsert(
#                                     collection_name=self.collection_name, 
#                                     points=[point],
#                                     wait=True
#                                 )
#                             except Exception as point_error:
#                                 print(f"   ❌ Failed to insert point {j}: {point_error}")
                
#                 print(f"🎉 Successfully inserted {len(points)} chunks into Qdrant!")
                
#                 # Verify insertion
#                 try:
#                     final_count = self.qdrant.count(collection_name=self.collection_name).count
#                     print(f"📊 Total vectors in collection: {final_count}")
#                 except Exception as count_error:
#                     print(f"⚠️ Could not verify count: {count_error}")
                
#             except Exception as e:
#                 print(f"❌ Error inserting into Qdrant: {str(e)}")
#         else:
#             print("⚠️ No points to insert into Qdrant")

#     def search_knowledge_base(self, query, limit=5):
#         """Search the knowledge base for similar content - FIXED: Using query_points instead of deprecated search"""
#         try:
#             # Embed the query
#             query_vector = self.embedder.encode(query).tolist()
            
#             # FIXED: Use query_points instead of deprecated search method
#             results = self.qdrant.query_points(
#                 collection_name=self.collection_name,
#                 query=query_vector,
#                 limit=limit,
#                 with_payload=True,
#                 with_vectors=False
#             )
            
#             return results.points
#         except Exception as e:
#             print(f"❌ Error searching knowledge base: {e}")
#             return []

# # Example usage with better error handling
# if __name__ == "__main__":
#     try:
#         # Initialize the knowledge base manager
#         kb_manager = KnowledgeBaseManager()
        
#         # Example search
#         print("\n🔎 Testing search functionality...")
#         results = kb_manager.search_knowledge_base("data lineage in Atlan", limit=3)
        
#         if results:
#             print(f"\n📋 Search results for 'data lineage in Atlan':")
#             print("-" * 50)
#             for i, result in enumerate(results, 1):
#                 print(f"{i}. {result.payload['title']} (Score: {result.score:.3f})")
#                 print(f"   URL: {result.payload['url']}")
#                 print(f"   Content preview: {result.payload['content'][:100]}...")
#                 print()
#         else:
#             print("❌ No search results found")
            
#     except Exception as e:
#         print(f"❌ Fatal error: {e}")
#         print("💡 Check your Qdrant connection and API key")

import uuid
from datetime import datetime
from firecrawl import Firecrawl
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import time
import requests
import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional
import json

class EnhancedAtlanKnowledgeBase:
    def __init__(self):
        print("=" * 80)
        print("🚀 Initializing Enhanced Atlan Knowledge Base with RAG System")
        print("=" * 80)

        # ---- Embedding Model ----
        print("📚 Initializing embedding model...")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Loaded embedding model: all-MiniLM-L6-v2")

        # ---- Text Splitter ----
        print("📝 Initializing text splitter...")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        print("✅ Text splitter configured (chunk_size=1000, overlap=200)")

        # ---- Scrapers ----
        print("🌐 Initializing scrapers...")
        self.firecrawl = Firecrawl(api_key="fc-0f0bca73568742ed9c8a11e488ce3b07")
        self.jina_headers = {
            "Authorization": "Bearer jina_55344b955b224c19bcb21c73260811c1_Xp6JVTtQb7QDe8CLhVlXSnFHBMQ"
        }
        print("✅ Firecrawl and Jina AI scrapers initialized")

        # ---- Qdrant ----
        print("\n🔌 Connecting to Qdrant database...")
        try:
            self.qdrant = QdrantClient(
                url="https://2926feae-a2ea-4ce3-bafb-b4a47075e39a.eu-central-1-0.aws.cloud.qdrant.io:6333",
                api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ySsf9zVCNaQqrirLbX-pc8oBJUDbOmzU5xfdLNHgR8Q",
                timeout=30.0
            )
            print("✅ Connected to Qdrant")
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant: {e}")
            raise

        self.collection_name = "atlan_knowledge_base_v2"
        self._setup_collection()
        self._initialize_knowledge_base()
        print("✅ Enhanced Atlan Knowledge Base initialization complete!")

    def _get_categorized_urls(self) -> Dict[str, List[str]]:
        """Get categorized URLs for comprehensive scraping"""
        return {
            "product_documentation": [
                "https://docs.atlan.com/",
                "https://docs.atlan.com/getting-started",
                "https://docs.atlan.com/product/capabilities/discovery",
                "https://docs.atlan.com/product/capabilities/data-products/concepts/what-are-data-products",
                "https://docs.atlan.com/product/capabilities/data-products/how-tos/add-stakeholders",
                "https://docs.atlan.com/product/capabilities/discovery/how-tos/add-certificates",
                "https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/use-atlan-ai-for-lineage-analysis",
                "https://docs.atlan.com/product/administration/labs/how-tos/enable-sample-data-download",
                "https://docs.atlan.com/product/integrations/identity-management/sso/how-tos/enable-okta-for-sso",
                "https://docs.atlan.com/product/capabilities/discovery/concepts/what-are-asset-profiles",
                "https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/implement-the-atlan-mcp-server",
                "https://docs.atlan.com/product/capabilities/discovery/concepts/how-to-interpret-timestamps",
                "https://docs.atlan.com/product/capabilities/insights",
                "https://docs.atlan.com/product/capabilities/atlan-ai",
                "https://docs.atlan.com/product/capabilities/atlan-ai/concepts/security",
                "https://docs.atlan.com/product/capabilities/reporting",
                "https://docs.atlan.com/product/capabilities/playbooks",
                "https://docs.atlan.com/product/capabilities/requests/requests",
                "https://docs.atlan.com/product/capabilities/data-models/how-tos/view-data-models",
                "https://docs.atlan.com/lineage",
                "https://docs.atlan.com/governance",
                "https://docs.atlan.com/connectors",
                "https://docs.atlan.com/sso",
                "https://docs.atlan.com/glossary",
                "https://docs.atlan.com/security",
                "https://docs.atlan.com/best-practices"
            ],
            "developer_hub": [
                "https://developer.atlan.com/",
                "https://developer.atlan.com/snippets/authentication",
                "https://developer.atlan.com/snippets/security/audit-logs",
                "https://developer.atlan.com/snippets/security/api-tokens",
                "https://developer.atlan.com/snippets/assets/create",
                "https://developer.atlan.com/snippets/assets/update",
                "https://developer.atlan.com/snippets/assets/delete",
                "https://developer.atlan.com/snippets/assets/search",
                "https://developer.atlan.com/snippets/assets/lineage",
                "https://developer.atlan.com/snippets/glossary/create",
                "https://developer.atlan.com/snippets/glossary/update",
                "https://developer.atlan.com/snippets/glossary/delete",
                "https://developer.atlan.com/snippets/glossary/read",
                "https://developer.atlan.com/snippets/workflows/run",
                "https://developer.atlan.com/snippets/workflows/schedule",
                "https://developer.atlan.com/snippets/workflows/monitor",
                "https://developer.atlan.com/snippets/lineage/custom",
                "https://developer.atlan.com/snippets/lineage/update",
                "https://developer.atlan.com/snippets/lineage/delete",
                "https://developer.atlan.com/sdks/python",
                "https://developer.atlan.com/sdks/java",
                "https://developer.atlan.com/sdks/javascript",
                "https://developer.atlan.com/sdks/go",
                "https://developer.atlan.com/snippets/governance/policies",
                "https://developer.atlan.com/snippets/governance/roles",
                "https://developer.atlan.com/snippets/governance/classifications",
                "https://developer.atlan.com/snippets/governance/certifications",
                "https://developer.atlan.com/snippets/events/setup",
                "https://developer.atlan.com/snippets/events/listen",
                "https://developer.atlan.com/snippets/events/retry"
            ]
        }

    def _categorize_url(self, url: str) -> Dict[str, Any]:
        """Categorize URL and extract metadata"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Base categorization
        if "developer.atlan.com" in domain:
            main_category = "developer_hub"
            source_type = "API/SDK Documentation"
        else:
            main_category = "product_documentation"
            source_type = "Product Documentation"
        
        # Subcategory classification based on URL patterns
        subcategory = "general"
        tags = []
        
        if "/authentication" in path or "/security" in path or "/sso" in path:
            subcategory = "authentication_security"
            tags = ["authentication", "security", "SSO"]
        elif "/assets" in path or "/discovery" in path:
            subcategory = "assets_discovery"
            tags = ["assets", "discovery", "metadata"]
        elif "/glossary" in path:
            subcategory = "glossary"
            tags = ["glossary", "business_metadata"]
        elif "/lineage" in path:
            subcategory = "lineage"
            tags = ["lineage", "data_flow"]
        elif "/governance" in path or "/policies" in path:
            subcategory = "governance"
            tags = ["governance", "policies", "compliance"]
        elif "/workflows" in path or "/playbooks" in path:
            subcategory = "workflows"
            tags = ["workflows", "automation", "playbooks"]
        elif "/connectors" in path:
            subcategory = "connectors"
            tags = ["connectors", "integrations"]
        elif "/sdks" in path:
            subcategory = "sdks"
            # Extract SDK language
            if "/python" in path:
                tags = ["SDK", "Python"]
            elif "/java" in path:
                tags = ["SDK", "Java"]
            elif "/javascript" in path:
                tags = ["SDK", "JavaScript"]
            elif "/go" in path:
                tags = ["SDK", "Go"]
            else:
                tags = ["SDK"]
        elif "/atlan-ai" in path or "/ai" in path:
            subcategory = "atlan_ai"
            tags = ["AI", "artificial_intelligence", "automation"]
        elif "/data-products" in path:
            subcategory = "data_products"
            tags = ["data_products", "data_management"]
        elif "/insights" in path or "/reporting" in path:
            subcategory = "insights_reporting"
            tags = ["insights", "reporting", "analytics"]
        
        return {
            "main_category": main_category,
            "subcategory": subcategory,
            "source_type": source_type,
            "domain": domain,
            "tags": tags,
            "url_path": path
        }

    def _extract_content_with_fallback(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content using multiple methods with fallback"""
        content_data = None
        
        # Method 1: Try Firecrawl first
        try:
            print(f"   🔥 Trying Firecrawl...")
            data = self.firecrawl.scrape(url, formats=["markdown"])
            
            if isinstance(data, dict):
                text = data.get("markdown", "") or data.get("content", "")
                if data.get("data"):
                    text = text or data["data"].get("markdown", "") or data["data"].get("content", "")
                metadata = data.get("metadata", {})
            else:
                text = getattr(data, 'markdown', '') or getattr(data, 'content', '')
                metadata = getattr(data, 'metadata', {})
            
            if text and text.strip():
                content_data = {
                    "content": text,
                    "title": metadata.get("title", ""),
                    "description": metadata.get("description", ""),
                    "method": "firecrawl"
                }
                print(f"   ✅ Firecrawl successful")
        except Exception as e:
            print(f"   ❌ Firecrawl failed: {str(e)}")
        
        # Method 2: Fallback to Jina AI if Firecrawl fails
        if not content_data:
            try:
                print(f"   🤖 Trying Jina AI...")
                jina_url = f"https://r.jina.ai/{url}"
                response = requests.get(jina_url, headers=self.jina_headers, timeout=30)
                
                if response.status_code == 200 and response.text.strip():
                    # Extract title from content if available
                    title_match = re.search(r'^#\s+(.+?)$', response.text, re.MULTILINE)
                    title = title_match.group(1) if title_match else ""
                    
                    content_data = {
                        "content": response.text,
                        "title": title or url.split('/')[-1],
                        "description": "",
                        "method": "jina"
                    }
                    print(f"   ✅ Jina AI successful")
            except Exception as e:
                print(f"   ❌ Jina AI failed: {str(e)}")
        
        return content_data

    def _setup_collection(self):
        """Setup Qdrant collection with proper error handling"""
        try:
            collections = self.qdrant.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                print(f"✅ Collection '{self.collection_name}' already exists")
                collection_info = self.qdrant.get_collection(collection_name=self.collection_name)
                print(f"📊 Collection vectors: {collection_info.vectors_count}")
            else:
                print(f"📝 Creating new collection: {self.collection_name}")
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
                )
                print("✅ Qdrant collection created successfully")
                
        except Exception as e:
            print(f"❌ Error with collection setup: {e}")
            raise

    def _initialize_knowledge_base(self):
        """Initialize knowledge base if empty"""
        try:
            count = self.qdrant.count(collection_name=self.collection_name).count
            if count == 0:
                print("📝 Knowledge base empty → building now...")
                self.build_comprehensive_knowledge_base()
            else:
                print(f"📊 Knowledge base already has {count} vectors")
        except Exception as e:
            print(f"❌ Error checking collection count: {e}")
            print("📝 Proceeding with building knowledge base...")
            self.build_comprehensive_knowledge_base()

    def build_comprehensive_knowledge_base(self):
        """Build comprehensive knowledge base with categorization"""
        print("\n🏗️  Building Comprehensive Atlan Knowledge Base...")
        
        categorized_urls = self._get_categorized_urls()
        all_documents = []
        total_urls = sum(len(urls) for urls in categorized_urls.values())
        processed_count = 0
        
        print(f"🌐 Processing {total_urls} URLs across {len(categorized_urls)} categories...")
        print("=" * 60)
        
        for category, urls in categorized_urls.items():
            print(f"\n📁 Processing Category: {category.upper()}")
            print("-" * 50)
            
            for i, url in enumerate(urls, 1):
                processed_count += 1
                try:
                    print(f"🔍 [{processed_count}/{total_urls}] Scraping: {url}")
                    
                    # Add delay to avoid rate limiting
                    time.sleep(1)
                    
                    # Get content with fallback methods
                    content_data = self._extract_content_with_fallback(url)
                    
                    if not content_data:
                        print(f"   ❌ No content extracted")
                        continue
                    
                    # Get URL metadata and categorization
                    url_metadata = self._categorize_url(url)
                    
                    # Combine all metadata
                    document = {
                        "url": url,
                        "title": content_data["title"] or url.split('/')[-1] or "Homepage",
                        "content": content_data["content"],
                        "description": content_data["description"],
                        "extraction_method": content_data["method"],
                        "scraped_at": datetime.utcnow().isoformat(),
                        **url_metadata  # Add categorization metadata
                    }
                    
                    char_count = len(content_data["content"])
                    print(f"   ✅ Success! Title: '{document['title']}', Characters: {char_count}")
                    print(f"   🏷️  Category: {url_metadata['main_category']}/{url_metadata['subcategory']}")
                    print(f"   📋 Tags: {', '.join(url_metadata['tags'])}")
                    
                    all_documents.append(document)
                    
                except Exception as e:
                    print(f"   ❌ Failed: {str(e)}")
                    continue
        
        print(f"\n📄 Total documents scraped: {len(all_documents)}/{total_urls}")
        
        if not all_documents:
            print("⚠️ No documents scraped, skipping indexing")
            return
        
        # Process and embed documents
        self._process_and_embed_documents(all_documents)

    def _process_and_embed_documents(self, documents: List[Dict[str, Any]]):
        """Process documents into chunks and embed them"""
        print(f"\n🔨 Processing {len(documents)} documents for embedding...")
        print("-" * 60)
        
        points = []
        total_chunks = 0
        
        for doc_idx, doc in enumerate(documents, 1):
            try:
                print(f"📄 [{doc_idx}/{len(documents)}] Processing: {doc['title']}")
                
                # Split into chunks
                chunks = self.splitter.split_text(doc["content"])
                print(f"   🧩 Created {len(chunks)} chunks")
                total_chunks += len(chunks)
                
                # Process each chunk
                for chunk_idx, chunk in enumerate(chunks, 1):
                    try:
                        # Embed the chunk
                        vector = self.embedder.encode(chunk).tolist()
                        
                        # Create comprehensive metadata
                        payload = {
                            "url": doc["url"],
                            "title": doc["title"],
                            "content": chunk,
                            "description": doc["description"],
                            "main_category": doc["main_category"],
                            "subcategory": doc["subcategory"],
                            "source_type": doc["source_type"],
                            "domain": doc["domain"],
                            "tags": doc["tags"],
                            "url_path": doc["url_path"],
                            "extraction_method": doc["extraction_method"],
                            "scraped_at": doc["scraped_at"],
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks),
                            "chunk_length": len(chunk)
                        }
                        
                        points.append(
                            rest.PointStruct(
                                id=str(uuid.uuid4()),
                                vector=vector,
                                payload=payload
                            )
                        )
                        
                        # Print progress every 20 chunks
                        if chunk_idx % 20 == 0:
                            print(f"   📊 Embedded {chunk_idx}/{len(chunks)} chunks")
                            
                    except Exception as e:
                        print(f"   ❌ Error embedding chunk {chunk_idx}: {str(e)}")
                        continue
                        
                print(f"   ✅ Finished processing: {doc['title']}")
                
            except Exception as e:
                print(f"❌ Error processing document {doc['title']}: {str(e)}")
                continue
        
        # Insert into Qdrant
        self._insert_points_to_qdrant(points)

    def _insert_points_to_qdrant(self, points: List[rest.PointStruct]):
        """Insert points into Qdrant with batch processing"""
        if not points:
            print("⚠️ No points to insert into Qdrant")
            return
        
        print(f"\n📥 Inserting {len(points)} chunks into Qdrant...")
        try:
            batch_size = 100
            successful_inserts = 0
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                try:
                    self.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=batch,
                        wait=True
                    )
                    successful_inserts += len(batch)
                    print(f"   ✅ Inserted batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
                except Exception as batch_error:
                    print(f"   ⚠️ Batch {i//batch_size + 1} failed: {batch_error}")
            
            print(f"🎉 Successfully inserted {successful_inserts}/{len(points)} chunks!")
            
            # Verify insertion
            try:
                final_count = self.qdrant.count(collection_name=self.collection_name).count
                print(f"📊 Total vectors in collection: {final_count}")
            except Exception as count_error:
                print(f"⚠️ Could not verify count: {count_error}")
                
        except Exception as e:
            print(f"❌ Error inserting into Qdrant: {str(e)}")

    def search_knowledge_base(self, query: str, limit: int = 5, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enhanced search with category filtering and better results"""
        try:
            # Embed the query
            query_vector = self.embedder.encode(query).tolist()
            
            # Build filter conditions
            filter_conditions = None
            if category_filter:
                filter_conditions = rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="main_category",
                            match=rest.MatchValue(value=category_filter)
                        )
                    ]
                )
            
            # Search in Qdrant
            results = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=filter_conditions,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            return results.points
            
        except Exception as e:
            print(f"❌ Error searching knowledge base: {e}")
            return []

    def generate_rag_response(self, query: str, limit: int = 5, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Generate RAG response with source citations"""
        print(f"🔍 Searching for: '{query}'")
        if category_filter:
            print(f"🏷️  Filtering by category: {category_filter}")
        
        # Search knowledge base
        search_results = self.search_knowledge_base(query, limit, category_filter)
        
        if not search_results:
            return {
                "answer": "I couldn't find relevant information in the Atlan knowledge base for your query.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Compile context and sources
        context_chunks = []
        sources = []
        unique_sources = set()
        
        for result in search_results:
            payload = result.payload
            context_chunks.append({
                "content": payload["content"],
                "title": payload["title"],
                "url": payload["url"],
                "score": result.score,
                "category": f"{payload['main_category']}/{payload['subcategory']}",
                "tags": payload["tags"]
            })
            
            # Collect unique sources
            source_key = (payload["url"], payload["title"])
            if source_key not in unique_sources:
                unique_sources.add(source_key)
                sources.append({
                    "url": payload["url"],
                    "title": payload["title"],
                    "category": payload["main_category"],
                    "subcategory": payload["subcategory"],
                    "tags": payload["tags"]
                })
        
        # Calculate confidence based on best match score
        confidence = search_results[0].score if search_results else 0.0
        
        # Generate contextual answer
        context_text = "\n\n".join([
            f"From {chunk['title']} ({chunk['category']}):\n{chunk['content']}" 
            for chunk in context_chunks
        ])
        
        # Simple answer generation (you can replace this with a more sophisticated LLM)
        answer = f"""Based on the Atlan documentation, here's what I found regarding your query:

{context_text[:2000]}...

The information above comes from {len(sources)} different sources in the Atlan documentation."""
        
        return {
            "answer": answer,
            "sources": sources,
            "context_chunks": context_chunks,
            "confidence": confidence,
            "query": query,
            "category_filter": category_filter
        }

    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get comprehensive stats about the knowledge base"""
        try:
            collection_info = self.qdrant.get_collection(self.collection_name)
            
            # Get category distribution
            category_scroll = self.qdrant.scroll(
                collection_name=self.collection_name,
                limit=10000,
                with_payload=["main_category", "subcategory", "source_type"]
            )
            
            categories = {}
            subcategories = {}
            source_types = {}
            
            for point in category_scroll[0]:
                main_cat = point.payload.get("main_category", "unknown")
                sub_cat = point.payload.get("subcategory", "unknown")
                source_type = point.payload.get("source_type", "unknown")
                
                categories[main_cat] = categories.get(main_cat, 0) + 1
                subcategories[f"{main_cat}/{sub_cat}"] = subcategories.get(f"{main_cat}/{sub_cat}", 0) + 1
                source_types[source_type] = source_types.get(source_type, 0) + 1
            
            return {
                "total_vectors": collection_info.vectors_count,
                "collection_status": collection_info.status,
                "categories": categories,
                "subcategories": subcategories,
                "source_types": source_types,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize the enhanced knowledge base
        kb = EnhancedAtlanKnowledgeBase()
        
        print("\n" + "="*80)
        print("🧪 TESTING RAG SYSTEM")
        print("="*80)
        
        # Test queries with different categories
        test_queries = [
            # ("How do I authenticate with Atlan API?", "developer_hub"),
            # ("What are data products in Atlan?", "product_documentation"), 
            ("what are asset profies?",None),
            ("How do we have to connect to python? ",None), 
            #("How to set up lineage in Atlan?", None),  # No category filter
        ]
        
        for query, category_filter in test_queries:
            print(f"\n🔍 Query: {query}")
            if category_filter:
                print(f"📁 Category Filter: {category_filter}")
            print("-" * 60)
            
            # Generate RAG response
            response = kb.generate_rag_response(query, limit=3, category_filter=category_filter)
            
            print(f"💡 Confidence: {response['confidence']:.3f}")
            print(f"📚 Sources ({len(response['sources'])}):")
            for i, source in enumerate(response['sources'], 1):
                print(f"   {i}. {source['title']} ({source['category']}/{source['subcategory']})")
                print(f"      URL: {source['url']}")
                print(f"      Tags: {', '.join(source['tags'])}")
            
            print(f"\n📖 Answer Preview:")
            print(response['answer'][:300] + "...")
            print()
        
        # Display knowledge base statistics
        print("\n" + "="*80)
        print("📊 KNOWLEDGE BASE STATISTICS")
        print("="*80)
        
        stats = kb.get_knowledge_base_stats()
        if "error" not in stats:
            print(f"📈 Total Vectors: {stats['total_vectors']}")
            print(f"📁 Categories: {', '.join(stats['categories'].keys())}")
            print(f"🏷️  Source Types: {', '.join(stats['source_types'].keys())}")
            print(f"⏰ Last Updated: {stats['last_updated']}")
        else:
            print(f"❌ Error getting stats: {stats['error']}")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()