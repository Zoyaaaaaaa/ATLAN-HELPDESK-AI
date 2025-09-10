from firecrawl import Firecrawl
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

# Initialize the enhanced knowledge base with the fix for the Qdrant index issue
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

        self.collection_name = "atlan_knowledge_base_v3"
        self._setup_collection()
        self._initialize_knowledge_base()
        print("✅ Enhanced Atlan Knowledge Base initialization complete!")

    def _setup_collection(self):
        """Setup Qdrant collection with proper error handling and index creation"""
        try:
            collections = self.qdrant.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                print(f"✅ Collection '{self.collection_name}' already exists")
                collection_info = self.qdrant.get_collection(collection_name=self.collection_name)
                print(f"📊 Collection vectors: {collection_info.vectors_count}")
                
                # FIXED: Always ensure the index exists, regardless of data presence
                self._ensure_indexes_exist()
                
            else:
                print(f"📝 Creating new collection: {self.collection_name}")
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
                )
                # Create indexes immediately after collection creation
                self._create_all_indexes()
                print("✅ Qdrant collection and indexes created successfully")
                
        except Exception as e:
            print(f"❌ Error with collection setup: {e}")
            raise

    def _ensure_indexes_exist(self):
        """Ensure all necessary indexes exist on the collection"""
        try:
            print("🔍 Checking and creating missing indexes...")
            
            # List of fields that need indexes for filtering
            index_fields = [
                ("main_category", rest.PayloadSchemaType.KEYWORD),
                ("subcategory", rest.PayloadSchemaType.KEYWORD),
                ("source_type", rest.PayloadSchemaType.KEYWORD),
                ("domain", rest.PayloadSchemaType.KEYWORD)
            ]
            
            for field_name, field_type in index_fields:
                try:
                    # Try to create index (will fail silently if it already exists)
                    self.qdrant.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=field_type,
                        wait=True
                    )
                    print(f"✅ Index ensured for field: {field_name}")
                except Exception as idx_error:
                    # Index might already exist, which is fine
                    if "already exists" in str(idx_error).lower() or "index exists" in str(idx_error).lower():
                        print(f"ℹ️  Index already exists for field: {field_name}")
                    else:
                        print(f"⚠️  Could not create index for {field_name}: {idx_error}")
                        
        except Exception as e:
            print(f"❌ Error ensuring indexes: {e}")

    def _create_all_indexes(self):
        """Create all necessary indexes for filtering"""
        index_fields = [
            ("main_category", rest.PayloadSchemaType.KEYWORD),
            ("subcategory", rest.PayloadSchemaType.KEYWORD),
            ("source_type", rest.PayloadSchemaType.KEYWORD),
            ("domain", rest.PayloadSchemaType.KEYWORD)
        ]
        
        for field_name, field_type in index_fields:
            try:
                self.qdrant.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=field_type,
                    wait=True
                )
                print(f"✅ Created index for field: {field_name}")
            except Exception as e:
                print(f"⚠️  Could not create index for {field_name}: {e}")

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
            
            # Search in Qdrant - FIXED: Use search instead of query_points for better compatibility
            try:
                results = self.qdrant.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=filter_conditions,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
            except Exception as search_error:
                if "query_points" in str(search_error) or "query" in str(search_error):
                    # Fallback to scroll if search fails
                    print("⚠️ Search failed, trying scroll method...")
                    scroll_result = self.qdrant.scroll(
                        collection_name=self.collection_name,
                        scroll_filter=filter_conditions,
                        limit=limit,
                        with_payload=True,
                        with_vectors=False
                    )
                    results = scroll_result[0] if scroll_result else []
                else:
                    raise search_error
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching knowledge base: {e}")
            # Try search without filter as fallback
            try:
                print("🔄 Retrying search without category filter...")
                query_vector = self.embedder.encode(query).tolist()
                results = self.qdrant.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
                return results
            except Exception as fallback_error:
                print(f"❌ Fallback search also failed: {fallback_error}")
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
            
            # Get category distribution using scroll (safer than filtered queries)
            category_scroll = self.qdrant.scroll(
                collection_name=self.collection_name,
                limit=1000,  # Reduced limit for better performance
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

# Initialize the AI classifier
class AtlanTicketClassifier:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        
    def classify_ticket(self, ticket_text):
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
        
        try:
            response = self.llm.invoke(classification_prompt)
            # Extract JSON from response
            json_str = response.content.strip()
            # Clean up the response to extract just the JSON
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                classification = json.loads(json_str)
                return classification
            else:
                # Fallback if JSON parsing fails
                return {
                    "topic_tags": ["Product"],
                    "sentiment": "Neutral",
                    "priority": "P1 (Medium)"
                }
        except Exception as e:
            st.error(f"Classification error: {e}")
            return {
                "topic_tags": ["Product"],
                "sentiment": "Neutral",
                "priority": "P1 (Medium)"
            }

# Initialize the RAG agent
class AtlanRAGAgent:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        
    def generate_response(self, query, classification):
        # Internal analysis view
        internal_analysis = {
            "classification": classification,
            "timestamp": datetime.now().isoformat(),
            "query": query
        }
        
        # Check if we should use RAG or just route the ticket
        rag_topics = ["How-to", "Product", "Best practices", "API/SDK", "SSO"]
        use_rag = any(topic in rag_topics for topic in classification["topic_tags"])
        
        if use_rag:
            # Determine which knowledge base category to use
            if any(topic in ["API/SDK"] for topic in classification["topic_tags"]):
                category_filter = "developer_hub"
            else:
                category_filter = "product_documentation"
                
            # Generate RAG response
            rag_response = self.kb.generate_rag_response(query, category_filter=category_filter)
            
            # Final response view
            final_response = {
                "answer": rag_response["answer"],
                "sources": rag_response["sources"],
                "type": "RAG Response"
            }
        else:
            # Route the ticket
            final_response = {
                "answer": f"This ticket has been classified as a '{classification['topic_tags'][0]}' issue and routed to the appropriate team.",
                "sources": [],
                "type": "Routing Response"
            }
            
        return {
            "internal_analysis": internal_analysis,
            "final_response": final_response
        }

# Load sample tickets
def load_sample_tickets():
    # In a real application, you would load from a file
    # For now, using the provided example and some additional ones
    return [
        {
            "id": "TICKET-245",
            "subject": "Connecting Snowflake to Atlan - required permissions?",
            "body": "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing. We've tried using our standard service account, but it's not working. Our entire BI team is blocked on this integration for a major upcoming project, so it's quite urgent. Could you please provide a definitive list of the exact permissions and credentials needed on the Snowflake side to get this working? Thanks."
        },
        {
            "id": "TICKET-301",
            "subject": "How to create custom lineage in Atlan?",
            "body": "I need to create custom lineage for our ETL processes that aren't automatically captured. The documentation seems sparse on this topic. Can you provide a step-by-step guide?"
        },
        {
            "id": "TICKET-422",
            "subject": "API authentication issues",
            "body": "I'm getting a 401 error when trying to authenticate with the Atlan API using my service account credentials. The same credentials work in the UI. What could be causing this?"
        },
        {
            "id": "TICKET-523",
            "subject": "SSO configuration problems",
            "body": "We're trying to set up SAML SSO with Okta but keep getting an error when users try to log in. The error message is vague and doesn't help us troubleshoot. Can you provide detailed configuration instructions?"
        },
        {
            "id": "TICKET-615",
            "subject": "Data glossary not syncing",
            "body": "Our business glossary terms aren't syncing properly with the technical assets. Some terms show up correctly, but others are missing. This is causing confusion among our data users."
        }
    ]

# Add manual index creation function for troubleshooting
def create_indexes_manually(kb_instance):
    """Manually create indexes if automatic creation fails"""
    try:
        print("🔧 Manually creating indexes...")
        
        index_fields = [
            ("main_category", rest.PayloadSchemaType.KEYWORD),
            ("subcategory", rest.PayloadSchemaType.KEYWORD),
            ("source_type", rest.PayloadSchemaType.KEYWORD),
            ("domain", rest.PayloadSchemaType.KEYWORD)
        ]
        
        for field_name, field_type in index_fields:
            try:
                kb_instance.qdrant.create_payload_index(
                    collection_name=kb_instance.collection_name,
                    field_name=field_name,
                    field_schema=field_type,
                    wait=True
                )
                print(f"✅ Successfully created index for: {field_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️  Index already exists for: {field_name}")
                else:
                    print(f"❌ Failed to create index for {field_name}: {e}")
        
        print("🎉 Index creation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in manual index creation: {e}")
        return False

# Streamlit application
def main():
    st.set_page_config(
        page_title="Atlan Helpdesk AI",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS (keeping the existing styles)
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .ticket-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        background-color: #F3F4F6;
        margin-bottom: 1rem;
    }
    .classification-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .topic-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    .sentiment-badge {
        background-color: #FCE7F3;
        color: #9D174D;
    }
    .priority-badge {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .priority-p0 {
        background-color: #FEE2E2;
        color: #DC2626;
    }
    .priority-p1 {
        background-color: #FEF3C7;
        color: #D97706;
    }
    .priority-p2 {
        background-color: #DCFCE7;
        color: #16A34A;
    }
    .internal-analysis {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .final-response {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .source-item {
        padding: 0.5rem;
        border-left: 3px solid #3B82F6;
        background-color: #EFF6FF;
        margin-bottom: 0.5rem;
        border-radius: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🔍 Atlan Helpdesk AI Assistant</h1>', unsafe_allow_html=True)
    
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
    
    # Initialize components
    with st.spinner("Initializing AI components..."):
        try:
            kb = init_knowledge_base()
            classifier = init_classifier()
            rag_agent = init_rag_agent(kb)
            st.success("AI components initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing components: {e}")
            
            # Offer manual index creation as a troubleshooting option
            if st.button("🔧 Try Manual Index Creation"):
                with st.spinner("Creating indexes manually..."):
                    if 'kb' in locals():
                        success = create_indexes_manually(kb)
                        if success:
                            st.success("Manual index creation completed! Try running the search again.")
                        else:
                            st.error("Manual index creation failed. Please check the logs.")
            return
    
    # Sidebar for KB stats and controls
    st.sidebar.markdown("## Knowledge Base Stats")
    if st.sidebar.button("Refresh Stats"):
        stats = kb.get_knowledge_base_stats()
        st.sidebar.json(stats)
    
    # Manual index creation button in sidebar
    st.sidebar.markdown("## Troubleshooting")
    if st.sidebar.button("🔧 Create Indexes Manually"):
        with st.spinner("Creating indexes..."):
            success = create_indexes_manually(kb)
            if success:
                st.sidebar.success("Indexes created successfully!")
            else:
                st.sidebar.error("Index creation failed.")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📧 Process Tickets", "🔍 Knowledge Search", "📊 System Status"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Process Support Tickets</h2>', unsafe_allow_html=True)
        
        # Load sample tickets
        sample_tickets = load_sample_tickets()
        
        # Ticket selection
        selected_ticket = st.selectbox(
            "Select a sample ticket:",
            options=sample_tickets,
            format_func=lambda x: f"{x['id']}: {x['subject']}"
        )
        
        # Display selected ticket
        if selected_ticket:
            st.markdown(f"""
            <div class="ticket-card">
                <h4>{selected_ticket['subject']}</h4>
                <p><strong>ID:</strong> {selected_ticket['id']}</p>
                <p>{selected_ticket['body']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Process ticket button
            if st.button("🤖 Process Ticket with AI"):
                with st.spinner("Processing ticket..."):
                    try:
                        # Classify the ticket
                        ticket_text = f"{selected_ticket['subject']}\n\n{selected_ticket['body']}"
                        classification = classifier.classify_ticket(ticket_text)
                        
                        # Generate response
                        response = rag_agent.generate_response(ticket_text, classification)
                        
                        # Display results
                        st.markdown('<h3 class="sub-header">AI Analysis Results</h3>', unsafe_allow_html=True)
                        
                        # Internal Analysis
                        st.markdown("### 🔍 Internal Analysis")
                        st.markdown(f"""
                        <div class="internal-analysis">
                            <p><strong>Classification:</strong></p>
                            <div>
                                <span class="classification-badge topic-badge">Topics: {', '.join(classification['topic_tags'])}</span>
                                <span class="classification-badge sentiment-badge">Sentiment: {classification['sentiment']}</span>
                                <span class="classification-badge priority-badge">Priority: {classification['priority']}</span>
                            </div>
                            <p><strong>Processed:</strong> {response['internal_analysis']['timestamp']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Final Response
                        st.markdown("### 💬 AI Response")
                        st.markdown(f"""
                        <div class="final-response">
                            <p><strong>Response Type:</strong> {response['final_response']['type']}</p>
                            <p>{response['final_response']['answer']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Sources (if any)
                        if response['final_response']['sources']:
                            st.markdown("### 📚 Sources")
                            for source in response['final_response']['sources']:
                                st.markdown(f"""
                                <div class="source-item">
                                    <strong>{source['title']}</strong><br>
                                    <small>Category: {source['category']} | Tags: {', '.join(source['tags'])}</small><br>
                                    <a href="{source['url']}" target="_blank">📖 Read Documentation</a>
                                </div>
                                """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error processing ticket: {e}")
    
    with tab2:
        st.markdown('<h2 class="sub-header">Search Knowledge Base</h2>', unsafe_allow_html=True)
        
        # Search interface
        search_query = st.text_input("Enter your search query:", placeholder="e.g., How to connect Snowflake to Atlan")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            category_filter = st.selectbox(
                "Filter by category:",
                options=["None", "product_documentation", "developer_hub"],
                index=0
            )
        with col2:
            search_limit = st.slider("Number of results:", min_value=1, max_value=10, value=5)
        
        if st.button("🔍 Search Knowledge Base"):
            if search_query:
                with st.spinner("Searching..."):
                    try:
                        category = None if category_filter == "None" else category_filter
                        rag_response = kb.generate_rag_response(search_query, limit=search_limit, category_filter=category)
                        
                        # Display results
                        st.markdown("### 📋 Search Results")
                        st.markdown(f"**Confidence Score:** {rag_response['confidence']:.3f}")
                        
                        if rag_response['sources']:
                            st.markdown("### 💡 Answer")
                            st.write(rag_response['answer'])
                            
                            st.markdown("### 📚 Sources")
                            for i, source in enumerate(rag_response['sources'], 1):
                                st.markdown(f"""
                                <div class="source-item">
                                    <strong>{i}. {source['title']}</strong><br>
                                    <small>Category: {source['category']}/{source['subcategory']} | Tags: {', '.join(source['tags'])}</small><br>
                                    <a href="{source['url']}" target="_blank">📖 Read Full Documentation</a>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("No relevant information found in the knowledge base.")
                            
                    except Exception as e:
                        st.error(f"Search error: {e}")
                        st.info("Try using the manual index creation button in the sidebar if you're getting indexing errors.")
            else:
                st.warning("Please enter a search query.")
    
    with tab3:
        st.markdown('<h2 class="sub-header">System Status</h2>', unsafe_allow_html=True)
        
        if st.button("🔄 Refresh System Status"):
            try:
                stats = kb.get_knowledge_base_stats()
                
                if "error" not in stats:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Vectors", stats["total_vectors"])
                        st.metric("Collection Status", stats["collection_status"])
                    
                    with col2:
                        st.markdown("**Categories:**")
                        for cat, count in stats["categories"].items():
                            st.write(f"• {cat}: {count}")
                    
                    with col3:
                        st.markdown("**Source Types:**")
                        for source_type, count in stats["source_types"].items():
                            st.write(f"• {source_type}: {count}")
                    
                    st.markdown("### 📊 Detailed Breakdown")
                    st.json(stats)
                else:
                    st.error(f"Error getting stats: {stats['error']}")
                    
            except Exception as e:
                st.error(f"Error retrieving system status: {e}")

if __name__ == "__main__":
    main()