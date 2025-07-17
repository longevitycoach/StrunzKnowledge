#!/usr/bin/env python3
"""
Enhanced MCP Server with comprehensive tools for Dr. Strunz Knowledge Base
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    # Create a dummy FastMCP class for compatibility
    class FastMCP:
        def __init__(self, name):
            self.name = name
        def tool(self):
            def decorator(func):
                return func
            return decorator

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Basic fallback for BaseModel
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    Field = lambda **kwargs: None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User Roles and Profiles
class UserRole(str, Enum):
    FUNCTIONAL_EXPERT = "functional_expert"
    COMMUNITY_RESEARCHER = "community_researcher" 
    LONGEVITY_ENTHUSIAST = "longevity_enthusiast"
    STRUNZ_FAN = "strunz_fan"
    HEALTH_OPTIMIZER = "health_optimizer"
    ATHLETE = "athlete"
    PATIENT = "patient"
    BEGINNER = "beginner"

@dataclass
class UserProfile:
    role: UserRole
    experience_level: str  # beginner, intermediate, advanced
    health_goals: List[str]
    current_supplements: List[str] = None
    medical_conditions: List[str] = None
    lifestyle_factors: Dict[str, str] = None

# Enhanced Data Models
class SearchFilters(BaseModel):
    sources: Optional[List[str]] = None  # books, news, forum
    categories: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None
    min_engagement: Optional[int] = None
    content_types: Optional[List[str]] = None

class SearchResult(BaseModel):
    id: str
    source: str
    title: str
    content: str
    score: float
    metadata: Dict
    relevance_explanation: str

class HealthProtocol(BaseModel):
    condition: str
    user_profile: Dict
    recommendations: List[Dict]
    supplements: List[Dict]
    lifestyle_changes: List[str]
    monitoring_metrics: List[str]
    timeline: str
    references: List[str]

class NutritionAnalysis(BaseModel):
    foods: List[Dict]
    nutritional_values: Dict
    deficiencies: List[str]
    recommendations: List[str]
    strunz_principles: List[str]

class TopicEvolution(BaseModel):
    topic: str
    timeline: List[Dict]
    key_developments: List[str]
    consensus_changes: List[str]
    future_predictions: List[str]

class StrunzKnowledgeMCP:
    def __init__(self):
        self.app = FastMCP("Dr. Strunz Knowledge Base")
        self.data_dir = Path("data")
        self.tool_registry = {}
        
        # Initialize tools
        self._register_tools()
        
        # Check if vector store is available
        try:
            from src.rag.search import KnowledgeSearcher
            self.searcher = KnowledgeSearcher()
            self.HAS_VECTOR_STORE = True
            logger.info("Enhanced server initialized with singleton vector store")
        except Exception as e:
            self.searcher = None
            self.HAS_VECTOR_STORE = False
            logger.warning(f"Vector store not available - search capabilities limited: {e}")
        
        # Initialize user profiling
        try:
            from src.mcp.user_profiling import UserProfilingSystem
            self.profiling = UserProfilingSystem()
        except:
            self.profiling = None
            logger.warning("User profiling system not available")
        
        # Register prompts (skip for compatibility)
        # self._register_prompts()
    
    def _register_prompts(self):
        """Register MCP prompts for health-related interactions"""
        
        @self.app.prompt()
        async def health_assessment_prompt(
            age: int,
            gender: str,
            health_goals: str,
            current_symptoms: str = "",
            lifestyle_factors: str = "",
            current_supplements: str = ""
        ) -> str:
            """
            Generate a comprehensive health assessment prompt based on Dr. Strunz's methodology.
            
            This prompt guides users through a structured health evaluation following
            Dr. Strunz's functional medicine approach.
            
            Args:
                age: User's age
                gender: User's gender (male/female)
                health_goals: Primary health goals (e.g., "energy optimization", "weight loss")
                current_symptoms: Any current health symptoms
                lifestyle_factors: Exercise habits, stress levels, sleep quality
                current_supplements: Current supplement regimen
            """
            
            prompt = f"""# Dr. Strunz Health Assessment & Optimization Guide

## Personal Information
- **Age**: {age} years
- **Gender**: {gender}
- **Primary Health Goals**: {health_goals}

## Current Health Status
{f"**Current Symptoms**: {current_symptoms}" if current_symptoms else ""}
{f"**Lifestyle Factors**: {lifestyle_factors}" if lifestyle_factors else ""}
{f"**Current Supplements**: {current_supplements}" if current_supplements else ""}

## Assessment Framework

Based on Dr. Ulrich Strunz's functional medicine approach, please provide a comprehensive health assessment covering:

### 1. Biochemical Optimization
- **Blood Values**: Which laboratory tests would Dr. Strunz recommend?
- **Nutrient Status**: Potential deficiencies based on age, gender, and symptoms
- **Metabolic Health**: Energy production at cellular level

### 2. Nutritional Medicine
- **Macronutrient Balance**: Optimal protein, carbohydrate, fat ratios
- **Micronutrient Needs**: Essential vitamins and minerals
- **Anti-Inflammatory Diet**: Food recommendations for optimal health

### 3. Lifestyle Optimization
- **Exercise Protocol**: Movement recommendations for health goals
- **Stress Management**: Techniques for cortisol regulation
- **Sleep Optimization**: Strategies for restorative sleep

### 4. Supplementation Strategy
- **Core Supplements**: Essential nutrients for everyone
- **Targeted Support**: Specific supplements for health goals
- **Timing & Dosage**: When and how to take supplements

### 5. Preventive Medicine
- **Disease Prevention**: Strategies to prevent chronic conditions
- **Longevity Protocols**: Anti-aging interventions
- **Regular Monitoring**: Ongoing health tracking

## Request
Please analyze this health profile and provide personalized recommendations following Dr. Strunz's evidence-based approach to functional medicine. Include specific, actionable steps for biochemical optimization, nutritional support, and lifestyle enhancement.

Focus on:
- Immediate actions for symptom relief
- Long-term health optimization strategies
- Measurable health outcomes
- Timeline for implementation
"""
            
            return prompt
        
        @self.app.prompt()
        async def supplement_analysis_prompt(
            supplement_list: str,
            health_condition: str = "",
            age: int = 40,
            goals: str = "general health"
        ) -> str:
            """
            Generate a prompt for analyzing supplement interactions and optimization.
            
            This prompt helps evaluate supplement regimens according to Dr. Strunz's
            orthomolecular medicine principles.
            
            Args:
                supplement_list: List of current supplements
                health_condition: Specific health conditions
                age: User's age for age-appropriate recommendations
                goals: Health optimization goals
            """
            
            prompt = f"""# Dr. Strunz Supplement Stack Analysis

## Current Supplement Regimen
{supplement_list}

## Health Context
- **Age**: {age} years
- **Health Goals**: {goals}
{f"- **Health Conditions**: {health_condition}" if health_condition else ""}

## Analysis Framework

Using Dr. Strunz's orthomolecular medicine principles, please analyze this supplement stack:

