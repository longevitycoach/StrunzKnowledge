# Comprehensive Test Plan - StrunzKnowledge MCP Server v0.9.0

## Overview

This document outlines the comprehensive testing strategy for the StrunzKnowledge MCP Server, covering all environments, user roles, and MCP capabilities with detailed input/output validation.

## Test Environments

### 1. Local Development Environment
- **Purpose**: Development and initial validation
- **Setup**: `python main.py` (auto-detects stdio transport)
- **URL**: Direct stdio connection or `http://localhost:8000`
- **Docker**: `docker build -t strunzknowledge:test .`

### 2. Docker Container Environment  
- **Purpose**: Production-like environment testing
- **Setup**: Docker build with unified requirements
- **Port**: 8001 (to avoid conflicts)
- **Validation**: Health checks, tool availability, performance

### 3. Railway Production Environment
- **Purpose**: Live production validation
- **URL**: https://strunz.up.railway.app/
- **Deployment**: Automatic via GitHub push
- **Monitoring**: Continuous health checks

## User Roles & Test Scenarios

### Role 1: Health Enthusiast 👨‍⚕️
**Profile**: Beginner seeking wellness optimization
**Goals**: Prevent disease, optimize wellness
**Journey**: Health assessment → Protocol creation → Progress tracking

#### Test Scenario: Complete Health Assessment Journey
```yaml
inputs:
  user_profile:
    age: 35
    gender: "male"
    symptoms: ["fatigue", "brain_fog", "low_energy"]
    goals: ["energy_optimization", "cognitive_enhancement"]
    activity_level: "moderate"
    dietary_preferences: ["low_carb"]

expected_outputs:
  health_assessment:
    risk_factors: ["vitamin_d_deficiency", "magnesium_deficiency"]
    recommendations: ["blood_work", "supplement_protocol"]
    timeline: "4-8_weeks_improvement"
  
  personalized_protocol:
    supplements: 
      - name: "Vitamin D3"
        dosage: "5000 IU"
        timing: "morning_with_fat"
      - name: "Magnesium Glycinate" 
        dosage: "400mg"
        timing: "evening"
    lifestyle:
      - "morning_sunlight_exposure"
      - "consistent_sleep_schedule"
    monitoring:
      - "energy_levels_daily"
      - "blood_work_8_weeks"
```

### Role 2: Medical Professional 👩‍⚕️
**Profile**: Evidence-based researcher seeking clinical insights
**Goals**: Patient recommendations, research validation
**Journey**: Literature search → Evidence analysis → Protocol validation

#### Test Scenario: Evidence-Based Research Journey
```yaml
inputs:
  research_query:
    topic: "vitamin_d_deficiency_autoimmune"
    evidence_level: "clinical_trials"
    patient_demographics: "adult_females_30_50"
    
expected_outputs:
  research_results:
    studies_found: ">= 10"
    evidence_quality: "peer_reviewed"
    contradictions: 
      - claim: "high_dose_vitamin_d_safe"
        counter_evidence: "hypercalcemia_risk"
    clinical_recommendations:
      dosage_range: "1000-4000_IU"
      monitoring_required: ["25_oh_vitamin_d", "calcium", "pth"]
      contraindications: ["sarcoidosis", "hyperparathyroidism"]
```

### Role 3: Biohacker 🧬
**Profile**: Advanced optimizer seeking cutting-edge protocols
**Goals**: Performance optimization, longevity enhancement
**Journey**: Biomarker analysis → Advanced protocols → Tracking optimization

#### Test Scenario: Advanced Optimization Journey
```yaml
inputs:
  optimization_request:
    biomarkers: 
      - name: "vitamin_d"
        current_value: "35_ng_ml"
        target_value: "60_ng_ml"
    goals: ["cognitive_enhancement", "immune_optimization"]
    current_stack: ["vitamin_d", "k2", "magnesium"]
    
expected_outputs:
  optimization_protocol:
    advanced_diagnostics:
      - "25_oh_vitamin_d"
      - "1_25_dihydroxy_vitamin_d" 
      - "vitamin_d_binding_protein"
    supplement_interactions:
      synergistic: ["vitamin_k2", "magnesium", "boron"]
      antagonistic: ["calcium_timing"]
    personalized_dosing:
      algorithm: "weight_based_calculation"
      starting_dose: "calculated_per_kg"
      titration_schedule: "monthly_increases"
```

