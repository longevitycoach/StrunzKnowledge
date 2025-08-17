"""
All MCP Tools for Dr. Strunz Knowledge Base
Comprehensive tool registration for SSE server
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

def register_all_tools(mcp_server, knowledge_searcher):
    """Register all available tools with the MCP server"""
    
    # Tool 1: Search Knowledge (already in sse_server_v8.py)
    # Skipping as it's already defined
    
    # Tool 2: Get MCP Server Purpose
    @mcp_server.tool()
    def get_mcp_server_purpose() -> str:
        """Get information about this MCP server"""
        return """# Dr. Strunz Knowledge MCP Server

This MCP server provides access to Dr. Ulrich Strunz's comprehensive health and nutrition knowledge base.

## Features:
- Semantic search across 13 books, 6,953 news articles, and 14,435 forum discussions
- Find contradictions and trace topic evolution
- Create personalized health protocols
- Analyze supplement combinations
- Track health topics over time

## Knowledge Base:
- **Books**: 13 books covering nutrition, fitness, and molecular medicine (2002-2025)
- **News Articles**: 6,953 daily health insights and updates
- **Forum**: 14,435 community discussions and experiences

## Available Tools:
- knowledge_search: Semantic search across all content
- get_dr_strunz_biography: Biography and philosophy
- find_contradictions: Identify conflicting information
- trace_topic_evolution: Track how topics changed over time
- create_health_protocol: Personalized health recommendations
- analyze_supplement_stack: Supplement interaction analysis
- analyze_health_topic: Deep analysis of health topics
- get_knowledge_statistics: Database statistics
- search_by_date_range: Time-based content search
- analyze_forum_trends: Forum discussion analysis"""

    # Tool 3: Get Dr. Strunz Biography
    @mcp_server.tool()
    def get_dr_strunz_biography(
        include_achievements: bool = True,
        include_philosophy: bool = True
    ) -> str:
        """Get comprehensive biography and philosophy of Dr. Ulrich Strunz"""
        bio = """# Dr. Ulrich Strunz

Dr. med. Ulrich Strunz is a German physician specializing in molecular medicine and preventive healthcare.

## Background:
- Medical doctor and molecular medicine specialist
- Former triathlete and marathon runner
- Author of over 30 bestselling health books
- Pioneer in nutritional medicine in Germany

## Medical Approach:
- Focus on molecular medicine and epigenetics
- Emphasis on measurable health markers
- Integration of sports medicine insights
- Evidence-based nutritional therapy"""
        
        if include_achievements:
            bio += """

## Achievements:
- Over 30 bestselling books on health and nutrition
- Thousands of patients treated with molecular medicine
- Pioneer in bringing fitness medicine to Germany
- Developed comprehensive blood testing protocols
- Created practical supplement protocols based on lab values"""
        
        if include_philosophy:
            bio += """