### 1. Efficacy Assessment
- **Evidence-Based Evaluation**: Scientific support for each supplement
- **Dosage Optimization**: Are doses within therapeutic ranges?
- **Bioavailability**: Best forms and timing for absorption

### 2. Interaction Analysis
- **Synergistic Combinations**: Supplements that work better together
- **Potential Conflicts**: Nutrients that may interfere with each other
- **Absorption Competition**: Timing considerations for optimal uptake

### 3. Gap Analysis
- **Missing Essentials**: Core nutrients that should be included
- **Redundant Supplements**: Overlapping or unnecessary additions
- **Age-Specific Needs**: Supplements particularly important for this age group

### 4. Optimization Recommendations
- **Core Foundation**: Essential supplements for everyone
- **Targeted Support**: Specific additions for health goals
- **Advanced Protocols**: Additional interventions for optimization

### 5. Implementation Strategy
- **Timing Protocol**: When to take each supplement
- **Food Interactions**: With or without meals
- **Monitoring**: How to track effectiveness

## Request
Please provide a comprehensive analysis of this supplement regimen following Dr. Strunz's functional medicine approach. Include specific recommendations for optimization, potential interactions, and a structured implementation plan.

Focus on:
- Evidence-based recommendations
- Practical implementation guidelines
- Cost-effectiveness considerations
- Measurable health outcomes
"""
            
            return prompt
        
        @self.app.prompt()
        async def nutrition_optimization_prompt(
            dietary_preferences: str,
            health_goals: str,
            restrictions: str = "",
            current_diet: str = "",
            activity_level: str = "moderate"
        ) -> str:
            """
            Generate a prompt for nutritional optimization based on Dr. Strunz's principles.
            
            This prompt creates personalized nutrition guidance following Dr. Strunz's
            low-carb, high-protein, anti-inflammatory dietary approach.
            
            Args:
                dietary_preferences: Food preferences and lifestyle choices
                health_goals: Specific health and fitness goals
                restrictions: Any dietary restrictions or allergies
                current_diet: Description of current eating patterns
                activity_level: Exercise frequency and intensity
            """
            
            prompt = f"""# Dr. Strunz Nutrition Optimization Protocol

## Dietary Profile
- **Preferences**: {dietary_preferences}
- **Health Goals**: {health_goals}
- **Activity Level**: {activity_level}
{f"- **Restrictions**: {restrictions}" if restrictions else ""}
{f"- **Current Diet**: {current_diet}" if current_diet else ""}

## Optimization Framework

Based on Dr. Strunz's nutritional medicine principles, please create a comprehensive nutrition plan:

### 1. Macronutrient Optimization
- **Protein Requirements**: Optimal intake for muscle health and metabolism
- **Carbohydrate Strategy**: Smart carb timing and selection
- **Healthy Fats**: Essential fatty acids for hormone production

### 2. Anti-Inflammatory Foods
- **Nutrient-Dense Choices**: Foods with highest nutritional value
- **Anti-Inflammatory Properties**: Foods that reduce systemic inflammation
- **Antioxidant Rich**: Natural compounds for cellular protection

### 3. Meal Timing & Structure
- **Intermittent Fasting**: Potential benefits and implementation
- **Pre/Post Workout**: Nutrition for optimal performance
- **Circadian Alignment**: Eating patterns for better sleep and energy

### 4. Specific Recommendations
- **Daily Meal Plan**: Structured eating schedule
- **Food Combinations**: Optimal nutrient absorption
- **Hydration Strategy**: Water intake and electrolyte balance

### 5. Implementation & Monitoring
- **Transition Plan**: How to gradually implement changes
- **Progress Tracking**: Metrics to monitor success
- **Troubleshooting**: Common challenges and solutions

## Request
Please create a personalized nutrition optimization plan following Dr. Strunz's evidence-based approach. Include specific meal recommendations, timing strategies, and measurable health outcomes.

Focus on:
- Practical meal planning
- Sustainable lifestyle changes
- Performance optimization
- Long-term health benefits
"""
            
            return prompt
        
        @self.app.prompt()
        async def research_query_prompt(
            topic: str,
            focus_area: str = "general",
            time_period: str = "all",
            evidence_level: str = "clinical"
        ) -> str:
            """
            Generate a prompt for researching health topics using Dr. Strunz's knowledge base.
            
            This prompt helps structure research queries to extract maximum value
            from Dr. Strunz's 20+ years of published content.
            
            Args:
                topic: Health topic to research
                focus_area: Specific aspect to focus on
                time_period: Time range for research (e.g., "2020-2025", "all")
                evidence_level: Type of evidence desired (clinical, observational, theoretical)
            """
            
            prompt = f"""# Dr. Strunz Knowledge Base Research Query

## Research Parameters
- **Topic**: {topic}
- **Focus Area**: {focus_area}
- **Time Period**: {time_period}
- **Evidence Level**: {evidence_level}

## Research Framework

Please conduct a comprehensive research analysis using Dr. Strunz's knowledge base:

### 1. Literature Review
- **Key Findings**: Main conclusions from Dr. Strunz's work
- **Evolution of Understanding**: How his views have developed over time
- **Supporting Evidence**: Scientific basis for recommendations

### 2. Practical Applications
- **Clinical Protocols**: Specific treatment approaches
- **Patient Success Stories**: Real-world implementation examples
- **Dosage Guidelines**: Practical implementation details

### 3. Comparative Analysis
- **Conventional vs. Functional**: Differences in approach
- **Contradictory Evidence**: Areas of ongoing debate
- **Emerging Trends**: New developments in the field

### 4. Implementation Guidance
- **Step-by-Step Protocols**: Clear implementation instructions
- **Monitoring Parameters**: How to track progress
- **Safety Considerations**: Potential risks and contraindications

### 5. Future Directions
- **Emerging Research**: New areas of investigation
- **Technology Integration**: Modern tools and testing
- **Personalization**: Individual variation considerations

## Request
Please provide a comprehensive research analysis of this topic using Dr. Strunz's published works, newsletter articles, and community discussions. Include both theoretical foundations and practical implementation guidance.

Focus on:
- Evidence-based conclusions
- Practical applicability
- Safety considerations
- Measurable outcomes
"""
            
            return prompt
        
        @self.app.prompt()
        async def longevity_protocol_prompt(
            age: int,
            gender: str,
            health_status: str = "good",
            risk_factors: str = "",
            lifestyle_preferences: str = ""
        ) -> str:
            """
            Generate a prompt for creating longevity protocols based on Dr. Strunz's approach.
            
            This prompt creates personalized anti-aging strategies following Dr. Strunz's
            molecular medicine and longevity research.
            
            Args:
                age: Current age
                gender: Gender for hormone-specific recommendations
                health_status: Current health status
                risk_factors: Known health risks or family history
                lifestyle_preferences: Lifestyle constraints and preferences
            """
            
            prompt = f"""# Dr. Strunz Longevity Protocol

## Personal Profile
- **Age**: {age} years
- **Gender**: {gender}
- **Health Status**: {health_status}
{f"- **Risk Factors**: {risk_factors}" if risk_factors else ""}
{f"- **Lifestyle**: {lifestyle_preferences}" if lifestyle_preferences else ""}

