"""
MCP Prompt Templates for Knowledge Activation
Structured prompts that guide users to discover and apply Dr. Strunz's knowledge
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class PromptCategory(Enum):
    """Categories of knowledge activation prompts"""
    DIAGNOSTIC = "diagnostic"  # Help identify health issues
    THERAPEUTIC = "therapeutic"  # Treatment protocols
    PREVENTIVE = "preventive"  # Prevention strategies
    OPTIMIZATION = "optimization"  # Performance enhancement
    EDUCATIONAL = "educational"  # Learning about topics
    COMMUNITY = "community"  # Community insights

@dataclass
class PromptTemplate:
    """Structured prompt template"""
    name: str
    category: PromptCategory
    description: str
    variables: List[str]
    template: str
    follow_up_templates: List[str]
    required_capabilities: List[str]
    example_values: Dict[str, str]

class KnowledgeActivationPrompts:
    """Manages prompt templates for knowledge activation"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize all prompt templates"""
        return {
            "health_assessment": PromptTemplate(
                name="Personal Health Assessment",
                category=PromptCategory.DIAGNOSTIC,
                description="Comprehensive health assessment based on symptoms and goals",
                variables=["symptoms", "age", "gender", "goals"],
                template="""Based on Dr. Strunz's knowledge, analyze this health profile:
                
Symptoms: {symptoms}
Age: {age}
Gender: {gender}
Health Goals: {goals}

Please provide:
1. Likely nutritional deficiencies based on symptoms
2. Recommended blood tests according to Dr. Strunz
3. Initial supplement recommendations
4. Lifestyle modifications
5. Relevant articles or forum discussions about similar cases""",
                follow_up_templates=["protocol_creation", "test_interpretation"],
                required_capabilities=["search_knowledge", "create_health_protocol"],
                example_values={
                    "symptoms": "fatigue, brain fog, cold hands",
                    "age": "45",
                    "gender": "female",
                    "goals": "increase energy, improve mental clarity"
                }
            ),
            
            "protocol_creation": PromptTemplate(
                name="Personalized Protocol Builder",
                category=PromptCategory.THERAPEUTIC,
                description="Create detailed supplement and lifestyle protocol",
                variables=["condition", "current_supplements", "restrictions", "budget"],
                template="""Create a Dr. Strunz-based protocol for:

Condition: {condition}
Current Supplements: {current_supplements}
Restrictions: {restrictions}
Monthly Budget: {budget}

Include:
1. Core supplements with specific brands/forms Dr. Strunz recommends
2. Dosages and timing (morning/evening)
3. Ramp-up schedule for beginners
4. Potential interactions to avoid
5. Expected timeline for results
6. Forum success stories with this protocol""",
                follow_up_templates=["protocol_optimization", "side_effect_management"],
                required_capabilities=["create_health_protocol", "analyze_supplement_stack"],
                example_values={
                    "condition": "chronic fatigue syndrome",
                    "current_supplements": "Vitamin D 2000 IU, Magnesium 200mg",
                    "restrictions": "vegetarian, sensitive stomach",
                    "budget": "€150"
                }
            ),
            
            "evolution_tracker": PromptTemplate(
                name="Knowledge Evolution Tracker",
                category=PromptCategory.EDUCATIONAL,
                description="Track how recommendations changed over time",
                variables=["topic", "start_year", "end_year"],
                template="""Trace the evolution of Dr. Strunz's recommendations on {topic} from {start_year} to {end_year}.

Show:
1. Initial stance in {start_year} (with source)
2. Key changes and when they occurred
3. Scientific discoveries that influenced changes
4. Current recommendation as of {end_year}
5. Forum discussions about these changes
6. Any contradictions and their explanations""",
                follow_up_templates=["contradiction_analysis", "scientific_backing"],
                required_capabilities=["trace_topic_evolution", "find_contradictions"],
                example_values={
                    "topic": "vitamin D dosage",
                    "start_year": "2005",
                    "end_year": "2025"
                }
            ),
            
            "community_wisdom": PromptTemplate(
                name="Community Experience Aggregator",
                category=PromptCategory.COMMUNITY,
                description="Aggregate community experiences on specific topics",
                variables=["supplement", "condition", "timeframe"],
                template="""Analyze forum discussions about {supplement} for {condition} over the past {timeframe}.

Provide:
1. Most common dosages used by community members
2. Reported benefits and timeline
3. Side effects and how users managed them
4. Best brands/forms according to users
5. Combination protocols that worked
6. Warning signs to watch for
7. Success rate based on forum reports""",
                follow_up_templates=["user_protocol_comparison", "troubleshooting_guide"],
                required_capabilities=["search_knowledge", "analyze_health_topic"],
                example_values={
                    "supplement": "CoQ10",
                    "condition": "statin-related muscle pain",
                    "timeframe": "2 years"
                }
            ),
            
            "optimization_guide": PromptTemplate(
                name="Performance Optimization Guide",
                category=PromptCategory.OPTIMIZATION,
                description="Optimize health for specific performance goals",
                variables=["goal", "current_fitness", "timeline", "constraints"],
                template="""Design a Dr. Strunz optimization protocol for:

Performance Goal: {goal}
Current Fitness: {current_fitness}
Timeline: {timeline}
Constraints: {constraints}

Create:
1. Supplement stack for this specific goal
2. Nutrition guidelines from Dr. Strunz's books
3. Training recommendations if applicable
4. Blood markers to track progress
5. Month-by-month progression plan
6. Forum examples of similar transformations""",
                follow_up_templates=["progress_tracker", "plateau_breaker"],
                required_capabilities=["create_health_protocol", "search_knowledge"],
                example_values={
                    "goal": "marathon in 6 months",
                    "current_fitness": "5k runner",
                    "timeline": "6 months",
                    "constraints": "limited to 4 training days/week"
                }
            ),
            
            "contradiction_resolver": PromptTemplate(
                name="Contradiction Analysis & Resolution",
                category=PromptCategory.EDUCATIONAL,
                description="Understand and resolve conflicting recommendations",
                variables=["topic", "source1", "source2"],
                template="""Analyze conflicting Dr. Strunz recommendations on {topic}:

Source 1: {source1}
Source 2: {source2}

Explain:
1. What each source recommends
2. Why the recommendations differ
3. Context that explains the contradiction
4. Which recommendation applies to which situation
5. Dr. Strunz's current stance
6. How the community handles this contradiction""",
                follow_up_templates=["contextual_application", "decision_framework"],
                required_capabilities=["find_contradictions", "search_knowledge"],
                example_values={
                    "topic": "protein intake",
                    "source1": "2010 book - max 1g/kg body weight",
                    "source2": "2023 article - 2g/kg for athletes"
                }
            )
        }
    
    def get_prompt_by_category(self, category: PromptCategory) -> List[PromptTemplate]:
        """Get all prompts for a specific category"""
        return [t for t in self.templates.values() if t.category == category]
    
    def get_prompt_flow(self, starting_prompt: str) -> List[PromptTemplate]:
        """Get a flow of prompts starting from a specific template"""
        flow = []
        current = self.templates.get(starting_prompt)
        
        if current:
            flow.append(current)
            # Add follow-up templates
            for follow_up_name in current.follow_up_templates:
                if follow_up_name in self.templates:
                    flow.append(self.templates[follow_up_name])
        
        return flow
    
    def fill_template(self, template_name: str, values: Dict[str, str]) -> str:
        """Fill a template with user-provided values"""
        template = self.templates.get(template_name)
        if not template:
            return ""
        
        filled = template.template
        for var in template.variables:
            if var in values:
                filled = filled.replace(f"{{{var}}}", values[var])
            else:
                # Use example value if not provided
                filled = filled.replace(f"{{{var}}}", template.example_values.get(var, f"[{var}]"))
        
        return filled
    
    def get_interactive_prompt_builder(self, template_name: str) -> Dict[str, Any]:
        """Get an interactive prompt builder for a template"""
        template = self.templates.get(template_name)
        if not template:
            return {}
        
        return {
            "template_name": template.name,
            "description": template.description,
            "category": template.category.value,
            "required_inputs": [
                {
                    "variable": var,
                    "example": template.example_values.get(var, ""),
                    "description": self._get_variable_description(var)
                }
                for var in template.variables
            ],
            "capabilities_used": template.required_capabilities,
            "next_steps": [
                {
                    "name": self.templates[t].name,
                    "description": self.templates[t].description
                }
                for t in template.follow_up_templates if t in self.templates
            ]
        }
    
    def _get_variable_description(self, variable: str) -> str:
        """Get description for a variable"""
        descriptions = {
            "symptoms": "List your current symptoms or health concerns",
            "age": "Your age (important for dosage recommendations)",
            "gender": "Biological sex (affects certain nutrient needs)",
            "goals": "What you want to achieve health-wise",
            "condition": "Specific health condition or diagnosis",
            "current_supplements": "Supplements you're already taking",
            "restrictions": "Dietary restrictions, allergies, or sensitivities",
            "budget": "Monthly budget for supplements",
            "topic": "Health topic to analyze",
            "supplement": "Specific supplement name",
            "timeframe": "Time period to analyze",
            "goal": "Specific performance or health goal",
            "current_fitness": "Your current fitness level",
            "timeline": "How long you have to achieve your goal",
            "constraints": "Any limitations or restrictions"
        }
        return descriptions.get(variable, f"Enter {variable}")

