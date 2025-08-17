"""
MCP Sampling Support for Dr. Strunz Knowledge Base
Provides guided discovery through example queries and interactive prompts
"""

from typing import List, Dict, Any
import random
from dataclasses import dataclass

@dataclass
class SampleQuery:
    """Represents a sample query with metadata"""
    query: str
    category: str
    capability: str
    expected_insights: List[str]
    difficulty: str  # beginner, intermediate, advanced

class KnowledgeSampler:
    """Provides intelligent sampling for knowledge discovery"""
    
    def __init__(self):
        self.sample_queries = self._initialize_samples()
        self.user_history = []
        
    def _initialize_samples(self) -> List[SampleQuery]:
        """Initialize sample queries from extended samples"""
        from src.mcp.extended_samples import get_all_contextual_samples
        
        # Convert extended samples to SampleQuery format
        extended = get_all_contextual_samples()
        samples = []
        
        for ext in extended:
            samples.append(SampleQuery(
                query=ext.query,
                category=ext.category,
                capability=ext.capability,
                expected_insights=ext.expected_insights,
                difficulty=ext.difficulty
            ))
        
        return samples
    
    def _initialize_samples_old(self) -> List[SampleQuery]:
        """Initialize sample queries for different knowledge areas"""
        return [
            # Beginner samples - common health questions
            SampleQuery(
                query="What vitamins should I take daily?",
                category="basic_nutrition",
                capability="search_knowledge",
                expected_insights=["Vitamin D3", "Magnesium", "Omega-3", "B-Complex"],
                difficulty="beginner"
            ),
            SampleQuery(
                query="How can I improve my energy levels?",
                category="energy_optimization",
                capability="create_health_protocol",
                expected_insights=["Mitochondrial support", "CoQ10", "B vitamins", "Exercise"],
                difficulty="beginner"
            ),
            
            # Intermediate samples - specific conditions
            SampleQuery(
                query="What does Dr. Strunz recommend for high cholesterol?",
                category="cardiovascular",
                capability="search_knowledge",
                expected_insights=["Statins criticism", "Natural alternatives", "Niacin", "Exercise"],
                difficulty="intermediate"
            ),
            SampleQuery(
                query="Show me forum discussions about Q10 dosage",
                category="community_wisdom",
                capability="search_knowledge",
                expected_insights=["User experiences", "Dosage ranges", "Timing", "Forms"],
                difficulty="intermediate"
            ),
            
            # Advanced samples - complex analysis
            SampleQuery(
                query="How has Dr. Strunz's stance on protein evolved from 2002 to 2025?",
                category="evolution_analysis",
                capability="trace_topic_evolution",
                expected_insights=["Early low-carb focus", "Protein timing", "Quality emphasis"],
                difficulty="advanced"
            ),
            SampleQuery(
                query="Find contradictions in vitamin D recommendations",
                category="contradiction_analysis",
                capability="find_contradictions",
                expected_insights=["Dosage changes", "Sun exposure", "Testing frequency"],
                difficulty="advanced"
            ),
            
            # Community-focused samples
            SampleQuery(
                query="What are the most discussed supplements in the forum?",
                category="community_trends",
                capability="analyze_health_topic",
                expected_insights=["Popular supplements", "User results", "Common questions"],
                difficulty="intermediate"
            )
        ]
    
    def get_contextual_samples(self, user_context: Dict[str, Any]) -> List[SampleQuery]:
        """Get samples based on user context and history"""
        
        # Analyze user's interests from history
        if user_context.get("previous_queries"):
            categories = self._analyze_interests(user_context["previous_queries"])
            relevant_samples = [s for s in self.sample_queries if s.category in categories]
        else:
            # New user - provide diverse beginner samples
            relevant_samples = [s for s in self.sample_queries if s.difficulty == "beginner"]
        
        # Add progressive difficulty
        if user_context.get("experience_level", "beginner") == "intermediate":
            relevant_samples.extend([s for s in self.sample_queries if s.difficulty == "intermediate"])
        
        return relevant_samples[:5]  # Return top 5 most relevant
    
    def _analyze_interests(self, previous_queries: List[str]) -> List[str]:
        """Analyze user's interests from query history"""
        interests = []
        
        keyword_map = {
            "energy_optimization": ["energy", "tired", "fatigue", "mitochondria"],
            "cardiovascular": ["heart", "cholesterol", "blood pressure"],
            "community_wisdom": ["forum", "discussion", "community", "users"],
            "basic_nutrition": ["vitamin", "supplement", "daily", "basic"],
            "evolution_analysis": ["evolved", "changed", "history", "timeline"],
            "contradiction_analysis": ["contradiction", "conflict", "different"]
        }
        
        for query in previous_queries:
            query_lower = query.lower()
            for category, keywords in keyword_map.items():
                if any(keyword in query_lower for keyword in keywords):
                    interests.append(category)
        
        return list(set(interests))  # Remove duplicates
    
    def generate_interactive_prompt(self, sample: SampleQuery) -> Dict[str, Any]:
        """Generate an interactive prompt that guides the user"""
        return {
            "type": "interactive_sample",
            "sample_query": sample.query,
            "guidance": {
                "what_to_expect": f"This query will use the '{sample.capability}' capability to explore {sample.category.replace('_', ' ')}",
                "key_insights": sample.expected_insights,
                "follow_up_suggestions": self._generate_follow_ups(sample),
                "learning_path": self._suggest_learning_path(sample)
            },
            "metadata": {
                "difficulty": sample.difficulty,
                "estimated_time": "2-3 minutes",
                "sources": ["books", "news", "forum"] if "forum" in sample.query else ["books", "news"]
            }
        }
    
    def _generate_follow_ups(self, sample: SampleQuery) -> List[str]:
        """Generate follow-up questions based on the sample"""
        follow_ups = []
        
        if sample.category == "basic_nutrition":
            follow_ups = [
                "What are the optimal dosages for these vitamins?",
                "When should I take each supplement?",
                "Are there any interactions I should know about?"
            ]
        elif sample.category == "community_wisdom":
            follow_ups = [
                "What side effects do users report?",
                "Which brands does the community recommend?",
                "How long before seeing results?"
            ]
        elif sample.category == "evolution_analysis":
            follow_ups = [
                "What triggered these changes in recommendations?",
                "Which book introduced each new concept?",
                "How does this compare to mainstream medicine?"
            ]
        
        return follow_ups
    
    def _suggest_learning_path(self, sample: SampleQuery) -> List[Dict[str, str]]:
        """Suggest a learning path based on the sample query"""
        paths = {
            "basic_nutrition": [
                {"step": 1, "action": "Search for basic vitamin guide", "capability": "search_knowledge"},
                {"step": 2, "action": "Create personalized protocol", "capability": "create_health_protocol"},
                {"step": 3, "action": "Check forum for user experiences", "capability": "search_knowledge"}
            ],
            "energy_optimization": [
                {"step": 1, "action": "Search mitochondrial health", "capability": "search_knowledge"},
                {"step": 2, "action": "Analyze supplement stack", "capability": "analyze_supplement_stack"},
                {"step": 3, "action": "Track topic evolution", "capability": "trace_topic_evolution"}
            ],
            "community_wisdom": [
                {"step": 1, "action": "Search specific forum topics", "capability": "search_knowledge"},
                {"step": 2, "action": "Analyze community trends", "capability": "analyze_health_topic"},
                {"step": 3, "action": "Compare with book recommendations", "capability": "find_contradictions"}
            ]
        }
        
        return paths.get(sample.category, [])