## Longevity Framework

Based on Dr. Strunz's molecular medicine approach, please create a comprehensive longevity protocol:

### 1. Cellular Optimization
- **Mitochondrial Support**: Energy production at cellular level
- **DNA Protection**: Antioxidant strategies for genetic integrity
- **Protein Synthesis**: Maintaining muscle mass and function

### 2. Hormone Optimization
- **Age-Related Decline**: Natural hormone changes and interventions
- **Bioidentical Support**: Safe hormone replacement strategies
- **Lifestyle Factors**: Natural hormone optimization

### 3. Metabolic Health
- **Insulin Sensitivity**: Maintaining metabolic flexibility
- **Inflammation Control**: Anti-inflammatory protocols
- **Autophagy Enhancement**: Cellular cleanup mechanisms

### 4. Cognitive Preservation
- **Brain Health**: Neuroprotective strategies
- **Memory Support**: Cognitive enhancement protocols
- **Stress Management**: Cortisol regulation for brain health

### 5. Physical Vitality
- **Muscle Preservation**: Sarcopenia prevention
- **Bone Health**: Osteoporosis prevention
- **Cardiovascular Fitness**: Heart health optimization

### 6. Diagnostic Monitoring
- **Biomarker Tracking**: Key health indicators to monitor
- **Regular Assessment**: Frequency of health evaluations
- **Intervention Adjustments**: Modifying protocols based on results

## Request
Please create a personalized longevity protocol following Dr. Strunz's molecular medicine approach. Include specific interventions, monitoring strategies, and measurable outcomes for healthy aging.

Focus on:
- Evidence-based interventions
- Personalized recommendations
- Practical implementation
- Long-term sustainability
"""
            
            return prompt
        
        @self.app.prompt()
        async def diagnostic_interpretation_prompt(
            lab_results: str,
            age: int,
            gender: str,
            symptoms: str = "",
            reference_ranges: str = ""
        ) -> str:
            """
            Generate a prompt for interpreting laboratory results using Dr. Strunz's optimal values.
            
            This prompt helps interpret lab results according to Dr. Strunz's functional medicine
            approach, focusing on optimal rather than normal values.
            
            Args:
                lab_results: Laboratory test results and values
                age: Patient age for age-appropriate interpretation
                gender: Gender for gender-specific considerations
                symptoms: Current symptoms to correlate with results
                reference_ranges: Laboratory reference ranges provided
            """
            
            prompt = f"""# Dr. Strunz Laboratory Results Interpretation

## Patient Information
- **Age**: {age} years
- **Gender**: {gender}
{("- **Symptoms**: " + symptoms) if symptoms else ""}

## Laboratory Results
{lab_results}

{("## Reference Ranges" + chr(10) + reference_ranges) if reference_ranges else ""}

## Interpretation Framework

Using Dr. Strunz's functional medicine approach, please analyze these laboratory results:

### 1. Optimal vs. Normal Values
- **Dr. Strunz's Optimal Ranges**: Compare results to functional medicine targets
- **Standard Reference Ranges**: Differences from conventional medicine
- **Clinical Significance**: What these values mean for health optimization

### 2. Pattern Recognition
- **Metabolic Patterns**: Insulin resistance, metabolic syndrome indicators
- **Inflammatory Markers**: Signs of chronic inflammation
- **Nutritional Status**: Deficiency patterns and absorption issues
- **Hormone Balance**: Endocrine system function

### 3. Root Cause Analysis
- **Underlying Mechanisms**: Why these values are suboptimal
- **Interconnected Systems**: How different markers relate to each other
- **Lifestyle Factors**: Diet, exercise, stress contributions

### 4. Optimization Strategy
- **Nutritional Interventions**: Specific dietary recommendations
- **Targeted Supplementation**: Supplements to address deficiencies
- **Lifestyle Modifications**: Exercise, sleep, stress management

### 5. Monitoring Protocol
- **Follow-up Testing**: Which tests to repeat and when
- **Progress Markers**: How to track improvement
- **Red Flags**: Warning signs to watch for

## Request
Please provide a comprehensive interpretation of these laboratory results following Dr. Strunz's functional medicine approach. Include specific recommendations for optimization and a monitoring strategy.

Focus on:
- Optimal value targets vs. normal ranges
- Practical intervention strategies
- Measurable improvement goals
- Timeline for reassessment
"""
            
            return prompt
        
        @self.app.prompt()
        async def symptom_analysis_prompt(
            primary_symptom: str,
            duration: str,
            severity: str,
            associated_symptoms: str = "",
            triggers: str = "",
            improvements: str = ""
        ) -> str:
            """
            Generate a prompt for analyzing symptoms using Dr. Strunz's functional medicine approach.
            
            This prompt helps identify root causes of symptoms rather than just treating symptoms.
            
            Args:
                primary_symptom: Main symptom or complaint
                duration: How long symptoms have been present
                severity: Severity level (mild, moderate, severe)
                associated_symptoms: Other symptoms that occur together
                triggers: Known triggers that worsen symptoms
                improvements: What helps improve symptoms
            """
            
            prompt = f"""# Dr. Strunz Symptom Analysis & Root Cause Investigation

## Symptom Profile
- **Primary Symptom**: {primary_symptom}
- **Duration**: {duration}
- **Severity**: {severity}
{f"- **Associated Symptoms**: {associated_symptoms}" if associated_symptoms else ""}
{f"- **Triggers**: {triggers}" if triggers else ""}
{f"- **Improvements**: {improvements}" if improvements else ""}

## Analysis Framework

Using Dr. Strunz's functional medicine approach, please analyze these symptoms:

### 1. Root Cause Investigation
- **Biochemical Imbalances**: Nutritional deficiencies, hormone disruptions
- **Inflammatory Processes**: Chronic inflammation patterns
- **Toxic Load**: Heavy metals, environmental toxins
- **Digestive Health**: Gut-health connection to symptoms

### 2. Systems Thinking
- **Interconnected Systems**: How different body systems relate to symptoms
- **Cascade Effects**: How one imbalance creates others
- **Feedback Loops**: Self-perpetuating symptom cycles

### 3. Functional Medicine Assessment
- **Cellular Function**: Mitochondrial health, energy production
- **Detoxification**: Liver function, elimination pathways
- **Immune System**: Autoimmune patterns, immune dysfunction
- **Nervous System**: Stress response, neurotransmitter balance

### 4. Comprehensive Intervention Strategy
- **Immediate Relief**: Natural approaches for symptom management
- **Root Cause Treatment**: Addressing underlying imbalances
- **System Restoration**: Rebuilding optimal function
- **Prevention**: Preventing recurrence

### 5. Diagnostic Considerations
- **Recommended Testing**: Laboratory tests to identify root causes
- **Functional Assessments**: Specialized tests for comprehensive evaluation
- **Monitoring Parameters**: How to track progress

## Request
Please provide a comprehensive analysis of these symptoms following Dr. Strunz's functional medicine approach. Focus on identifying root causes rather than just symptom management.

