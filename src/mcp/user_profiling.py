#!/usr/bin/env python3
"""
User Profiling and Health Assessment Module for Dr. Strunz Knowledge Base
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class HealthStatus(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    CHRONIC_CONDITION = "chronic_condition"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    ATHLETE = "athlete"

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class UserHealthProfile:
    # Basic Information
    age: int
    gender: str
    height: float  # cm
    weight: float  # kg
    
    # Health Status
    current_health_status: HealthStatus
    medical_conditions: List[str]
    medications: List[str]
    allergies: List[str]
    
    # Lifestyle Factors
    activity_level: ActivityLevel
    sleep_hours: float
    stress_level: int  # 1-10
    diet_type: str  # omnivore, vegetarian, vegan, keto, etc.
    
    # Current Supplementation
    current_supplements: List[Dict[str, str]]  # name, dosage, frequency
    
    # Health Goals (ranked by priority)
    primary_goal: str
    secondary_goals: List[str]
    
    # Experience with Dr. Strunz
    strunz_experience: ExperienceLevel
    books_read: List[str]
    newsletter_subscriber: bool
    years_following: int
    
    # Biomarkers (if available)
    recent_blood_work: Optional[Dict[str, float]] = None
    genetic_data: Optional[Dict[str, str]] = None
    
    # Symptoms and Concerns
    current_symptoms: List[str] = None
    energy_level: int = 5  # 1-10
    cognitive_clarity: int = 5  # 1-10
    
    # Journey Preference
    preferred_approach: str = "balanced"  # aggressive, balanced, gentle
    time_commitment: str = "moderate"  # minimal, moderate, intensive

class UserProfiler:
    """Comprehensive user profiling system for personalized health guidance"""
    
    def __init__(self):
        self.assessment_questions = self._initialize_questions()
        self.role_mapping = self._initialize_role_mapping()
        
    def _initialize_questions(self) -> Dict[str, List[Dict]]:
        """Initialize comprehensive health assessment questions"""
        return {
            "basic_info": [
                {
                    "id": "age",
                    "question": "What is your age?",
                    "type": "number",
                    "validation": {"min": 18, "max": 100},
                    "required": True
                },
                {
                    "id": "gender",
                    "question": "What is your biological gender?",
                    "type": "choice",
                    "options": ["male", "female"],
                    "required": True
                },
                {
                    "id": "height",
                    "question": "What is your height in cm?",
                    "type": "number",
                    "validation": {"min": 100, "max": 250},
                    "required": True
                },
                {
                    "id": "weight",
                    "question": "What is your weight in kg?",
                    "type": "number",
                    "validation": {"min": 30, "max": 300},
                    "required": True
                }
            ],
            "health_status": [
                {
                    "id": "overall_health",
                    "question": "How would you rate your overall health?",
                    "type": "choice",
                    "options": {
                        "excellent": "Excellent - Rarely sick, high energy, optimal weight",
                        "good": "Good - Occasionally sick, decent energy, near ideal weight",
                        "moderate": "Moderate - Frequent minor illnesses, variable energy",
                        "poor": "Poor - Chronic issues, low energy, weight problems",
                        "chronic_condition": "Managing chronic condition(s)"
                    },
                    "required": True
                },
                {
                    "id": "medical_conditions",
                    "question": "Do you have any diagnosed medical conditions? (Select all that apply)",
                    "type": "multi_choice",
                    "options": [
                        "Diabetes Type 2",
                        "Cardiovascular Disease",
                        "Hypertension",
                        "Autoimmune Condition",
                        "Thyroid Disorder",
                        "Digestive Issues",
                        "Mental Health Condition",
                        "Cancer (current or history)",
                        "Metabolic Syndrome",
                        "Chronic Fatigue",
                        "None"
                    ],
                    "required": True
                },
                {
                    "id": "medications",
                    "question": "Are you currently taking any medications?",
                    "type": "text_list",
                    "placeholder": "List medications and dosages",
                    "required": False
                },
                {
                    "id": "symptoms",
                    "question": "Which symptoms are you currently experiencing? (Select all that apply)",
                    "type": "multi_choice",
                    "options": [
                        "Fatigue",
                        "Brain fog",
                        "Poor sleep",
                        "Digestive issues",
                        "Joint pain",
                        "Muscle weakness",
                        "Mood changes",
                        "Weight gain",
                        "Hair loss",
                        "Skin problems",
                        "Frequent infections",
                        "None"
                    ],
                    "required": True
                }
            ],
            "lifestyle": [
                {
                    "id": "activity_level",
                    "question": "How would you describe your physical activity level?",
                    "type": "choice",
                    "options": {
                        "sedentary": "Sedentary - Little to no exercise",
                        "lightly_active": "Lightly Active - Exercise 1-2 times/week",
                        "moderately_active": "Moderately Active - Exercise 3-4 times/week",
                        "very_active": "Very Active - Exercise 5-6 times/week",
                        "athlete": "Athlete - Training daily, competitive sports"
                    },
                    "required": True
                },
                {
                    "id": "sleep_hours",
                    "question": "How many hours of sleep do you average per night?",
                    "type": "number",
                    "validation": {"min": 3, "max": 12},
                    "required": True
                },
                {
                    "id": "stress_level",
                    "question": "Rate your average stress level (1-10, where 10 is extreme stress)",
                    "type": "scale",
                    "min": 1,
                    "max": 10,
                    "required": True
                },
                {
                    "id": "diet_type",
                    "question": "Which best describes your current diet?",
                    "type": "choice",
                    "options": [
                        "Standard/Mixed",
                        "Mediterranean",
                        "Low Carb/Keto",
                        "Vegetarian",
                        "Vegan",
                        "Paleo",
                        "Intermittent Fasting",
                        "Other"
                    ],
                    "required": True
                }
            ],
            "goals": [
                {
                    "id": "primary_goal",
                    "question": "What is your PRIMARY health goal?",
                    "type": "choice",
                    "options": [
                        "Increase energy levels",
                        "Improve cognitive function",
                        "Lose weight",
                        "Build muscle/strength",
                        "Manage chronic condition",
                        "Optimize longevity",
                        "Enhance athletic performance",
                        "Improve sleep quality",
                        "Reduce stress/anxiety",
                        "General health optimization"
                    ],
                    "required": True
                },
                {
                    "id": "secondary_goals",
                    "question": "Select any additional health goals (up to 3)",
                    "type": "multi_choice",
                    "max_selections": 3,
                    "options": [
                        "Better digestion",
                        "Clearer skin",
                        "Stronger immune system",
                        "Hormonal balance",
                        "Reduced inflammation",
                        "Better mood",
                        "Increased libido",
                        "Hair/nail health",
                        "Faster recovery",
                        "Disease prevention"
                    ],
                    "required": False
                }
            ],
            "strunz_experience": [
                {
                    "id": "familiarity",
                    "question": "How familiar are you with Dr. Strunz's approach?",
                    "type": "choice",
                    "options": {
                        "beginner": "New to Dr. Strunz - Just discovering",
                        "intermediate": "Some knowledge - Read a few articles/books",
                        "advanced": "Well-versed - Following protocols for 1+ years",
                        "expert": "Expert - Deep understanding, helping others"
                    },
                    "required": True
                },
                {
                    "id": "books_read",
                    "question": "Which Dr. Strunz books have you read? (Select all)",
                    "type": "multi_choice",
                    "options": [
                        "Die Amino-Revolution",
                        "Der Gen-Trick",
                        "Das Geheimnis der Gesundheit",
                        "Das Stress-weg-Buch",
                        "Blut - Die Geheimnisse unseres flüssigen Organs",
                        "Das neue Anti-Krebs-Programm",
                        "None yet"
                    ],
                    "required": True
                },
                {
                    "id": "newsletter_subscriber",
                    "question": "Do you subscribe to Dr. Strunz's newsletter?",
                    "type": "boolean",
                    "required": True
                }
            ],
            "supplementation": [
                {
                    "id": "current_supplements",
                    "question": "Which supplements are you currently taking? (Select all)",
                    "type": "multi_choice",
                    "options": [
                        "Vitamin D3",
                        "Omega-3",
                        "Magnesium",
                        "B-Complex",
                        "Vitamin C",
                        "Zinc",
                        "Multivitamin",
                        "Probiotics",
                        "Amino Acids",
                        "CoQ10",
                        "None"
                    ],
                    "required": True
                },
                {
                    "id": "supplement_details",
                    "question": "Please provide dosages for your key supplements",
                    "type": "text",
                    "placeholder": "e.g., Vitamin D3 4000 IU, Omega-3 2g",
                    "required": False
                }
            ],
            "biomarkers": [
                {
                    "id": "recent_bloodwork",
                    "question": "Have you had blood work done in the last 6 months?",
                    "type": "boolean",
                    "required": True
                },
                {
                    "id": "key_markers",
                    "question": "If yes, please enter key values (optional)",
                    "type": "biomarker_input",
                    "markers": [
                        {"name": "25(OH)D", "unit": "ng/ml", "optimal": "60-80"},
                        {"name": "Ferritin", "unit": "ng/ml", "optimal": "50-150"},
                        {"name": "hs-CRP", "unit": "mg/L", "optimal": "<0.5"},
                        {"name": "HbA1c", "unit": "%", "optimal": "<5.4"},
                        {"name": "TSH", "unit": "mIU/L", "optimal": "1.0-2.0"}
                    ],
                    "required": False
                }
            ],
            "commitment": [
                {
                    "id": "time_available",
                    "question": "How much time can you dedicate daily to health optimization?",
                    "type": "choice",
                    "options": {
                        "minimal": "15-30 minutes",
                        "moderate": "30-60 minutes",
                        "intensive": "60+ minutes"
                    },
                    "required": True
                },
                {
                    "id": "budget_range",
                    "question": "What's your monthly budget for supplements?",
                    "type": "choice",
                    "options": {
                        "basic": "€50-100",
                        "moderate": "€100-200",
                        "comprehensive": "€200-400",
                        "unlimited": "€400+"
                    },
                    "required": True
                },
                {
                    "id": "preferred_pace",
                    "question": "How would you like to approach changes?",
                    "type": "choice",
                    "options": {
                        "gentle": "Gentle - Gradual changes over time",
                        "balanced": "Balanced - Steady progress",
                        "aggressive": "Aggressive - Maximum results quickly"
                    },
                    "required": True
                }
            ]
        }
    
    def _initialize_role_mapping(self) -> Dict:
        """Map user profiles to appropriate roles and journeys"""
        return {
            "role_criteria": {
                "functional_expert": {
                    "indicators": ["expert", "chronic_condition", "helping_others"],
                    "experience": ["advanced", "expert"],
                    "goals": ["manage_chronic_condition", "general_optimization"]
                },
                "community_researcher": {
                    "indicators": ["research_interest", "trend_tracking"],
                    "experience": ["intermediate", "advanced", "expert"],
                    "goals": ["general_optimization", "disease_prevention"]
                },
                "longevity_enthusiast": {
                    "indicators": ["longevity_focus", "anti_aging"],
                    "experience": ["intermediate", "advanced"],
                    "goals": ["optimize_longevity", "disease_prevention"]
                },
                "strunz_fan": {
                    "indicators": ["multiple_books", "newsletter_subscriber"],
                    "experience": ["advanced", "expert"],
                    "goals": ["general_optimization", "optimize_longevity"]
                },
                "health_optimizer": {
                    "indicators": ["performance_focus", "data_driven"],
                    "experience": ["intermediate", "advanced"],
                    "goals": ["enhance_athletic_performance", "increase_energy"]
                }
            }
        }
    
    def assess_user(self, responses: Dict) -> UserHealthProfile:
        """Create comprehensive user health profile from assessment responses"""
        profile = UserHealthProfile(
            age=responses["age"],
            gender=responses["gender"],
            height=responses["height"],
            weight=responses["weight"],
            current_health_status=HealthStatus(responses["overall_health"]),
            medical_conditions=responses.get("medical_conditions", []),
            medications=responses.get("medications", []),
            allergies=responses.get("allergies", []),
            activity_level=ActivityLevel(responses["activity_level"]),
            sleep_hours=responses["sleep_hours"],
            stress_level=responses["stress_level"],
            diet_type=responses["diet_type"],
            current_supplements=self._parse_supplements(responses.get("supplement_details", "")),
            primary_goal=responses["primary_goal"],
            secondary_goals=responses.get("secondary_goals", []),
            strunz_experience=ExperienceLevel(responses["familiarity"]),
            books_read=responses.get("books_read", []),
            newsletter_subscriber=responses.get("newsletter_subscriber", False),
            years_following=responses.get("years_following", 0),
            current_symptoms=responses.get("symptoms", []),
            preferred_approach=responses.get("preferred_pace", "balanced"),
            time_commitment=responses.get("time_available", "moderate")
        )
        
        # Add biomarkers if available
        if responses.get("recent_bloodwork") and responses.get("key_markers"):
            profile.recent_blood_work = responses["key_markers"]
            
        return profile
    
    def determine_user_role(self, profile: UserHealthProfile) -> str:
        """Determine the most appropriate user role based on profile"""
        scores = {
            "functional_expert": 0,
            "community_researcher": 0,
            "longevity_enthusiast": 0,
            "strunz_fan": 0,
            "health_optimizer": 0
        }
        
        # Score based on experience level
        if profile.strunz_experience in [ExperienceLevel.ADVANCED, ExperienceLevel.EXPERT]:
            scores["functional_expert"] += 2
            scores["strunz_fan"] += 3
        
        # Score based on goals
        if "optimize_longevity" in [profile.primary_goal] + profile.secondary_goals:
            scores["longevity_enthusiast"] += 4
        
        if "enhance_athletic_performance" in [profile.primary_goal] + profile.secondary_goals:
            scores["health_optimizer"] += 4
            
        # Score based on current status
        if profile.current_health_status == HealthStatus.CHRONIC_CONDITION:
            scores["functional_expert"] += 3
            
        # Score based on engagement
        if len(profile.books_read) > 3:
            scores["strunz_fan"] += 3
            
        if profile.newsletter_subscriber and profile.years_following > 2:
            scores["strunz_fan"] += 2
            
        # Return role with highest score
        return max(scores, key=scores.get)
    
    def create_personalized_journey(self, profile: UserHealthProfile, role: str) -> Dict:
        """Create a personalized health journey based on profile and role"""
        journey = {
            "role": role,
            "phase": self._determine_phase(profile),
            "immediate_priorities": self._get_immediate_priorities(profile),
            "protocol_recommendations": self._get_protocol_recommendations(profile, role),
            "learning_path": self._create_learning_path(profile, role),
            "milestone_targets": self._set_milestone_targets(profile),
            "supplement_strategy": self._design_supplement_strategy(profile),
            "lifestyle_modifications": self._suggest_lifestyle_changes(profile),
            "monitoring_plan": self._create_monitoring_plan(profile)
        }
        
        return journey
    
    def _determine_phase(self, profile: UserHealthProfile) -> str:
        """Determine current phase of health journey"""
        if profile.strunz_experience == ExperienceLevel.BEGINNER:
            return "Foundation Building"
        elif profile.current_health_status in [HealthStatus.POOR, HealthStatus.CHRONIC_CONDITION]:
            return "Health Restoration"
        elif profile.primary_goal in ["enhance_athletic_performance", "optimize_longevity"]:
            return "Optimization Phase"
        else:
            return "Maintenance & Enhancement"
    
    def _get_immediate_priorities(self, profile: UserHealthProfile) -> List[str]:
        """Identify top 3-5 immediate priorities"""
        priorities = []
        
        # Critical health issues first
        if profile.current_health_status == HealthStatus.CHRONIC_CONDITION:
            priorities.append("Stabilize chronic condition with targeted protocols")
            
        # Address severe deficiencies
        if profile.energy_level <= 3:
            priorities.append("Restore energy through mitochondrial support")
            
        if profile.sleep_hours < 6:
            priorities.append("Optimize sleep quality and duration")
            
        if profile.stress_level >= 8:
            priorities.append("Implement stress reduction protocols")
            
        # Add goal-specific priorities
        if profile.primary_goal == "lose_weight":
            priorities.append("Initiate metabolic optimization protocol")
            
        return priorities[:5]
    
    def _get_protocol_recommendations(self, profile: UserHealthProfile, role: str) -> Dict:
        """Generate specific protocol recommendations"""
        protocols = {
            "immediate": [],
            "week_2_4": [],
            "month_2_3": [],
            "long_term": []
        }
        
        # Immediate protocols (Week 1)
        if profile.energy_level <= 5:
            protocols["immediate"].append({
                "name": "Energy Foundation Protocol",
                "components": ["Vitamin D3 4000 IU", "Magnesium 400mg", "B-Complex"],
                "timing": "Morning with breakfast"
            })
            
        # Progressive protocols based on role
        if role == "health_optimizer":
            protocols["week_2_4"].append({
                "name": "Performance Enhancement Stack",
                "components": ["Amino acids 10g pre-workout", "CoQ10 200mg", "PQQ 20mg"],
                "timing": "Pre and post workout"
            })
            
        return protocols
    
    def _create_learning_path(self, profile: UserHealthProfile, role: str) -> List[Dict]:
        """Create personalized learning path"""
        path = []
        
        # Beginners start with fundamentals
        if profile.strunz_experience == ExperienceLevel.BEGINNER:
            path.append({
                "week": 1,
                "resource": "Das Geheimnis der Gesundheit",
                "focus": "Chapters 1-3: Foundation principles"
            })
            
        # Role-specific learning
        if role == "longevity_enthusiast":
            path.append({
                "week": 2,
                "resource": "Der Gen-Trick",
                "focus": "Epigenetic optimization chapters"
            })
            
        return path
    
    def _set_milestone_targets(self, profile: UserHealthProfile) -> List[Dict]:
        """Set realistic milestone targets"""
        milestones = []
        
        # 30-day milestone
        milestones.append({
            "timeframe": "30 days",
            "targets": [
                "Energy level increase by 2 points",
                "Establish consistent supplement routine",
                "Complete foundation reading"
            ],
            "measurements": ["Energy self-assessment", "Compliance tracking"]
        })
        
        # 90-day milestone
        milestones.append({
            "timeframe": "90 days",
            "targets": [
                "Optimize key biomarkers",
                "Achieve primary health goal progress",
                "Master core protocols"
            ],
            "measurements": ["Blood work", "Symptom diary", "Performance metrics"]
        })
        
        return milestones
    
    def _design_supplement_strategy(self, profile: UserHealthProfile) -> Dict:
        """Design personalized supplement strategy"""
        strategy = {
            "foundation": [],
            "optimization": [],
            "advanced": [],
            "timing_guide": {}
        }
        
        # Foundation for everyone
        strategy["foundation"] = [
            {"name": "Vitamin D3", "dose": "4000-6000 IU", "timing": "morning"},
            {"name": "Magnesium", "dose": "400-600mg", "timing": "evening"},
            {"name": "Omega-3", "dose": "2-3g EPA/DHA", "timing": "with meals"}
        ]
        
        # Add based on symptoms and goals
        if "fatigue" in profile.current_symptoms:
            strategy["optimization"].append(
                {"name": "CoQ10", "dose": "200mg", "timing": "morning"}
            )
            
        return strategy
    
    def _suggest_lifestyle_changes(self, profile: UserHealthProfile) -> List[Dict]:
        """Suggest specific lifestyle modifications"""
        changes = []
        
        if profile.sleep_hours < 7:
            changes.append({
                "area": "Sleep",
                "recommendation": "Establish 10pm bedtime routine",
                "protocol": "Magnesium 400mg + L-Theanine 200mg 1hr before bed"
            })
            
        if profile.stress_level > 6:
            changes.append({
                "area": "Stress",
                "recommendation": "Daily 10-min breathing practice",
                "protocol": "4-7-8 breathing technique + adaptogenic herbs"
            })
            
        return changes
    
    def _create_monitoring_plan(self, profile: UserHealthProfile) -> Dict:
        """Create comprehensive monitoring plan"""
        return {
            "daily": ["Energy level (1-10)", "Sleep quality", "Supplement compliance"],
            "weekly": ["Weight", "Exercise performance", "Symptom diary"],
            "monthly": ["Progress photos", "Measurement review", "Protocol adjustments"],
            "quarterly": ["Comprehensive blood work", "Biomarker analysis", "Goal reassessment"]
        }
    
    def _parse_supplements(self, supplement_text: str) -> List[Dict[str, str]]:
        """Parse supplement details from text input"""
        supplements = []
        if supplement_text:
            lines = supplement_text.split(',')
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    supplements.append({
                        "name": ' '.join(parts[:-1]),
                        "dosage": parts[-1]
                    })
        return supplements
    
    def generate_assessment_report(self, profile: UserHealthProfile, journey: Dict) -> str:
        """Generate comprehensive assessment report"""
        report = f"""
