"""
Extended Contextual Samples for Dr. Strunz Knowledge Base
50 carefully crafted samples covering all knowledge areas
"""

from typing import List
from dataclasses import dataclass

@dataclass
class ExtendedSampleQuery:
    """Extended sample query with full metadata"""
    id: str
    query: str
    query_de: str  # German version
    category: str
    capability: str
    expected_insights: List[str]
    difficulty: str
    tags: List[str]
    follow_up_queries: List[str]

def get_all_contextual_samples() -> List[ExtendedSampleQuery]:
    """Get all 50 contextual samples"""
    
    return [
        # === BEGINNER SAMPLES (1-15) ===
        
        # Basic Nutrition
        ExtendedSampleQuery(
            id="sample_001",
            query="What are the most important vitamins I should take daily?",
            query_de="Welche sind die wichtigsten Vitamine, die ich täglich nehmen sollte?",
            category="basic_nutrition",
            capability="search_knowledge",
            expected_insights=["Vitamin D3", "Magnesium", "Omega-3", "B-Complex", "Vitamin C"],
            difficulty="beginner",
            tags=["vitamins", "daily", "basics"],
            follow_up_queries=["What dosages does Dr. Strunz recommend?", "When should I take each vitamin?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_002",
            query="How can I boost my energy naturally?",
            query_de="Wie kann ich meine Energie natürlich steigern?",
            category="energy_optimization",
            capability="create_health_protocol",
            expected_insights=["CoQ10", "B vitamins", "Iron", "Mitochondrial support", "Exercise"],
            difficulty="beginner",
            tags=["energy", "fatigue", "vitality"],
            follow_up_queries=["What supplements help mitochondria?", "How long before I see results?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_003",
            query="What does Dr. Strunz say about protein intake?",
            query_de="Was sagt Dr. Strunz über Proteinaufnahme?",
            category="basic_nutrition",
            capability="search_knowledge",
            expected_insights=["1-2g per kg body weight", "Quality over quantity", "Amino acids", "Timing"],
            difficulty="beginner",
            tags=["protein", "nutrition", "basics"],
            follow_up_queries=["Which protein sources are best?", "What about vegetarian protein?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_004",
            query="How much water should I drink daily?",
            query_de="Wie viel Wasser sollte ich täglich trinken?",
            category="basic_health",
            capability="search_knowledge",
            expected_insights=["30-40ml per kg body weight", "Quality matters", "Mineral content", "Timing"],
            difficulty="beginner",
            tags=["hydration", "water", "basics"],
            follow_up_queries=["What type of water is best?", "Should I add minerals to water?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_005",
            query="What supplements help with sleep?",
            query_de="Welche Nahrungsergänzungsmittel helfen beim Schlafen?",
            category="sleep_health",
            capability="search_knowledge",
            expected_insights=["Magnesium glycinate", "L-Theanine", "Melatonin", "GABA", "5-HTP"],
            difficulty="beginner",
            tags=["sleep", "insomnia", "relaxation"],
            follow_up_queries=["What's the best magnesium form for sleep?", "Is melatonin safe long-term?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_006",
            query="How do I start with low-carb diet?",
            query_de="Wie fange ich mit Low-Carb-Diät an?",
            category="diet",
            capability="search_knowledge",
            expected_insights=["Gradual reduction", "Protein focus", "Good fats", "Vegetable increase"],
            difficulty="beginner",
            tags=["low-carb", "diet", "weight-loss"],
            follow_up_queries=["What can I eat for breakfast?", "How many carbs per day?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_007",
            query="What's Dr. Strunz's view on coffee?",
            query_de="Was ist Dr. Strunz' Meinung zu Kaffee?",
            category="lifestyle",
            capability="search_knowledge",
            expected_insights=["Moderation", "Quality matters", "Timing important", "Individual tolerance"],
            difficulty="beginner",
            tags=["coffee", "caffeine", "lifestyle"],
            follow_up_queries=["How much coffee is okay?", "Best time to drink coffee?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_008",
            query="Which blood tests should I get regularly?",
            query_de="Welche Bluttests sollte ich regelmäßig machen?",
            category="diagnostics",
            capability="search_knowledge",
            expected_insights=["Vitamin D", "B12", "Ferritin", "Thyroid panel", "Inflammation markers"],
            difficulty="beginner",
            tags=["blood-tests", "diagnostics", "prevention"],
            follow_up_queries=["What are optimal ranges?", "How often should I test?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_009",
            query="What helps with muscle cramps?",
            query_de="Was hilft bei Muskelkrämpfen?",
            category="symptoms",
            capability="search_knowledge",
            expected_insights=["Magnesium", "Potassium", "Calcium", "Hydration", "B vitamins"],
            difficulty="beginner",
            tags=["cramps", "muscles", "minerals"],
            follow_up_queries=["Which magnesium form is best?", "How much potassium daily?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_010",
            query="How can I strengthen my immune system?",
            query_de="Wie kann ich mein Immunsystem stärken?",
            category="immunity",
            capability="create_health_protocol",
            expected_insights=["Vitamin D", "Vitamin C", "Zinc", "Selenium", "Gut health"],
            difficulty="beginner",
            tags=["immune", "prevention", "health"],
            follow_up_queries=["What dosage for prevention?", "What about probiotics?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_011",
            query="What causes hair loss according to Dr. Strunz?",
            query_de="Was verursacht Haarausfall laut Dr. Strunz?",
            category="symptoms",
            capability="search_knowledge",
            expected_insights=["Iron deficiency", "B vitamins", "Zinc", "Protein", "Thyroid"],
            difficulty="beginner",
            tags=["hair", "deficiency", "symptoms"],
            follow_up_queries=["Which tests for hair loss?", "Best supplements for hair?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_012",
            query="How do I reduce inflammation naturally?",
            query_de="Wie reduziere ich Entzündungen natürlich?",
            category="inflammation",
            capability="search_knowledge",
            expected_insights=["Omega-3", "Curcumin", "Diet changes", "Antioxidants", "Exercise"],
            difficulty="beginner",
            tags=["inflammation", "chronic", "natural"],
            follow_up_queries=["Best omega-3 sources?", "How much curcumin daily?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_013",
            query="What's the best time to take vitamins?",
            query_de="Was ist die beste Zeit für Vitamine?",
            category="supplementation",
            capability="search_knowledge",
            expected_insights=["Fat-soluble with meals", "B vitamins morning", "Magnesium evening", "Iron empty stomach"],
            difficulty="beginner",
            tags=["timing", "supplements", "absorption"],
            follow_up_queries=["Can I take all vitamins together?", "What about interactions?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_014",
            query="How can I improve my concentration?",
            query_de="Wie kann ich meine Konzentration verbessern?",
            category="cognitive",
            capability="search_knowledge",
            expected_insights=["B vitamins", "Omega-3", "Iron", "Blood sugar stability", "Sleep"],
            difficulty="beginner",
            tags=["focus", "brain", "concentration"],
            follow_up_queries=["What about nootropics?", "Best brain foods?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_015",
            query="What helps with joint pain?",
            query_de="Was hilft bei Gelenkschmerzen?",
            category="pain_management",
            capability="search_knowledge",
            expected_insights=["Glucosamine", "MSM", "Omega-3", "Vitamin D", "Movement"],
            difficulty="beginner",
            tags=["joints", "pain", "arthritis"],
            follow_up_queries=["How long for glucosamine to work?", "Best exercises for joints?"]
        ),
        
        # === INTERMEDIATE SAMPLES (16-35) ===
        
        ExtendedSampleQuery(
            id="sample_016",
            query="What does the forum say about CoQ10 dosage for heart health?",
            query_de="Was sagt das Forum über CoQ10-Dosierung für Herzgesundheit?",
            category="community_wisdom",
            capability="search_knowledge",
            expected_insights=["100-300mg daily", "Ubiquinol preferred", "User experiences", "Side effects"],
            difficulty="intermediate",
            tags=["forum", "CoQ10", "heart", "dosage"],
            follow_up_queries=["Which brands do users recommend?", "Any negative experiences?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_017",
            query="Compare Dr. Strunz's cholesterol approach with conventional medicine",
            query_de="Vergleiche Dr. Strunz' Cholesterin-Ansatz mit Schulmedizin",
            category="controversy",
            capability="find_contradictions",
            expected_insights=["Statin criticism", "Natural alternatives", "HDL importance", "Inflammation focus"],
            difficulty="intermediate",
            tags=["cholesterol", "controversy", "comparison"],
            follow_up_queries=["What about familial hypercholesterolemia?", "Success stories without statins?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_018",
            query="Create a supplement protocol for a 45-year-old woman with fatigue",
            query_de="Erstelle ein Supplement-Protokoll für 45-jährige Frau mit Müdigkeit",
            category="protocols",
            capability="create_health_protocol",
            expected_insights=["Iron status check", "B12", "Thyroid support", "Mitochondrial nutrients"],
            difficulty="intermediate",
            tags=["protocol", "fatigue", "women", "personalized"],
            follow_up_queries=["What if she's vegetarian?", "Hormone considerations?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_019",
            query="How has Dr. Strunz's vitamin D recommendation changed from 2010 to 2025?",
            query_de="Wie hat sich Dr. Strunz' Vitamin-D-Empfehlung von 2010 bis 2025 geändert?",
            category="evolution",
            capability="trace_topic_evolution",
            expected_insights=["Dosage increase", "Testing emphasis", "Co-factors added", "Personalization"],
            difficulty="intermediate",
            tags=["evolution", "vitamin-d", "timeline"],
            follow_up_queries=["Why did recommendations change?", "What's the current optimal range?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_020",
            query="Analyze supplement interactions for: Magnesium, Iron, Zinc, Calcium",
            query_de="Analysiere Supplement-Wechselwirkungen für: Magnesium, Eisen, Zink, Kalzium",
            category="interactions",
            capability="analyze_supplement_stack",
            expected_insights=["Timing separation", "Absorption competition", "Synergies", "Best schedule"],
            difficulty="intermediate",
            tags=["interactions", "minerals", "timing"],
            follow_up_queries=["Can I take magnesium and calcium together?", "Best gap between iron and zinc?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_021",
            query="What are the most discussed topics in the fitness forum section?",
            query_de="Was sind die meistdiskutierten Themen im Fitness-Forum?",
            category="community_trends",
            capability="analyze_health_topic",
            expected_insights=["Protein timing", "Recovery", "Supplements for athletes", "Training frequency"],
            difficulty="intermediate",
            tags=["forum", "fitness", "trends"],
            follow_up_queries=["What supplements do athletes prefer?", "Common training mistakes discussed?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_022",
            query="Find contradictions in Dr. Strunz's carbohydrate recommendations",
            query_de="Finde Widersprüche in Dr. Strunz' Kohlenhydrat-Empfehlungen",
            category="contradictions",
            capability="find_contradictions",
            expected_insights=["Low-carb evolution", "Athletic exceptions", "Context matters", "Individual variation"],
            difficulty="intermediate",
            tags=["carbs", "contradictions", "diet"],
            follow_up_queries=["When are carbs recommended?", "What about endurance athletes?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_023",
            query="What's Dr. Strunz's protocol for chronic inflammation markers?",
            query_de="Was ist Dr. Strunz' Protokoll für chronische Entzündungsmarker?",
            category="protocols",
            capability="search_knowledge",
            expected_insights=["CRP reduction", "Omega-3 ratio", "Antioxidants", "Lifestyle factors"],
            difficulty="intermediate",
            tags=["inflammation", "protocols", "biomarkers"],
            follow_up_queries=["Target CRP levels?", "How long to see improvement?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_024",
            query="Compare book recommendations vs forum experiences for depression",
            query_de="Vergleiche Buch-Empfehlungen mit Forum-Erfahrungen bei Depression",
            category="mental_health",
            capability="search_knowledge",
            expected_insights=["Nutrient approach", "User testimonials", "Supplement combinations", "Timeline"],
            difficulty="intermediate",
            tags=["depression", "mental-health", "comparison"],
            follow_up_queries=["Most successful protocols?", "Side effects reported?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_025",
            query="What blood values indicate mitochondrial dysfunction?",
            query_de="Welche Blutwerte zeigen mitochondriale Dysfunktion?",
            category="diagnostics",
            capability="search_knowledge",
            expected_insights=["Lactate/pyruvate ratio", "CoQ10 levels", "Organic acids", "ATP markers"],
            difficulty="intermediate",
            tags=["mitochondria", "blood-tests", "diagnostics"],
            follow_up_queries=["How to improve mitochondrial function?", "Which supplements help?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_026",
            query="Track the evolution of Dr. Strunz's cancer prevention approach",
            query_de="Verfolge die Entwicklung von Dr. Strunz' Krebspräventions-Ansatz",
            category="evolution",
            capability="trace_topic_evolution",
            expected_insights=["Vitamin D emphasis", "Immune focus", "Metabolic approach", "Latest research"],
            difficulty="intermediate",
            tags=["cancer", "prevention", "evolution"],
            follow_up_queries=["Key supplements for prevention?", "Lifestyle factors emphasized?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_027",
            query="What do forum users say about B12 forms and absorption?",
            query_de="Was sagen Forum-Nutzer über B12-Formen und Absorption?",
            category="community_wisdom",
            capability="search_knowledge",
            expected_insights=["Methylcobalamin preferred", "Sublingual vs injection", "Absorption issues", "Dosing"],
            difficulty="intermediate",
            tags=["B12", "forum", "absorption"],
            follow_up_queries=["Best B12 for vegans?", "Signs of deficiency discussed?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_028",
            query="Create a pre-surgery supplement protocol for optimal healing",
            query_de="Erstelle ein Prä-OP Supplement-Protokoll für optimale Heilung",
            category="protocols",
            capability="create_health_protocol",
            expected_insights=["Vitamin C", "Zinc", "Protein", "Stop blood thinners", "Immune support"],
            difficulty="intermediate",
            tags=["surgery", "healing", "protocol"],
            follow_up_queries=["Post-surgery protocol?", "When to stop supplements?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_029",
            query="Analyze thyroid optimization beyond standard TSH testing",
            query_de="Analysiere Schilddrüsen-Optimierung jenseits Standard-TSH",
            category="thyroid",
            capability="search_knowledge",
            expected_insights=["fT3, fT4 importance", "Reverse T3", "Selenium", "Iodine controversy"],
            difficulty="intermediate",
            tags=["thyroid", "hormones", "optimization"],
            follow_up_queries=["Optimal ranges for fT3?", "Hashimoto's protocol?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_030",
            query="What's the forum consensus on intermittent fasting benefits?",
            query_de="Was ist der Forum-Konsens zu Intervallfasten-Vorteilen?",
            category="community_wisdom",
            capability="search_knowledge",
            expected_insights=["16:8 popular", "Weight loss results", "Energy improvements", "Adaptation period"],
            difficulty="intermediate",
            tags=["fasting", "forum", "weight-loss"],
            follow_up_queries=["Best fasting schedule?", "Who shouldn't fast?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_031",
            query="Compare Dr. Strunz's approach to diabetes with ADA guidelines",
            query_de="Vergleiche Dr. Strunz' Diabetes-Ansatz mit ADA-Richtlinien",
            category="controversy",
            capability="find_contradictions",
            expected_insights=["Carb restriction", "Supplement use", "Exercise emphasis", "Medication views"],
            difficulty="intermediate",
            tags=["diabetes", "comparison", "guidelines"],
            follow_up_queries=["Success stories with low-carb?", "When are meds necessary?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_032",
            query="What's Dr. Strunz's view on bio-identical hormone replacement?",
            query_de="Was ist Dr. Strunz' Sicht auf bioidentische Hormonersatztherapie?",
            category="hormones",
            capability="search_knowledge",
            expected_insights=["Natural first", "Testing important", "Individual approach", "Risk assessment"],
            difficulty="intermediate",
            tags=["hormones", "menopause", "anti-aging"],
            follow_up_queries=["Natural hormone boosters?", "When to consider HRT?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_033",
            query="Analyze gut health protocol for IBS according to forum experiences",
            query_de="Analysiere Darmgesundheits-Protokoll für Reizdarm laut Forum",
            category="gut_health",
            capability="search_knowledge",
            expected_insights=["Probiotics strains", "L-Glutamine", "Elimination diets", "Success timelines"],
            difficulty="intermediate",
            tags=["IBS", "gut", "forum"],
            follow_up_queries=["Best probiotic strains?", "FODMAP experiences?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_034",
            query="Track omega-3 recommendation changes in Dr. Strunz's books",
            query_de="Verfolge Omega-3-Empfehlungsänderungen in Dr. Strunz' Büchern",
            category="evolution",
            capability="trace_topic_evolution",
            expected_insights=["Dosage increases", "EPA/DHA ratios", "Quality emphasis", "Testing added"],
            difficulty="intermediate",
            tags=["omega-3", "evolution", "books"],
            follow_up_queries=["Current optimal dose?", "Best omega-3 sources?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_035",
            query="What supplement stack helps with ADHD symptoms in adults?",
            query_de="Welcher Supplement-Stack hilft bei ADHS-Symptomen bei Erwachsenen?",
            category="mental_health",
            capability="search_knowledge",
            expected_insights=["Omega-3", "Magnesium", "B vitamins", "Iron status", "Amino acids"],
            difficulty="intermediate",
            tags=["ADHD", "mental", "supplements"],
            follow_up_queries=["Dosages for ADHD?", "Lifestyle factors?"]
        ),
        
        # === ADVANCED SAMPLES (36-50) ===
        
        ExtendedSampleQuery(
            id="sample_036",
            query="Analyze all contradictions in vitamin K2 recommendations across sources",
            query_de="Analysiere alle Widersprüche in Vitamin K2-Empfehlungen über alle Quellen",
            category="deep_analysis",
            capability="find_contradictions",
            expected_insights=["MK-7 vs MK-4", "Dosage variations", "D3 combination", "Safety concerns"],
            difficulty="advanced",
            tags=["K2", "contradictions", "comprehensive"],
            follow_up_queries=["Resolution of contradictions?", "Current best practice?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_037",
            query="Create a comprehensive longevity protocol based on all Dr. Strunz sources",
            query_de="Erstelle ein umfassendes Langlebigkeits-Protokoll basierend auf allen Dr. Strunz Quellen",
            category="longevity",
            capability="create_health_protocol",
            expected_insights=["Telomere support", "Mitochondria", "Inflammation", "Hormones", "Lifestyle"],
            difficulty="advanced",
            tags=["longevity", "anti-aging", "comprehensive"],
            follow_up_queries=["Age-specific modifications?", "Cost optimization?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_038",
            query="Map the complete evolution of Dr. Strunz's autoimmune disease approach",
            query_de="Kartiere die komplette Evolution von Dr. Strunz' Autoimmunkrankheits-Ansatz",
            category="evolution",
            capability="trace_topic_evolution",
            expected_insights=["Gut focus addition", "Vitamin D emphasis", "Molecular approach", "Protocol changes"],
            difficulty="advanced",
            tags=["autoimmune", "evolution", "comprehensive"],
            follow_up_queries=["Disease-specific protocols?", "Success rate changes?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_039",
            query="Compare all forum discussions about statin side effects and solutions",
            query_de="Vergleiche alle Forum-Diskussionen über Statin-Nebenwirkungen und Lösungen",
            category="community_analysis",
            capability="analyze_health_topic",
            expected_insights=["Muscle pain solutions", "CoQ10 protocols", "Alternative approaches", "Success stories"],
            difficulty="advanced",
            tags=["statins", "forum", "side-effects"],
            follow_up_queries=["Most effective solutions?", "Doctor cooperation strategies?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_040",
            query="Design a molecular medicine approach to metabolic syndrome",
            query_de="Entwerfe einen molekularmedizinischen Ansatz für metabolisches Syndrom",
            category="complex_conditions",
            capability="create_health_protocol",
            expected_insights=["Multi-target approach", "Insulin sensitivity", "Inflammation", "Mitochondria"],
            difficulty="advanced",
            tags=["metabolic", "molecular", "syndrome"],
            follow_up_queries=["Biomarker tracking?", "Timeline for reversal?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_041",
            query="Analyze the scientific evolution behind Dr. Strunz's protein recommendations",
            query_de="Analysiere die wissenschaftliche Evolution hinter Dr. Strunz' Protein-Empfehlungen",
            category="scientific_analysis",
            capability="trace_topic_evolution",
            expected_insights=["Research citations", "Paradigm shifts", "Athletic influence", "Aging considerations"],
            difficulty="advanced",
            tags=["protein", "science", "evolution"],
            follow_up_queries=["Latest research integration?", "Future direction predictions?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_042",
            query="Create a troubleshooting guide for non-responders to vitamin D supplementation",
            query_de="Erstelle einen Troubleshooting-Guide für Non-Responder bei Vitamin-D-Supplementierung",
            category="troubleshooting",
            capability="create_health_protocol",
            expected_insights=["Absorption factors", "Co-factor needs", "Genetic variants", "Testing protocols"],
            difficulty="advanced",
            tags=["vitamin-d", "troubleshooting", "non-responders"],
            follow_up_queries=["VDR polymorphisms?", "Maximum safe doses?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_043",
            query="Map all neurotransmitter optimization strategies across books and forums",
            query_de="Kartiere alle Neurotransmitter-Optimierungsstrategien über Bücher und Foren",
            category="neuroscience",
            capability="analyze_health_topic",
            expected_insights=["Amino acid protocols", "Cofactor requirements", "Testing methods", "Balance strategies"],
            difficulty="advanced",
            tags=["neurotransmitters", "brain", "optimization"],
            follow_up_queries=["Serotonin vs dopamine focus?", "Testing availability?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_044",
            query="Analyze all conflicting views on iron supplementation for athletes",
            query_de="Analysiere alle widersprüchlichen Ansichten zur Eisensupplementierung für Athleten",
            category="sports_nutrition",
            capability="find_contradictions",
            expected_insights=["Performance benefits", "Oxidative stress", "Testing importance", "Gender differences"],
            difficulty="advanced",
            tags=["iron", "athletes", "contradictions"],
            follow_up_queries=["Ferritin targets for athletes?", "Hepcidin considerations?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_045",
            query="Create a comprehensive methylation support protocol with genetic considerations",
            query_de="Erstelle ein umfassendes Methylierungs-Support-Protokoll mit genetischen Überlegungen",
            category="genetics",
            capability="create_health_protocol",
            expected_insights=["MTHFR variants", "B vitamin forms", "Methyl donors", "Detox support"],
            difficulty="advanced",
            tags=["methylation", "genetics", "MTHFR"],
            follow_up_queries=["Testing recommendations?", "Overmethylation signs?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_046",
            query="Track the integration of epigenetics into Dr. Strunz's recommendations",
            query_de="Verfolge die Integration von Epigenetik in Dr. Strunz' Empfehlungen",
            category="cutting_edge",
            capability="trace_topic_evolution",
            expected_insights=["Gene expression focus", "Lifestyle emphasis", "Nutrient timing", "Future medicine"],
            difficulty="advanced",
            tags=["epigenetics", "genetics", "evolution"],
            follow_up_queries=["Practical applications?", "Testing availability?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_047",
            query="Analyze forum success stories for reversing pre-diabetes naturally",
            query_de="Analysiere Forum-Erfolgsgeschichten zur natürlichen Umkehr von Prädiabetes",
            category="success_analysis",
            capability="analyze_health_topic",
            expected_insights=["Common protocols", "Timeline patterns", "Key supplements", "Lifestyle changes"],
            difficulty="advanced",
            tags=["pre-diabetes", "success", "forum"],
            follow_up_queries=["Failure patterns?", "Maintenance strategies?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_048",
            query="Design a molecular approach to cognitive decline prevention",
            query_de="Entwerfe einen molekularen Ansatz zur Prävention kognitiven Abbaus",
            category="brain_health",
            capability="create_health_protocol",
            expected_insights=["Multi-modal approach", "Neuroprotection", "Metabolic support", "Inflammation control"],
            difficulty="advanced",
            tags=["cognitive", "prevention", "aging"],
            follow_up_queries=["Early biomarkers?", "Genetic risk factors?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_049",
            query="Compare all approaches to histamine intolerance across sources",
            query_de="Vergleiche alle Ansätze zu Histaminintoleranz über alle Quellen",
            category="food_intolerance",
            capability="analyze_health_topic",
            expected_insights=["DAO support", "Low histamine diet", "Gut healing", "Supplement protocols"],
            difficulty="advanced",
            tags=["histamine", "intolerance", "comprehensive"],
            follow_up_queries=["Testing methods?", "Recovery timeline?"]
        ),
        
        ExtendedSampleQuery(
            id="sample_050",
            query="Create the ultimate biohacking protocol combining all Dr. Strunz principles",
            query_de="Erstelle das ultimative Biohacking-Protokoll mit allen Dr. Strunz Prinzipien",
            category="biohacking",
            capability="create_health_protocol",
            expected_insights=["Optimization hierarchy", "Testing schedule", "Progressive implementation", "Personalization"],
            difficulty="advanced",
            tags=["biohacking", "optimization", "comprehensive"],
            follow_up_queries=["Cost-benefit analysis?", "Risk assessment?"]
        )
    ]