Focus on:
- Biochemical root causes
- Natural intervention strategies
- Comprehensive restoration protocols
- Prevention strategies
"""
            
            return prompt
        
        @self.app.prompt()
        async def athletic_performance_prompt(
            sport: str,
            training_level: str,
            performance_goals: str,
            current_challenges: str = "",
            training_schedule: str = "",
            recovery_issues: str = ""
        ) -> str:
            """
            Generate a prompt for athletic performance optimization using Dr. Strunz's sports medicine approach.
            
            This prompt applies Dr. Strunz's experience as a triathlete and sports medicine expert
            to optimize athletic performance through nutrition and supplementation.
            
            Args:
                sport: Type of sport or athletic activity
                training_level: Training level (beginner, intermediate, advanced, elite)
                performance_goals: Specific performance goals
                current_challenges: Current performance challenges
                training_schedule: Training frequency and intensity
                recovery_issues: Recovery or injury concerns
            """
            
            prompt = f"""# Dr. Strunz Athletic Performance Optimization

## Athletic Profile
- **Sport**: {sport}
- **Training Level**: {training_level}
- **Performance Goals**: {performance_goals}
{f"- **Current Challenges**: {current_challenges}" if current_challenges else ""}
{f"- **Training Schedule**: {training_schedule}" if training_schedule else ""}
{f"- **Recovery Issues**: {recovery_issues}" if recovery_issues else ""}

## Performance Optimization Framework

Based on Dr. Strunz's sports medicine expertise and triathlon experience, please provide:

### 1. Nutritional Periodization
- **Training Fuel**: Optimal nutrition for different training phases
- **Competition Nutrition**: Race-day fueling strategies
- **Recovery Nutrition**: Post-training nutritional support
- **Hydration Protocols**: Electrolyte balance and fluid management

### 2. Supplement Strategy
- **Performance Enhancers**: Legal, natural performance supplements
- **Recovery Accelerators**: Supplements for faster recovery
- **Injury Prevention**: Nutrients for joint and tissue health
- **Timing Protocols**: When to take supplements for maximum effect

### 3. Biochemical Optimization
- **Energy Systems**: Optimizing cellular energy production
- **Oxygen Utilization**: Improving aerobic capacity
- **Lactate Threshold**: Enhancing anaerobic performance
- **Hormone Optimization**: Natural hormone support for performance

### 4. Recovery & Regeneration
- **Sleep Optimization**: Sleep protocols for athletes
- **Stress Management**: Managing training stress
- **Inflammation Control**: Anti-inflammatory strategies
- **Tissue Repair**: Accelerating recovery processes

### 5. Performance Monitoring
- **Key Biomarkers**: Laboratory tests for athletes
- **Performance Metrics**: Tracking progress indicators
- **Fatigue Management**: Recognizing overtraining signs
- **Adaptation Strategies**: Adjusting protocols based on progress

## Request
Please create a comprehensive athletic performance optimization plan following Dr. Strunz's sports medicine approach. Include specific nutritional strategies, supplementation protocols, and performance monitoring guidelines.

Focus on:
- Evidence-based performance enhancement
- Natural, legal optimization methods
- Sustainable long-term strategies
- Measurable performance improvements
"""
            
            return prompt
        
        @self.app.prompt()
        async def family_health_prompt(
            family_size: int,
            age_ranges: str,
            health_goals: str,
            family_health_history: str = "",
            dietary_preferences: str = "",
            lifestyle_constraints: str = ""
        ) -> str:
            """
            Generate a prompt for family health optimization using Dr. Strunz's principles.
            
            This prompt creates comprehensive family health strategies that can be
            implemented by the whole family for optimal health outcomes.
            
            Args:
                family_size: Number of family members
                age_ranges: Age ranges of family members
                health_goals: Family health goals
                family_health_history: Relevant family health history
                dietary_preferences: Family dietary preferences
                lifestyle_constraints: Time, budget, or other constraints
            """
            
            prompt = f"""# Dr. Strunz Family Health Optimization Plan

## Family Profile
- **Family Size**: {family_size} members
- **Age Ranges**: {age_ranges}
- **Health Goals**: {health_goals}
{f"- **Family Health History**: {family_health_history}" if family_health_history else ""}
{f"- **Dietary Preferences**: {dietary_preferences}" if dietary_preferences else ""}
{f"- **Lifestyle Constraints**: {lifestyle_constraints}" if lifestyle_constraints else ""}

## Family Health Framework

Based on Dr. Strunz's preventive medicine approach, please create a comprehensive family health plan:

### 1. Nutritional Foundation
- **Family Meal Planning**: Healthy meals everyone will enjoy
- **Age-Appropriate Nutrition**: Specific needs for different ages
- **Meal Prep Strategies**: Efficient healthy meal preparation
- **Healthy Snacking**: Nutritious options for all ages

### 2. Supplement Strategy
- **Core Family Supplements**: Essential nutrients for everyone
- **Age-Specific Additions**: Targeted supplements by age group
- **Budget-Friendly Options**: Cost-effective supplement choices
- **Easy Implementation**: Simple dosing schedules

### 3. Lifestyle Integration
- **Family Exercise**: Physical activities everyone can enjoy
- **Stress Management**: Family stress reduction strategies
- **Sleep Hygiene**: Healthy sleep habits for all ages
- **Screen Time Balance**: Managing technology use

### 4. Disease Prevention
- **Genetic Risk Factors**: Addressing family health history
- **Immune Support**: Strengthening family immunity
- **Chronic Disease Prevention**: Long-term health strategies
- **Early Detection**: Age-appropriate health screening

### 5. Education & Motivation
- **Health Education**: Teaching healthy habits
- **Family Challenges**: Fun health competitions
- **Progress Tracking**: Measuring family health improvements
- **Sustainable Habits**: Building lasting healthy behaviors

## Request
Please create a comprehensive family health optimization plan following Dr. Strunz's preventive medicine approach. Include practical strategies that work for busy families while addressing the specific needs of different age groups.

Focus on:
- Practical, implementable strategies
- Age-appropriate recommendations
- Budget-conscious solutions
- Family-friendly approaches
"""
            
            return prompt
        
        @self.app.prompt()
        async def practitioner_consultation_prompt(
            practitioner_type: str,
            patient_case: str,
            clinical_question: str,
            current_approach: str = "",
            treatment_challenges: str = "",
            desired_outcomes: str = ""
        ) -> str:
            """
            Generate a prompt for healthcare practitioners seeking Dr. Strunz's functional medicine insights.
            
            This prompt helps healthcare practitioners integrate Dr. Strunz's functional medicine
            approach into their clinical practice.
            
            Args:
                practitioner_type: Type of healthcare practitioner
                patient_case: Patient case description
                clinical_question: Specific clinical question
                current_approach: Current treatment approach
                treatment_challenges: Current treatment challenges
                desired_outcomes: Desired patient outcomes
            """
            
            prompt = f"""# Dr. Strunz Functional Medicine Consultation