# Personalized Health Assessment Report

## Profile Summary
- **Age**: {profile.age} years
- **Gender**: {profile.gender}
- **BMI**: {profile.weight / (profile.height/100)**2:.1f}
- **Health Status**: {profile.current_health_status.value}
- **Primary Goal**: {profile.primary_goal}
- **Dr. Strunz Experience**: {profile.strunz_experience.value}

## Assigned Role: {journey['role']}
## Current Phase: {journey['phase']}

## Immediate Priorities
{chr(10).join(f"1. {p}" for p in journey['immediate_priorities'])}

## Recommended Protocol Timeline

### Week 1-2: Foundation
{self._format_protocols(journey['protocol_recommendations']['immediate'])}

### Week 3-4: Building
{self._format_protocols(journey['protocol_recommendations']['week_2_4'])}

### Month 2-3: Optimization
{self._format_protocols(journey['protocol_recommendations']['month_2_3'])}

## Supplement Strategy
### Foundation Stack
{self._format_supplements(journey['supplement_strategy']['foundation'])}

### Optimization Stack
{self._format_supplements(journey['supplement_strategy']['optimization'])}

## Lifestyle Modifications
{self._format_lifestyle(journey['lifestyle_modifications'])}

## Monitoring Plan
- **Daily**: {', '.join(journey['monitoring_plan']['daily'])}
- **Weekly**: {', '.join(journey['monitoring_plan']['weekly'])}
- **Monthly**: {', '.join(journey['monitoring_plan']['monthly'])}
- **Quarterly**: {', '.join(journey['monitoring_plan']['quarterly'])}