### Role 4: Nutritionist 🥗
**Profile**: Professional creating client protocols
**Goals**: Evidence-based meal plans, supplement protocols
**Journey**: Client assessment → Meal planning → Protocol creation

#### Test Scenario: Professional Nutrition Planning
```yaml
inputs:
  client_profile:
    age: 45
    weight: "70kg"
    height: "165cm"  
    activity_level: "moderate"
    goals: ["weight_management", "metabolic_health"]
    restrictions: ["gluten_free", "dairy_free"]
    
expected_outputs:
  nutrition_protocol:
    macros:
      calories: "calculated_tdee"
      protein: "1.2-1.6g_per_kg"
      carbs: "100-150g"
      fat: "remaining_calories"
    meal_plan:
      duration: "7_days"
      recipes: ">= 21_meals"
      shopping_list: "categorized_by_section"
    supplement_protocol:
      evidence_based: true
      dosages: "research_backed"
      timing: "optimized_absorption"
```

## MCP Tool Test Matrix

### Knowledge & Search Tools

#### 1. knowledge_search
```yaml
test_cases:
  - input: {"query": "vitamin D deficiency symptoms", "max_results": 5}
    expected: {"results": "array", "sources": "dr_strunz_books", "relevance_score": ">0.8"}
  - input: {"query": "magnesium types comparison", "filters": ["supplements"]}
    expected: {"results": "comparative_analysis", "evidence_level": "clinical"}
```

#### 2. find_contradictions
```yaml
test_cases:
  - input: {"topic": "high dose vitamin C"}
    expected: {"contradictions": "array", "sources": "multiple", "confidence": "scored"}
```

#### 3. trace_topic_evolution
```yaml
test_cases:
  - input: {"topic": "intermittent fasting", "timeframe": "2010-2025"}
    expected: {"evolution": "chronological", "key_insights": "array", "trend_analysis": "object"}
```

### Protocol Creation Tools

#### 4. create_health_protocol
```yaml
test_cases:
  - input: {"condition": "metabolic syndrome", "approach": "nutrition_focused"}
    expected: {"protocol": "structured", "timeline": "defined", "monitoring": "measurable"}
```

#### 5. create_personalized_protocol
```yaml
test_cases:
  - input: {"health_profile": {"age": 40, "symptoms": ["fatigue"], "goals": ["energy"]}}
    expected: {"supplements": "array", "lifestyle": "array", "monitoring": "defined"}
```

### Analysis Tools

#### 6. analyze_supplement_stack
```yaml
test_cases:
  - input: {"supplements": ["vitamin_d", "magnesium", "b12"], "dosages": ["5000iu", "400mg", "1000mcg"]}
    expected: {"interactions": "analyzed", "recommendations": "optimized", "warnings": "identified"}
```

#### 7. compare_approaches
```yaml
test_cases:
  - input: {"topic": "vitamin D supplementation", "approaches": ["daily", "weekly_high_dose"]}
    expected: {"comparison": "evidence_based", "pros_cons": "balanced", "recommendation": "clear"}
```

### Assessment Tools

#### 8. assess_user_health_profile
```yaml
test_cases:
  - input: {"age": 35, "symptoms": ["fatigue", "brain_fog"], "goals": ["energy"]}
    expected: {"assessment": "comprehensive", "risk_factors": "identified", "recommendations": "actionable"}
```

#### 9. get_health_assessment_questions
```yaml
test_cases:
  - input: {"category": "cardiovascular"}
    expected: {"questions": "array", "scoring": "defined", "interpretation": "guidelines"}
```

### Calculation Tools

#### 10. nutrition_calculator
```yaml
test_cases:
  - input: {"age": 30, "weight": 70, "height": 175, "activity": "moderate", "goal": "maintenance"}
    expected: {"calories": "calculated", "macros": "balanced", "micronutrients": "essential"}
```

#### 11. get_optimal_diagnostic_values
```yaml
test_cases:
  - input: {"biomarker": "vitamin_d", "demographics": {"age": 40, "gender": "female"}}
    expected: {"optimal_range": "evidence_based", "units": "standard", "rationale": "referenced"}
```