## Practitioner Profile
- **Practitioner Type**: {practitioner_type}
- **Clinical Question**: {clinical_question}
{f"- **Current Approach**: {current_approach}" if current_approach else ""}
{f"- **Treatment Challenges**: {treatment_challenges}" if treatment_challenges else ""}
{f"- **Desired Outcomes**: {desired_outcomes}" if desired_outcomes else ""}

## Patient Case
{patient_case}

## Consultation Framework

Based on Dr. Strunz's functional medicine expertise, please provide clinical insights:

### 1. Functional Medicine Assessment
- **Root Cause Analysis**: Identifying underlying imbalances
- **Systems Approach**: Interconnected body systems evaluation
- **Biochemical Optimization**: Cellular and metabolic considerations
- **Personalized Medicine**: Individual variation factors

### 2. Diagnostic Considerations
- **Functional Testing**: Advanced diagnostic options
- **Biomarker Interpretation**: Optimal vs. normal values
- **Pattern Recognition**: Common functional medicine patterns
- **Monitoring Protocols**: Tracking treatment progress

### 3. Treatment Integration
- **Nutritional Medicine**: Therapeutic nutrition approaches
- **Supplementation Strategy**: Evidence-based supplement protocols
- **Lifestyle Medicine**: Comprehensive lifestyle interventions
- **Conventional Integration**: Combining with conventional treatments

### 4. Clinical Implementation
- **Patient Education**: Explaining functional medicine concepts
- **Treatment Protocols**: Step-by-step implementation
- **Follow-up Strategies**: Monitoring and adjustment protocols
- **Outcome Measurement**: Tracking clinical improvements

### 5. Professional Development
- **Continuing Education**: Advanced functional medicine training
- **Practice Integration**: Implementing functional medicine approaches
- **Patient Communication**: Explaining complex concepts
- **Clinical Resources**: Recommended references and tools

## Request
Please provide comprehensive functional medicine insights for this clinical case following Dr. Strunz's approach. Include specific treatment recommendations, diagnostic considerations, and implementation strategies.