## Learning Path
{self._format_learning_path(journey['learning_path'])}

## Success Milestones
{self._format_milestones(journey['milestone_targets'])}

---
*This assessment is personalized based on your unique profile and goals. 
Regular reassessment is recommended as you progress on your health journey.*
"""
        return report
    
    def _format_protocols(self, protocols: List[Dict]) -> str:
        """Format protocol recommendations"""
        if not protocols:
            return "No specific protocols for this phase"
        
        formatted = []
        for p in protocols:
            formatted.append(f"**{p['name']}**\n  - {', '.join(p['components'])}\n  - Timing: {p['timing']}")
        return "\n\n".join(formatted)
    
    def _format_supplements(self, supplements: List[Dict]) -> str:
        """Format supplement recommendations"""
        if not supplements:
            return "No supplements in this category"
            
        formatted = []
        for s in supplements:
            formatted.append(f"- **{s['name']}**: {s['dose']} ({s['timing']})")
        return "\n".join(formatted)
    
    def _format_lifestyle(self, changes: List[Dict]) -> str:
        """Format lifestyle modifications"""
        if not changes:
            return "No immediate lifestyle changes needed"
            
        formatted = []
        for c in changes:
            formatted.append(f"**{c['area']}**\n- {c['recommendation']}\n- Protocol: {c['protocol']}")
        return "\n\n".join(formatted)
    
    def _format_learning_path(self, path: List[Dict]) -> str:
        """Format learning path"""
        if not path:
            return "Custom learning path to be determined"
            
        formatted = []
        for p in path:
            formatted.append(f"**Week {p['week']}**: {p['resource']}\n- Focus: {p['focus']}")
        return "\n\n".join(formatted)
    
    def _format_milestones(self, milestones: List[Dict]) -> str:
        """Format milestone targets"""
        if not milestones:
            return "Milestones to be set after initial assessment"
            
        formatted = []
        for m in milestones:
            targets = "\n  - ".join(m['targets'])
            measurements = ", ".join(m['measurements'])
            formatted.append(f"**{m['timeframe']}**\n  - {targets}\n  - Measurements: {measurements}")
        return "\n\n".join(formatted)