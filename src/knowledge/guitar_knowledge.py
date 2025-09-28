"""
Guitar Domain Knowledge Base
Contains expert knowledge about guitars, brands, and musical styles
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class GuitarSpec:
    """Guitar specification details"""
    brand: str
    model: str
    body_type: str
    pickups: str
    typical_genres: List[str]
    price_range: tuple  # (min, max)
    skill_level: List[str]
    tone_characteristics: List[str]
    famous_players: List[str]

class GuitarKnowledgeBase:
    """Expert knowledge about guitars and music"""
    
    # Technical Specifications Database
    TECHNICAL_SPECS = {
        "bridge_types": {
            "tune-o-matic": {
                "description": "Fixed bridge with adjustable intonation and action",
                "characteristics": ["stable tuning", "maximum sustain", "no tremolo"],
                "typical_guitars": ["Les Paul", "SG", "ES-335"],
                "genres": ["rock", "blues", "jazz", "metal"]
            },
            "floyd_rose": {
                "description": "Locking tremolo system for extreme pitch bending",
                "characteristics": ["dive bombs", "flutter effects", "locking nut"],
                "typical_guitars": ["Modern Strats", "Superstrats", "Metal guitars"],
                "genres": ["metal", "progressive", "hard rock"]
            },
            "vintage_tremolo": {
                "description": "Traditional Stratocaster-style vibrato",
                "characteristics": ["smooth vibrato", "vintage tone", "subtle pitch bending"],
                "typical_guitars": ["Stratocaster", "Vintage reissues"],
                "genres": ["blues", "rock", "country", "surf"]
            },
            "hardtail": {
                "description": "Fixed bridge without tremolo system",
                "characteristics": ["maximum sustain", "stable tuning", "simple design"],
                "typical_guitars": ["Telecaster", "Some Strats"],
                "genres": ["country", "blues", "punk", "alternative"]
            }
        },
        
        "pickup_types": {
            "single_coil": {
                "description": "Traditional single-coil pickup design",
                "characteristics": ["bright tone", "clear articulation", "vintage sound", "some hum"],
                "typical_outputs": ["vintage", "medium"],
                "genres": ["blues", "country", "surf", "indie"]
            },
            "humbucker": {
                "description": "Dual-coil design that cancels hum",
                "characteristics": ["warm tone", "thick midrange", "noise-free", "higher output"],
                "typical_outputs": ["medium", "high"],
                "genres": ["rock", "metal", "jazz", "blues"]
            },
            "p90": {
                "description": "Single-coil with higher output and growl",
                "characteristics": ["midrange growl", "vintage tone", "moderate hum"],
                "typical_outputs": ["medium"],
                "genres": ["blues", "rock", "alternative", "punk"]
            },
            "active_emg": {
                "description": "Battery-powered active pickups",
                "characteristics": ["high output", "low noise", "compressed tone", "modern"],
                "typical_outputs": ["very high"],
                "genres": ["metal", "hard rock", "progressive"]
            }
        },
        
        "body_woods": {
            "alder": {
                "description": "Balanced tonal properties with good sustain",
                "characteristics": ["balanced tone", "clear highs", "present mids"],
                "weight": "medium",
                "typical_guitars": ["Stratocaster", "Modern guitars"]
            },
            "ash": {
                "description": "Bright, punchy tone with good attack",
                "characteristics": ["bright tone", "punchy attack", "clear definition"],
                "weight": "medium-heavy",
                "typical_guitars": ["Telecaster", "Some Strats"]
            },
            "mahogany": {
                "description": "Warm, thick tone with emphasis on midrange",
                "characteristics": ["warm tone", "thick midrange", "good sustain"],
                "weight": "medium-heavy",
                "typical_guitars": ["Les Paul", "SG", "PRS"]
            },
            "basswood": {
                "description": "Neutral tone that works well with effects",
                "characteristics": ["neutral tone", "soft attack", "effects-friendly"],
                "weight": "light",
                "typical_guitars": ["Modern metal guitars", "Budget guitars"]
            }
        },
        
        "neck_construction": {
            "bolt_on": {
                "description": "Neck attached with bolts/screws",
                "characteristics": ["punchy attack", "bright tone", "easy repair"],
                "typical_guitars": ["Stratocaster", "Telecaster", "Modern guitars"]
            },
            "set_neck": {
                "description": "Neck glued into body joint",
                "characteristics": ["warm sustain", "smooth joint", "classic tone"],
                "typical_guitars": ["Les Paul", "SG", "ES-335"]
            },
            "neck_through": {
                "description": "Neck extends through entire body",
                "characteristics": ["maximum sustain", "deep resonance", "smooth playability"],
                "typical_guitars": ["High-end guitars", "Progressive instruments"]
            }
        }
    }
    
    # Artist-Guitar Associations
    ARTIST_GUITARS = {
        "jimmy page": {
            "primary": ["Gibson Les Paul", "Gibson EDS-1275"],
            "also_used": ["Fender Telecaster", "Danelectro"],
            "brands": ["Gibson", "Epiphone", "Fender"],
            "characteristics": ["humbucker pickups", "thick tone", "versatile"]
        },
        "david gilmour": {
            "primary": ["Fender Stratocaster"],
            "also_used": ["Gibson Les Paul Goldtop", "Gretsch"],
            "brands": ["Fender", "Gibson"],
            "characteristics": ["single coil pickups", "smooth sustain", "expressive bends"]
        },
        "jimi hendrix": {
            "primary": ["Fender Stratocaster"],
            "also_used": ["Gibson Flying V", "Gibson SG"],
            "brands": ["Fender", "Gibson"],
            "characteristics": ["single coil pickups", "bright tone", "feedback-friendly"]
        },
        "eric clapton": {
            "primary": ["Fender Stratocaster", "Gibson Les Paul"],
            "also_used": ["Gibson ES-335", "Martin Acoustic"],
            "brands": ["Fender", "Gibson", "Martin"],
            "characteristics": ["blues tone", "smooth sustain", "versatile"]
        },
        "bb king": {
            "primary": ["Gibson ES-355", "Gibson ES-335"],
            "also_used": ["Gibson Les Paul"],
            "brands": ["Gibson", "Epiphone"],
            "characteristics": ["semi-hollow body", "warm tone", "sustain"]
        },
        "slash": {
            "primary": ["Gibson Les Paul"],
            "also_used": ["Gibson ES-335", "B.C. Rich Mockingbird"],
            "brands": ["Gibson", "Epiphone"],
            "characteristics": ["humbucker pickups", "thick sustain", "rock tone"]
        },
        "eddie van halen": {
            "primary": ["Frankenstrat", "Kramer", "EVH Wolfgang"],
            "also_used": ["Charvel", "Peavey Wolfgang"],
            "brands": ["EVH", "Fender", "Charvel", "Kramer"],
            "characteristics": ["humbucker pickup", "floyd rose tremolo", "hot output"]
        },
        "john mayer": {
            "primary": ["Fender Stratocaster", "PRS Silver Sky"],
            "also_used": ["Martin Acoustic", "Gibson SG"],
            "brands": ["Fender", "PRS", "Martin"],
            "characteristics": ["single coil pickups", "clear tone", "versatile"]
        },
        "george benson": {
            "primary": ["Ibanez GB10", "Gibson L-5"],
            "also_used": ["Gibson ES-175"],
            "brands": ["Ibanez", "Gibson"],
            "characteristics": ["hollow body", "jazz tone", "warm and smooth"]
        },
        "kurt cobain": {
            "primary": ["Fender Jaguar", "Fender Mustang"],
            "also_used": ["Fender Stratocaster", "Gibson SG"],
            "brands": ["Fender", "Gibson"],
            "characteristics": ["offset body", "grunge tone", "alternative tunings"]
        }
    }
    
    # Genre-Guitar Mapping
    GENRE_GUITARS = {
        "blues": {
            "recommended_types": ["Stratocaster", "Les Paul", "ES-335", "Telecaster"],
            "pickups": ["single coil", "P90", "humbucker"],
            "brands": ["Fender", "Gibson", "Epiphone", "PRS"],
            "characteristics": ["warm tone", "good sustain", "expressive bends"],
            "price_range": (500, 3000)
        },
        "rock": {
            "recommended_types": ["Les Paul", "SG", "Stratocaster", "PRS Custom"],
            "pickups": ["humbucker", "high output", "active"],
            "brands": ["Gibson", "Fender", "PRS", "ESP", "Schecter"],
            "characteristics": ["versatile", "good sustain", "handles overdrive well"],
            "price_range": (600, 4000)
        },
        "metal": {
            "recommended_types": ["Ibanez RG", "Jackson Soloist", "ESP Eclipse", "Schecter Hellraiser", "ESP LTD"],
            "pickups": ["active pickups", "high output humbucker", "EMG 81/85", "Fishman Fluence"],
            "brands": ["Ibanez", "Jackson", "ESP", "Schecter", "Dean", "ESP LTD", "Jackson Pro"],
            "characteristics": ["fast neck", "floyd rose", "high output", "low action", "24 frets", "compound radius"],
            "price_range": (700, 3500)
        },
        "jazz": {
            "recommended_types": ["ES-175", "L-5", "Hollow body", "Semi-hollow"],
            "pickups": ["humbucker", "P90", "floating pickup"],
            "brands": ["Gibson", "Ibanez", "Gretsch", "D'Angelico", "Epiphone"],
            "characteristics": ["warm tone", "hollow/semi-hollow body", "smooth"],
            "price_range": (800, 5000)
        },
        "country": {
            "recommended_types": ["Telecaster", "Gretsch", "Acoustic"],
            "pickups": ["single coil", "TV Jones", "P90"],
            "brands": ["Fender", "Gretsch", "Gibson", "G&L"],
            "characteristics": ["twangy", "bright", "clear tone"],
            "price_range": (500, 3000)
        },
        "indie": {
            "recommended_types": ["Jaguar", "Jazzmaster", "Mustang", "Telecaster"],
            "pickups": ["single coil", "P90", "Jazzmaster pickups"],
            "brands": ["Fender", "Squier", "Reverend", "G&L"],
            "characteristics": ["unique tones", "offset body", "versatile"],
            "price_range": (400, 2000)
        },
        "funk": {
            "recommended_types": ["Stratocaster", "Telecaster", "Semi-hollow"],
            "pickups": ["single coil", "P90"],
            "brands": ["Fender", "Gibson", "PRS", "Ibanez"],
            "characteristics": ["bright", "percussive", "clear", "good rhythm tone"],
            "price_range": (500, 2500)
        }
    }
    
    # Skill Level Recommendations
    SKILL_LEVEL_GUITARS = {
        "beginner": {
            "considerations": ["comfortable neck", "stable tuning", "versatile", "affordable"],
            "recommended_types": ["Stratocaster", "Les Paul Special", "Yamaha Pacifica"],
            "brands": ["Squier", "Epiphone", "Yamaha", "Ibanez"],
            "price_range": (200, 700),
            "avoid": ["floyd rose", "complex electronics", "heavy guitars"]
        },
        "intermediate": {
            "considerations": ["better pickups", "improved hardware", "specific tone"],
            "recommended_types": ["Player Series", "Studio models", "SE models"],
            "brands": ["Fender", "Gibson", "PRS", "Ibanez", "ESP"],
            "price_range": (700, 2000),
            "features": ["coil tap", "locking tuners", "better woods"]
        },
        "advanced": {
            "considerations": ["professional features", "specific requirements", "tone woods"],
            "recommended_types": ["American/USA made", "Custom Shop", "Prestige"],
            "brands": ["Fender USA", "Gibson USA", "PRS Core", "Suhr", "Music Man"],
            "price_range": (1500, 5000),
            "features": ["boutique pickups", "nitro finish", "premium hardware"]
        },
        "professional": {
            "considerations": ["touring reliability", "unique tone", "custom specs"],
            "recommended_types": ["Custom Shop", "Masterbuilt", "Private Stock"],
            "brands": ["Any premium brand", "Custom builders"],
            "price_range": (3000, 10000),
            "features": ["artist specs", "rare woods", "custom electronics"]
        }
    }
    
    # Technical Features Explanation
    TECHNICAL_FEATURES = {
        "pickups": {
            "single_coil": {
                "tone": "bright, clear, articulate",
                "genres": ["blues", "country", "indie", "funk"],
                "pros": ["clarity", "note definition", "classic tone"],
                "cons": ["60-cycle hum", "less output"]
            },
            "humbucker": {
                "tone": "warm, thick, powerful",
                "genres": ["rock", "metal", "jazz", "blues"],
                "pros": ["no hum", "high output", "sustain"],
                "cons": ["less clarity", "can be muddy"]
            },
            "p90": {
                "tone": "midrange focused, gritty",
                "genres": ["rock", "punk", "blues", "indie"],
                "pros": ["unique tone", "good dynamics"],
                "cons": ["some hum", "specific sound"]
            },
            "active": {
                "tone": "high output, compressed",
                "genres": ["metal", "hard rock"],
                "pros": ["consistent tone", "high gain", "quiet"],
                "cons": ["needs battery", "less dynamic"]
            }
        },
        "body_types": {
            "solid_body": {
                "characteristics": ["sustain", "feedback resistant", "versatile"],
                "weight": "heavier",
                "genres": ["rock", "metal", "blues", "country"]
            },
            "hollow_body": {
                "characteristics": ["warm", "acoustic-like", "resonant"],
                "weight": "lighter",
                "genres": ["jazz", "rockabilly", "blues"]
            },
            "semi_hollow": {
                "characteristics": ["balanced", "some resonance", "versatile"],
                "weight": "medium",
                "genres": ["blues", "rock", "jazz", "indie"]
            }
        },
        "neck_profiles": {
            "c_shape": "comfortable, versatile, most common",
            "d_shape": "fuller, vintage feel",
            "u_shape": "thick, vintage, baseball bat",
            "v_shape": "vintage, good for thumb-over players",
            "slim/fast": "thin, good for speed and small hands"
        },
        "scale_length": {
            "24.75": "Gibson scale, warmer, easier bends",
            "25.5": "Fender scale, brighter, more tension",
            "24": "PRS scale, compromise between Gibson and Fender"
        }
    }
    
    # Brand Quality Tiers
    BRAND_TIERS = {
        "budget": {
            "brands": ["Squier", "Epiphone", "Yamaha", "Harley Benton", "Jackson JS"],
            "price_range": (100, 500),
            "quality": "good for beginners, decent quality"
        },
        "mid_range": {
            "brands": ["Fender Player", "Epiphone Inspired", "PRS SE", "Ibanez", "Schecter"],
            "price_range": (500, 1500),
            "quality": "gigging quality, good value"
        },
        "high_end": {
            "brands": ["Fender American", "Gibson USA", "PRS S2/Core", "ESP", "Music Man"],
            "price_range": (1500, 4000),
            "quality": "professional quality, excellent craftsmanship"
        },
        "boutique": {
            "brands": ["Suhr", "Tom Anderson", "Collings", "PRS Private Stock", "Custom Shop"],
            "price_range": (3000, 10000),
            "quality": "exceptional quality, custom options"
        }
    }
    
    @classmethod
    def get_artist_info(cls, artist_name: str) -> Optional[Dict]:
        """Get guitar information for a specific artist"""
        artist_key = artist_name.lower().strip()
        for key, value in cls.ARTIST_GUITARS.items():
            if key in artist_key or artist_key in key:
                return value
        return None
    
    @classmethod
    def get_genre_recommendations(cls, genre: str) -> Optional[Dict]:
        """Get guitar recommendations for a genre"""
        genre_key = genre.lower().strip()
        for key, value in cls.GENRE_GUITARS.items():
            if key in genre_key or genre_key in key:
                return value
        return None
    
    @classmethod
    def get_skill_level_advice(cls, skill_level: str) -> Optional[Dict]:
        """Get recommendations based on skill level"""
        level_key = skill_level.lower().strip()
        for key, value in cls.SKILL_LEVEL_GUITARS.items():
            if key in level_key or level_key in key:
                return value
        return None
    
    @classmethod
    def explain_feature(cls, feature_type: str, feature_name: str) -> Optional[Dict]:
        """Explain a technical feature"""
        if feature_type in cls.TECHNICAL_FEATURES:
            features = cls.TECHNICAL_FEATURES[feature_type]
            for key, value in features.items():
                if key.replace('_', ' ') in feature_name.lower() or feature_name.lower() in key:
                    return value
        return None
    
    @classmethod
    def get_brand_tier(cls, brand: str) -> Optional[Dict]:
        """Get brand tier information"""
        brand_lower = brand.lower()
        for tier, info in cls.BRAND_TIERS.items():
            if any(brand_lower in b.lower() or b.lower() in brand_lower for b in info["brands"]):
                return {"tier": tier, **info}
        return None
    
    @classmethod
    def generate_knowledge_prompt(cls, user_query: str, search_params: Dict) -> str:
        """Generate a knowledge-enhanced prompt for the agent"""
        knowledge_parts = []
        
        # Add artist knowledge
        if search_params.get("artist_reference"):
            artist_info = cls.get_artist_info(search_params["artist_reference"])
            if artist_info:
                knowledge_parts.append(
                    f"Artist {search_params['artist_reference']} is known for: "
                    f"Primary guitars: {', '.join(artist_info['primary'])}, "
                    f"Tone characteristics: {', '.join(artist_info['characteristics'])}"
                )
        
        # Add genre knowledge
        if search_params.get("musical_style"):
            genre_info = cls.get_genre_recommendations(search_params["musical_style"])
            if genre_info:
                knowledge_parts.append(
                    f"For {search_params['musical_style']}: "
                    f"Recommended types: {', '.join(genre_info['recommended_types'][:3])}, "
                    f"Key characteristics: {', '.join(genre_info['characteristics'])}"
                )
        
        # Add skill level knowledge
        if search_params.get("skill_level"):
            skill_info = cls.get_skill_level_advice(search_params["skill_level"])
            if skill_info:
                knowledge_parts.append(
                    f"For {search_params['skill_level']} players: "
                    f"Consider: {', '.join(skill_info['considerations'][:3])}, "
                    f"Price range: ${skill_info['price_range'][0]}-${skill_info['price_range'][1]}"
                )
        
        return "\n".join(knowledge_parts) if knowledge_parts else ""