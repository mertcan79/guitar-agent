"""
Agent Validation and Testing Utilities
Ensures the agent works correctly and provides quality recommendations
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime

from ..knowledge.guitar_knowledge import GuitarKnowledgeBase

logger = logging.getLogger(__name__)

class AgentValidator:
    """Validates agent responses and recommendations"""
    
    @staticmethod
    def validate_search_params(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate search parameters"""
        errors = []
        
        # Check price range
        if params.get("min_price") and params.get("max_price"):
            if params["min_price"] > params["max_price"]:
                errors.append("Minimum price is greater than maximum price")
        
        # Check price reasonableness
        if params.get("max_price", 0) > 50000:
            errors.append("Maximum price seems unreasonably high")
        
        if params.get("min_price", 0) < 0:
            errors.append("Minimum price cannot be negative")
        
        # Validate guitar type
        valid_types = ["electric", "acoustic", "bass", "classical"]
        if params.get("guitar_type") and params["guitar_type"] not in valid_types:
            errors.append(f"Invalid guitar type: {params['guitar_type']}")
        
        # Validate skill level
        valid_levels = ["beginner", "intermediate", "advanced", "professional"]
        if params.get("skill_level") and params["skill_level"] not in valid_levels:
            errors.append(f"Invalid skill level: {params['skill_level']}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_recommendation(rec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single recommendation"""
        errors = []
        
        # Check required fields
        required = ["guitar_title", "price", "why_recommended"]
        for field in required:
            if field not in rec or not rec[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check price validity
        if rec.get("price"):
            if not isinstance(rec["price"], (int, float)) or rec["price"] <= 0:
                errors.append("Invalid price value")
        
        # Check match score
        if "match_score" in rec:
            if not 0 <= rec["match_score"] <= 1:
                errors.append("Match score must be between 0 and 1")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def score_recommendation_quality(rec: Dict[str, Any], user_requirements: Dict[str, Any]) -> Dict[str, float]:
        """Score the quality of a recommendation"""
        scores = {}
        
        # Price match score
        if user_requirements.get("budget") and rec.get("price"):
            budget = user_requirements["budget"]
            price = rec["price"]
            
            if price <= budget:
                scores["price_score"] = 1.0
            elif price <= budget * 1.2:
                scores["price_score"] = 0.8
            elif price <= budget * 1.5:
                scores["price_score"] = 0.5
            else:
                scores["price_score"] = 0.2
        
        # Brand match score
        if user_requirements.get("preferred_brands") and rec.get("guitar_title"):
            title_lower = rec["guitar_title"].lower()
            brand_match = any(
                brand.lower() in title_lower 
                for brand in user_requirements["preferred_brands"]
            )
            scores["brand_score"] = 1.0 if brand_match else 0.5
        
        # Explanation quality score
        if rec.get("why_recommended"):
            explanation_length = len(rec["why_recommended"])
            if explanation_length > 100:
                scores["explanation_score"] = 1.0
            elif explanation_length > 50:
                scores["explanation_score"] = 0.7
            else:
                scores["explanation_score"] = 0.4
        
        # Feature completeness score
        feature_count = sum([
            1 for key in ["pros", "cons", "best_for", "match_score"]
            if key in rec and rec[key]
        ])
        scores["completeness_score"] = feature_count / 4.0
        
        # Overall score
        if scores:
            scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores

class TestScenarios:
    """Test scenarios to validate agent behavior"""
    
    SCENARIOS = [
        {
            "name": "Beginner Blues Player",
            "query": "I'm a beginner looking for an electric guitar for blues, budget around $500",
            "expected": {
                "price_range": (300, 600),
                "guitar_types": ["Stratocaster", "Les Paul Special", "Epiphone"],
                "key_features": ["comfortable neck", "versatile", "good value"]
            }
        },
        {
            "name": "Artist Reference - Jimmy Page",
            "query": "I want something like Jimmy Page plays, around $1000",
            "expected": {
                "price_range": (800, 1200),
                "guitar_types": ["Les Paul", "SG", "Epiphone Les Paul"],
                "key_features": ["humbucker", "sustain", "rock tone"]
            }
        },
        {
            "name": "Metal Player",
            "query": "Need a metal guitar with active pickups, budget $1500",
            "expected": {
                "price_range": (1200, 1800),
                "guitar_types": ["Ibanez", "Jackson", "ESP", "Schecter"],
                "key_features": ["active pickups", "fast neck", "high output"]
            }
        },
        {
            "name": "Jazz Guitar",
            "query": "Looking for a jazz guitar, hollow body preferred, around $2000",
            "expected": {
                "price_range": (1600, 2400),
                "guitar_types": ["ES-335", "ES-175", "Ibanez", "Gretsch"],
                "key_features": ["hollow body", "warm tone", "smooth"]
            }
        },
        {
            "name": "Budget Constraint",
            "query": "Best electric guitar under $300 for a student",
            "expected": {
                "price_range": (150, 300),
                "guitar_types": ["Squier", "Yamaha", "Harley Benton"],
                "key_features": ["affordable", "reliable", "beginner-friendly"]
            }
        }
    ]
    
    @classmethod
    def run_scenario_test(cls, agent, scenario: Dict) -> Dict[str, Any]:
        """Run a test scenario and evaluate results"""
        
        result = {
            "scenario": scenario["name"],
            "query": scenario["query"],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Run agent
            recommendations = agent.find_guitars(scenario["query"])
            
            # Validate response
            if recommendations.recommendations:
                result["success"] = True
                result["recommendation_count"] = len(recommendations.recommendations)
                
                # Check price range
                prices = [r.get("price", 0) for r in recommendations.recommendations]
                avg_price = sum(prices) / len(prices) if prices else 0
                expected_min, expected_max = scenario["expected"]["price_range"]
                
                result["price_check"] = expected_min <= avg_price <= expected_max
                
                # Check guitar types
                titles = " ".join([
                    r.get("guitar_title", "").lower() 
                    for r in recommendations.recommendations
                ])
                
                type_matches = sum([
                    1 for guitar_type in scenario["expected"]["guitar_types"]
                    if guitar_type.lower() in titles
                ])
                
                result["type_match_rate"] = type_matches / len(scenario["expected"]["guitar_types"])
                
                # Check features mentioned
                all_text = " ".join([
                    r.get("why_recommended", "") + " ".join(r.get("pros", []))
                    for r in recommendations.recommendations
                ]).lower()
                
                feature_matches = sum([
                    1 for feature in scenario["expected"]["key_features"]
                    if feature.lower() in all_text
                ])
                
                result["feature_match_rate"] = feature_matches / len(scenario["expected"]["key_features"])
                
                # Overall score
                result["overall_score"] = (
                    (1.0 if result["price_check"] else 0.0) +
                    result["type_match_rate"] +
                    result["feature_match_rate"]
                ) / 3.0
                
            else:
                result["success"] = False
                result["error"] = "No recommendations generated"
                
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    @classmethod
    def run_all_tests(cls, agent) -> Dict[str, Any]:
        """Run all test scenarios"""
        
        results = {
            "test_time": datetime.now().isoformat(),
            "scenarios": []
        }
        
        for scenario in cls.SCENARIOS:
            logger.info(f"Running test scenario: {scenario['name']}")
            result = cls.run_scenario_test(agent, scenario)
            results["scenarios"].append(result)
        
        # Calculate overall statistics
        successful = [s for s in results["scenarios"] if s.get("success")]
        
        results["summary"] = {
            "total_scenarios": len(cls.SCENARIOS),
            "successful": len(successful),
            "failed": len(cls.SCENARIOS) - len(successful),
            "success_rate": len(successful) / len(cls.SCENARIOS) if cls.SCENARIOS else 0
        }
        
        if successful:
            avg_score = sum(s.get("overall_score", 0) for s in successful) / len(successful)
            results["summary"]["average_score"] = avg_score
        
        return results

class ExplainabilityAnalyzer:
    """Analyzes and improves agent explainability"""
    
    @staticmethod
    def analyze_explanation(explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of an explanation"""
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        # Count reasoning steps
        reasoning_steps = explanation.get("reasoning_steps", [])
        analysis["metrics"]["reasoning_depth"] = len(reasoning_steps)
        
        # Count tool uses
        tool_uses = explanation.get("tools_used", [])
        analysis["metrics"]["tools_used"] = len(tool_uses)
        
        # Analyze tool diversity
        unique_tools = set(t.get("tool") for t in tool_uses if t.get("tool"))
        analysis["metrics"]["tool_diversity"] = len(unique_tools)
        
        # Check for knowledge base usage
        knowledge_used = any(
            "knowledge" in str(step).lower() 
            for step in reasoning_steps
        )
        analysis["metrics"]["used_knowledge_base"] = knowledge_used
        
        # Score explanation quality
        score = 0
        if analysis["metrics"]["reasoning_depth"] >= 3:
            score += 0.3
        if analysis["metrics"]["tools_used"] >= 2:
            score += 0.3
        if analysis["metrics"]["tool_diversity"] >= 2:
            score += 0.2
        if knowledge_used:
            score += 0.2
        
        analysis["explanation_quality_score"] = score
        
        # Generate recommendations
        recommendations = []
        if analysis["metrics"]["reasoning_depth"] < 3:
            recommendations.append("Consider adding more reasoning steps")
        if not knowledge_used:
            recommendations.append("Utilize guitar knowledge base more")
        if analysis["metrics"]["tool_diversity"] < 2:
            recommendations.append("Use more diverse tools for better analysis")
        
        analysis["improvement_recommendations"] = recommendations
        
        return analysis
    
    @staticmethod
    def format_explanation_for_user(explanation: Dict[str, Any], reasoning_trace: List[str]) -> str:
        """Format explanation in user-friendly way"""
        
        formatted = "🤔 How I Found Your Perfect Guitar:\n\n"
        
        # Add reasoning trace
        if reasoning_trace:
            formatted += "My Thought Process:\n"
            for i, step in enumerate(reasoning_trace[:5], 1):
                formatted += f"{i}. {step}\n"
            formatted += "\n"
        
        # Add tool usage summary
        tools = explanation.get("tools_used", [])
        if tools:
            formatted += "Actions I Took:\n"
            tool_counts = {}
            for tool in tools:
                tool_name = tool.get("tool", "Unknown")
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            
            for tool, count in tool_counts.items():
                formatted += f"• {tool}: Used {count} time(s)\n"
            formatted += "\n"
        
        # Add decision summary
        if explanation.get("decisions"):
            formatted += "Final Decision:\n"
            formatted += "Based on my analysis, I've found guitars that match your needs.\n"
        
        return formatted