class MCPPromptHandler:
    """Handles MCP prompt requests"""
    
    def __init__(self):
        self.prompt_system = KnowledgeActivationPrompts()
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts"""
        prompts = []
        
        for category in PromptCategory:
            category_prompts = self.prompt_system.get_prompt_by_category(category)
            for template in category_prompts:
                prompts.append({
                    "name": template.name,
                    "description": template.description,
                    "category": category.value,
                    "arguments": [
                        {"name": var, "description": self.prompt_system._get_variable_description(var)}
                        for var in template.variables
                    ]
                })
        
        return prompts
    
    async def get_prompt(self, name: str, arguments: Dict[str, str]) -> Dict[str, Any]:
        """Get a specific prompt filled with arguments"""
        
        # Find template by name
        template = None
        for t in self.prompt_system.templates.values():
            if t.name == name:
                template = t
                break
        
        if not template:
            return {"error": f"Prompt '{name}' not found"}
        
        # Fill the template
        filled_prompt = self.prompt_system.fill_template(
            list(self.prompt_system.templates.keys())[list(self.prompt_system.templates.values()).index(template)],
            arguments
        )
        
        return {
            "messages": [
                {
                    "role": "user",
                    "content": filled_prompt
                }
            ],
            "metadata": {
                "category": template.category.value,
                "capabilities_required": template.required_capabilities,
                "follow_up_available": len(template.follow_up_templates) > 0
            }
        }