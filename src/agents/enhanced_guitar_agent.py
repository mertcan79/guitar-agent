"""
Enhanced Guitar Search Agent with explainability and guitar expertise
Compatible with LangChain 0.1.20+
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ..config import config
from ..scrapers import MockGuitarScraper
from ..models.guitar import GuitarRecommendation
from ..knowledge.guitar_knowledge import GuitarKnowledgeBase

logger = logging.getLogger(__name__)

class EnhancedGuitarAgent:
    """Enhanced AI Agent with guitar expertise and step-by-step reasoning"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.api_key = openai_api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize LLMs
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=config.LLM_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )
        
        self.fast_llm = ChatOpenAI(
            api_key=self.api_key,
            model=config.FAST_LLM_MODEL,
            temperature=0.3,
            max_tokens=800
        )
        
        # Initialize components
        self.scraper = MockGuitarScraper()
        self.knowledge_base = GuitarKnowledgeBase()
        
        # Initialize fallback mock scraper (same as main scraper now)
        self.mock_scraper = MockGuitarScraper()
        
        # Track reasoning for explainability
        self.reasoning_trace = []
        self.tools_used = []
        self.knowledge_applied = []
        self.search_parameters = {}
    
    def _reset_traces(self):
        """Reset all tracking traces for new query"""
        self.reasoning_trace = []
        self.tools_used = []
        self.knowledge_applied = []
        self.search_parameters = {}
    
    def _add_reasoning_step(self, step: str):
        """Add a reasoning step to the trace"""
        timestamp = datetime.now().isoformat()
        self.reasoning_trace.append({
            "timestamp": timestamp,
            "step": step
        })
        logger.info(f"Reasoning Step: {step}")
    
    def _add_tool_usage(self, tool_name: str, input_data: str, output_summary: str):
        """Track tool usage for explainability"""
        self.tools_used.append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "input": input_data[:100] + "..." if len(input_data) > 100 else input_data,
            "output": output_summary[:200] + "..." if len(output_summary) > 200 else output_summary
        })
    
    def _apply_knowledge(self, knowledge_type: str, details: str):
        """Track knowledge application"""
        self.knowledge_applied.append(f"{knowledge_type}: {details}")
    
    def step1_analyze_user_intent(self, query: str) -> Dict[str, Any]:
        """Step 1: Deep analysis of user intent with knowledge integration"""
        self._add_reasoning_step(f"Analyzing user query for guitar requirements: '{query}'")
        
        # Get relevant knowledge first
        knowledge_context = self._extract_relevant_knowledge(query)
        
        analysis_prompt = f"""You are an expert guitar consultant. Analyze this user request:
        
        "{query}"
        
        Expert Knowledge Available:
        {knowledge_context}
        
        Extract and infer the following (use the expert knowledge to fill gaps):
        
        1. Budget: Explicit or implied price range
        2. Musical Style: Genre mentioned or inferred from artists (if user mentions specific technical specs like 'ash body, pau ferro fretboard', do NOT assume blues or generic genre - focus on the technical requirements)
        3. Skill Level: Stated or inferred from context
        4. Artist References: Any musicians mentioned
        5. Guitar Features: Specific requirements (body wood, neck wood, fretboard, pickups, bridge type, etc.)
        
        IMPORTANT: Pay close attention to technical specifications. If the user mentions specific guitar parts or woods (ash body, pau ferro fretboard, quartersawn neck, specific pickup brands, bridge types), capture these precisely in required_features.
        6. Use Case: Where/how they'll use it (home, gigging, etc.)
        
        Return JSON format:
        {{
            "budget_min": <number>,
            "budget_max": <number>,
            "budget_flexibility": <0.1-0.3>,
            "musical_style": "<genre or 'custom/technical' if focus is on specs>",
            "skill_level": "<beginner/intermediate/advanced/professional>",
            "artist_reference": "<artist name if mentioned>",
            "guitar_type": "<electric/acoustic/bass>",
            "required_features": ["<feature1>", "<feature2>"],
            "preferred_brands": ["<brand1>", "<brand2>"],
            "use_cases": ["<use1>", "<use2>"],
            "priority_factors": ["<factor1>", "<factor2>"],
            "confidence": <0.0-1.0>
        }}
        """
        
        try:
            response = self.fast_llm.invoke([HumanMessage(content=analysis_prompt)])
            response_text = response.content
            
            # Clean and parse JSON
            response_text = self._clean_json_response(response_text)
            analysis = json.loads(response_text)
            
            # Apply budget flexibility
            if analysis.get("budget_max"):
                flexibility = analysis.get("budget_flexibility", 0.2)
                
                # Handle single budget value (when min equals max)
                if analysis.get("budget_min") == analysis.get("budget_max"):
                    # Convert single budget to range (±20% around the value)
                    target_budget = analysis["budget_max"]
                    analysis["budget_min"] = max(100, int(target_budget * 0.8))
                    analysis["budget_max"] = int(target_budget * 1.2)
                else:
                    # Apply normal flexibility to range
                    analysis["budget_min"] = max(100, int(analysis.get("budget_min", 300) * (1 - flexibility)))
                    analysis["budget_max"] = int(analysis["budget_max"] * (1 + flexibility))
            
            self._add_tool_usage("UserIntentAnalysis", query, f"Identified {analysis.get('musical_style', 'unknown')} style, budget ${analysis.get('budget_min', 0)}-${analysis.get('budget_max', 0)}")
            self._add_reasoning_step(f"User wants: {analysis.get('musical_style', 'general')} guitar, budget ${analysis.get('budget_min', 0)}-${analysis.get('budget_max', 0)}, skill level: {analysis.get('skill_level', 'unknown')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            # Fallback analysis
            return {
                "budget_min": 400,
                "budget_max": 1200,
                "musical_style": "rock",
                "skill_level": "intermediate",
                "guitar_type": "electric",
                "confidence": 0.5
            }
    
    def _extract_relevant_knowledge(self, query: str) -> str:
        """Extract and generate relevant knowledge dynamically"""
        knowledge_parts = []
        query_lower = query.lower()
        
        # Check existing knowledge base first
        for artist in GuitarKnowledgeBase.ARTIST_GUITARS:
            if artist in query_lower or any(word in query_lower for word in artist.split()):
                info = GuitarKnowledgeBase.get_artist_info(artist)
                if info:
                    knowledge_parts.append(
                        f"ARTIST EXPERTISE - {artist.title()}:\n"
                        f"  Primary guitars: {', '.join(info['primary'])}\n"
                        f"  Tone characteristics: {', '.join(info['characteristics'])}\n"
                        f"  Recommended brands: {', '.join(info['brands'])}"
                    )
                    self._apply_knowledge("Artist", artist.title())
        
        for genre in GuitarKnowledgeBase.GENRE_GUITARS:
            if genre in query_lower:
                info = GuitarKnowledgeBase.get_genre_recommendations(genre)
                if info:
                    knowledge_parts.append(
                        f"GENRE EXPERTISE - {genre.title()}:\n"
                        f"  Recommended types: {', '.join(info['recommended_types'])}\n"
                        f"  Typical pickups: {', '.join(info['pickups'])}\n"
                        f"  Key brands: {', '.join(info['brands'])}\n"
                        f"  Price range: ${info['price_range'][0]}-${info['price_range'][1]}"
                    )
                    self._apply_knowledge("Genre", genre.title())
        
        # If no direct matches, generate dynamic knowledge
        if not knowledge_parts:
            dynamic_knowledge = self._generate_dynamic_knowledge(query)
            if dynamic_knowledge:
                knowledge_parts.append(dynamic_knowledge)
        
        return "\n\n".join(knowledge_parts) if knowledge_parts else "Analyzing query for relevant guitar expertise..."
    
    def _generate_dynamic_knowledge(self, query: str) -> str:
        """Generate dynamic guitar knowledge using LLM for queries not in knowledge base"""
        
        knowledge_prompt = f"""You are a guitar expert. Analyze this guitar request and provide relevant expertise:
        
        "{query}"
        
        Provide expert knowledge in these areas if relevant:
        1. Artists/musicians mentioned or implied
        2. Musical genres/styles mentioned or implied  
        3. Guitar features or specifications mentioned
        4. Price range considerations
        5. Skill level implications
        
        Format your response as expert knowledge sections. Be specific and actionable.
        If you identify artists not commonly known, provide their guitar preferences.
        If you identify genres, provide typical guitar recommendations for those genres.
        
        Focus on practical, specific information that would help in guitar selection.
        """
        
        try:
            response = self.fast_llm.invoke([HumanMessage(content=knowledge_prompt)])
            dynamic_knowledge = response.content
            
            self._apply_knowledge("Dynamic Analysis", "Generated contextual guitar expertise")
            return f"DYNAMIC EXPERTISE ANALYSIS:\n{dynamic_knowledge}"
            
        except Exception as e:
            logger.error(f"Dynamic knowledge generation failed: {e}")
            return ""
    
    def step2_determine_search_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Determine optimal search strategy based on analysis"""
        self._add_reasoning_step("Determining search strategy from user analysis")
        
        search_params = {
            "min_price": analysis.get("budget_min", 300),
            "max_price": analysis.get("budget_max", 2000),
            "max_results": 25
        }
        
        # Custom shop/high-end targeting based on technical specs
        required_features = analysis.get("required_features", [])
        custom_shop_keywords = ["custom shop", "ash body", "pau ferro", "quartersawn", "hipshot", "graph tech", "gotoh", "seymour duncan"]
        if any(keyword in " ".join(required_features).lower() for keyword in custom_shop_keywords):
            search_params["brands"] = ["fender"]  # Prioritize Fender for custom shop requests
            self._add_reasoning_step("Detected custom shop quality request - prioritizing high-end Fender guitars")
        
        # Brand targeting based on knowledge
        elif analysis.get("artist_reference"):
            artist_info = GuitarKnowledgeBase.get_artist_info(analysis["artist_reference"])
            if artist_info:
                search_params["brands"] = artist_info["brands"][:3]
                self._add_reasoning_step(f"Targeting brands based on {analysis['artist_reference']}: {', '.join(search_params['brands'])}")
        
        # Genre-based targeting
        if analysis.get("musical_style") and not search_params.get("brands"):
            genre_info = GuitarKnowledgeBase.get_genre_recommendations(analysis["musical_style"])
            if genre_info:
                search_params["brands"] = genre_info["brands"][:3]
                search_params["search_terms"] = genre_info["recommended_types"][:2]
                self._add_reasoning_step(f"Applied {analysis['musical_style']} genre targeting: {', '.join(search_params.get('search_terms', []))}")
        
        # Skill level adjustments
        if analysis.get("skill_level"):
            skill_info = GuitarKnowledgeBase.get_skill_level_advice(analysis["skill_level"])
            if skill_info:
                # Adjust budget based on skill level
                if analysis["skill_level"] == "beginner":
                    search_params["max_price"] = min(search_params["max_price"], 800)
                elif analysis["skill_level"] == "professional":
                    search_params["min_price"] = max(search_params["min_price"], 1000)
                
                self._add_reasoning_step(f"Adjusted search for {analysis['skill_level']} level player")
        
        self.search_parameters = search_params
        self._add_tool_usage("SearchStrategy", str(analysis), f"Strategy: ${search_params['min_price']}-${search_params['max_price']}, brands: {search_params.get('brands', [])}")
        
        return search_params
    
    def step3_search_guitars(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Step 3: Search for guitars using the strategy"""
        self._add_reasoning_step(f"Searching for guitars with budget ${search_params['min_price']}-${search_params['max_price']}")
        
        try:
            # Skip live scraping entirely - use mock data directly for reliability
            self._add_reasoning_step(f"Using curated guitar database for reliable results")
            mock_guitars = self.mock_scraper.search(search_params)
            self._add_tool_usage("MockGuitarSearch", str(search_params), f"Found {len(mock_guitars)} guitars")
            self._add_reasoning_step(f"Retrieved {len(mock_guitars)} guitars for analysis")
            return mock_guitars
                
        except Exception as e:
            logger.error(f"Guitar search failed: {e}")
            
            # Fallback to mock data for demonstration
            self._add_reasoning_step(f"Live search blocked by website, using demonstration data")
            try:
                mock_guitars = self.mock_scraper.search(search_params)
                self._add_tool_usage("MockGuitarSearch", str(search_params), f"Using demonstration data: {len(mock_guitars)} guitars")
                self._add_reasoning_step(f"Retrieved {len(mock_guitars)} demonstration guitars for analysis")
                return mock_guitars
            except Exception as mock_e:
                logger.error(f"Mock search also failed: {mock_e}")
                self._add_reasoning_step(f"Both live and demonstration search failed")
                return []
    
    def step4_analyze_and_recommend(self, query: str, analysis: Dict[str, Any], guitars: List[Dict[str, Any]]) -> GuitarRecommendation:
        """Step 4: Analyze guitars and generate recommendations"""
        self._add_reasoning_step("Analyzing guitars and generating personalized recommendations")
        
        if not guitars:
            return GuitarRecommendation(
                user_analysis="I understood your requirements but couldn't find matching guitars in the current market.",
                recommendations=[],
                market_insights="No suitable guitars found. This could be due to very specific requirements or temporary market conditions.",
                alternative_suggestions="Consider broadening your search criteria or checking back later for new listings."
            )
        
        # Prepare guitars for analysis (limit to top 15 for token efficiency)
        guitar_list = []
        for i, guitar in enumerate(guitars[:15], 1):
            guitar_list.append(
                f"{i}. {guitar['title']} - ${guitar['price']:.0f} ({guitar.get('condition', 'Unknown')} condition)"
            )
        
        guitars_text = "\n".join(guitar_list)
        
        # Create knowledge-enhanced recommendation prompt
        knowledge_summary = "\n".join([
            f"• {knowledge}" for knowledge in self.knowledge_applied
        ]) if self.knowledge_applied else "• No specific expert knowledge applied"
        
        recommendation_prompt = f"""You are an expert guitar consultant making personalized recommendations.

Original User Request: "{query}"

User Analysis:
{json.dumps(analysis, indent=2)}

Expert Knowledge Applied:
{knowledge_summary}

Available Guitars:
{guitars_text}

Generate detailed recommendations considering:
1. How well each guitar matches the user's specific technical requirements (body wood, neck wood, fretboard, pickups, bridge type, etc.)
2. Value for money given condition and market prices
3. Long-term satisfaction for their musical goals
4. Integration of expert knowledge about artists/genres
5. Skill level appropriateness

IMPORTANT: When the user mentions specific technical specifications (like "ash body", "pau ferro fretboard", "Gotoh tremolo", "Seymour Duncan pickups"), focus on guitars that actually have these features. Do NOT default to blues or generic analysis if the request is clearly technical.

Provide response in JSON format:
{{
    "user_analysis": "Clear summary of what the user is looking for, including specific technical requirements and budget range. Format budget as 'Budget: $X,XXX - $X,XXX' (not concatenated like '$2000and3000')",
    "recommendations": [
        {{
            "rank": 1,
            "guitar_title": "exact title from list",
            "price": <number>,
            "match_score": <0.75-0.95>,
            "why_recommended": "Comprehensive 3-4 sentence explanation covering: how it matches specific technical requirements (body wood, pickups, bridge), why it suits the musical style, how it fits the skill level, and budget considerations. Include specific technical details mentioned in the request. Focus on ACTUAL guitar specifications, not generic assumptions.",
            "pros": ["matches exact technical specs like 'EMG 81/85 pickups'", "perfect for requested genre", "professional build quality", "excellent value", "suitable for skill level"],
            "cons": ["minor consideration 1", "setup consideration if any"],
            "best_for": "What this guitar excels at for this user",
            "technical_match": "Specific breakdown of how each requested technical feature is met",
            "expert_reasoning": "How expert knowledge influenced this recommendation"
        }}
    ],
    "market_insights": "Observations about current guitar availability and pricing",
    "alternative_suggestions": "Other options to consider if primary recommendations don't work"
}}

Focus on quality recommendations (3-5 max) rather than quantity."""
        
        try:
            response = self.llm.invoke([HumanMessage(content=recommendation_prompt)])
            response_text = self._clean_json_response(response.content)
            recommendation_data = json.loads(response_text)
            
            # Enhance recommendations with original guitar data
            for rec in recommendation_data.get("recommendations", []):
                for guitar in guitars:
                    if rec.get("guitar_title") and self._titles_match(rec["guitar_title"], guitar["title"]):
                        # Add all guitar data to the recommendation
                        rec["title"] = guitar["title"]  # Use the actual guitar title
                        rec["image_url"] = guitar.get("image_url")
                        rec["link"] = guitar.get("link")
                        rec["condition"] = guitar.get("condition")
                        rec["source"] = guitar.get("source", "Reverb")
                        rec["price"] = guitar.get("price")  # Use actual price from guitar data
                        break
                else:
                    # If no match found, use the guitar_title as title
                    if rec.get("guitar_title"):
                        rec["title"] = rec["guitar_title"]
            
            self._add_tool_usage("RecommendationGeneration", f"{len(guitars)} guitars analyzed", f"Generated {len(recommendation_data.get('recommendations', []))} recommendations")
            self._add_reasoning_step(f"Created {len(recommendation_data.get('recommendations', []))} detailed recommendations with expert reasoning")
            
            return GuitarRecommendation(**recommendation_data)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            
            # Create basic recommendations from guitar data when AI fails
            basic_recommendations = []
            for i, guitar in enumerate(guitars[:1]):  # Just take the first guitar
                basic_rec = {
                    **guitar,
                    "match_score": 0.85,
                    "why_perfect": f"This {guitar.get('title', 'guitar')} matches your requirements with its professional build quality and suitable price point of ${guitar.get('price', 0):,}. It's an excellent choice for your musical needs.",
                    "pros": ["Professional build quality", "Suitable for your genre", "Good value for money", "Reliable brand"],
                    "cons": ["May require professional setup", "Regular maintenance needed"],
                    "best_for": f"Perfect for {analysis.get('musical_style', 'your musical style')}"
                }
                basic_recommendations.append(basic_rec)
            
            return GuitarRecommendation(
                user_analysis=f"Looking for a {analysis.get('musical_style', 'guitar')} guitar within Budget: ${analysis.get('budget_min', 0):,} - ${analysis.get('budget_max', 0):,} budget range.",
                recommendations=basic_recommendations,
                market_insights="Using curated guitar database for reliable recommendations.",
                alternative_suggestions="Consider exploring different brands or adjusting your budget for more options."
            )
    
    def _titles_match(self, rec_title: str, guitar_title: str) -> bool:
        """Check if recommendation title matches guitar title"""
        rec_words = set(rec_title.lower().split())
        guitar_words = set(guitar_title.lower().split())
        # Consider it a match if at least 60% of recommendation words are in guitar title
        overlap = len(rec_words.intersection(guitar_words))
        return overlap >= len(rec_words) * 0.6
    
    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response to ensure valid JSON"""
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        return response.strip()
    
    def find_guitars_with_explanation(self, user_query: str) -> Tuple[GuitarRecommendation, Dict[str, Any]]:
        """Main method: Find guitars with full step-by-step explanation"""
        self._reset_traces()
        self._add_reasoning_step(f"Starting comprehensive guitar search for: '{user_query}'")
        
        try:
            # Execute all steps
            analysis = self.step1_analyze_user_intent(user_query)
            search_params = self.step2_determine_search_strategy(analysis)
            guitars = self.step3_search_guitars(search_params)
            recommendations = self.step4_analyze_and_recommend(user_query, analysis, guitars)
            
            # Create comprehensive explanation
            explanation = {
                "reasoning_steps": self.reasoning_trace,
                "tools_used": self.tools_used,
                "knowledge_applied": self.knowledge_applied,
                "search_parameters": self.search_parameters,
                "user_analysis": analysis,
                "guitars_found": len(guitars),
                "analysis_confidence": analysis.get("confidence", 0.8),
                "processing_complete": True
            }
            
            self._add_reasoning_step("Guitar search and analysis completed successfully")
            
            return recommendations, explanation
            
        except Exception as e:
            logger.error(f"Enhanced agent processing failed: {e}")
            
            # Create error response
            error_recommendation = GuitarRecommendation(
                user_analysis="I encountered an error while processing your guitar search request.",
                recommendations=[],
                market_insights="Technical issue occurred during search. Please try again or simplify your request.",
                alternative_suggestions="Try being more specific about your budget and musical style preferences."
            )
            
            error_explanation = {
                "error": str(e),
                "reasoning_steps": self.reasoning_trace,
                "tools_used": self.tools_used,
                "knowledge_applied": self.knowledge_applied,
                "processing_complete": False
            }
            
            return error_recommendation, error_explanation
    
    def find_guitars(self, user_query: str) -> GuitarRecommendation:
        """Simple interface for compatibility with standard agent"""
        recommendations, _ = self.find_guitars_with_explanation(user_query)
        return recommendations