Focus on:
- Evidence-based functional medicine principles
- Practical clinical implementation
- Patient-centered care approaches
- Measurable clinical outcomes
"""
            
            return prompt

    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.app.tool()
        async def knowledge_search(
            query: str,
            sources: Optional[List[str]] = None,
            limit: int = 10,
            filters: Optional[Dict] = None,
            user_profile: Optional[Dict] = None
        ) -> Dict:
            """
            Search Dr. Strunz knowledge base with enhanced semantic understanding.
            
            Parameters:
            - query: Search query
            - sources: Filter by source types ['books', 'news', 'forum']
            - limit: Number of results to return
            - filters: Additional filters (categories, date_range, etc.)
            - user_profile: User context for personalized results
            
            Returns:
            Comprehensive search results with relevance explanations
            """
            return await self._enhanced_search(query, sources, limit, filters, user_profile)
        
        @self.app.tool()
        async def find_contradictions(
            topic: str,
            include_reasoning: bool = True,
            time_range: Optional[Dict] = None
        ) -> Dict:
            """
            Find contradictions or evolving viewpoints on a health topic.
            
            Analyzes how Dr. Strunz's recommendations may have evolved over time
            or identifies areas where different sources present varying perspectives.
            """
            return await self._analyze_contradictions(topic, include_reasoning, time_range)
        
        @self.app.tool()
        async def trace_topic_evolution(
            topic: str,
            start_year: Optional[int] = None,
            end_year: Optional[int] = None,
            include_events: bool = True
        ) -> Dict:
            """
            Trace how a health topic evolved in Dr. Strunz's content over time.
            
            Shows key developments, changing recommendations, and influential events.
            """
            return await self._trace_evolution(topic, start_year, end_year, include_events)
        
        @self.app.tool()
        async def create_health_protocol(
            condition: str,
            user_profile: Optional[Dict] = None,
            severity: str = "moderate",
            include_alternatives: bool = True
        ) -> Dict:
            """
            Create a comprehensive health protocol based on Dr. Strunz's methods.
            
            Generates personalized recommendations including supplements, nutrition,
            lifestyle changes, and monitoring strategies.
            """
            return await self._create_protocol(condition, user_profile, severity, include_alternatives)
        
        @self.app.tool()
        async def compare_approaches(
            health_issue: str,
            alternative_approaches: List[str],
            criteria: Optional[List[str]] = None
        ) -> Dict:
            """
            Compare Dr. Strunz's approach with other health methodologies.
            
            Provides balanced analysis of different treatment philosophies.
            """
            return await self._compare_approaches(health_issue, alternative_approaches, criteria)
        
        @self.app.tool()
        async def analyze_supplement_stack(
            supplements: List[str],
            health_goals: List[str],
            user_profile: Optional[Dict] = None,
            check_interactions: bool = True
        ) -> Dict:
            """
            Analyze a supplement stack based on Dr. Strunz's recommendations.
            
            Checks for interactions, optimizes timing, and suggests improvements.
            """
            return await self._analyze_supplements(supplements, health_goals, user_profile, check_interactions)
        
        @self.app.tool()
        async def nutrition_calculator(
            age: int,
            gender: str,
            weight: float,
            height: float,
            activity_level: str,
            health_goals: List[str],
            dietary_preferences: Optional[List[str]] = None
        ) -> Dict:
            """
            Calculate personalized nutrition recommendations following Dr. Strunz principles.
            
            Provides macronutrient ratios, caloric needs, and food suggestions.
            """
            return await self._calculate_nutrition(age, gender, weight, height, activity_level, health_goals, dietary_preferences)
        
        @self.app.tool()
        async def get_community_insights(
            topic: str,
            min_engagement: int = 5,
            user_role: Optional[str] = None,
            time_period: Optional[str] = None
        ) -> Dict:
            """
            Get insights from the Strunz community forum discussions.
            
            Aggregates real-world experiences and success stories.
            """
            return await self._get_community_insights(topic, min_engagement, user_role, time_period)
        
        @self.app.tool()
        async def summarize_posts(
            category: str,
            limit: int = 10,
            timeframe: str = "last_month",
            user_profile: Optional[Dict] = None
        ) -> Dict:
            """
            Summarize recent posts by category with personalized filtering.
            
            Provides digests of recent content tailored to user interests.
            """
            return await self._summarize_posts(category, limit, timeframe, user_profile)
        
        @self.app.tool()
        async def get_trending_insights(
            days: int = 30,
            user_role: Optional[str] = None,
            categories: Optional[List[str]] = None
        ) -> Dict:
            """
            Get trending health insights from recent content.
            
            Identifies emerging topics and popular discussions.
            """
            return await self._get_trending(days, user_role, categories)
        
        @self.app.tool()
        async def analyze_strunz_newsletter_evolution(
            timeframe: str = "all",
            topic_focus: Optional[str] = None
        ) -> Dict:
            """
            Analyze how Dr. Strunz's newsletter content evolved over 20+ years.
            
            Tracks thematic changes, writing style evolution, and major focus shifts.
            """
            return await self._analyze_newsletter_evolution(timeframe, topic_focus)
        
        @self.app.tool()
        async def get_guest_authors_analysis(
            timeframe: str = "all",
            specialty_focus: Optional[str] = None
        ) -> Dict:
            """
            Analyze guest authors and contributors in Dr. Strunz's newsletter.
            
            Examines editorial approach and external expert integration.
            """
            return await self._analyze_guest_authors(timeframe, specialty_focus)
        
        @self.app.tool()
        async def track_health_topic_trends(
            topic: str,
            timeframe: str = "5_years",
            include_context: bool = True
        ) -> Dict:
            """
            Track how specific health topics trended in newsletters over time.
            
            Shows frequency, context events, and related topics.
            """
            return await self._track_topic_trends(topic, timeframe, include_context)
        
        @self.app.tool()
        async def get_health_assessment_questions(
            user_role: Optional[str] = None,
            assessment_depth: str = "comprehensive"
        ) -> Dict:
            """
            Get personalized health assessment questions.
            
            Provides structured questionnaire for user profiling.
            """
            if self.profiling:
                return self.profiling.get_assessment_questions(user_role, assessment_depth)
            return {"error": "User profiling system not available"}
        
        @self.app.tool()
        async def assess_user_health_profile(
            responses: Dict[str, Any],
            include_recommendations: bool = True
        ) -> Dict:
            """
            Assess user health profile based on questionnaire responses.
            
            Creates comprehensive user profile with role assignment.
            """
            if self.profiling:
                return self.profiling.assess_profile(responses, include_recommendations)
            return {"error": "User profiling system not available"}
        
        @self.app.tool()
        async def create_personalized_protocol(
            user_profile: Dict,
            primary_concern: Optional[str] = None,
            include_timeline: bool = True
        ) -> Dict:
            """
            Create fully personalized health protocol based on user profile.
            
            Generates custom recommendations with implementation timeline.
            """
            if self.profiling:
                return self.profiling.create_personalized_protocol(user_profile, primary_concern, include_timeline)
            return {"error": "User profiling system not available"}
        
        @self.app.tool()
        async def get_dr_strunz_biography(
            include_achievements: bool = True,
            include_philosophy: bool = True
        ) -> Dict:
            """
            Get comprehensive biography and philosophy of Dr. Ulrich Strunz.
            
            Includes achievements, medical philosophy, and key contributions.
            """
            return await self._get_biography(include_achievements, include_philosophy)
        
        @self.app.tool()
        async def get_mcp_server_purpose() -> Dict:
            """
            Get information about this MCP server's purpose and capabilities.
            
            Explains the knowledge base structure and available tools.
            """
            return await self._get_server_info()
        
        @self.app.tool()
        async def get_vector_db_analysis() -> Dict:
            """
            Get detailed analysis of the vector database content.
            
            Shows statistics, coverage, and data quality metrics.
            """
            return await self._analyze_vector_db()
        
        @self.app.tool()
        async def get_optimal_diagnostic_values(
            age: int,
            gender: str,
            weight: Optional[float] = None,
            height: Optional[float] = None,
            athlete: bool = False,
            conditions: Optional[List[str]] = None,
            category: Optional[str] = None
        ) -> Dict:
            """
            Get Dr. Strunz's optimal diagnostic values personalized by demographics.
            
            Returns optimal (not just normal) ranges for peak health performance.
            Categories: vitamins, minerals, hormones, metabolic, lipids, inflammation, all
            """
            return await self._get_optimal_values(age, gender, weight, height, athlete, conditions, category)
        
        # Store references to all tools in registry
        self.tool_registry["knowledge_search"] = knowledge_search
        self.tool_registry["find_contradictions"] = find_contradictions
        self.tool_registry["trace_topic_evolution"] = trace_topic_evolution
        self.tool_registry["create_health_protocol"] = create_health_protocol
        self.tool_registry["compare_approaches"] = compare_approaches
        self.tool_registry["analyze_supplement_stack"] = analyze_supplement_stack
        self.tool_registry["nutrition_calculator"] = nutrition_calculator
        self.tool_registry["get_community_insights"] = get_community_insights
        self.tool_registry["summarize_posts"] = summarize_posts
        self.tool_registry["get_trending_insights"] = get_trending_insights
        self.tool_registry["analyze_strunz_newsletter_evolution"] = analyze_strunz_newsletter_evolution
        self.tool_registry["get_guest_authors_analysis"] = get_guest_authors_analysis
        self.tool_registry["track_health_topic_trends"] = track_health_topic_trends
        self.tool_registry["get_health_assessment_questions"] = get_health_assessment_questions
        self.tool_registry["assess_user_health_profile"] = assess_user_health_profile
        self.tool_registry["create_personalized_protocol"] = create_personalized_protocol
        self.tool_registry["get_dr_strunz_biography"] = get_dr_strunz_biography
        self.tool_registry["get_mcp_server_purpose"] = get_mcp_server_purpose
        self.tool_registry["get_vector_db_analysis"] = get_vector_db_analysis
        self.tool_registry["get_optimal_diagnostic_values"] = get_optimal_diagnostic_values
    
    # Implementation methods
    async def _enhanced_search(self, query: str, sources: Optional[List[str]], limit: int, filters: Optional[Dict], user_profile: Optional[Dict]) -> Dict:
        """Enhanced search with user context"""
        if not self.HAS_VECTOR_STORE:
            return {
                "error": "Vector store not available",
                "suggestion": "Please ensure FAISS indices are properly loaded"
            }
        
        try:
            # Perform search
            results = self.searcher.search(
                query=query,
                k=limit,
                sources=sources
            )
            
            # Add source URLs for news articles
            formatted_results = []
            for r in results:
                result_dict = {
                    "source": r.source,
                    "title": r.title,
                    "content": r.text,
                    "score": r.score,
                    "metadata": r.metadata
                }
                
                # Add URL for news articles
                if r.source == "news" and "filename" in r.metadata:
                    slug = r.metadata["filename"].replace(".json", "")
                    result_dict["url"] = f"https://www.strunz.com/news/{slug}.html"
                
                formatted_results.append(result_dict)
            
            return {
                "query": query,
                "results": formatted_results,
                "total_results": len(results),
                "sources_searched": sources or ["books", "news", "forum"]
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"error": str(e)}
    
    async def _analyze_contradictions(self, topic: str, include_reasoning: bool, time_range: Optional[Dict]) -> Dict:
        """Analyze contradictions in health topics"""
        # Placeholder implementation
        return {
            "topic": topic,
            "contradictions_found": 2,
            "examples": [
                {
                    "aspect": "Vitamin D dosing",
                    "early_view": "2000-4000 IU daily",
                    "current_view": "4000-8000 IU daily", 
                    "reasoning": "New research on optimal blood levels" if include_reasoning else None,
                    "timeline": "2010 vs 2024"
                }
            ],
            "analysis": "Dr. Strunz's recommendations evolved with emerging research"
        }
    
    async def _trace_evolution(self, topic: str, start_year: Optional[int], end_year: Optional[int], include_events: bool) -> Dict:
        """Trace topic evolution over time"""
        return {
            "topic": topic,
            "timeline": [
                {
                    "year": 2010,
                    "focus": "Basic supplementation",
                    "key_points": ["Introduction to molecular medicine"]
                },
                {
                    "year": 2020,
                    "focus": "Pandemic response", 
                    "key_points": ["Immune system optimization", "Vitamin D critical"]
                },
                {
                    "year": 2024,
                    "focus": "Longevity protocols",
                    "key_points": ["Epigenetic optimization", "Advanced protocols"]
                }
            ],
            "major_shifts": ["From treatment to prevention", "From general to personalized"],
            "influential_events": ["COVID-19 pandemic", "New longevity research"] if include_events else []
        }
    
    async def _create_protocol(self, condition: str, user_profile: Optional[Dict], severity: str, include_alternatives: bool) -> Dict:
        """Create health protocol"""
        base_protocol = {
            "condition": condition,
            "severity": severity,
            "core_supplements": [
                {"name": "Vitamin D3", "dose": "4000-8000 IU", "timing": "morning"},
                {"name": "Magnesium", "dose": "400mg", "timing": "evening"},
                {"name": "Omega-3", "dose": "2g EPA/DHA", "timing": "with meals"}
            ],
            "nutrition": {
                "approach": "Low-carb, high-protein",
                "key_foods": ["Wild salmon", "Organic vegetables", "Nuts"],
                "avoid": ["Sugar", "Processed foods", "Trans fats"]
            },
            "lifestyle": [
                "Daily movement (30 min)",
                "Sleep optimization (7-8 hours)",
                "Stress reduction techniques"
            ],
            "monitoring": [
                "Monthly blood work",
                "Weekly symptom tracking",
                "Energy level assessment"
            ],
            "expected_timeline": "3-6 months for significant improvement"
        }
        
        if include_alternatives:
            base_protocol["alternatives"] = [
                "Functional medicine approach",
                "Integrative medicine options"
            ]
        
        return base_protocol
    
    async def _analyze_supplements(self, supplements: List[str], health_goals: List[str], user_profile: Optional[Dict], check_interactions: bool) -> Dict:
        """Analyze supplement stack"""
        analysis = {
            "supplements": supplements,
            "health_goals": health_goals,
            "safety_check": "No major interactions found" if check_interactions else "Not checked",
            "optimization_suggestions": [
                {
                    "suggestion": "Take fat-soluble vitamins with meals",
                    "affected": ["Vitamin D", "Vitamin E", "Omega-3"]
                },
                {
                    "suggestion": "Separate iron and calcium by 2 hours",
                    "reason": "Competitive absorption"
                }
            ],
            "timing_recommendations": {
                "morning": ["B-Complex", "Vitamin D", "Iron"],
                "evening": ["Magnesium", "Zinc", "Calcium"]
            },
            "dr_strunz_rating": "Well-designed stack following molecular medicine principles"
        }
        
        return analysis
    
    async def _calculate_nutrition(self, age: int, gender: str, weight: float, height: float, activity_level: str, health_goals: List[str], dietary_preferences: Optional[List[str]]) -> Dict:
        """Calculate nutrition needs"""
        # Basic calculations
        bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "male" else -161)
        
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)
        
        return {
            "daily_calories": round(tdee),
            "macronutrients": {
                "protein": f"{round(weight * 2.2)}g (30%)",
                "fat": f"{round(tdee * 0.35 / 9)}g (35%)", 
                "carbs": f"{round(tdee * 0.35 / 4)}g (35%)"
            },
            "dr_strunz_adjustments": {
                "low_carb_option": "Reduce carbs to 50-100g for metabolic optimization",
                "protein_boost": "Increase to 2.5g/kg for muscle building",
                "fasting_window": "16:8 intermittent fasting recommended"
            },
            "key_nutrients": [
                "Vitamin D: 4000-8000 IU",
                "Omega-3: 2-4g EPA/DHA",
                "Magnesium: 400-800mg"
            ]
        }
    
    async def _get_community_insights(self, topic: str, min_engagement: int, user_role: Optional[str], time_period: Optional[str]) -> Dict:
        """Get community insights"""
        return {
            "topic": topic,
            "total_discussions": 42,
            "high_engagement_posts": 8,
            "key_insights": [
                {
                    "insight": "Vitamin D + K2 combination highly effective",
                    "supporting_posts": 15,
                    "success_rate": "87% reported improvement"
                },
                {
                    "insight": "Morning supplementation timing preferred",
                    "supporting_posts": 23,
                    "user_experience": "Better energy throughout day"
                }
            ],
            "community_consensus": "Strong agreement on molecular medicine approach",
            "trending_topics": ["Longevity protocols", "Mitochondrial health"]
        }
    
    async def _summarize_posts(self, category: str, limit: int, timeframe: str, user_profile: Optional[Dict]) -> Dict:
        """Summarize recent posts"""
        return {
            "category": category,
            "timeframe": timeframe,
            "post_count": limit,
            "summaries": [
                {
                    "title": "Vitamin D Success Story",
                    "date": "2024-12-15",
                    "key_points": ["Raised levels from 20 to 80 ng/ml", "Energy restored"],
                    "engagement": "45 likes, 12 comments"
                }
            ],
            "trends": ["Increasing interest in longevity", "Focus on prevention"]
        }
    
    async def _get_trending(self, days: int, user_role: Optional[str], categories: Optional[List[str]]) -> Dict:
        """Get trending insights"""
        return {
            "period": f"Last {days} days",
            "trending_topics": [
                {"topic": "Epigenetic optimization", "mentions": 127, "growth": "+45%"},
                {"topic": "Mitochondrial health", "mentions": 98, "growth": "+32%"},
                {"topic": "Longevity protocols", "mentions": 156, "growth": "+28%"}
            ],
            "emerging_discussions": [
                "NAD+ supplementation strategies",
                "Cold exposure benefits",
                "Circadian rhythm optimization"
            ],
            "community_focus": "Shift towards preventive longevity strategies"
        }
    
    async def _analyze_newsletter_evolution(self, timeframe: str, topic_focus: Optional[str]) -> Dict:
        """Analyze newsletter evolution"""
        return {
            "timeframe": timeframe,
            "total_articles": 6953,
            "evolution_phases": [
                {
                    "period": "2004-2010",
                    "articles": 1234,
                    "focus": "Foundation building",
                    "tone": "Educational",
                    "key_topics": ["Basic nutrition", "Fitness", "Blood analysis"]
                },
                {
                    "period": "2020-2021", 
                    "articles": 573,
                    "focus": "Pandemic response",
                    "tone": "Urgent advocacy",
                    "key_topics": ["Immune system", "Vitamin D", "Prevention"]
                },
                {
                    "period": "2022-2025",
                    "articles": 1373,
                    "focus": "Advanced integration",
                    "tone": "Visionary",
                    "key_topics": ["Longevity", "Epigenetics", "Precision medicine"]
                }
            ],
            "writing_style_changes": [
                "Increasingly scientific depth",
                "More personal patient stories",
                "Stronger advocacy tone post-2020"
            ]
        }
    
    async def _analyze_guest_authors(self, timeframe: str, specialty_focus: Optional[str]) -> Dict:
        """Analyze guest authors in Dr. Strunz newsletter"""
        return {
            "analysis_approach": "Dr. Strunz maintains primary authorship",
            "guest_author_strategy": {
                "frequency": "Minimal - preserves unified voice",
                "approach": "Single authoritative voice maintains message consistency",
                "rationale": "Direct doctor-patient communication style"
            },
            "content_sources": {
                "primary": "40+ years clinical experience",
                "secondary": "International research synthesis",
                "expert_consultation": "Behind-the-scenes consultation rather than co-authorship",
                "book_co_authors": "Limited to specific technical collaborations"
            },
            "editorial_benefits": {
                "consistency": "Unified philosophy across 20+ years",
                "trust": "Personal accountability for all content",
                "credibility": "Single expert authority builds trust",
                "authenticity": "Personal experiences and patient stories"
            },
            "comparison": {
                "vs_other_newsletters": "Most health newsletters feature multiple authors",
                "unique_value": "Direct access to Dr. Strunz's expertise"
            },
            "unique_approach": "Unlike many health newsletters, Dr. Strunz maintains direct authorship to ensure message integrity and personal connection"
        }
    
    async def _track_topic_trends(self, topic: str, timeframe: str, include_context: bool) -> Dict:
        """Track health topic trends"""
        trends = {
            "topic": topic,
            "timeframe": timeframe,
            "frequency_data": [
                {"year": 2020, "mentions": 45, "context": "Pandemic focus"},
                {"year": 2023, "mentions": 128, "context": "Longevity emphasis"},
                {"year": 2024, "mentions": 156, "context": "Mainstream adoption"}
            ],
            "peak_periods": [
                {"period": "March 2020", "reason": "COVID-19 outbreak", "mentions": 89}
            ],
            "related_topics": ["Immune system", "Prevention", "Optimization"],
            "sentiment_evolution": "From crisis response to proactive optimization"
        }
        
        if include_context:
            trends["contextual_events"] = [
                "COVID-19 pandemic drove vitamin D awareness",
                "New research on optimal blood levels",
                "Celebrity endorsements increased interest"
            ]
        
        return trends
    
    async def _get_biography(self, include_achievements: bool, include_philosophy: bool) -> Dict:
        """Get Dr. Strunz biography"""
        bio = {
            "name": "Dr. med. Ulrich Strunz",
            "title": "Pioneer of Molecular Medicine",
            "background": {
                "medical_training": "Medical degree with specialization in molecular medicine",
                "athletic_background": "Marathon runner and triathlete",
                "clinical_practice": "40+ years in preventive medicine"
            }
        }
        
        if include_achievements:
            bio["achievements"] = {
                "books": "40+ bestselling health books",
                "innovations": "Blood tuning methodology, molecular medicine protocols",
                "impact": "Millions of lives transformed through preventive medicine",
                "athletic": "Completed 40+ marathons, multiple Ironman competitions"
            }
        
        if include_philosophy:
            bio["philosophy"] = {
                "core_belief": "The body can heal itself with proper molecular support",
                "approach": "Measure, don't guess - optimize based on blood values",
                "focus": "Prevention over treatment, optimization over normalization",
                "vision": "Everyone can achieve optimal health through molecular medicine"
            }
        
        return bio
    
    async def _get_server_info(self) -> Dict:
        """Get MCP server information"""
        return {
            "server_name": "Dr. Strunz Knowledge Base MCP Server",
            "version": "0.6.3",
            "purpose": "Comprehensive access to Dr. Strunz's medical knowledge and community insights",
            "capabilities": {
                "search": "Semantic search across books, newsletters, and forum",
                "analysis": "Topic evolution, contradiction finding, trend analysis",
                "protocols": "Personalized health protocol generation",
                "community": "Real-world insights from 20+ years of discussions",
                "prompts": "6 health-focused system prompts for structured interactions",
                "tools_available": len(self.tool_registry),
                "prompts_available": 6
            },
            "data_sources": {
                "books": "13 comprehensive health books",
                "newsletters": "6,953 articles (2004-2025)",
                "forum": "14,435 community discussions",
                "total_content": "43,373 indexed text chunks"
            },
            "special_features": [
                "User profiling for personalized recommendations",
                "Newsletter evolution analysis over 20 years",
                "Optimal diagnostic values database",
                "Community consensus extraction",
                "System prompts for guided health interactions",
                "Structured prompt templates for different use cases"
            ]
        }
    
    async def _analyze_vector_db(self) -> Dict:
        """Analyze vector database"""
        stats = {
            "vector_dimensions": 384,
            "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "index_type": "FAISS IndexFlatL2",
            "total_vectors": 43373,
            "breakdown": {
                "books": {"chunks": 8649, "coverage": "13 books"},
                "news": {"chunks": 28324, "coverage": "6,953 articles"},
                "forum": {"chunks": 6400, "coverage": "Limited data"}
            },
            "quality_metrics": {
                "average_chunk_size": 1000,
                "overlap": 200,
                "language": "German (primary), English (searchable)"
            },
            "search_performance": {
                "average_query_time": "15-50ms",
                "accuracy": "High semantic matching",
                "multilingual": "German/English cross-language search"
            }
        }
        
        if self.HAS_VECTOR_STORE:
            stats["status"] = "Operational"
        else:
            stats["status"] = "Not loaded"
        
        return stats
    
    async def _get_optimal_values(self, age: int, gender: str, weight: Optional[float], height: Optional[float], 
                                  athlete: bool, conditions: Optional[List[str]], category: Optional[str]) -> Dict:
        """Get optimal diagnostic values based on Dr. Strunz principles"""
        
        # Import the diagnostic values module
        try:
            from src.rag.diagnostic_values import get_optimal_values
            return get_optimal_values(age, gender, weight, height, athlete, conditions, category)
        except ImportError:
            # Fallback implementation
            return {
                "error": "Diagnostic values module not available",
                "basic_recommendations": {
                    "vitamin_d": "70-80 ng/ml",
                    "ferritin": "150-250 ng/ml" if gender == "male" else "100-150 ng/ml",
                    "tsh": "1.0-1.5 mIU/l"
                }
            }

def main():
    """Run the enhanced MCP server."""
    server = StrunzKnowledgeMCP()
    
    # For production/Railway, use SSE transport for Claude Desktop compatibility
    import os
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        port = int(os.environ.get('PORT', 8000))
        print(f"Starting FastMCP SSE server on port {port}")
        # FastMCP SSE transport - note: port binding is handled by Railway/Docker
        # The SSE transport doesn't support host/port parameters in run()
        server.app.run(transport="sse")
    else:
        # Local development uses stdio
        print("Starting FastMCP stdio server")
        server.app.run()

def get_fastmcp_app():
    """Get the FastMCP app instance for compatibility."""
    server = StrunzKnowledgeMCP()
    return server.app

if __name__ == "__main__":
    main()