class MCPSamplingHandler:
    """Handles MCP sampling requests and responses"""
    
    def __init__(self, knowledge_searcher):
        self.sampler = KnowledgeSampler()
        self.knowledge_searcher = knowledge_searcher
    
    async def handle_sampling_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP sampling request"""
        
        # Get user context
        user_context = {
            "previous_queries": request.get("history", []),
            "experience_level": request.get("experience_level", "beginner"),
            "interests": request.get("interests", [])
        }
        
        # Get contextual samples
        samples = self.sampler.get_contextual_samples(user_context)
        
        # Generate interactive prompts
        interactive_samples = []
        for sample in samples:
            prompt = self.sampler.generate_interactive_prompt(sample)
            
            # Add actual search preview
            if self.knowledge_searcher:
                preview_results = await self._get_preview_results(sample.query)
                prompt["preview"] = preview_results
            
            interactive_samples.append(prompt)
        
        return {
            "type": "sampling_response",
            "samples": interactive_samples,
            "guidance": {
                "how_to_use": "Click any sample to execute it, or modify it to explore related topics",
                "tips": [
                    "Start with beginner samples to understand the system",
                    "Use follow-up questions to dive deeper",
                    "Combine different capabilities for comprehensive insights"
                ]
            },
            "personalization": {
                "detected_interests": user_context.get("interests", []),
                "suggested_next_steps": self._suggest_next_steps(user_context)
            }
        }
    
    async def _get_preview_results(self, query: str) -> Dict[str, Any]:
        """Get preview of what the query would return"""
        try:
            # Quick search with limit 3
            results = self.knowledge_searcher.search(query, k=3)
            
            return {
                "result_count": len(results),
                "source_types": list(set(r.metadata.get("source", "") for r in results)),
                "preview_snippet": results[0].text[:150] + "..." if results else "No preview available"
            }
        except:
            return {"error": "Preview not available"}
    
    def _suggest_next_steps(self, user_context: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on user progress"""
        if user_context.get("experience_level") == "beginner":
            return [
                "Try searching for a specific vitamin or supplement",
                "Ask about a health condition you're interested in",
                "Explore what the community discusses in forums"
            ]
        else:
            return [
                "Compare recommendations across different time periods",
                "Analyze supplement combinations for synergy",
                "Find contradictions to understand nuanced views"
            ]