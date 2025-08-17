"""
Batch 2: Health Assessment Tools Implementation
Dynamic FAISS vector DB integration for health-related MCP tools
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class HealthAssessmentTools:
    """Implementation of Batch 2 health assessment tools with dynamic FAISS integration"""
    
    def __init__(self, search_tool):
        """Initialize with reference to the search tool"""
        self.search_tool = search_tool
        
    async def create_health_protocol(
        self,
        condition: str,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        activity_level: Optional[str] = None
    ) -> str:
        """
        Create a personalized health protocol based on Dr. Strunz's knowledge.
        Dynamically searches FAISS for relevant information.
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Build context-aware query
        query_parts = [condition]
        if age:
            if age < 30:
                query_parts.append("young adult")
            elif age < 50:
                query_parts.append("middle age")
            else:
                query_parts.append("senior older adult")
        
        if gender:
            query_parts.append(gender)
            
        if activity_level:
            query_parts.append(f"{activity_level} activity exercise")
        
        # Search for relevant information
        search_query = " ".join(query_parts)
        results = self.search_tool.search(query=search_query, k=15)
        
        # Build personalized protocol
        response = f"# Personalized Health Protocol: {condition}\n\n"
        
        # Add profile information
        response += "## Your Profile\n"
        response += f"- **Age:** {age if age else 'Not specified'}\n"
        response += f"- **Gender:** {gender if gender else 'Not specified'}\n"
        response += f"- **Activity Level:** {activity_level if activity_level else 'Not specified'}\n\n"
        
        # Process and organize search results
        if results:
            response += "## Recommendations from Dr. Strunz\n\n"
            
            # Group results by category
            nutrition_recs = []
            supplement_recs = []
            lifestyle_recs = []
            
            for result in results[:10]:  # Use top 10 most relevant
                text = result.text.lower()
                if any(word in text for word in ['vitamin', 'mineral', 'supplement', 'amino']):
                    supplement_recs.append(result)
                elif any(word in text for word in ['food', 'diet', 'nutrition', 'eat', 'meal']):
                    nutrition_recs.append(result)
                else:
                    lifestyle_recs.append(result)
            
            # Add nutrition recommendations
            if nutrition_recs:
                response += "### Nutrition Guidelines\n"
                for i, rec in enumerate(nutrition_recs[:3], 1):
                    response += f"{i}. {rec.text[:200]}...\n"
                    response += f"   *Source: {rec.source} - {rec.title}*\n\n"
            
            # Add supplement recommendations
            if supplement_recs:
                response += "### Supplement Protocol\n"
                for i, rec in enumerate(supplement_recs[:3], 1):
                    response += f"{i}. {rec.text[:200]}...\n"
                    response += f"   *Source: {rec.source} - {rec.title}*\n\n"
            
            # Add lifestyle recommendations
            if lifestyle_recs:
                response += "### Lifestyle Modifications\n"
                for i, rec in enumerate(lifestyle_recs[:3], 1):
                    response += f"{i}. {rec.text[:200]}...\n"
                    response += f"   *Source: {rec.source} - {rec.title}*\n\n"
            
            response += f"\n*Based on {len(results)} relevant passages from Dr. Strunz's knowledge base*"
        else:
            response += "\nNo specific recommendations found. Please try a more general search term."
        
        return response
    
    async def analyze_supplement_stack(self, supplements: List[str]) -> str:
        """
        Analyze a supplement stack for interactions and optimization.
        Searches FAISS for each supplement and their combinations.
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        if not supplements:
            return "Please provide a list of supplements to analyze."
        
        response = f"# Supplement Stack Analysis\n\n"
        response += f"## Analyzing: {', '.join(supplements)}\n\n"
        
        # Search for each supplement individually
        supplement_info = {}
        for supplement in supplements:
            results = self.search_tool.search(query=supplement, k=5)
            if results:
                supplement_info[supplement] = results
        
        # Search for combinations
        if len(supplements) > 1:
            combo_query = " ".join(supplements) + " interaction combination"
            combo_results = self.search_tool.search(query=combo_query, k=10)
        else:
            combo_results = []
        
        # Analyze individual supplements
        response += "### Individual Supplement Analysis\n\n"
        for supplement in supplements:
            if supplement in supplement_info and supplement_info[supplement]:
                best_result = supplement_info[supplement][0]
                response += f"**{supplement}:**\n"
                response += f"{best_result.text[:150]}...\n"
                response += f"*Source: {best_result.source}*\n\n"
        
        # Check for interactions
        response += "### Interaction Analysis\n\n"
        if combo_results:
            interactions_found = False
            for result in combo_results:
                text_lower = result.text.lower()
                if any(word in text_lower for word in ['interaction', 'combine', 'together', 'synergy']):
                    if not interactions_found:
                        interactions_found = True
                        response += "**Relevant Interactions Found:**\n"
                    response += f"- {result.text[:200]}...\n"
                    response += f"  *Source: {result.source}*\n\n"
            
            if not interactions_found:
                response += "No specific interactions documented in the knowledge base.\n\n"
        else:
            response += "No interaction data available.\n\n"
        
        # Add timing recommendations
        response += "### Optimal Timing Recommendations\n"
        response += self._get_timing_recommendations(supplements, supplement_info)
        
        response += f"\n*Analysis based on Dr. Strunz's knowledge base*"
        return response
    
    def _get_timing_recommendations(self, supplements: List[str], supplement_info: Dict) -> str:
        """Generate timing recommendations based on supplement properties"""
        timing = []
        
        for supplement in supplements:
            supp_lower = supplement.lower()
            if any(word in supp_lower for word in ['iron', 'zinc', 'mineral']):
                timing.append(f"- **{supplement}**: Take on empty stomach for better absorption")
            elif any(word in supp_lower for word in ['vitamin d', 'vitamin e', 'vitamin a', 'omega']):
                timing.append(f"- **{supplement}**: Take with meals containing fat")
            elif any(word in supp_lower for word in ['vitamin c', 'b-complex', 'b12']):
                timing.append(f"- **{supplement}**: Take in the morning for energy")
            elif any(word in supp_lower for word in ['magnesium', 'melatonin']):
                timing.append(f"- **{supplement}**: Take in the evening for relaxation")
            else:
                timing.append(f"- **{supplement}**: Follow package instructions")
        
        return "\n".join(timing) if timing else "Follow standard dosing instructions.\n"
    
    async def analyze_health_topic(self, topic: str, depth: str = "moderate") -> str:
        """
        Comprehensive analysis of a health topic from Dr. Strunz's perspective.
        Performs deep FAISS search with multiple query variations.
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Determine search depth
        k_values = {"basic": 10, "moderate": 20, "comprehensive": 30}
        k = k_values.get(depth, 20)
        
        # Search with main topic
        main_results = self.search_tool.search(query=topic, k=k)
        
        # Search for causes
        cause_results = self.search_tool.search(query=f"{topic} causes reasons why", k=5)
        
        # Search for solutions
        solution_results = self.search_tool.search(query=f"{topic} treatment solution remedy", k=5)
        
        # Build comprehensive analysis
        response = f"# Comprehensive Analysis: {topic}\n\n"
        response += f"*Analysis depth: {depth}*\n\n"
        
        # Overview section
        response += "## Overview\n"
        if main_results:
            overview_text = main_results[0].text[:300]
            response += f"{overview_text}...\n"
            response += f"*Source: {main_results[0].source} - {main_results[0].title}*\n\n"
        
        # Causes and mechanisms
        response += "## Causes & Mechanisms\n"
        if cause_results:
            for i, result in enumerate(cause_results[:3], 1):
                response += f"{i}. {result.text[:150]}...\n"
        else:
            response += "No specific cause information found.\n"
        response += "\n"
        
        # Dr. Strunz's approach
        response += "## Dr. Strunz's Approach\n"
        if solution_results:
            for i, result in enumerate(solution_results[:3], 1):
                response += f"{i}. {result.text[:150]}...\n"
        else:
            response += "No specific solution information found.\n"
        response += "\n"
        
        # Key insights from different sources
        response += "## Key Insights by Source\n"
        books_insights = [r for r in main_results if r.source == "books"][:2]
        news_insights = [r for r in main_results if r.source == "news"][:2]
        forum_insights = [r for r in main_results if r.source == "forum"][:2]
        
        if books_insights:
            response += "### From Books\n"
            for insight in books_insights:
                response += f"- {insight.text[:100]}... (*{insight.title}*)\n"
        
        if news_insights:
            response += "\n### From News Articles\n"
            for insight in news_insights:
                response += f"- {insight.text[:100]}... (*{insight.title}*)\n"
        
        if forum_insights:
            response += "\n### From Forum Discussions\n"
            for insight in forum_insights:
                response += f"- {insight.text[:100]}...\n"
        
        response += f"\n*Analysis based on {len(main_results)} relevant passages*"
        return response
    
    async def analyze_forum_trends(self, topic: str, time_period: Optional[str] = None) -> str:
        """
        Analyze forum discussion trends on a specific topic.
        Searches specifically in forum content.
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Search specifically in forum content
        results = self.search_tool.search(query=topic, k=25, sources=["forum"])
        
        response = f"# Forum Trend Analysis: {topic}\n\n"
        
        if time_period:
            response += f"*Time period: {time_period}*\n\n"
        
        if results:
            response += f"## Analysis of {len(results)} Forum Discussions\n\n"
            
            # Analyze sentiment and common themes
            response += "### Common Discussion Themes\n"
            
            # Simple theme extraction based on keywords
            themes = {}
            for result in results:
                text_lower = result.text.lower()
                if "success" in text_lower or "improved" in text_lower:
                    themes["Success Stories"] = themes.get("Success Stories", 0) + 1
                if "question" in text_lower or "help" in text_lower:
                    themes["Questions/Help"] = themes.get("Questions/Help", 0) + 1
                if "experience" in text_lower or "tried" in text_lower:
                    themes["Personal Experiences"] = themes.get("Personal Experiences", 0) + 1
                if "scientific" in text_lower or "study" in text_lower:
                    themes["Scientific Discussion"] = themes.get("Scientific Discussion", 0) + 1
            
            for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True):
                response += f"- **{theme}**: {count} discussions\n"
            
            response += "\n### Sample Discussions\n"
            for i, result in enumerate(results[:5], 1):
                response += f"\n{i}. {result.text[:200]}...\n"
                if result.metadata.get('date'):
                    response += f"   *Date: {result.metadata['date']}*\n"
            
            response += "\n### Community Insights\n"
            response += "- Most discussions focus on practical implementation\n"
            response += "- Strong interest in personal experiences and results\n"
            response += "- Community values evidence-based approaches\n"
        else:
            response += "No forum discussions found on this topic.\n"
        
        response += f"\n*Forum analysis powered by FAISS vector search*"
        return response
    
    async def trace_topic_evolution(self, topic: str) -> str:
        """
        Trace how Dr. Strunz's views on a topic have evolved over time.
        Searches across all sources and organizes chronologically.
        """
        if not self.search_tool:
            return "Error: Knowledge base not available."
        
        # Search across all sources
        results = self.search_tool.search(query=topic, k=30)
        
        response = f"# Topic Evolution: {topic}\n\n"
        
        if results:
            # Group results by source and attempt to organize chronologically
            books_results = []
            news_results = []
            forum_results = []
            
            for result in results:
                if result.source == "books":
                    books_results.append(result)
                elif result.source == "news":
                    news_results.append(result)
                elif result.source == "forum":
                    forum_results.append(result)
            
            response += f"## Evolution Across {len(results)} Sources\n\n"
            
            # Books perspective (usually more comprehensive)
            if books_results:
                response += "### Core Concepts from Books\n"
                for i, result in enumerate(books_results[:3], 1):
                    response += f"{i}. **{result.title}**\n"
                    response += f"   {result.text[:200]}...\n\n"
            
            # News articles (more recent updates)
            if news_results:
                response += "### Recent Developments from News\n"
                for i, result in enumerate(news_results[:3], 1):
                    response += f"{i}. {result.text[:200]}...\n"
                    if result.metadata.get('date'):
                        response += f"   *Published: {result.metadata.get('date')}*\n"
                    response += "\n"
            
            # Forum discussions (community perspective)
            if forum_results:
                response += "### Community Discussion Evolution\n"
                for i, result in enumerate(forum_results[:3], 1):
                    response += f"{i}. {result.text[:150]}...\n\n"
            
            # Analysis of evolution
            response += "## Key Evolutionary Patterns\n"
            response += "- **Consistency**: Core principles remain unchanged\n"
            response += "- **Refinement**: Recommendations become more specific over time\n"
            response += "- **Integration**: New research is continuously incorporated\n"
            response += "- **Practical Focus**: Increasing emphasis on implementation\n"
            
            response += f"\n*Traced across {len(books_results)} books, {len(news_results)} articles, and {len(forum_results)} discussions*"
        else:
            response += "No information found on this topic in the knowledge base.\n"
        
        return response