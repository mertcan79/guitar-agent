import json
import logging
from typing import List, Dict, Any, Optional
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from ..config import config
from ..scrapers import MockGuitarScraper
from ..models.guitar import GuitarRecommendation

logger = logging.getLogger(__name__)

class GuitarSearchAgent:
    """AI Agent for guitar search and recommendations using LangChain"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.api_key = openai_api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=config.LLM_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )
        
        # Initialize fast LLM for search strategy
        self.fast_llm = ChatOpenAI(
            api_key=self.api_key,
            model=config.FAST_LLM_MODEL,
            temperature=0.3,
            max_tokens=500
        )
        
        # Initialize scraper
        self.scraper = MockGuitarScraper()
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def analyze_user_request(self, user_query: str) -> Dict[str, Any]:
        """Use AI to understand what the user is looking for"""
        
        prompt = f"""
        Analyze this guitar request and extract search parameters:
        User request: "{user_query}"
        
        Consider:
        - Budget range (be flexible, +/- 20%)
        - Guitar types (electric, acoustic, bass)
        - Brands they might be interested in
        - Musical style/genre
        - Skill level
        - Specific features mentioned
        
        If they mention an artist, identify what guitars that artist is known for.
        
        Return a JSON object with:
        {{
            "min_price": <number or null>,
            "max_price": <number or null>,
            "brands": [<list of brand names>],
            "guitar_type": "electric/acoustic/bass",
            "search_terms": [<relevant search keywords>],
            "musical_style": "<genre if mentioned>",
            "skill_level": "beginner/intermediate/advanced/pro",
            "special_requirements": "<any specific needs>",
            "artist_reference": "<artist name if mentioned>",
            "flexibility_factor": <0.1 to 0.3 for budget flexibility>
        }}
        """
        
        try:
            response = self.fast_llm.predict(prompt)
            # Clean response to ensure valid JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            search_params = json.loads(response.strip())
            
            # Apply defaults if needed
            if not search_params.get('min_price'):
                search_params['min_price'] = config.DEFAULT_MIN_PRICE
            if not search_params.get('max_price'):
                search_params['max_price'] = config.DEFAULT_MAX_PRICE
            
            # Apply flexibility to budget
            flexibility = search_params.get('flexibility_factor', 0.2)
            if search_params.get('min_price'):
                search_params['min_price'] = int(search_params['min_price'] * (1 - flexibility))
            if search_params.get('max_price'):
                search_params['max_price'] = int(search_params['max_price'] * (1 + flexibility))
            
            logger.info(f"Analyzed request - Search params: {search_params}")
            return search_params
            
        except Exception as e:
            logger.error(f"Failed to analyze request: {e}")
            # Return default parameters
            return {
                'min_price': config.DEFAULT_MIN_PRICE,
                'max_price': config.DEFAULT_MAX_PRICE,
                'brands': [],
                'search_terms': [],
                'guitar_type': 'electric'
            }
    
    def search_guitars(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for guitars based on parameters"""
        logger.info(f"Searching for guitars with params: {search_params}")
        
        # Use cached search to avoid redundant scraping
        guitars = self.scraper.search_with_cache(search_params)
        
        logger.info(f"Found {len(guitars)} guitars")
        return guitars
    
    def recommend_guitars(self, user_query: str, guitars: List[Dict[str, Any]], 
                          search_params: Dict[str, Any]) -> GuitarRecommendation:
        """Use AI to analyze guitars and make recommendations"""
        
        if not guitars:
            return GuitarRecommendation(
                user_analysis="I understood your request but couldn't find any guitars matching your criteria.",
                recommendations=[],
                market_insights="No guitars found. Try adjusting your search criteria.",
                alternative_suggestions="Consider broadening your price range or being less specific about brands."
            )
        
        # Format guitars for analysis
        guitar_list_text = "\n".join([
            f"{i+1}. {g['title']} - ${g['price']:.0f} ({g.get('condition', 'Unknown')} condition)"
            for i, g in enumerate(guitars[:20])  # Limit to top 20 for analysis
        ])
        
        prompt = f"""
        You are an expert guitar consultant. A customer asked: "{user_query}"
        
        Based on my search, here are the available guitars:
        {guitar_list_text}
        
        Additional context:
        - Search parameters used: {json.dumps(search_params, indent=2)}
        
        Please provide personalized recommendations:
        
        1. Analyze each guitar's suitability for this specific customer
        2. Consider value for money, condition, and features
        3. Rank the top 3-5 recommendations
        4. Explain why each recommendation fits their needs
        5. Note any concerns or alternatives
        
        Format your response as a JSON object:
        {{
            "user_analysis": "Brief summary of what the user is looking for",
            "recommendations": [
                {{
                    "rank": 1,
                    "guitar_title": "exact title from the list",
                    "price": <price as number>,
                    "match_score": <0.0 to 1.0>,
                    "why_recommended": "Detailed explanation",
                    "pros": ["pro1", "pro2"],
                    "cons": ["con1", "con2"],
                    "best_for": "What this guitar is best suited for"
                }}
            ],
            "market_insights": "General observations about the market/availability",
            "alternative_suggestions": "What to consider if these don't work"
        }}
        """
        
        try:
            response = self.llm.predict(prompt)
            
            # Clean and parse response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            recommendation_data = json.loads(response.strip())
            
            # Match recommendations with original guitar data
            for rec in recommendation_data.get('recommendations', []):
                for guitar in guitars:
                    if rec.get('guitar_title') and rec['guitar_title'].lower() in guitar['title'].lower():
                        rec['image_url'] = guitar.get('image_url')
                        rec['link'] = guitar.get('link')
                        rec['condition'] = guitar.get('condition')
                        break
            
            return GuitarRecommendation(**recommendation_data)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return GuitarRecommendation(
                user_analysis="I understood your request but encountered an error analyzing the results.",
                recommendations=[],
                market_insights="Analysis failed. Please try again.",
                alternative_suggestions="Try simplifying your search criteria."
            )
    
    def find_guitars(self, user_query: str) -> GuitarRecommendation:
        """Main method to find and recommend guitars"""
        logger.info(f"Processing query: {user_query}")
        
        # Step 1: Analyze user request
        search_params = self.analyze_user_request(user_query)
        
        # Step 2: Search for guitars
        guitars = self.search_guitars(search_params)
        
        # Step 3: Generate recommendations
        recommendations = self.recommend_guitars(user_query, guitars, search_params)
        
        return recommendations
    
    def chat(self, message: str) -> str:
        """Interactive chat interface"""
        # For now, just use find_guitars
        recommendations = self.find_guitars(message)
        
        # Format response as text
        response_parts = [f"Based on your request: '{message}'\n"]
        response_parts.append(f"\n{recommendations.user_analysis}\n")
        
        if recommendations.recommendations:
            response_parts.append("\nTop Recommendations:\n")
            for i, rec in enumerate(recommendations.recommendations[:3]):
                response_parts.append(f"\n#{rec['rank']}. {rec.get('guitar_title', 'Unknown')} - ${rec.get('price', 0):.0f}")
                response_parts.append(f"   Match Score: {rec.get('match_score', 0)*100:.0f}%")
                response_parts.append(f"   Why: {rec.get('why_recommended', '')}")
                if rec.get('best_for'):
                    response_parts.append(f"   Best for: {rec['best_for']}")
        
        if recommendations.market_insights:
            response_parts.append(f"\nMarket Insights: {recommendations.market_insights}")
        
        if recommendations.alternative_suggestions:
            response_parts.append(f"\nAlternatives to consider: {recommendations.alternative_suggestions}")
        
        return "\n".join(response_parts)