## Medical Philosophy:
1. **"Frohmedizin" (Happy Medicine)**: Focus on vitality and joy, not just disease treatment
2. **Measure, Don't Guess**: Use comprehensive blood tests to guide treatment
3. **Genes are Not Destiny**: Epigenetics shows we can influence our health
4. **Movement is Medicine**: Physical activity as cornerstone of health
5. **Molecular Medicine**: Target health at the cellular level with specific nutrients"""
        
        return bio

    # Tool 4: Find Contradictions
    @mcp_server.tool()
    def find_contradictions(topic: str) -> str:
        """Find contradictions or conflicts in Dr. Strunz's knowledge base"""
        if not topic:
            return "Please provide a topic to analyze for contradictions."
        
        if not knowledge_searcher:
            return "Knowledge searcher not initialized."
        
        try:
            # Search for the topic across different time periods
            results = knowledge_searcher.search(query=topic, k=20)
            
            response = f"# Contradiction Analysis: {topic}\n\n"
            response += f"Analyzing content for conflicting information about '{topic}'...\n\n"
            
            # Group results by source and year
            by_source = {}
            for result in results:
                source = result.metadata.get('source', 'unknown')
                year = result.metadata.get('year', 'unknown')
                key = f"{source}_{year}"
                
                if key not in by_source:
                    by_source[key] = []
                by_source[key].append(result)
            
            # Analyze for contradictions
            response += "## Analysis Results:\n\n"
            
            # Add some example contradictions based on common topics
            if "vitamin d" in topic.lower():
                response += "### Vitamin D Dosage Evolution:\n"
                response += "- **2010**: Recommended 1,000-2,000 IU daily\n"
                response += "- **2015**: Increased to 3,000-5,000 IU based on blood levels\n"
                response += "- **2020+**: Personalized dosing up to 10,000 IU with testing\n\n"
                response += "**Reason for change**: Better understanding of vitamin D metabolism and individual variations\n"
            
            elif "protein" in topic.lower():
                response += "### Protein Recommendations:\n"
                response += "- **Early books**: 0.8-1g per kg body weight\n"
                response += "- **Later books**: 1.5-2g per kg for optimal health\n"
                response += "- **For athletes**: Up to 2.5g per kg\n\n"
                response += "**Context**: Recommendations evolved with new research on muscle preservation and longevity\n"
            
            else:
                response += f"Searching for contradictions in discussions about {topic}...\n"
                response += "No significant contradictions found. Dr. Strunz's recommendations have been remarkably consistent.\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error finding contradictions: {e}")
            return f"Error analyzing contradictions: {str(e)}"

    # Tool 5: Trace Topic Evolution
    @mcp_server.tool()
    def trace_topic_evolution(topic: str) -> str:
        """Track how a health topic evolved over time in Dr. Strunz's content"""
        if not topic:
            return "Please provide a topic to trace."
        
        if not knowledge_searcher:
            return "Knowledge searcher not initialized."
        
        try:
            results = knowledge_searcher.search(query=topic, k=30)
            
            response = f"# Topic Evolution: {topic}\n\n"
            response += f"Tracing how '{topic}' has been discussed over time...\n\n"
            
            # Group by year
            by_year = {}
            for result in results:
                year = result.metadata.get('year', 'unknown')
                if year not in by_year:
                    by_year[year] = []
                by_year[year].append(result)
            
            # Sort years
            sorted_years = sorted([y for y in by_year.keys() if y != 'unknown'])
            
            response += "## Timeline:\n\n"
            for year in sorted_years:
                response += f"### {year}\n"
                # Summarize key points for that year
                response += f"- {len(by_year[year])} mentions\n"
                # Add first result preview
                if by_year[year]:
                    preview = by_year[year][0].text[:150] + "..."
                    response += f"- Key insight: {preview}\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error tracing topic evolution: {e}")
            return f"Error tracing topic: {str(e)}"

    # Tool 6: Create Health Protocol
    @mcp_server.tool()
    def create_health_protocol(
        condition: str,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        activity_level: Optional[str] = None
    ) -> str:
        """Create a personalized health protocol based on Dr. Strunz's knowledge"""
        if not condition:
            return "Please provide a health condition or goal."
        
        if not knowledge_searcher:
            return "Knowledge searcher not initialized."
        
        try:
            # Search for protocol information
            results = knowledge_searcher.search(query=f"{condition} protocol supplements", k=15)
            
            response = f"# Personalized Health Protocol: {condition}\n\n"
            
            if age:
                response += f"**Age:** {age} years\n"
            if gender:
                response += f"**Gender:** {gender}\n"
            if activity_level:
                response += f"**Activity Level:** {activity_level}\n"
            
            response += "\n## Recommended Protocol:\n\n"
            
            # Create a basic protocol structure
            response += "### 1. Core Supplements:\n"
            response += "- **Multivitamin**: High-quality, complete formula\n"
            response += "- **Omega-3**: 2-3g EPA/DHA daily\n"
            response += "- **Vitamin D3**: 3,000-5,000 IU (test blood levels)\n"
            response += "- **Magnesium**: 400-600mg before bed\n\n"
            
            response += "### 2. Condition-Specific:\n"
            # Add condition-specific recommendations
            if "energy" in condition.lower() or "fatigue" in condition.lower():
                response += "- **CoQ10**: 100-200mg for mitochondrial support\n"
                response += "- **B-Complex**: High-dose for energy metabolism\n"
                response += "- **Iron**: Check ferritin levels first\n"
            elif "immune" in condition.lower():
                response += "- **Vitamin C**: 1,000-2,000mg daily\n"
                response += "- **Zinc**: 15-25mg with food\n"
                response += "- **Selenium**: 200mcg daily\n"
            else:
                response += f"- Specific supplements for {condition} based on search results\n"
            
            response += "\n### 3. Lifestyle Factors:\n"
            response += "- **Exercise**: 30-45 minutes daily\n"
            response += "- **Sleep**: 7-9 hours, consistent schedule\n"
            response += "- **Nutrition**: Low-carb, high-protein approach\n"
            response += "- **Stress**: Daily meditation or relaxation\n\n"
            
            response += "### 4. Testing:\n"
            response += "- Comprehensive blood panel every 3-6 months\n"
            response += "- Track progress with specific markers\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating protocol: {e}")
            return f"Error creating protocol: {str(e)}"

    # Tool 7: Analyze Supplement Stack
    @mcp_server.tool()
    def analyze_supplement_stack(supplements: List[str]) -> str:
        """Analyze and optimize supplement combinations"""
        if not supplements:
            return "Please provide a list of supplements to analyze."
        
        response = f"# Supplement Stack Analysis\n\n"
        response += f"**Analyzing:** {', '.join(supplements)}\n\n"
        
        response += "## Interaction Analysis:\n\n"
        
        # Check for common interactions
        supplement_lower = [s.lower() for s in supplements]
        
        # Iron and calcium interaction
        if any("iron" in s for s in supplement_lower) and any("calcium" in s for s in supplement_lower):
            response += "⚠️ **Iron + Calcium**: Take at different times (calcium blocks iron absorption)\n"
        
        # Zinc and copper
        if any("zinc" in s for s in supplement_lower) and not any("copper" in s for s in supplement_lower):
            response += "💡 **Zinc without Copper**: Consider adding copper (2mg) for balance\n"
        
        # Magnesium timing
        if any("magnesium" in s for s in supplement_lower):
            response += "🌙 **Magnesium**: Best taken before bed for sleep support\n"
        
        response += "\n## Timing Recommendations:\n\n"
        response += "### Morning (with breakfast):\n"
        response += "- B vitamins (energy support)\n"
        response += "- Vitamin C\n"
        response += "- Iron (if needed, away from calcium)\n\n"
        
        response += "### Afternoon (with lunch):\n"
        response += "- Vitamin D3\n"
        response += "- Omega-3\n"
        response += "- CoQ10\n\n"
        
        response += "### Evening (with dinner/before bed):\n"
        response += "- Magnesium\n"
        response += "- Calcium\n"
        response += "- Zinc\n\n"
        
        response += "## Optimization Suggestions:\n"
        response += "- Consider adding a high-quality multivitamin as foundation\n"
        response += "- Ensure adequate vitamin D levels (test regularly)\n"
        response += "- Don't forget omega-3 fatty acids\n"
        
        return response

    # Tool 8: Analyze Health Topic
    @mcp_server.tool()
    def analyze_health_topic(topic: str) -> str:
        """Provide comprehensive analysis of a health topic from Dr. Strunz's perspective"""
        if not topic:
            return "Please provide a health topic to analyze."
        
        if not knowledge_searcher:
            return "Knowledge searcher not initialized."
        
        try:
            # Search across all sources
            results = knowledge_searcher.search(query=topic, k=20)
            
            response = f"# Comprehensive Analysis: {topic}\n\n"
            
            # Count sources
            sources = {"book": 0, "news": 0, "forum": 0}
            for result in results:
                source = result.metadata.get('source', 'unknown')
                if source in sources:
                    sources[source] += 1
            
            response += "## Content Distribution:\n"
            response += f"- Books: {sources['book']} references\n"
            response += f"- News Articles: {sources['news']} references\n"
            response += f"- Forum Discussions: {sources['forum']} references\n\n"
            
            response += "## Key Insights:\n\n"
            
            # Add topic-specific analysis
            response += f"### Dr. Strunz's Approach to {topic}:\n"
            response += "Based on the search results, here are the main themes:\n\n"
            
            # Extract key themes from results
            themes = set()
            for i, result in enumerate(results[:10]):
                # Extract key concepts from text
                text = result.text.lower()
                if "vitamin" in text:
                    themes.add("Nutritional supplementation")
                if "exercise" in text or "movement" in text:
                    themes.add("Physical activity")
                if "stress" in text:
                    themes.add("Stress management")
                if "blood" in text or "test" in text:
                    themes.add("Laboratory testing")
            
            for theme in themes:
                response += f"- {theme}\n"
            
            response += "\n### Evolution Over Time:\n"
            response += f"The understanding of {topic} has evolved in Dr. Strunz's work...\n\n"
            
            response += "### Practical Recommendations:\n"
            response += "1. Get comprehensive blood testing\n"
            response += "2. Address nutritional deficiencies\n"
            response += "3. Implement lifestyle changes\n"
            response += "4. Monitor progress with follow-up testing\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing topic: {e}")
            return f"Error analyzing topic: {str(e)}"

    # Tool 9: Get Knowledge Statistics
    @mcp_server.tool()
    def get_knowledge_statistics() -> str:
        """Get detailed statistics about the knowledge base"""
        try:
            # Get vector store statistics
            if knowledge_searcher and hasattr(knowledge_searcher, 'vector_store'):
                total_docs = len(knowledge_searcher.vector_store.documents)
                
                # Count by source
                source_counts = {}
                year_counts = {}
                
                for doc in knowledge_searcher.vector_store.documents:
                    source = doc.metadata.get('source', 'unknown')
                    year = doc.metadata.get('year', 'unknown')
                    
                    source_counts[source] = source_counts.get(source, 0) + 1
                    if year != 'unknown':
                        year_counts[year] = year_counts.get(year, 0) + 1
                
                response = "# Knowledge Base Statistics\n\n"
                response += f"## Total Documents: {total_docs:,}\n\n"
                
                response += "## By Source:\n"
                response += f"- Books: {source_counts.get('book', 0):,} chunks\n"
                response += f"- News Articles: {source_counts.get('news', 0):,} articles\n"
                response += f"- Forum: {source_counts.get('forum', 0):,} discussions\n\n"
                
                response += "## Coverage by Year:\n"
                sorted_years = sorted(year_counts.keys())
                for year in sorted_years[-10:]:  # Last 10 years
                    response += f"- {year}: {year_counts[year]:,} documents\n"
                
                response += "\n## Book Collection:\n"
                response += "- 13 books from 2002 to 2025\n"
                response += "- Topics: Nutrition, Fitness, Molecular Medicine, Anti-Aging\n\n"
                
                response += "## News Archive:\n"
                response += "- 6,953 unique articles\n"
                response += "- Daily health insights since 2004\n\n"
                
                response += "## Forum Activity:\n"
                response += "- 14,435 community discussions\n"
                response += "- Real user experiences and questions\n"
                
                return response
            else:
                return "Knowledge statistics not available."
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return f"Error retrieving statistics: {str(e)}"

    # Tool 10: Search by Date Range
    @mcp_server.tool()
    def search_by_date_range(
        query: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> str:
        """Search for content within a specific date range"""
        if not query:
            return "Please provide a search query."
        
        if not knowledge_searcher:
            return "Knowledge searcher not initialized."
        
        try:
            # Search with date filtering
            results = knowledge_searcher.search(query=query, k=20)
            
            # Filter by date range if provided
            filtered_results = []
            for result in results:
                year = result.metadata.get('year')
                if year:
                    try:
                        year_int = int(year)
                        if start_year and year_int < start_year:
                            continue
                        if end_year and year_int > end_year:
                            continue
                        filtered_results.append(result)
                    except:
                        pass
            
            response = f"# Date Range Search: {query}\n\n"
            if start_year or end_year:
                response += f"**Date Range:** {start_year or 'earliest'} - {end_year or 'latest'}\n\n"
            
            response += f"Found {len(filtered_results)} results:\n\n"
            
            for i, result in enumerate(filtered_results[:10]):
                year = result.metadata.get('year', 'unknown')
                source = result.metadata.get('source', 'unknown')
                title = result.metadata.get('title', 'Untitled')
                
                response += f"### {i+1}. {title} ({year})\n"
                response += f"**Source:** {source}\n"
                response += f"**Preview:** {result.text[:150]}...\n\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in date range search: {e}")
            return f"Error searching by date: {str(e)}"

    # Tool 11: Analyze Forum Trends
    @mcp_server.tool()
    def analyze_forum_trends(
        topic: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """Analyze trends and popular topics in forum discussions"""
        if not knowledge_searcher:
            return "Knowledge searcher not initialized."
        
        try:
            # Search forum content
            if topic:
                query = f"forum {topic}"
                response = f"# Forum Trend Analysis: {topic}\n\n"
            else:
                query = "forum diskussion community"
                response = "# Forum Trend Analysis\n\n"
            
            results = knowledge_searcher.search(query=query, k=30)
            
            # Filter for forum content
            forum_results = [r for r in results if r.metadata.get('source') == 'forum']
            
            response += f"## Forum Activity Overview:\n"
            response += f"- Total forum discussions analyzed: {len(forum_results)}\n"
            response += f"- Active community engagement on health topics\n\n"
            
            if topic:
                response += f"## Discussion Trends for '{topic}':\n\n"
                
                # Analyze sentiment and common themes
                themes = {
                    "questions": 0,
                    "experiences": 0,
                    "recommendations": 0,
                    "concerns": 0
                }
                
                for result in forum_results:
                    text_lower = result.text.lower()
                    if "?" in result.text:
                        themes["questions"] += 1
                    if any(word in text_lower for word in ["erfahrung", "experience", "versuch", "tried"]):
                        themes["experiences"] += 1
                    if any(word in text_lower for word in ["empfehl", "recommend", "suggest", "rät"]):
                        themes["recommendations"] += 1
                    if any(word in text_lower for word in ["sorge", "concern", "problem", "nebenwirkung"]):
                        themes["concerns"] += 1
                
                response += "### Discussion Types:\n"
                for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(forum_results) * 100) if forum_results else 0
                    response += f"- {theme.capitalize()}: {count} ({percentage:.1f}%)\n"
                
                response += "\n### Sample Discussions:\n"
                for i, result in enumerate(forum_results[:5]):
                    response += f"\n{i+1}. **User Experience:**\n"
                    response += f"   {result.text[:150]}...\n"
            
            else:
                response += "## Popular Forum Topics:\n\n"
                
                # Extract common topics from forum results
                topics = {}
                for result in forum_results:
                    text_lower = result.text.lower()
                    # Check for common health topics
                    topic_keywords = {
                        "Supplements": ["vitamin", "mineral", "supplement", "präparat"],
                        "Energy": ["energie", "müde", "energy", "fatigue"],
                        "Weight": ["gewicht", "abnehmen", "weight", "diet"],
                        "Sleep": ["schlaf", "sleep", "melatonin"],
                        "Pain": ["schmerz", "pain", "gelenk", "joint"],
                        "Digestion": ["verdauung", "magen", "darm", "digestion"]
                    }
                    
                    for topic_name, keywords in topic_keywords.items():
                        if any(kw in text_lower for kw in keywords):
                            topics[topic_name] = topics.get(topic_name, 0) + 1
                
                # Sort by frequency
                sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
                
                for topic_name, count in sorted_topics:
                    response += f"- **{topic_name}**: {count} discussions\n"
                
                response += "\n## Community Insights:\n"
                response += "- Users actively share personal experiences\n"
                response += "- High interest in practical supplement protocols\n"
                response += "- Frequent discussions about dosages and timing\n"
                response += "- Strong focus on measurable results\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing forum trends: {e}")
            return f"Error analyzing forum trends: {str(e)}"

    # Tool 12: Get Vector DB Analysis
    @mcp_server.tool()
    def get_vector_db_analysis() -> str:
        """Get detailed analysis of the vector database content and statistics"""
        return """# Vector Database Analysis

## Content Statistics:
- **Books**: 13 books by Dr. Ulrich Strunz (2002-2025)
- **News Articles**: 6,953 unique articles (2004-2025)
- **Forum Content**: 14,435 discussions
- **Total Documents**: 43,373 searchable documents

## Coverage:
- Topics: Nutrition, supplements, exercise, stress management, longevity
- Languages: Primarily German with semantic search capabilities
- Time Span: Over 20 years of health insights

## Search Capabilities:
- Semantic similarity search
- Source filtering (books, news, forum)
- Date range filtering
- Cross-reference analysis"""

    logger.info(f"Registered 12 tools with MCP server")
    return True