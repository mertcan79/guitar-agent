"""
User-Ready Guitar Finder Application
Clean, intuitive interface for finding the perfect guitar
"""

import streamlit as st
import logging
from datetime import datetime
import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from PIL import Image

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.enhanced_guitar_agent import EnhancedGuitarAgent
from src.knowledge.guitar_knowledge import GuitarKnowledgeBase
from src.config import config

# Configure logging (minimal for user version)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Find Me a Guitar",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Disable analytics tracking
st.markdown("""
<script>
// Disable any analytics or tracking
if (typeof gtag !== 'undefined') { gtag = function() {}; }
if (typeof analytics !== 'undefined') { analytics = {}; }
</script>
""", unsafe_allow_html=True)

# Custom CSS for improved design
st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding-top: 1rem;
        background-color: #e6f3ff;
    }
    
    /* Light blue background for the whole app */
    .stApp {
        background: linear-gradient(180deg, #e6f3ff 0%, #f0f8ff 100%);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1);
    }
    
    /* Guitar cards */
    .guitar-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .guitar-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    /* Example cards in sidebar */
    .example-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-card:hover {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    /* Price display */
    .price-tag {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    
    /* Match score */
    .match-score {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    /* Pros/cons lists */
    .pros-list {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
    }
    
    .cons-list {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Sidebar styling */
    .sidebar .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    /* Loading animation */
    .searching {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        background-size: 200% 100%;
        animation: gradient-shift 2s ease infinite;
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Advanced example queries with comprehensive technical specifications
EXAMPLE_QUERIES = [
    {
        "title": "🎸 David Gilmour Tone",
        "query": "I want David Gilmour's tone from Pink Floyd. Need Stratocaster with alder body, maple neck, rosewood fretboard, vintage-style tremolo bridge, single-coil pickups, and 9.5\" radius. Budget $1500",
        "category": "Artist Reference"
    },
    {
        "title": "🎭 Jimmy Page Les Paul",
        "query": "Looking for Jimmy Page's Les Paul sound. Need mahogany body with maple cap, set neck, PAF-style humbuckers, tune-o-matic bridge, bound neck, and vintage sunburst finish. Budget $2000",
        "category": "Artist Reference"
    },
    {
        "title": "🤘 Modern Metal Machine",
        "query": "Need a metal guitar with basswood body, bolt-on maple neck, ebony fretboard, Floyd Rose Original tremolo, active EMG 81/85 pickups, 24 frets, compound radius 12-16\", locking tuners. Budget $1800",
        "category": "Technical Specs"
    },
    {
        "title": "🎷 Jazz Archtop Pro",
        "query": "Professional jazz guitar needed. Hollow body construction, spruce top, maple back/sides, ebony fretboard, floating pickup, adjustable bridge, tailpiece, P90 or humbucker. Budget $3000",
        "category": "Technical Specs"
    },
    {
        "title": "🔧 Custom Shop Specs",
        "query": "Want custom shop quality: ash body, quartersawn maple neck, pau ferro fretboard, hipshot locking tuners, Graph Tech nut, Gotoh 510 tremolo, Seymour Duncan SSL-5 pickups. Budget $2500",
        "category": "Technical Specs"
    },
    {
        "title": "🎚️ Studio Recording Guitar",
        "query": "Recording studio guitar: chambered mahogany body, set neck, coil-tap humbuckers, push-pull pots, bone nut, Grover tuners, wraparound bridge, medium jumbo frets. Budget $1600",
        "category": "Technical Specs"
    },
    {
        "title": "🎸 Vintage Spec Tele",
        "query": "Vintage Telecaster specs: ash body, one-piece maple neck, 7.25\" radius, vintage frets, 3-saddle bridge, single-coil pickups, vintage wiring, nitro finish. Budget $1200",
        "category": "Technical Specs"
    },
    {
        "title": "🌊 Progressive Rock Setup",
        "query": "Progressive rock guitar: mahogany body, neck-through construction, 24 frets, compound radius, locking tremolo, piezo pickups, coil-split humbuckers, active electronics. Budget $2200",
        "category": "Technical Specs"
    }
]

def init_session_state():
    """Initialize session state variables"""
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_explanation' not in st.session_state:
        st.session_state.search_explanation = None
    if 'saved_guitars' not in st.session_state:
        st.session_state.saved_guitars = []
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'selected_query' not in st.session_state:
        st.session_state.selected_query = ''

def create_agent():
    """Create the guitar search agent"""
    try:
        config.validate()
        return EnhancedGuitarAgent()
    except ValueError as e:
        st.error(f"⚠️ Configuration error: {e}")
        return None

def search_for_guitars(query: str):
    """Search for guitars with the given query"""
    if not query.strip():
        st.warning("Please tell us what kind of guitar you're looking for!")
        return
        
    agent = create_agent()
    if not agent:
        return
        
    with st.spinner("🔍 Finding your perfect guitar..."):
        # Show animated searching message
        search_placeholder = st.empty()
        search_placeholder.markdown('<div class="searching">🎸 Analyzing your preferences and searching guitars...</div>', unsafe_allow_html=True)
        
        try:
            start_time = time.time()
            recommendations, explanation = agent.find_guitars_with_explanation(query)
            duration = time.time() - start_time
            
            # Clear the searching message
            search_placeholder.empty()
            
            # Store results
            st.session_state.search_results = recommendations
            st.session_state.search_explanation = explanation
            
            # Add to history
            st.session_state.search_history.append({
                'query': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'duration': duration,
                'results_count': len(recommendations.recommendations)
            })
            
            # Display results
            display_results(recommendations, explanation)
            
        except Exception as e:
            search_placeholder.empty()
            st.error(f"Sorry, something went wrong: {str(e)}")

def display_results(recommendations, explanation):
    """Display search results - show only the best match with detailed view"""
    if not recommendations.recommendations:
        st.warning("No guitars found matching your criteria. Try adjusting your requirements.")
        return
    
    # User analysis summary
    st.markdown("### 🎯 What We Understood")
    st.info(recommendations.user_analysis)
    
    # Show only the best result
    best_guitar = recommendations.recommendations[0]  # Take the first (best) result
    
    # Results header
    st.markdown("### 🏆 Perfect Match Found")
    
    # Display the single best guitar with enhanced format
    display_single_guitar_detailed(best_guitar, explanation)

def create_budget_visualization(guitar_price, user_budget_str):
    """Create a visual representation of price vs budget"""
    import re
    
    # Extract budget from user query - look for larger numbers (typical guitar budgets)
    budget_matches = re.findall(r'\$?(\d+)', user_budget_str)
    target_budget = 1500  # Default
    
    if budget_matches:
        # Look for numbers that are likely budgets (> 300 for guitars)
        for match in budget_matches:
            budget_val = int(match)
            if budget_val >= 300:  # Reasonable guitar budget
                target_budget = budget_val
                break
    
    # Create price distribution visualization
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### 💰 Price Analysis")
        
        # Calculate price difference
        price_diff = guitar_price - target_budget
        percentage_diff = (price_diff / target_budget) * 100
        
        # Create visual representation
        if price_diff <= 0:
            status = "✅ Under Budget"
            color = "#28a745"
        elif percentage_diff <= 10:
            status = "⚠️ Slightly Over Budget"
            color = "#ffc107"
        else:
            status = "🔴 Over Budget"
            color = "#dc3545"
        
        # Visual price bar
        budget_ratio = min(guitar_price / target_budget, 2.0)  # Cap at 200%
        bar_width = int(budget_ratio * 100)
        
        price_diff_text = ""
        if price_diff != 0:
            price_diff_text = f'<div style="text-align: center; margin-top: 5px; font-size: 14px;">${abs(price_diff):,} {"over" if price_diff > 0 else "under"} budget</div>'
        
        st.markdown(f"""
        <div style="background: #f0f2f6; border-radius: 10px; padding: 20px; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span><strong>Your Budget:</strong> ${target_budget:,}</span>
                <span><strong>Guitar Price:</strong> ${guitar_price:,}</span>
            </div>
            <div style="background: #e0e0e0; height: 20px; border-radius: 10px; position: relative; overflow: hidden;">
                <div style="background: linear-gradient(90deg, {color} 0%, {color} 100%); 
                     height: 100%; width: {bar_width}%; border-radius: 10px; 
                     transition: all 0.3s ease;"></div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                     color: white; font-weight: bold; font-size: 12px;">
                     {budget_ratio:.1f}x Budget
                </div>
            </div>
            <div style="text-align: center; margin-top: 10px; font-weight: bold; color: {color};">
                {status}
            </div>
            {price_diff_text}
        </div>
        """, unsafe_allow_html=True)

def display_single_guitar_detailed(guitar, explanation):
    """Display a single guitar with comprehensive details"""
    
    # Make the entire layout MUCH wider
    st.markdown('<div style="max-width: 1600px; margin: 0 auto;">', unsafe_allow_html=True)
    
    # Main guitar info header
    guitar_title = guitar.get('title', 'Unknown Guitar')
    price = guitar.get('price', 0)
    
    # Header section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
         color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px;
         box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
        <h2 style="margin: 0; text-align: center;">{guitar_title}</h2>
        <h3 style="margin: 10px 0 0 0; text-align: center; opacity: 0.9;">${price:,}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content in wide columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display guitar icon
        brand = "Guitar"
        for brand_name in ["Fender", "Gibson", "Ibanez", "ESP", "Schecter", "PRS", "Jackson", "Dean", "Epiphone"]:
            if brand_name.lower() in guitar_title.lower():
                brand = brand_name
                break
        
        # Display stylish guitar icon card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             color: white; padding: 40px; border-radius: 15px; text-align: center; 
             box-shadow: 0 8px 24px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <div style="font-size: 64px; margin-bottom: 15px;">🎸</div>
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">{brand}</div>
            <div style="font-size: 14px; opacity: 0.9; line-height: 1.4;">{guitar_title}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Guitar details
        condition = guitar.get('condition', 'Unknown')
        source = guitar.get('source', 'Unknown')
        
        st.markdown("#### 📋 Guitar Details")
        st.markdown(f"""
        **Condition:** {condition}  
        **Source:** {source}  
        **Brand:** {brand}
        """)
        
        # Link to original listing
        if guitar.get('link'):
            st.markdown(f"[🔗 View Original Listing]({guitar['link']})")
    
    with col2:
        # Match score (fixed formatting)
        match_score = guitar.get('match_score', 0.85)
        if isinstance(match_score, float) and match_score <= 1.0:
            match_percentage = int(match_score * 100)
        else:
            match_percentage = int(match_score)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
             color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
            <h3 style="margin: 0;">🎯 {match_percentage}% Match</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Perfect fit for your requirements</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced "Why It's Perfect" section
        why_perfect = guitar.get('why_perfect', guitar.get('why_recommended', 
            "This guitar matches your technical specifications perfectly. It features the exact components you requested and is ideal for your musical style."))
        
        st.markdown("#### 🌟 Why It's Perfect")
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; 
             border-left: 4px solid #667eea; margin-bottom: 20px;">
            <p style="margin: 0; line-height: 1.6; font-size: 16px;">{why_perfect}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed technical specifications (outside of column context)
        pass
    
    # Technical Analysis section (outside column nesting)
    st.markdown("#### 🔧 Technical Analysis")
    
    # Create new columns for technical specs
    specs_col1, specs_col2 = st.columns(2)
    
    with specs_col1:
        st.markdown("**✅ Matched Specifications:**")
        pros = guitar.get('pros', [
            "Professional build quality",
            "Excellent tone characteristics", 
            "Suitable for requested genre",
            "High-quality hardware"
        ])
        for pro in pros:
            st.markdown(f"• {pro}")
    
    with specs_col2:
        st.markdown("**⚠️ Considerations:**")
        cons = guitar.get('cons', [
            "Regular maintenance required",
            "Setup may need adjustment"
        ])
        for con in cons:
            st.markdown(f"• {con}")
    
    # Budget visualization (full width)
    # Get user query from search history or explanation
    user_query = ""
    if st.session_state.search_history:
        user_query = st.session_state.search_history[-1].get('query', '$1800')
    else:
        user_query = '$1800'  # Default budget
    
    create_budget_visualization(price, user_query)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_guitar_card(guitar, rank):
    """Display individual guitar recommendation card"""
    with st.container():
        st.markdown(f"""
        <div class="guitar-card">
            <h4>#{rank} - {guitar.get('title', 'Unknown Guitar')}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Make the layout wider for better display
        col1, col2, col3 = st.columns([1.5, 3, 1.5])
        
        with col1:
            # Guitar image with improved display
            guitar_title = guitar.get('title', 'Unknown Guitar')
            image_url = guitar.get('image_url', '')
            
            # Extract brand for placeholder
            brand = "Guitar"
            for brand_name in ["Fender", "Gibson", "Ibanez", "ESP", "Schecter", "PRS", "Jackson", "Dean"]:
                if brand_name.lower() in guitar_title.lower():
                    brand = brand_name
                    break
            
            # Always show a visual placeholder since external URLs might not work
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 25px; border-radius: 12px; text-align: center; 
                 box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 10px;">
                <div style="font-size: 48px; margin-bottom: 10px;">🎸</div>
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">{brand}</div>
                <div style="font-size: 12px; opacity: 0.9;">{guitar_title[:30]}{'...' if len(guitar_title) > 30 else ''}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # If there's an image URL, show it as a link
            if image_url:
                st.markdown(f"[🔗 View Original Image]({image_url})", unsafe_allow_html=True)
            else:
                st.caption("Representative display")
        
        with col2:
            # Price and details
            price = guitar.get('price', 0)
            st.markdown(f'<div class="price-tag">${price:,.0f}</div>', unsafe_allow_html=True)
            
            # Match score (if available)
            match_score = guitar.get('match_score', 95)
            st.markdown(f'<div class="match-score">{match_score}% match</div>', unsafe_allow_html=True)
            
            # Condition
            condition = guitar.get('condition', 'Unknown')
            st.markdown(f"**Condition:** {condition}")
            
            # Source
            source = guitar.get('source', 'Unknown')
            st.markdown(f"**Source:** {source}")
            
            # Why it's perfect
            why_perfect = guitar.get('why_perfect', "This guitar matches your requirements well.")
            st.markdown("**🌟 Why It's Perfect**")
            st.write(why_perfect)
        
        with col3:
            # Pros and cons
            pros = guitar.get('pros', [])
            if pros:
                st.markdown('<div class="pros-list"><strong>✅ Pros</strong><br>', unsafe_allow_html=True)
                for pro in pros[:3]:  # Limit to 3 pros
                    st.markdown(f"• {pro}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            cons = guitar.get('cons', [])
            if cons:
                st.markdown('<div class="cons-list"><strong>⚠️ Consider</strong><br>', unsafe_allow_html=True)
                for con in cons[:2]:  # Limit to 2 cons
                    st.markdown(f"• {con}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        col_link, col_save = st.columns(2)
        
        with col_link:
            if guitar.get('link'):
                st.link_button("🔗 View Listing", guitar['link'], use_container_width=True)
            else:
                st.button("🔗 Link Not Available", disabled=True, use_container_width=True)
        
        with col_save:
            if st.button(f"💾 Save Guitar", key=f"save_{rank}", use_container_width=True):
                save_guitar(guitar)
                st.success("Guitar saved!")
        
        st.divider()

def save_guitar(guitar):
    """Save a guitar to the user's collection"""
    saved_guitar = {
        'title': guitar.get('title', 'Unknown Guitar'),
        'price': guitar.get('price', 0),
        'image_url': guitar.get('image_url', ''),
        'link': guitar.get('link', ''),
        'saved_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'condition': guitar.get('condition', 'Unknown'),
        'source': guitar.get('source', 'Unknown')
    }
    
    st.session_state.saved_guitars.append(saved_guitar)

def main():
    """Main application function"""
    init_session_state()
    
    # Sidebar with examples, history, and other functionalities
    with st.sidebar:
        st.markdown("## 💡 Quick Examples")
        st.caption("Click any example to try it instantly")
        
        for example in EXAMPLE_QUERIES:
            if st.button(
                f"{example['title']}", 
                key=f"ex_{example['title']}", 
                use_container_width=True,
                help=f"Category: {example['category']}"
            ):
                # Set the query in session state to populate the main search
                st.session_state.selected_query = example['query']
                st.rerun()
        
        st.divider()
        
        # Search History
        if st.session_state.search_history:
            st.markdown("### 📜 Recent Searches")
            for i, search in enumerate(st.session_state.search_history[-5:]):  # Show last 5
                with st.expander(f"🔍 {search['query'][:40]}..."):
                    st.write(f"**When:** {search['timestamp']}")
                    st.write(f"**Results:** {search['results_count']} guitars found")
                    st.write(f"**Search time:** {search['duration']:.1f}s")
                    if st.button("Search Again", key=f"history_{i}"):
                        st.session_state.selected_query = search['query']
                        st.rerun()
            st.divider()
        
        # Saved guitars section
        if st.session_state.saved_guitars:
            st.markdown(f"### 💾 Saved Guitars ({len(st.session_state.saved_guitars)})")
            
            for i, saved in enumerate(st.session_state.saved_guitars[-3:]):  # Show last 3
                with st.expander(f"🎸 ${saved['price']:,.0f} - {saved['title'][:25]}..."):
                    st.write(f"**Saved:** {saved['saved_at']}")
                    st.write(f"**Condition:** {saved['condition']}")
                    if saved.get('link'):
                        st.link_button("View Listing", saved['link'])
            st.divider()
        
        # Technical terms help
        with st.expander("🔧 Advanced Technical Guide"):
            st.markdown("""
            **Pickup Types:**
            • Single coil - bright, clear, vintage tone
            • Humbucker - warm, thick, noise-canceling
            • P90 - growling midrange, vintage output
            • Active (EMG) - high output, modern metal
            • Coil-tap/split - versatile pickup switching
            
            **Bridge Types:**
            • Tune-o-matic - stable, sustain, adjustable
            • Floyd Rose - locking tremolo, dive bombs
            • Vintage tremolo - smooth vibrato
            • Hardtail - maximum sustain, no tremolo
            • Wraparound - simple, resonant
            • Hipshot - modern, precise tuning
            
            **Body Woods:**
            • Alder - balanced, clear highs
            • Ash - bright, punchy attack
            • Mahogany - warm, thick midrange
            • Basswood - neutral, good for effects
            • Maple - bright, articulate
            • Chambered - lighter, acoustic qualities
            
            **Neck Construction:**
            • Bolt-on - punchy attack, easy repair
            • Set neck - warm sustain, smooth joint
            • Neck-through - maximum sustain, resonance
            • Quartersawn - stable, minimal warping
            
            **Fretboard Materials:**
            • Rosewood - warm, smooth feel
            • Maple - bright, fast playing
            • Ebony - dense, clear articulation
            • Pau ferro - rosewood alternative
            
            **Fretboard Radius:**
            • 7.25" - vintage, good for chords
            • 9.5" - modern vintage, versatile
            • 12" - fast lead playing
            • 16" - extremely fast, modern metal
            • Compound - combines chord/lead comfort
            
            **Fret Types:**
            • Vintage - small, period correct
            • Medium jumbo - balanced feel
            • Jumbo - easy bending, modern
            • Stainless steel - long-lasting, bright
            
            **Electronics:**
            • Passive - traditional wiring
            • Active - battery-powered preamp
            • Coil-tap - humbucker to single coil
            • Push-pull pots - switching options
            • Piezo - acoustic-like tones
            
            **Hardware:**
            • Locking tuners - quick string changes
            • Bone nut - natural tone transfer
            • Graph Tech - synthetic, consistent
            • Grover tuners - vintage, reliable
            """)
            
        # Advanced search tips
        with st.expander("💡 Advanced Search Tips"):
            st.markdown("""
            **For Metal:** Mention EMG pickups, Floyd Rose, compound radius, 24 frets
            **For Jazz:** Specify hollow/semi-hollow, floating pickup, tailpiece
            **For Blues:** Ask for P90s, wraparound bridge, mahogany body
            **For Country:** Request Telecaster, single coils, ash body, vintage specs
            **For Recording:** Mention coil-tap, push-pull pots, versatile pickup switching
            **Custom Shop:** Specify premium woods, hardware brands (Hipshot, Gotoh)
            """)
    
    # Main content area with flashy title
    # Flashy animated title
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="
                background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
                background-size: 300% 300%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 3.5rem;
                font-weight: 800;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                animation: gradient-shift 3s ease infinite;
                margin-bottom: 0.5rem;
            ">Find Me A Guitar Pls</h1>
            <p style="color: #666; font-size: 1.2rem; font-style: italic;">Your AI-Powered Guitar Matchmaker 🎸</p>
        </div>
        <style>
            @keyframes gradient-shift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Load and display pic.png at the top (centered)
    try:
        # Use simple direct path since pic.png is in main folder
        main_image = Image.open("pic.png")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(main_image, width=400)
    except Exception as e:
        # Fallback if image not found
        st.info("🎸 Guitar image not available")
    
    # Main search section
    st.markdown("## 🔍 Search for Your Guitar")
    
    # Get the query from session state if set by example click
    default_query = st.session_state.get('selected_query', '')
    
    # Main search input
    user_query = st.text_area(
        "What's your dream guitar?",
        value=default_query,
        placeholder="E.g., I want David Gilmour's tone with alder body, maple neck, rosewood fretboard, vintage tremolo, single coils, 9.5\" radius, budget $1500",
        height=100,
        help="Describe your ideal guitar - mention artists, genres, budget, or specific technical features like pickups, bridge, woods, etc.",
        key="main_search_input"
    )
    
    # Clear the selected query after the user modifies it
    if default_query and user_query != default_query:
        st.session_state.selected_query = ''
    
    # Search button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎸 Find My Guitar", type="primary", use_container_width=True):
            search_for_guitars(user_query)
    
    # Results area or welcome screen
    if st.session_state.search_results is None:
        # Welcome screen with centered image and text below
        st.markdown("---")
        
        # How It Works section under the centered image
        st.markdown("## 🎵 How It Works")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Tell Us What You Want
            Describe your ideal guitar in natural language. Mention:
            - Your favorite artists
            - Musical genres you play
            - Your budget range
            - Specific features you want
            """)
        
        with col2:
            st.markdown("""
            ### 🤖 AI-Powered Search
            Our smart agent understands guitar terminology and finds instruments that match your style and needs perfectly.
            """)
        
        with col3:
            st.markdown("""
            ### 🎸 Expert Recommendations
            Get detailed explanations of why each guitar fits your requirements, plus pros and cons for each option.
            """)
    else:
        # Results are displayed - no additional wrapper needed
        pass

if __name__ == "__main__":
    main()