### Community & Trend Tools

#### 12. get_community_insights
```yaml
test_cases:
  - input: {"topic": "keto diet"}
    expected: {"insights": "aggregated", "trends": "analyzed", "discussions": "summarized"}
```

#### 13. analyze_strunz_newsletter_evolution
```yaml
test_cases:
  - input: {"timeframe": "2020-2025", "topic": "immune_health"}
    expected: {"evolution": "tracked", "key_themes": "identified", "insights": "extracted"}
```

### Specialized Tools

#### 14. validate_health_claims
```yaml
test_cases:
  - input: {"claim": "Vitamin C prevents common cold"}
    expected: {"validation": "evidence_based", "confidence": "scored", "sources": "peer_reviewed"}
```

#### 15. track_supplement_interactions
```yaml
test_cases:
  - input: {"supplements": ["warfarin", "vitamin_k", "fish_oil"]}
    expected: {"interactions": "critical", "severity": "scored", "recommendations": "clinical"}
```

#### 16. generate_meal_plans
```yaml
test_cases:
  - input: {"preferences": ["mediterranean"], "restrictions": ["gluten_free"], "duration": "7_days"}
    expected: {"meals": "21_planned", "recipes": "detailed", "nutrition": "calculated"}
```

## Performance Benchmarks

### Response Time Requirements
- **Health Check**: < 200ms
- **Simple Tools** (biography, server info): < 1s
- **Search Operations**: < 3s
- **Complex Analysis**: < 10s
- **Protocol Generation**: < 15s

### Concurrency Requirements
- **Simultaneous Users**: 50+
- **Concurrent Requests**: 100+
- **Memory Usage**: < 2GB under load
- **CPU Usage**: < 80% average

### Reliability Requirements
- **Uptime**: 99.9%
- **Error Rate**: < 0.1%
- **Graceful Degradation**: Yes
- **Automatic Recovery**: < 30s

## Quality Assurance Checklist

### Functional Testing
- [ ] All 24+ MCP tools respond correctly
- [ ] Input validation handles edge cases
- [ ] Output format consistent across tools
- [ ] Error messages clear and actionable
- [ ] Authentication works (OAuth endpoints)

### Integration Testing  
- [ ] Claude Desktop connection (stdio)
- [ ] Claude.ai web connection (HTTP/SSE)
- [ ] MCP protocol compliance
- [ ] Cross-tool data consistency
- [ ] Session management

### Performance Testing
- [ ] Load testing (sustained traffic)
- [ ] Stress testing (peak capacity)
- [ ] Memory leak detection
- [ ] Response time validation
- [ ] Scalability limits identified

### Security Testing
- [ ] Input sanitization
- [ ] OAuth flow security
- [ ] Access control validation
- [ ] Dependency vulnerability scan
- [ ] Network security assessment

### Deployment Testing
- [ ] Local environment parity
- [ ] Docker container functionality
- [ ] Railway deployment success
- [ ] Environment variable handling
- [ ] Configuration management

## Test Automation Strategy

### Unit Tests
- Individual tool functionality
- Input validation logic
- Output format compliance
- Error handling paths
- Edge case coverage

### Integration Tests
- End-to-end user journeys
- Cross-tool interactions
- Protocol compliance
- Authentication flows
- Session persistence

### System Tests
- Full deployment validation
- Performance benchmarking
- Security scanning
- Reliability testing
- Recovery procedures

### Continuous Integration
- Automated test execution on push
- Multi-environment validation
- Performance regression detection
- Security vulnerability scanning
- Automated deployment validation

## Success Criteria

### Release Readiness Checklist
- [ ] 95%+ test pass rate across all environments
- [ ] All user journeys complete successfully
- [ ] Performance benchmarks met
- [ ] Security scan clean (no critical issues)
- [ ] Production deployment validated

### Quality Gates
- **Functional**: All MCP tools working
- **Performance**: Sub-5s response times
- **Reliability**: 99.9% uptime in testing
- **Security**: No critical vulnerabilities
- **Usability**: Clear error messages, good UX

This comprehensive test plan ensures thorough validation of the StrunzKnowledge MCP Server across all dimensions of quality, performance, and reliability.