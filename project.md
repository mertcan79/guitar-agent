# Real-Time Guitar Analysis Agent
🎯 User: "I want something like Jimmy Page plays around $1000"

🤖 Agent thinks: 
   - Jimmy Page = Les Paul + Telecaster
   - Search Gibson, Epiphone in $800-1200 range
   - Focus on humbuckers

🔍 Searches live: Finds 22 relevant guitars

🤖 Analyzes each one:
   - Epiphone Les Paul Standard - $899
   - Gibson Les Paul Studio - $1,350  
   - Fender Telecaster Deluxe - $1,050

🏆 Recommends: "The Epiphone Les Paul Standard at $899 is perfect - 
    it's Page's primary guitar type, great value, and leaves 
    budget for a good amp. The Gibson Studio is worth the 
    extra $350 if you want that authentic Gibson feel..."
## The On-Demand Approach

Instead of pre-scraping, let the agent search and analyze guitars in real-time based on user requests. This is more dynamic and uses your API credits more efficiently!

```
User Query → Agent searches specific criteria → Live analysis → Personalized recommendations
```

## Core Real-Time Agent

### 1. Dynamic Search & Analysis Agent
```python
import openai
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import time

class RealTimeGuitarAgent:
    def __init__(self, openai_api_key):
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    def find_and_recommend(self, user_query: str):
        """Search and analyze guitars in real-time based on user request"""
        
        print(f"🎯 Analyzing request: '{user_query}'")
        
        # Step 1: Agent determines search strategy
        search_strategy = self._determine_search_strategy(user_query)
        print(f"🔍 Search strategy: {search_strategy}")
        
        # Step 2: Execute targeted search
        raw_guitars = self._search_guitars_live(search_strategy)
        print(f"📊 Found {len(raw_guitars)} guitars to analyze")
        
        # Step 3: Agent analyzes and recommends
        recommendations = self._analyze_and_recommend(user_query, raw_guitars)
        
        return recommendations
    
    def _determine_search_strategy(self, user_query: str) -> dict:
        """Use AI to determine optimal search parameters"""
        
        prompt = f"""
        User guitar request: "{user_query}"
        
        Determine optimal search parameters for guitar websites:
        
        Extract:
        1. Budget range (min/max prices to search)
        2. Specific brands to focus on (if mentioned)
        3. Guitar types/categories to search
        4. Keywords for search terms
        5. Priority factors (what matters most to this user)
        
        Return JSON:
        {{
            "price_min": 300,
            "price_max": 1500,
            "brands": ["Fender", "Gibson"],
            "categories": ["electric-guitars"],
            "search_terms": ["stratocaster", "les paul"],
            "priority": "value_for_money",
            "flexibility": 0.2
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"⚠️  Strategy determination failed: {e}")
            # Fallback to default strategy
            return {
                "price_min": 300,
                "price_max": 1500,
                "categories": ["electric-guitars"],
                "search_terms": [],
                "priority": "balanced"
            }
    
    def _search_guitars_live(self, strategy: dict, max_results: int = 20) -> list:
        """Perform live targeted search based on strategy"""
        
        guitars = []
        
        # Build search URL based on strategy
        base_url = "https://reverb.com/marketplace/electric-guitars"
        params = {
            'price_min': strategy.get('price_min', 300),
            'price_max': strategy.get('price_max', 2000)
        }
        
        # Add brand filter if specified
        if strategy.get('brands'):
            # Reverb allows brand filtering in URL
            brand_filter = strategy['brands'][0].lower()  # Use first brand as primary
            params['make'] = brand_filter
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Build URL with parameters
                url_params = '&'.join([f"{k}={v}" for k, v in params.items()])
                search_url = f"{base_url}?{url_params}"
                
                print(f"🌐 Searching: {search_url}")
                
                page.goto(search_url, wait_until='networkidle', timeout=30000)
                page.wait_for_selector('.tiles-container', timeout=10000)
                
                # Extract listings
                listings = page.query_selector_all('[data-testid="listing-card"], .listing-item')
                
                for i, listing in enumerate(listings[:max_results]):
                    guitar_data = self._extract_basic_info(listing)
                    if guitar_data:
                        guitars.append(guitar_data)
                
                browser.close()
                
        except Exception as e:
            print(f"❌ Live search failed: {e}")
            
        return guitars
    
    def _extract_basic_info(self, listing) -> dict:
        """Extract minimal info needed for AI analysis"""
        
        try:
            # Get title
            title_selectors = ['[data-testid="listing-title"]', '.listing-title', 'h4', 'h3']
            title = None
            for selector in title_selectors:
                element = listing.query_selector(selector)
                if element:
                    title = element.inner_text().strip()
                    break
            
            # Get price
            price_selectors = ['[data-testid="listing-price"]', '.listing-price', '.price']
            price_text = None
            for selector in price_selectors:
                element = listing.query_selector(selector)
                if element:
                    price_text = element.inner_text().strip()
                    break
            
            # Get condition
            condition_element = listing.query_selector('.condition, [data-testid="condition"]')
            condition = condition_element.inner_text().strip() if condition_element else "Unknown"
            
            # Get image
            image_element = listing.query_selector('img')
            image_url = image_element.get_attribute('src') if image_element else ""
            
            # Extract price number
            import re
            price_match = re.search(r'[\d,]+', price_text.replace('$', '').replace(',', '') if price_text else "0")
            price = float(price_match.group()) if price_match else 0
            
            if title and price > 0:
                return {
                    'title': title,
                    'price': price,
                    'condition': condition,
                    'image_url': image_url
                }
                
        except Exception as e:
            print(f"⚠️  Error extracting listing: {e}")
            
        return None
    
    def _analyze_and_recommend(self, user_query: str, guitars: list) -> dict:
        """Use AI to analyze guitars and make personalized recommendations"""
        
        if not guitars:
            return {"error": "No guitars found matching your criteria"}
        
        # Format guitars for AI analysis
        guitar_list = []
        for i, guitar in enumerate(guitars):
            guitar_list.append(f"{i+1}. {guitar['title']} - ${guitar['price']} ({guitar['condition']})")
        
        guitars_text = "\n".join(guitar_list)
        
        prompt = f"""
        You are an expert guitar consultant. A user asked: "{user_query}"
        
        Here are the current available guitars I found:
        
        {guitars_text}
        
        ANALYZE AND RECOMMEND:
        
        1. For each guitar, assess:
           - How well it matches the user's request
           - Value for money
           - Pros and cons for this specific user
           - Technical specs you can infer from the title
        
        2. Rank the top 3 recommendations
        
        3. Explain your reasoning clearly
        
        4. Consider:
           - Budget flexibility (sometimes worth spending 20% more)
           - Musical style compatibility  
           - Long-term satisfaction
           - Market value assessment
        
        Return detailed analysis in JSON format:
        {{
            "user_analysis": "what the user is looking for",
            "recommendations": [
                {{
                    "rank": 1,
                    "guitar": "exact title from list",
                    "price": 950,
                    "match_score": 0.95,
                    "why_perfect": "detailed explanation",
                    "pros": ["pro1", "pro2"],
                    "cons": ["con1", "con2"],
                    "value_assessment": "excellent deal because...",
                    "specs_inferred": {{
                        "brand": "Fender",
                        "model": "Stratocaster", 
                        "pickup_config": "HSS",
                        "suitable_genres": ["blues", "rock"]
                    }}
                }}
            ],
            "market_insights": "general observations about available options",
            "alternative_suggestions": "if nothing perfect was found"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for better analysis
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Add original guitar data to recommendations
            for rec in analysis.get("recommendations", []):
                # Find matching guitar data
                for guitar in guitars:
                    if guitar['title'] in rec['guitar']:
                        rec['image_url'] = guitar['image_url']
                        break
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}

# Enhanced version with multiple site search
class MultiSiteGuitarAgent(RealTimeGuitarAgent):
    """Extended version that searches multiple sites"""
    
    def _search_guitars_live(self, strategy: dict, max_results: int = 30) -> list:
        """Search multiple sites for better coverage"""
        
        all_guitars = []
        
        # Search Reverb
        reverb_guitars = self._search_reverb(strategy, max_results // 2)
        all_guitars.extend(reverb_guitars)
        
        # Search Guitar Center (if time permits)
        # gc_guitars = self._search_guitar_center(strategy, max_results // 2)
        # all_guitars.extend(gc_guitars)
        
        return all_guitars
    
    def _search_reverb(self, strategy: dict, max_results: int) -> list:
        """Reverb-specific search logic"""
        return super()._search_guitars_live(strategy, max_results)
```

