"""
MCP Resource Navigation for Dr. Strunz Knowledge Base
Provides structured access to knowledge resources
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class KnowledgeResource:
    """Represents a navigable knowledge resource"""
    uri: str
    name: str
    type: str  # book, article, forum_thread, topic_collection
    description: str
    metadata: Dict[str, Any]
    children: Optional[List['KnowledgeResource']] = None

class ResourceNavigator:
    """Provides hierarchical navigation through knowledge resources"""
    
    def __init__(self, knowledge_searcher):
        self.knowledge_searcher = knowledge_searcher
        self.resource_tree = self._build_resource_tree()
    
    def _build_resource_tree(self) -> KnowledgeResource:
        """Build hierarchical resource tree"""
        
        root = KnowledgeResource(
            uri="strunz://",
            name="Dr. Strunz Knowledge Base",
            type="root",
            description="Complete collection of Dr. Ulrich Strunz's health knowledge",
            metadata={
                "total_items": 43373,
                "last_updated": "2025-07-17"
            },
            children=[]
        )
        
        # Books collection
        books = KnowledgeResource(
            uri="strunz://books",
            name="Books (13 total)",
            type="collection",
            description="Complete book collection from 2002-2025",
            metadata={"count": 13, "date_range": "2002-2025"},
            children=self._get_book_resources()
        )
        
        # News articles by year
        news = KnowledgeResource(
            uri="strunz://news",
            name="News Articles (6,953 total)",
            type="collection",
            description="Daily health insights and news articles",
            metadata={"count": 6953, "date_range": "2004-2025"},
            children=self._get_news_year_resources()
        )
        
        # Forum by category
        forum = KnowledgeResource(
            uri="strunz://forum",
            name="Forum Discussions (14,435 posts)",
            type="collection",
            description="Community discussions and experiences",
            metadata={"count": 14435, "categories": 6},
            children=self._get_forum_category_resources()
        )
        
        # Topic collections
        topics = KnowledgeResource(
            uri="strunz://topics",
            name="Topic Collections",
            type="collection",
            description="Curated collections by health topic",
            metadata={"curated": True},
            children=self._get_topic_resources()
        )
        
        root.children = [books, news, forum, topics]
        return root
    
    def _get_book_resources(self) -> List[KnowledgeResource]:
        """Get book resources"""
        books = [
            ("fitness-drinks-2002", "Fitness Drinks", "2002", "Healthy drink recipes"),
            ("neue-diaet-2010", "Die neue Diät - Das Fitnessbuch", "2010", "Modern diet approach"),
            ("geheimnis-gesundheit-2010", "Das Geheimnis der Gesundheit", "2010", "Health secrets"),
            ("anti-krebs-2012", "Das neue Anti-Krebs-Programm", "2012", "Cancer prevention"),
            ("no-carb-smoothies-2015", "No-Carb-Smoothies", "2015", "Low-carb smoothie recipes"),
            ("wunder-heilung-2015", "Wunder der Heilung", "2015", "Healing miracles"),
            ("blut-geheimnisse-2016", "Blut - Die Geheimnisse", "2016", "Blood secrets"),
            ("low-carb-kochbuch-2016", "Das Strunz-Low-Carb-Kochbuch", "2016", "Low-carb cookbook"),
            ("heilung-erfahren-2019", "Heilung erfahren", "2019", "Experience healing"),
            ("77-tipps-ruecken-2021", "77 Tipps für Rücken und Gelenke", "2021", "Back and joint health"),
            ("stress-weg-buch-2022", "Das Stress-weg-Buch", "2022", "Stress management"),
            ("amino-revolution-2022", "Die Amino-Revolution", "2022", "Amino acid revolution"),
            ("gen-trick-2025", "Der Gen-Trick", "2025", "Genetic optimization")
        ]
        
        return [
            KnowledgeResource(
                uri=f"strunz://books/{book_id}",
                name=f"{title} ({year})",
                type="book",
                description=desc,
                metadata={"year": year, "book_id": book_id}
            )
            for book_id, title, year, desc in books
        ]
    
    def _get_news_year_resources(self) -> List[KnowledgeResource]:
        """Get news resources by year"""
        years = []
        for year in range(2004, 2026):
            years.append(
                KnowledgeResource(
                    uri=f"strunz://news/{year}",
                    name=f"News {year}",
                    type="news_year",
                    description=f"All articles from {year}",
                    metadata={"year": year}
                )
            )
        return years
    
    def _get_forum_category_resources(self) -> List[KnowledgeResource]:
        """Get forum category resources"""
        categories = [
            ("fitness", "Fitness", "Exercise and training discussions"),
            ("ernaehrung", "Ernährung", "Nutrition and diet topics"),
            ("gesundheit", "Gesundheit", "General health discussions"),
            ("bluttuning", "Bluttuning", "Blood optimization topics"),
            ("mental", "Mental", "Mental health and mindset"),
            ("infektion-praevention", "Infektion & Prävention", "Infection and prevention")
        ]
        
        return [
            KnowledgeResource(
                uri=f"strunz://forum/{cat_id}",
                name=name,
                type="forum_category",
                description=desc,
                metadata={"category_id": cat_id}
            )
            for cat_id, name, desc in categories
        ]
    
    def _get_topic_resources(self) -> List[KnowledgeResource]:
        """Get curated topic resources"""
        topics = [
            ("vitamin-d", "Vitamin D", "Everything about vitamin D optimization"),
            ("energy", "Energy & Fatigue", "Boost energy and fight fatigue"),
            ("immunity", "Immune System", "Strengthen your immune system"),
            ("anti-aging", "Anti-Aging", "Longevity and anti-aging strategies"),
            ("sports-nutrition", "Sports Nutrition", "Nutrition for athletes"),
            ("mental-health", "Mental Health", "Depression, anxiety, and mood"),
            ("cardiovascular", "Heart Health", "Cardiovascular optimization"),
            ("cancer-prevention", "Cancer Prevention", "Prevention strategies"),
            ("hormones", "Hormones", "Hormone optimization"),
            ("gut-health", "Gut Health", "Digestive health and microbiome")
        ]
        
        return [
            KnowledgeResource(
                uri=f"strunz://topics/{topic_id}",
                name=name,
                type="topic",
                description=desc,
                metadata={"topic_id": topic_id}
            )
            for topic_id, name, desc in topics
        ]
    
    async def list_resources(self, uri: Optional[str] = None) -> List[Dict[str, Any]]:
        """List resources at a given URI"""
        
        if not uri:
            uri = "strunz://"
        
        # Navigate to resource
        resource = self._find_resource(self.resource_tree, uri)
        if not resource:
            return []
        
        # Return children or resource itself
        if resource.children:
            return [
                {
                    "uri": child.uri,
                    "name": child.name,
                    "type": child.type,
                    "description": child.description,
                    "metadata": child.metadata
                }
                for child in resource.children
            ]
        else:
            return [{
                "uri": resource.uri,
                "name": resource.name,
                "type": resource.type,
                "description": resource.description,
                "metadata": resource.metadata
            }]
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read content from a specific resource"""
        
        resource = self._find_resource(self.resource_tree, uri)
        if not resource:
            return {"error": f"Resource not found: {uri}"}
        
        # Handle different resource types
        if resource.type == "book":
            return await self._read_book_resource(resource)
        elif resource.type == "news_year":
            return await self._read_news_year_resource(resource)
        elif resource.type == "forum_category":
            return await self._read_forum_category_resource(resource)
        elif resource.type == "topic":
            return await self._read_topic_resource(resource)
        else:
            return {
                "uri": resource.uri,
                "name": resource.name,
                "type": resource.type,
                "description": resource.description,
                "metadata": resource.metadata,
                "content": f"This is a {resource.type} collection. Navigate to its children for specific content."
            }
    
    async def _read_book_resource(self, resource: KnowledgeResource) -> Dict[str, Any]:
        """Read book summary and key points"""
        
        # Search for book content
        results = self.knowledge_searcher.search(
            f"book {resource.name}",
            k=5,
            sources=["book"]
        )
        
        key_points = []
        for result in results:
            if resource.metadata.get("year") in result.metadata.get("source", ""):
                key_points.append(result.text[:200] + "...")
        
        return {
            "uri": resource.uri,
            "name": resource.name,
            "type": "book_summary",
            "content": {
                "description": resource.description,
                "year": resource.metadata.get("year"),
                "key_points": key_points,
                "search_query": f"Use search_knowledge with: book:\"{resource.name}\" to find specific topics"
            }
        }
    
    async def _read_topic_resource(self, resource: KnowledgeResource) -> Dict[str, Any]:
        """Read curated topic content"""
        
        topic_id = resource.metadata.get("topic_id", "")
        
        # Search across all sources for this topic
        results = self.knowledge_searcher.search(
            resource.name,
            k=10
        )
        
        # Organize by source
        by_source = {"book": [], "news": [], "forum": []}
        for result in results:
            source = result.metadata.get("source", "unknown")
            if source in by_source:
                by_source[source].append({
                    "text": result.text[:200] + "...",
                    "score": result.score,
                    "metadata": result.metadata
                })
        
        return {
            "uri": resource.uri,
            "name": resource.name,
            "type": "topic_collection",
            "content": {
                "description": resource.description,
                "sources": {
                    "books": len(by_source["book"]),
                    "news": len(by_source["news"]),
                    "forum": len(by_source["forum"])
                },
                "key_insights": by_source,
                "suggested_queries": self._get_topic_queries(topic_id)
            }
        }
    
    def _find_resource(self, root: KnowledgeResource, uri: str) -> Optional[KnowledgeResource]:
        """Find resource by URI"""
        if root.uri == uri:
            return root
        
        if root.children:
            for child in root.children:
                found = self._find_resource(child, uri)
                if found:
                    return found
        
        return None
    
    def _get_topic_queries(self, topic_id: str) -> List[str]:
        """Get suggested queries for a topic"""
        queries = {
            "vitamin-d": [
                "vitamin d dosage Dr. Strunz",
                "vitamin d blood levels optimal",
                "vitamin d forum experiences"
            ],
            "energy": [
                "mitochondria energy Dr. Strunz",
                "chronic fatigue supplements",
                "energy protocol forum"
            ],
            "immunity": [
                "immune system vitamins Dr. Strunz",
                "zinc selenium immunity",
                "forum cold prevention"
            ]
        }
        return queries.get(topic_id, [f"{topic_id} Dr. Strunz recommendations"])