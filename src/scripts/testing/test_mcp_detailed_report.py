#!/usr/bin/env python3
"""
Detailed MCP Test Suite with Full Response Capture
Generates comprehensive report with complete tool outputs
"""
import asyncio
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import httpx

@dataclass
class TestCase:
    """Test case for MCP tool"""
    id: str
    tool_name: str
    description: str
    params: Dict[str, Any]
    expected_fields: List[str] = field(default_factory=list)
    category: str = "general"
    user_role: Optional[str] = None
    user_journey: Optional[str] = None

@dataclass 
class TestResult:
    """Test execution result"""
    test_id: str
    tool_name: str
    params: Dict[str, Any]
    result: Any
    duration_ms: float
    success: bool
    error: Optional[str] = None
    validation_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)

class DetailedMCPTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"detailed_test_{int(time.time())}"
        self.results: List[TestResult] = []
        
    async def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool using JSON-RPC protocol"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": f"{self.session_id}_{len(self.results)+1}"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/mcp",
                    json=request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": {
                            "code": response.status_code,
                            "message": response.text
                        }
                    }
            except Exception as e:
                return {
                    "error": {
                        "code": -1,
                        "message": str(e)
                    }
                }
    
    def generate_comprehensive_test_cases(self) -> List[TestCase]:
        """Generate comprehensive test cases covering all user roles and tools"""
        test_cases = []
        
        # 1. Information Tools (Fully test all 3)
        test_cases.extend([
            TestCase(
                id="info_biography",
                tool_name="get_dr_strunz_biography",
                description="Get complete Dr. Strunz biography",
                params={},
                expected_fields=["full_name", "title", "medical_education", "career_highlights"],
                category="information"
            ),
            TestCase(
                id="info_server_purpose", 
                tool_name="get_mcp_server_purpose",
                description="Get detailed MCP server purpose and capabilities",
                params={},
                expected_fields=["title", "primary_purpose", "key_capabilities", "mcp_tools_overview"],
                category="information"
            ),
            TestCase(
                id="info_vector_db",
                tool_name="get_vector_db_analysis", 
                description="Get comprehensive vector database statistics",
                params={},
                expected_fields=["database_overview", "content_distribution", "search_performance"],
                category="information"
            )
        ])
        
        # Add tests for the new diagnostic values tool
        test_cases.extend([
            TestCase(
                id="diagnostics_male_30_athlete",
                tool_name="get_optimal_diagnostic_values",
                description="Get optimal values for 30yo male athlete",
                params={
                    "age": 30,
                    "gender": "male",
                    "weight": 80,
                    "height": 180,
                    "athlete": True
                },
                expected_fields=["metadata", "vitamins", "minerals", "hormones"],
                category="diagnostics"
            ),
            TestCase(
                id="diagnostics_female_45_diabetes",
                tool_name="get_optimal_diagnostic_values",
                description="Get optimal values for 45yo female with diabetes",
                params={
                    "age": 45,
                    "gender": "female",
                    "conditions": ["diabetes"]
                },
                expected_fields=["metadata", "metabolic_markers", "special_considerations"],
                category="diagnostics"
            ),
            TestCase(
                id="diagnostics_male_60_cardiovascular",
                tool_name="get_optimal_diagnostic_values",
                description="Get cardiovascular markers for 60yo male",
                params={
                    "age": 60,
                    "gender": "male",
                    "category": "lipids"
                },
                expected_fields=["category", "values", "metadata"],
                category="diagnostics"
            ),
            TestCase(
                id="diagnostics_hormones_category",
                tool_name="get_optimal_diagnostic_values",
                description="Get hormone panel for health optimization",
                params={
                    "age": 35,
                    "gender": "male",
                    "category": "hormones"
                },
                expected_fields=["category", "values", "testing_recommendations"],
                category="diagnostics"
            )
        ])
        
        # 2. Search Functionality (Various queries and filters)
        test_cases.extend([
            TestCase(
                id="search_vitamin_d_books",
                tool_name="knowledge_search",
                description="Search Vitamin D in books",
                params={
                    "query": "Vitamin D Dosierung Mangel",
                    "filters": {"sources": ["books"]},
                    "semantic_boost": 1.2
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="health_optimizer"
            ),
            TestCase(
                id="search_magnesium_news",
                tool_name="knowledge_search", 
                description="Search magnesium in news/forum",
                params={
                    "query": "Magnesium Mangel Symptome Muskelkrampf",
                    "filters": {"sources": ["news", "forum"]}
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="patient"
            ),
            TestCase(
                id="search_amino_acids_athletes",
                tool_name="knowledge_search",
                description="Search amino acids for athletic performance", 
                params={
                    "query": "Aminosäuren Sport Leistung BCAA",
                    "user_profile": {"role": "athlete"},
                    "filters": {"sources": ["books", "news"]}
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="athlete"
            ),
            TestCase(
                id="search_corona_prevention",
                tool_name="knowledge_search",
                description="Search Corona/COVID prevention protocols",
                params={
                    "query": "Corona COVID-19 Prävention Immunsystem",
                    "filters": {"sources": ["news"], "date_range": {"start": "2020-01-01"}}
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="longevity_enthusiast"
            ),
            # Additional search tests
            TestCase(
                id="search_omega3_forum",
                tool_name="knowledge_search",
                description="Search Omega-3 discussions in forum",
                params={
                    "query": "Omega-3 EPA DHA Verhältnis Erfahrungen",
                    "filters": {"sources": ["forum"]},
                    "semantic_boost": 1.5
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="community_researcher"
            ),
            TestCase(
                id="search_stress_management",
                tool_name="knowledge_search",
                description="Search stress management techniques",
                params={
                    "query": "Stress Cortisol Magnesium Meditation",
                    "filters": {"sources": ["books", "news"]},
                    "user_profile": {"role": "health_optimizer"}
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="health_optimizer"
            ),
            TestCase(
                id="search_longevity_protocols",
                tool_name="knowledge_search",
                description="Search longevity and anti-aging protocols",
                params={
                    "query": "Longevity NAD+ Resveratrol Epigenetik",
                    "filters": {"sources": ["books"], "date_range": {"start": "2020-01-01"}}
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="longevity_enthusiast"
            ),
            TestCase(
                id="search_sleep_optimization",
                tool_name="knowledge_search",
                description="Search sleep optimization strategies",
                params={
                    "query": "Schlaf Melatonin Magnesium Regeneration",
                    "filters": {"sources": ["news", "forum"]}
                },
                expected_fields=["query", "results"],
                category="search",
                user_role="beginner"
            )
        ])
        
        # 3. Analysis Tools
        test_cases.extend([
            TestCase(
                id="analyze_contradictions_vitamin_d",
                tool_name="find_contradictions",
                description="Find contradictions about Vitamin D recommendations",
                params={
                    "topic": "Vitamin D Dosierung",
                    "time_range": "recent"
                },
                expected_fields=["contradictions_found", "examples"],
                category="analysis"
            ),
            TestCase(
                id="trace_topic_evolution_fasting",
                tool_name="trace_topic_evolution",
                description="Trace evolution of intermittent fasting",
                params={
                    "concept": "Intermittent Fasting",
                    "start_date": "2010-01-01",
                    "end_date": "2025-01-01"
                },
                expected_fields=["topic", "timeline", "key_developments"],
                category="analysis"
            ),
            TestCase(
                id="compare_approaches_diabetes",
                tool_name="compare_approaches",
                description="Compare diabetes treatment approaches",
                params={
                    "topic": "Diabetes Typ 2 Behandlung",
                    "sources": ["books", "news", "forum"],
                    "perspective": "functional_medicine"
                },
                expected_fields=["topic", "comparison_matrix"],
                category="analysis"
            ),
            # Additional analysis tests
            TestCase(
                id="analyze_contradictions_cholesterol",
                tool_name="find_contradictions",
                description="Find contradictions about cholesterol",
                params={
                    "topic": "Cholesterin LDL HDL Statine",
                    "time_range": "all"
                },
                expected_fields=["contradictions_found", "examples"],
                category="analysis"
            ),
            TestCase(
                id="trace_topic_evolution_ketogenic",
                tool_name="trace_topic_evolution",
                description="Trace evolution of ketogenic diet",
                params={
                    "concept": "Ketogene Ernährung",
                    "start_date": "2015-01-01",
                    "end_date": "2025-01-01"
                },
                expected_fields=["topic", "timeline", "key_developments"],
                category="analysis"
            ),
            TestCase(
                id="compare_approaches_depression",
                tool_name="compare_approaches",
                description="Compare depression treatment approaches",
                params={
                    "topic": "Depression natürliche Behandlung",
                    "sources": ["books", "news", "forum"],
                    "perspective": "nutritional_psychiatry"
                },
                expected_fields=["topic", "comparison_matrix"],
                category="analysis"
            )
        ])
        
        # 4. Health Protocol Generation
        test_cases.extend([
            TestCase(
                id="protocol_diabetes_male_45",
                tool_name="create_health_protocol",
                description="Create diabetes protocol for 45yo male",
                params={
                    "condition": "type 2 diabetes",
                    "user_profile": {
                        "age": 45,
                        "gender": "male", 
                        "symptoms": ["fatigue", "high_blood_sugar", "weight_gain"],
                        "medications": ["metformin"],
                        "lifestyle": {"exercise": "sedentary", "diet": "standard"}
                    },
                    "evidence_level": "high"
                },
                expected_fields=["condition", "recommendations", "supplements", "lifestyle_changes"],
                category="protocol",
                user_role="patient"
            ),
            TestCase(
                id="protocol_hypertension_female_55",
                tool_name="create_health_protocol",
                description="Create hypertension protocol for 55yo female",
                params={
                    "condition": "hypertension", 
                    "user_profile": {
                        "age": 55,
                        "gender": "female",
                        "symptoms": ["high_blood_pressure", "stress", "poor_sleep"],
                        "lifestyle": {"stress_level": "high", "exercise": "light"}
                    }
                },
                expected_fields=["condition", "recommendations", "supplements", "monitoring_metrics"],
                category="protocol",
                user_role="patient"
            ),
            TestCase(
                id="protocol_athletic_performance",
                tool_name="create_health_protocol",
                description="Create performance protocol for triathlete",
                params={
                    "condition": "athletic performance optimization",
                    "user_profile": {
                        "age": 30,
                        "gender": "male",
                        "sport": "triathlon",
                        "training_hours": 15,
                        "goals": ["endurance", "recovery", "injury_prevention"]
                    }
                },
                expected_fields=["condition", "recommendations", "supplements", "timeline"],
                category="protocol",
                user_role="athlete"
            ),
            # Additional protocol tests
            TestCase(
                id="protocol_autoimmune",
                tool_name="create_health_protocol",
                description="Create autoimmune disease protocol",
                params={
                    "condition": "autoimmune disorder",
                    "user_profile": {
                        "age": 38,
                        "gender": "female",
                        "symptoms": ["joint_pain", "fatigue", "inflammation"],
                        "conditions": ["hashimoto", "rheumatoid_arthritis"]
                    }
                },
                expected_fields=["condition", "recommendations", "supplements"],
                category="protocol"
            ),
            TestCase(
                id="protocol_cognitive_decline",
                tool_name="create_health_protocol",
                description="Create cognitive optimization protocol",
                params={
                    "condition": "cognitive decline prevention",
                    "user_profile": {
                        "age": 65,
                        "gender": "male",
                        "symptoms": ["memory_issues", "brain_fog"],
                        "family_history": ["alzheimer"]
                    }
                },
                expected_fields=["condition", "recommendations", "monitoring_metrics"],
                category="protocol"
            ),
            TestCase(
                id="protocol_metabolic_syndrome",
                tool_name="create_health_protocol",
                description="Create metabolic syndrome protocol",
                params={
                    "condition": "metabolic syndrome",
                    "user_profile": {
                        "age": 50,
                        "gender": "male",
                        "symptoms": ["obesity", "insulin_resistance", "fatty_liver"],
                        "lab_values": {"hba1c": 6.2, "triglycerides": 250}
                    }
                },
                expected_fields=["condition", "lifestyle_changes", "supplements"],
                category="protocol"
            )
        ])
        
        # 5. Supplement Analysis
        test_cases.extend([
            TestCase(
                id="supplement_stack_basic",
                tool_name="analyze_supplement_stack",
                description="Analyze basic supplement stack",
                params={
                    "supplements": ["Vitamin D3 5000 IU", "Magnesium 400mg", "Omega-3 2g", "Vitamin K2 200mcg"],
                    "health_goals": ["general_health", "heart_health", "bone_health"],
                    "user_profile": {"age": 40, "gender": "male"}
                },
                expected_fields=["supplements", "safety_analysis", "interactions", "optimization_suggestions"],
                category="supplements"
            ),
            TestCase(
                id="supplement_stack_complex",
                tool_name="analyze_supplement_stack",
                description="Analyze complex performance stack",
                params={
                    "supplements": [
                        "Creatine 5g", "Beta-Alanine 3g", "L-Citrulline 6g", 
                        "BCAA 10g", "Whey Protein 30g", "Multivitamin",
                        "CoQ10 200mg", "NAD+ 500mg", "Resveratrol 500mg"
                    ],
                    "health_goals": ["athletic_performance", "longevity", "recovery"],
                    "user_profile": {"age": 35, "sport": "crossfit"}
                },
                expected_fields=["supplements", "safety_analysis", "timing_recommendations"],
                category="supplements"
            ),
            # Additional supplement tests
            TestCase(
                id="supplement_stack_senior",
                tool_name="analyze_supplement_stack",
                description="Analyze senior health supplement stack",
                params={
                    "supplements": [
                        "Vitamin D3 4000 IU", "B12 1000mcg", "Folate 800mcg",
                        "CoQ10 200mg", "Curcumin 1000mg", "Probiotics"
                    ],
                    "health_goals": ["healthy_aging", "cognitive_health", "joint_health"],
                    "user_profile": {"age": 70, "gender": "female"}
                },
                expected_fields=["supplements", "safety_analysis", "interactions"],
                category="supplements"
            ),
            TestCase(
                id="supplement_stack_pregnancy",
                tool_name="analyze_supplement_stack",
                description="Analyze pregnancy supplement stack",
                params={
                    "supplements": [
                        "Prenatal Vitamin", "DHA 500mg", "Iron 30mg",
                        "Vitamin D3 2000 IU", "Probiotics"
                    ],
                    "health_goals": ["healthy_pregnancy", "fetal_development"],
                    "user_profile": {"age": 32, "gender": "female", "pregnant": True}
                },
                expected_fields=["supplements", "safety_analysis", "optimization_suggestions"],
                category="supplements"
            )
        ])
        
        # 6. Nutrition Analysis
        test_cases.extend([
            TestCase(
                id="nutrition_low_carb_day",
                tool_name="nutrition_calculator",
                description="Calculate low-carb daily nutrition",
                params={
                    "foods": [
                        {"name": "eggs", "quantity": "3 large"},
                        {"name": "salmon", "quantity": "200g"},
                        {"name": "avocado", "quantity": "1 medium"},
                        {"name": "spinach", "quantity": "200g"},
                        {"name": "olive oil", "quantity": "2 tbsp"}
                    ],
                    "activity_level": "moderate",
                    "health_goals": ["weight_loss", "blood_sugar_control"]
                },
                expected_fields=["foods", "nutritional_values", "recommendations"],
                category="nutrition"
            ),
            # Additional nutrition tests
            TestCase(
                id="nutrition_ketogenic_day",
                tool_name="nutrition_calculator",
                description="Calculate ketogenic daily nutrition",
                params={
                    "foods": [
                        {"name": "bacon", "quantity": "50g"},
                        {"name": "butter", "quantity": "30g"},
                        {"name": "steak", "quantity": "250g"},
                        {"name": "broccoli", "quantity": "150g"},
                        {"name": "macadamia nuts", "quantity": "30g"}
                    ],
                    "activity_level": "high",
                    "health_goals": ["ketosis", "fat_loss", "mental_clarity"]
                },
                expected_fields=["foods", "nutritional_values", "strunz_principles"],
                category="nutrition"
            ),
            TestCase(
                id="nutrition_vegetarian_athlete",
                tool_name="nutrition_calculator",
                description="Calculate vegetarian athlete nutrition",
                params={
                    "foods": [
                        {"name": "lentils", "quantity": "200g cooked"},
                        {"name": "quinoa", "quantity": "150g cooked"},
                        {"name": "tofu", "quantity": "200g"},
                        {"name": "mixed vegetables", "quantity": "300g"},
                        {"name": "nuts and seeds", "quantity": "50g"}
                    ],
                    "activity_level": "athlete",
                    "health_goals": ["muscle_building", "recovery", "performance"]
                },
                expected_fields=["foods", "deficiencies", "recommendations"],
                category="nutrition"
            )
        ])
        
        # 7. Community and Trending
        test_cases.extend([
            TestCase(
                id="community_insights_longevity",
                tool_name="get_community_insights",
                description="Get community insights on longevity",
                params={
                    "topic": "longevity protocols NAD+",
                    "user_role": "longevity_enthusiast",
                    "time_period": "recent"
                },
                expected_fields=["topic", "insights", "success_stories"],
                category="community"
            ),
            TestCase(
                id="trending_health_optimizer",
                tool_name="get_trending_insights",
                description="Get trending topics for health optimizers",
                params={
                    "user_role": "health_optimizer",
                    "timeframe": "month",
                    "categories": ["supplements", "biohacking", "performance"]
                },
                expected_fields=["trends", "engagement_metrics"],
                category="community"
            ),
            # Additional community tests
            TestCase(
                id="community_insights_diabetes",
                tool_name="get_community_insights",
                description="Get community insights on diabetes management",
                params={
                    "topic": "diabetes type 2 reversal success stories",
                    "user_role": "patient",
                    "time_period": "all"
                },
                expected_fields=["topic", "insights", "common_challenges"],
                category="community"
            ),
            TestCase(
                id="trending_athletes",
                tool_name="get_trending_insights",
                description="Get trending topics for athletes",
                params={
                    "user_role": "athlete",
                    "timeframe": "week",
                    "categories": ["performance", "recovery", "nutrition"]
                },
                expected_fields=["trends", "personalized_for"],
                category="community"
            ),
            TestCase(
                id="summarize_forum_posts",
                tool_name="summarize_posts",
                description="Summarize specific forum posts",
                params={
                    "post_ids": ["12345", "23456", "34567"],
                    "summary_style": "actionable"
                },
                expected_fields=["summary", "key_insights", "action_items"],
                category="community"
            )
        ])
        
        # 8. Newsletter Analysis
        test_cases.extend([
            TestCase(
                id="newsletter_evolution_analysis",
                tool_name="analyze_strunz_newsletter_evolution",
                description="Analyze newsletter evolution 2020-2025",
                params={
                    "start_year": "2020",
                    "end_year": "2025",
                    "focus_topics": ["COVID-19", "Immunsystem", "Vitamin D"]
                },
                expected_fields=["time_period", "topic_evolution", "key_themes"],
                category="newsletter"
            ),
            TestCase(
                id="topic_trends_vitamin_d",
                tool_name="track_health_topic_trends",
                description="Track Vitamin D topic trends",
                params={
                    "topic": "Vitamin D",
                    "analysis_type": "comprehensive",
                    "include_context": True
                },
                expected_fields=["topic", "trend_analysis", "context"],
                category="newsletter"
            ),
            # Additional newsletter tests
            TestCase(
                id="guest_authors_analysis",
                tool_name="get_guest_authors_analysis",
                description="Analyze guest authors in newsletters",
                params={
                    "timeframe": "2020-2025",
                    "specialty_focus": "molecular_medicine"
                },
                expected_fields=["analysis_approach", "guest_author_strategy", "editorial_philosophy"],
                category="newsletter"
            ),
            TestCase(
                id="topic_trends_magnesium",
                tool_name="track_health_topic_trends",
                description="Track magnesium topic trends",
                params={
                    "topic": "Magnesium",
                    "analysis_type": "detailed",
                    "include_context": True
                },
                expected_fields=["topic", "trend_analysis", "context"],
                category="newsletter"
            ),
            TestCase(
                id="newsletter_evolution_longevity",
                tool_name="analyze_strunz_newsletter_evolution",
                description="Analyze longevity focus evolution",
                params={
                    "start_year": "2015",
                    "end_year": "2025",
                    "focus_topics": ["Longevity", "Epigenetics", "NAD+"]
                },
                expected_fields=["time_period", "topic_evolution", "key_themes"],
                category="newsletter"
            )
        ])
        
        # 9. User Assessment and Profiling
        test_cases.extend([
            TestCase(
                id="assessment_questions_complete",
                tool_name="get_health_assessment_questions",
                description="Get all health assessment sections",
                params={},
                expected_fields=["all_sections", "questions", "total_questions"],
                category="assessment"
            ),
            TestCase(
                id="user_profile_beginner",
                tool_name="assess_user_health_profile",
                description="Assess beginner user profile",
                params={
                    "assessment_responses": {
                        "age": 35,
                        "gender": "female",
                        "current_health": "fair",
                        "symptoms": ["fatigue", "stress", "poor_sleep"],
                        "goals": ["weight_loss", "energy_increase", "better_sleep"],
                        "experience": "beginner",
                        "exercise": "never",
                        "diet": "standard"
                    }
                },
                expected_fields=["profile", "assigned_role", "journey_plan", "assessment_report"],
                category="assessment"
            ),
            TestCase(
                id="personalized_protocol_optimizer",
                tool_name="create_personalized_protocol",
                description="Create personalized protocol for health optimizer",
                params={
                    "user_profile": {
                        "role": "health_optimizer",
                        "age": 40,
                        "gender": "male",
                        "health_status": "good",
                        "primary_goal": "cognitive_performance",
                        "experience": "advanced",
                        "current_supplements": ["Vitamin D", "Omega-3", "Magnesium"]
                    },
                    "specific_focus": "brain_optimization"
                },
                expected_fields=["immediate_actions", "supplement_protocol", "monitoring_schedule"],
                category="assessment"
            ),
            # Additional assessment tests
            TestCase(
                id="assessment_questions_lifestyle",
                tool_name="get_health_assessment_questions",
                description="Get lifestyle assessment questions",
                params={"section": "lifestyle"},
                expected_fields=["section", "questions"],
                category="assessment"
            ),
            TestCase(
                id="user_profile_athlete_advanced",
                tool_name="assess_user_health_profile",
                description="Assess advanced athlete profile",
                params={
                    "assessment_responses": {
                        "age": 28,
                        "gender": "male",
                        "current_health": "excellent",
                        "sport": "triathlon",
                        "training_hours": 20,
                        "goals": ["performance", "recovery", "injury_prevention"],
                        "experience": "advanced"
                    }
                },
                expected_fields=["profile", "assigned_role", "journey_plan"],
                category="assessment"
            ),
            TestCase(
                id="personalized_protocol_longevity",
                tool_name="create_personalized_protocol",
                description="Create longevity optimization protocol",
                params={
                    "user_profile": {
                        "role": "longevity_enthusiast",
                        "age": 55,
                        "gender": "female",
                        "health_status": "good",
                        "primary_goal": "healthy_aging",
                        "experience": "intermediate"
                    },
                    "specific_focus": "mitochondrial_health"
                },
                expected_fields=["immediate_actions", "supplement_protocol", "lifestyle_interventions"],
                category="assessment"
            )
        ])
        
        # 10. Advanced Tools
        test_cases.extend([
            TestCase(
                id="user_journey_guide_athlete",
                tool_name="get_user_journey_guide",
                description="Get journey guide for athlete role",
                params={"user_role": "athlete"},
                expected_fields=["role", "journey_phases", "milestones"],
                category="advanced"
            ),
            TestCase(
                id="book_recommendations_longevity",
                tool_name="get_book_recommendations",
                description="Get book recommendations for longevity",
                params={
                    "user_profile": {"interests": ["longevity", "anti-aging"], "experience": "intermediate"},
                    "specific_interest": "mitochondrial_health"
                },
                expected_fields=["recommendations", "reading_order"],
                category="advanced"
            ),
            # Additional advanced tests
            TestCase(
                id="user_journey_guide_beginner",
                tool_name="get_user_journey_guide",
                description="Get journey guide for beginner",
                params={"user_role": "beginner"},
                expected_fields=["role", "journey_phases", "milestones"],
                category="advanced"
            ),
            TestCase(
                id="book_recommendations_stress",
                tool_name="get_book_recommendations",
                description="Get book recommendations for stress management",
                params={
                    "user_profile": {"interests": ["stress_management", "cortisol"], "experience": "beginner"},
                    "specific_interest": "burnout_prevention"
                },
                expected_fields=["recommendations", "primary_recommendations"],
                category="advanced"
            ),
            TestCase(
                id="knowledge_statistics",
                tool_name="get_knowledge_statistics",
                description="Get comprehensive knowledge base statistics",
                params={},
                expected_fields=["total_documents", "books", "news_articles"],
                category="advanced"
            ),
            TestCase(
                id="user_journey_guide_patient",
                tool_name="get_user_journey_guide",
                description="Get journey guide for patient role",
                params={"user_role": "patient"},
                expected_fields=["role", "journey_phases", "recommended_path"],
                category="advanced"
            ),
            TestCase(
                id="book_recommendations_nutrition",
                tool_name="get_book_recommendations",
                description="Get nutrition-focused book recommendations",
                params={
                    "user_profile": {"interests": ["nutrition", "low_carb"], "experience": "intermediate"},
                    "specific_interest": "metabolic_health"
                },
                expected_fields=["recommendations", "specific_chapters"],
                category="advanced"
            )
        ])
        
        return test_cases
    
    async def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            result = await self.call_mcp_tool(test_case.tool_name, test_case.params)
            duration_ms = (time.time() - start_time) * 1000
            
            # Check for errors
            if "error" in result:
                return TestResult(
                    test_id=test_case.id,
                    tool_name=test_case.tool_name,
                    params=test_case.params,
                    result=result,
                    duration_ms=duration_ms,
                    success=False,
                    error=result["error"].get("message", "Unknown error"),
                    validation_passed=False
                )
            
            # Validate expected fields
            validation_errors = []
            validation_passed = True
            
            if test_case.expected_fields and "result" in result:
                for field in test_case.expected_fields:
                    if field not in result["result"]:
                        validation_errors.append(f"Missing field: {field}")
                        validation_passed = False
            
            return TestResult(
                test_id=test_case.id,
                tool_name=test_case.tool_name,
                params=test_case.params,
                result=result,
                duration_ms=duration_ms,
                success=True,
                validation_passed=validation_passed,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_id=test_case.id,
                tool_name=test_case.tool_name,
                params=test_case.params,
                result={"error": str(e)},
                duration_ms=duration_ms,
                success=False,
                error=str(e),
                validation_passed=False
            )
    
    async def run_detailed_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🧪 Detailed MCP Test Suite")
        print(f"📍 Target: {self.base_url}")
        print("=" * 80)
        
        # Check server health
        print("🔍 Checking MCP server...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    server_info = response.json()
                    print(f"✅ Server is running: {server_info.get('server', 'Unknown')}")
                    print(f"   Version: {server_info.get('version', 'Unknown')}")
                    print(f"   Tools: {server_info.get('mcp_tools', 'Unknown')}")
                else:
                    print(f"❌ Server health check failed: {response.status_code}")
                    return {"error": "Server not healthy"}
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return {"error": f"Connection failed: {e}"}
        
        # Generate test cases
        test_cases = self.generate_comprehensive_test_cases()
        print(f"\n🚀 Running {len(test_cases)} comprehensive test cases")
        print("=" * 80)
        
        # Run tests by category
        categories = {}
        for test_case in test_cases:
            if test_case.category not in categories:
                categories[test_case.category] = []
            categories[test_case.category].append(test_case)
        
        all_results = []
        
        for category, tests in categories.items():
            print(f"\n📂 {category.upper()} ({len(tests)} tests)")
            print("-" * 60)
            
            for i, test_case in enumerate(tests, 1):
                result = await self.run_test_case(test_case)
                all_results.append(result)
                
                status = "✅" if result.success else "❌"
                validation = "✅" if result.validation_passed else "⚠️"
                
                print(f"  [{i}/{len(tests)}] {test_case.description}... {status} {validation} ({result.duration_ms:.1f}ms)")
                
                if not result.success and result.error:
                    print(f"    Error: {result.error}")
        
        self.results = all_results
        
        # Generate summary
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r.success)
        validated_tests = sum(1 for r in all_results if r.validation_passed)
        total_duration = sum(r.duration_ms for r in all_results)
        
        print(f"\n✅ Testing completed in {total_duration/1000:.2f}s")
        print(f"📊 Summary: {successful_tests}/{total_tests} passed, {validated_tests} fully validated")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "validated_tests": validated_tests,
            "total_duration_ms": total_duration,
            "average_response_ms": total_duration / total_tests if total_tests > 0 else 0,
            "results": all_results
        }
    
    def generate_detailed_report(self, summary: Dict[str, Any]) -> str:
        """Generate detailed test report with full responses"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        report = f"""# Detailed MCP Server Test Report - {timestamp}
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Server**: {self.base_url}
**Total Tests**: {summary['total_tests']}

## Executive Summary
- **Tests Executed**: {summary['total_tests']}
- **Successful**: {summary['successful_tests']} ({summary['successful_tests']/summary['total_tests']*100:.1f}%)
- **Fully Validated**: {summary['validated_tests']} ({summary['validated_tests']/summary['total_tests']*100:.1f}%)
- **Failed**: {summary['total_tests'] - summary['successful_tests']}
- **Total Duration**: {summary['total_duration_ms']/1000:.2f}s
- **Average Response**: {summary['average_response_ms']:.1f}ms

## Test Results by Category

"""
        
        # Group results by category
        categories = {}
        for result in self.results:
            # Find the test case to get category
            test_case = None
            for tc in self.generate_comprehensive_test_cases():
                if tc.id == result.test_id:
                    test_case = tc
                    break
            
            category = test_case.category if test_case else "unknown"
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Category summary
        for category, results in categories.items():
            successful = sum(1 for r in results if r.success)
            validated = sum(1 for r in results if r.validation_passed)
            avg_time = sum(r.duration_ms for r in results) / len(results)
            
            report += f"""### {category.upper()} Category
- **Total Tests**: {len(results)}
- **Success Rate**: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)
- **Validation Rate**: {validated}/{len(results)} ({validated/len(results)*100:.1f}%)
- **Average Response Time**: {avg_time:.1f}ms

"""
        
        # Add detailed results with FULL responses
        report += "\n## Detailed Test Results with Full Responses\n\n"
        
        for result in self.results:
            # Find test case for description
            test_case = None
            for tc in self.generate_comprehensive_test_cases():
                if tc.id == result.test_id:
                    test_case = tc
                    break
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            validation = "✅ VALID" if result.validation_passed else "⚠️ INVALID"
            
            report += f"""### Test: {result.test_id}
**Description**: {test_case.description if test_case else 'Unknown'}
**Tool**: `{result.tool_name}`
**Status**: {status} | Validation: {validation}
**Duration**: {result.duration_ms:.1f}ms
**Category**: {test_case.category if test_case else 'unknown'}
"""
            
            if test_case and test_case.user_role:
                report += f"**User Role**: {test_case.user_role}\n"
            
            report += f"""
**Request Parameters**:
```json
{json.dumps(result.params, indent=2, ensure_ascii=False)}
```

"""
            
            if result.success and "result" in result.result:
                # Show FULL result without truncation
                report += f"""**Full Response**:
```json
{json.dumps(result.result["result"], indent=2, ensure_ascii=False)}
```

"""
            elif result.error:
                report += f"""**Error**: {result.error}

**Full Error Response**:
```json
{json.dumps(result.result, indent=2, ensure_ascii=False)}
```

"""
            
            if result.validation_errors:
                report += f"**Validation Issues**: {', '.join(result.validation_errors)}\n\n"
            
            report += "---\n\n"
        
        # Add tool performance summary
        tool_stats = {}
        for result in self.results:
            if result.tool_name not in tool_stats:
                tool_stats[result.tool_name] = {
                    "calls": 0,
                    "success": 0,
                    "total_time": 0,
                    "errors": []
                }
            
            tool_stats[result.tool_name]["calls"] += 1
            if result.success:
                tool_stats[result.tool_name]["success"] += 1
            else:
                tool_stats[result.tool_name]["errors"].append(result.error)
            tool_stats[result.tool_name]["total_time"] += result.duration_ms
        
        report += "\n## Tool Performance Summary\n\n"
        report += "| Tool | Calls | Success | Avg Time (ms) | Success Rate |\n"
        report += "|------|-------|---------|---------------|-------------|\n"
        
        for tool, stats in sorted(tool_stats.items()):
            avg_time = stats["total_time"] / stats["calls"]
            success_rate = stats["success"] / stats["calls"] * 100
            report += f"| {tool} | {stats['calls']} | {stats['success']} | {avg_time:.1f} | {success_rate:.1f}% |\n"
        
        # Add recommendations
        report += "\n## Analysis and Recommendations\n\n"
        
        failed_tests = [r for r in self.results if not r.success]
        validation_issues = [r for r in self.results if r.success and not r.validation_passed]
        
        if failed_tests:
            report += f"### ❌ Failed Tests ({len(failed_tests)})\n"
            for test in failed_tests:
                report += f"- **{test.test_id}**: {test.error}\n"
            report += "\n"
        
        if validation_issues:
            report += f"### ⚠️ Validation Issues ({len(validation_issues)})\n"
            for test in validation_issues:
                report += f"- **{test.test_id}**: {', '.join(test.validation_errors)}\n"
            report += "\n"
        
        if not failed_tests and not validation_issues:
            report += "### ✅ All Tests Passed Successfully\n"
            report += "- All tools are functioning correctly\n"
            report += "- All expected fields are present in responses\n"
            report += "- Server is production-ready\n"
        
        # Add test coverage analysis
        report += "\n## Test Coverage Analysis\n\n"
        report += f"- **Total MCP Tools Tested**: {len(tool_stats)}\n"
        report += f"- **User Roles Covered**: {len(set(tc.user_role for tc in self.generate_comprehensive_test_cases() if tc.user_role))}\n"
        report += f"- **Test Categories**: {len(categories)}\n"
        report += f"- **Average Tests per Tool**: {summary['total_tests'] / len(tool_stats):.1f}\n"
        
        return report

async def main():
    """Main test execution"""
    # Run tests on local server
    tester = DetailedMCPTester("http://localhost:8000")
    
    print("\n🔧 Starting Detailed MCP Test Suite")
    print("📝 This test will capture FULL responses without truncation")
    print("=" * 80)
    
    summary = await tester.run_detailed_tests()
    
    if "error" in summary:
        print(f"❌ Test execution failed: {summary['error']}")
        return
    
    # Generate detailed report
    report = tester.generate_detailed_report(summary)
    
    # Save report with datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = Path(f"docs/test-reports/DETAILED_MCP_TEST_REPORT_{timestamp}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    print(f"📊 Final Summary: {summary['successful_tests']}/{summary['total_tests']} passed, {summary['validated_tests']} fully validated")
    print(f"⏱️ Total test duration: {summary['total_duration_ms']/1000:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())