### 2. Streamlined Usage Interface
```python
import streamlit as st
from datetime import datetime

def create_realtime_interface():
    st.title("🎸 Real-Time Guitar Recommendation Agent")
    
    # API key input
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    
    if not api_key:
        st.warning("Please enter your OpenAI API key to continue")
        return
    
    # Initialize agent
    agent = RealTimeGuitarAgent(api_key)
    
    # User input
    st.subheader("What guitar are you looking for?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_query = st.text_area(
            "Describe what you want:",
            placeholder="I want something like David Gilmour plays around $1000, good for blues and rock...",
            height=100
        )
    
    with col2:
        st.write("**Example queries:**")
        st.write("• *Metal guitar under $800*")
        st.write("• *Beginner guitar for blues*") 
        st.write("• *Like Jimmy Page plays*")
        st.write("• *Jazz guitar around $1200*")
    
    if st.button("🔍 Find My Guitar", type="primary"):
        if user_query:
            
            with st.spinner("🤖 Searching and analyzing guitars..."):
                start_time = datetime.now()
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🎯 Understanding your request...")
                progress_bar.progress(25)
                
                status_text.text("🔍 Searching current market...")
                progress_bar.progress(50)
                
                status_text.text("🤖 Analyzing guitars with AI...")
                progress_bar.progress(75)
                
                # Get recommendations
                result = agent.find_and_recommend(user_query)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                end_time = datetime.now()
                search_time = (end_time - start_time).total_seconds()
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            if "error" in result:
                st.error(f"Search failed: {result['error']}")
            else:
                st.success(f"Analysis completed in {search_time:.1f} seconds")
                
                # User analysis
                st.subheader("🎯 What You're Looking For")
                st.write(result.get("user_analysis", ""))
                
                # Recommendations
                st.subheader("🏆 Top Recommendations")
                
                for rec in result.get("recommendations", []):
                    with st.expander(
                        f"#{rec['rank']} - {rec['guitar']} - ${rec['price']:.0f} "
                        f"(Match: {rec['match_score']*100:.0f}%)"
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Why it's perfect:** {rec['why_perfect']}")
                            st.write(f"**Value assessment:** {rec['value_assessment']}")
                            
                            if rec.get('pros'):
                                st.write("**✅ Pros:**")
                                for pro in rec['pros']:
                                    st.write(f"• {pro}")
                            
                            if rec.get('cons'):
                                st.write("**⚠️ Considerations:**")
                                for con in rec['cons']:
                                    st.write(f"• {con}")
                        
                        with col2:
                            if rec.get('image_url'):
                                st.image(rec['image_url'], width=200)
                            
                            specs = rec.get('specs_inferred', {})
                            if specs:
                                st.write("**Inferred Specs:**")
                                for key, value in specs.items():
                                    if isinstance(value, list):
                                        value = ", ".join(value)
                                    st.write(f"• {key.title()}: {value}")
                
                # Market insights
                if result.get("market_insights"):
                    st.subheader("📊 Market Insights")
                    st.info(result["market_insights"])
                
                # Alternative suggestions
                if result.get("alternative_suggestions"):
                    st.subheader("💡 Alternative Suggestions")
                    st.write(result["alternative_suggestions"])
        
        else:
            st.warning("Please describe what kind of guitar you're looking for")

# Simple CLI version for testing
class CLIGuitarAgent:
    def __init__(self, api_key):
        self.agent = RealTimeGuitarAgent(api_key)
    
    def run_interactive(self):
        print("🎸 Real-Time Guitar Recommendation Agent")
        print("=" * 50)
        
        while True:
            print("\n" + "="*50)
            user_query = input("🎯 What guitar are you looking for? (or 'quit' to exit)\n> ")
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using Guitar Agent!")
                break
            
            if user_query.strip():
                print(f"\n🤖 Analyzing: '{user_query}'")
                print("-" * 50)
                
                result = self.agent.find_and_recommend(user_query)
                
                if "error" in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"🎯 {result.get('user_analysis', '')}")
                    print("\n🏆 TOP RECOMMENDATIONS:")
                    
                    for rec in result.get('recommendations', []):
                        print(f"\n#{rec['rank']} - {rec['guitar']} - ${rec['price']:.0f}")
                        print(f"   Match: {rec['match_score']*100:.0f}%")
                        print(f"   Why: {rec['why_perfect']}")
                        print(f"   Value: {rec['value_assessment']}")
            else:
                print("⚠️  Please enter a guitar request")

if __name__ == "__main__":
    import os
    api_key = os.getenv('OPENAI_API_KEY') or input("Enter OpenAI API key: ")
    
    # Choose interface
    interface = input("Choose interface (1=CLI, 2=Web): ")
    
    if interface == "2":
        create_realtime_interface()
    else:
        cli = CLIGuitarAgent(api_key)
        cli.run_interactive()
```

## Key Advantages of Real-Time Analysis

### 1. **Always Current**
- Fresh listings, current prices
- No stale data or sold items
- Market conditions reflected immediately

### 2. **Hyper-Targeted Search**
- Agent determines optimal search strategy per query
- "David Gilmour style" → searches specifically for Strats
- "Metal under $800" → focuses on humbuckers, specific brands

### 3. **Personalized Analysis**
- Every recommendation is tailored to that specific user
- Considers their exact budget, style, and preferences
- No generic "one-size-fits-all" recommendations

### 4. **Efficient API Usage**
- Only analyzes relevant guitars (20-30 instead of hundreds)
- Targeted search reduces noise
- $5 gives you many targeted searches vs few bulk analyses

## Sample Interaction Flow

```
User: "I want something like Edge from U2 uses around $1200"

Agent Search Strategy:
🎯 Price range: $800-1400 (20% flexibility)
🔍 Focus: Fender, Gibson Explorer, bright pickups
📊 Found 18 relevant guitars

Analysis Results:
🏆 #1: Fender Player Stratocaster HSS - $950
   Why perfect: Edge uses Strats extensively, HSS gives versatility
   Value: Excellent - $200 under typical retail
   
🏆 #2: Gibson Explorer Studio - $1,350  
   Why good: Edge's signature alternative guitar
   Value: Fair market price for Gibson quality
```

## Quick Setup

```bash
pip install openai playwright streamlit
playwright install chromium

# CLI version
python guitar_agent.py

# Web interface  
streamlit run guitar_app.py
```

This approach is **much more impressive** for a portfolio because it shows real-time AI decision-making rather than static database queries!