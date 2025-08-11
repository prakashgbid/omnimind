#!/usr/bin/env python3
"""
OSA Thinking States - Whimsical status messages
Adds personality and fun to the waiting experience
"""

import random
import time
import asyncio
from typing import List, Optional, Tuple
from enum import Enum


class ThinkingCategory(Enum):
    """Categories of thinking states"""
    WHIMSICAL = "whimsical"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    SCIENTIFIC = "scientific"
    CULINARY = "culinary"
    MYSTICAL = "mystical"
    MUSICAL = "musical"
    NATURE = "nature"


class ThinkingStates:
    """Collection of whimsical thinking states"""
    
    # Whimsical/Playful states
    WHIMSICAL_STATES = [
        "Flibbertigibbeting",
        "Ruminating",
        "Cogitating",
        "Pondering",
        "Noodling",
        "Mulling",
        "Contemplating",
        "Ideating",
        "Brainstorming",
        "Scheming",
        "Daydreaming",
        "Woolgathering",
        "Musing",
        "Deliberating",
        "Puzzling",
        "Wondering",
        "Meandering",
        "Perambulating",
        "Circumlocuting",
        "Discombobulating"
    ]
    
    # Technical/Programming states
    TECHNICAL_STATES = [
        "Compiling thoughts",
        "Parsing neurons",
        "Tokenizing ideas",
        "Optimizing synapses",
        "Refactoring logic",
        "Debugging reality",
        "Garbage collecting",
        "Cache warming",
        "Indexing knowledge",
        "Hashing possibilities",
        "Threading concepts",
        "Pipelining thoughts",
        "Vectorizing ideas",
        "Quantizing wisdom",
        "Backpropagating",
        "Gradient descending",
        "Neural networking",
        "Bit shifting",
        "Memory mapping",
        "Stack tracing"
    ]
    
    # Creative/Artistic states
    CREATIVE_STATES = [
        "Sculpting ideas",
        "Painting thoughts",
        "Composing responses",
        "Choreographing logic",
        "Sketching solutions",
        "Drafting plans",
        "Weaving narratives",
        "Crafting wisdom",
        "Molding concepts",
        "Etching patterns",
        "Carving pathways",
        "Embroidering details",
        "Quilting knowledge",
        "Origami folding",
        "Pottery wheeling",
        "Glass blowing ideas",
        "Woodworking thoughts",
        "Knitting neurons",
        "Crocheting connections",
        "Collaging concepts"
    ]
    
    # Scientific/Academic states
    SCIENTIFIC_STATES = [
        "Hypothesizing",
        "Theorizing",
        "Experimenting",
        "Analyzing samples",
        "Peer reviewing",
        "Calibrating instruments",
        "Measuring quanta",
        "Observing phenomena",
        "Crystallizing thoughts",
        "Distilling essence",
        "Synthesizing compounds",
        "Catalyzing reactions",
        "Precipitating solutions",
        "Centrifuging ideas",
        "Titrating knowledge",
        "Spectroscopy scanning",
        "Microscoping details",
        "Telescoping visions",
        "Particle accelerating",
        "Quantum entangling"
    ]
    
    # Culinary/Food states
    CULINARY_STATES = [
        "Marinating thoughts",
        "Simmering ideas",
        "Brewing solutions",
        "Percolating wisdom",
        "Steeping knowledge",
        "Fermenting concepts",
        "Baking insights",
        "Sautéing synapses",
        "Roasting reasoning",
        "Grilling questions",
        "Whisking wisdom",
        "Kneading knowledge",
        "Seasoning solutions",
        "Garnishing thoughts",
        "Plating presentations",
        "Caramelizing concepts",
        "Blanching basics",
        "Reducing complexity",
        "Emulsifying elements",
        "Flambéing facts"
    ]
    
    # Mystical/Magical states
    MYSTICAL_STATES = [
        "Divining answers",
        "Channeling cosmos",
        "Summoning wisdom",
        "Enchanting electrons",
        "Conjuring solutions",
        "Alchemizing ideas",
        "Transmuting thoughts",
        "Crystalball gazing",
        "Tarot reading",
        "Rune casting",
        "Astral projecting",
        "Mind melding",
        "Spirit walking",
        "Dream weaving",
        "Oracle consulting",
        "Sage burning",
        "Chakra aligning",
        "Aura reading",
        "Ley line tapping",
        "Phoenix rising"
    ]
    
    # Musical/Rhythmic states
    MUSICAL_STATES = [
        "Harmonizing thoughts",
        "Orchestrating ideas",
        "Composing symphonies",
        "Tuning frequencies",
        "Jamming neurons",
        "Beatboxing bytes",
        "Remixing reality",
        "Sampling solutions",
        "DJing data",
        "Conducting concerts",
        "Improvising jazz",
        "Syncopating synapses",
        "Crescendoing concepts",
        "Diminuendo-ing details",
        "Arpeggiating arrays",
        "Modulating melodies",
        "Transposing thoughts",
        "Vibing vibrations",
        "Riffing rhythms",
        "Freestyling flows"
    ]
    
    # Nature/Environmental states
    NATURE_STATES = [
        "Photosynthesizing",
        "Pollinating ideas",
        "Germinating thoughts",
        "Sprouting solutions",
        "Blossoming brilliance",
        "Weathering wisdom",
        "Precipitating patterns",
        "Evaporating excess",
        "Condensing concepts",
        "Crystallizing clarity",
        "Sedimenting sense",
        "Eroding errors",
        "Flowing freely",
        "Meandering minds",
        "Cascading consciousness",
        "Tidal thinking",
        "Volcanic visioning",
        "Earthquaking epiphanies",
        "Aurora borealis-ing",
        "Rainbow refracting"
    ]
    
    @classmethod
    def get_random_state(cls, category: Optional[ThinkingCategory] = None) -> str:
        """Get a random thinking state"""
        if category is None:
            # Pick from all categories
            all_states = (
                cls.WHIMSICAL_STATES + 
                cls.TECHNICAL_STATES + 
                cls.CREATIVE_STATES +
                cls.SCIENTIFIC_STATES +
                cls.CULINARY_STATES +
                cls.MYSTICAL_STATES +
                cls.MUSICAL_STATES +
                cls.NATURE_STATES
            )
            return random.choice(all_states)
        
        # Pick from specific category
        category_map = {
            ThinkingCategory.WHIMSICAL: cls.WHIMSICAL_STATES,
            ThinkingCategory.TECHNICAL: cls.TECHNICAL_STATES,
            ThinkingCategory.CREATIVE: cls.CREATIVE_STATES,
            ThinkingCategory.SCIENTIFIC: cls.SCIENTIFIC_STATES,
            ThinkingCategory.CULINARY: cls.CULINARY_STATES,
            ThinkingCategory.MYSTICAL: cls.MYSTICAL_STATES,
            ThinkingCategory.MUSICAL: cls.MUSICAL_STATES,
            ThinkingCategory.NATURE: cls.NATURE_STATES
        }
        
        states = category_map.get(category, cls.WHIMSICAL_STATES)
        return random.choice(states)
    
    @classmethod
    def get_contextual_state(cls, prompt: str) -> str:
        """Get a thinking state based on context"""
        prompt_lower = prompt.lower()
        
        # Choose category based on keywords
        if any(word in prompt_lower for word in ['code', 'debug', 'program', 'function', 'api']):
            return cls.get_random_state(ThinkingCategory.TECHNICAL)
        elif any(word in prompt_lower for word in ['create', 'design', 'draw', 'write', 'story']):
            return cls.get_random_state(ThinkingCategory.CREATIVE)
        elif any(word in prompt_lower for word in ['science', 'research', 'study', 'analyze', 'data']):
            return cls.get_random_state(ThinkingCategory.SCIENTIFIC)
        elif any(word in prompt_lower for word in ['recipe', 'cook', 'food', 'eat', 'taste']):
            return cls.get_random_state(ThinkingCategory.CULINARY)
        elif any(word in prompt_lower for word in ['music', 'song', 'rhythm', 'beat', 'melody']):
            return cls.get_random_state(ThinkingCategory.MUSICAL)
        elif any(word in prompt_lower for word in ['nature', 'environment', 'weather', 'plant', 'animal']):
            return cls.get_random_state(ThinkingCategory.NATURE)
        elif any(word in prompt_lower for word in ['magic', 'mystery', 'spiritual', 'cosmic', 'universe']):
            return cls.get_random_state(ThinkingCategory.MYSTICAL)
        else:
            return cls.get_random_state(ThinkingCategory.WHIMSICAL)


class ThinkingAnimator:
    """Handles animated thinking indicators (future enhancement)"""
    
    # Simple text-based animations for now
    SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    DOTS_FRAMES = ['.', '..', '...', '....', '.....', '......']
    PULSE_FRAMES = ['◯', '◉', '●', '◉', '◯']
    WAVE_FRAMES = ['≈', '≋', '≈', '~', '≈', '≋']
    STAR_FRAMES = ['✦', '✧', '✨', '✧', '✦']
    BRAIN_FRAMES = ['🧠', '🤯', '💭', '💡', '🧠']
    
    def __init__(self, animation_type: str = "spinner"):
        self.animation_type = animation_type
        self.current_frame = 0
        self.frames = self._get_frames(animation_type)
        self.running = False
        
    def _get_frames(self, animation_type: str) -> List[str]:
        """Get animation frames based on type"""
        animations = {
            "spinner": self.SPINNER_FRAMES,
            "dots": self.DOTS_FRAMES,
            "pulse": self.PULSE_FRAMES,
            "wave": self.WAVE_FRAMES,
            "star": self.STAR_FRAMES,
            "brain": self.BRAIN_FRAMES
        }
        return animations.get(animation_type, self.SPINNER_FRAMES)
    
    def next_frame(self) -> str:
        """Get the next animation frame"""
        frame = self.frames[self.current_frame]
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        return frame
    
    async def animate(self, message: str = "", delay: float = 0.1) -> None:
        """Run animation loop (for future implementation)"""
        self.running = True
        while self.running:
            frame = self.next_frame()
            # This would update the display in place
            print(f"\r{frame} {message}", end='', flush=True)
            await asyncio.sleep(delay)
    
    def stop(self) -> None:
        """Stop the animation"""
        self.running = False


class ThinkingEffects:
    """Special effects for thinking states (future enhancement)"""
    
    @staticmethod
    def rainbow_text(text: str) -> str:
        """Apply rainbow colors to text (ANSI)"""
        colors = [
            '\033[91m',  # Red
            '\033[93m',  # Yellow
            '\033[92m',  # Green
            '\033[96m',  # Cyan
            '\033[94m',  # Blue
            '\033[95m',  # Magenta
        ]
        
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                color = colors[i % len(colors)]
                result += f"{color}{char}"
            else:
                result += char
        
        return result + '\033[0m'
    
    @staticmethod
    def typewriter_effect(text: str, delay: float = 0.05) -> None:
        """Simulate typewriter effect (for future use)"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    @staticmethod
    def glitch_effect(text: str) -> str:
        """Add glitch characters for tech states"""
        glitch_chars = ['░', '▒', '▓', '█', '▄', '▀', '▌', '▐']
        
        # Randomly replace some characters
        result = list(text)
        for _ in range(len(text) // 10):  # Glitch 10% of characters
            pos = random.randint(0, len(result) - 1)
            if result[pos] != ' ':
                result[pos] = random.choice(glitch_chars)
        
        return ''.join(result)


def get_thinking_state(prompt: str = "", contextual: bool = True) -> Tuple[str, str]:
    """
    Get a thinking state and optional animation
    Returns: (state_message, animation_type)
    """
    if contextual and prompt:
        state = ThinkingStates.get_contextual_state(prompt)
    else:
        state = ThinkingStates.get_random_state()
    
    # Choose appropriate animation based on state
    if "compiling" in state.lower() or "parsing" in state.lower():
        animation = "spinner"
    elif "brewing" in state.lower() or "marinating" in state.lower():
        animation = "dots"
    elif "crystallizing" in state.lower() or "quantum" in state.lower():
        animation = "pulse"
    elif "flowing" in state.lower() or "cascading" in state.lower():
        animation = "wave"
    elif "divining" in state.lower() or "channeling" in state.lower():
        animation = "star"
    else:
        animation = "brain"
    
    return state, animation


# For testing
if __name__ == "__main__":
    print("Random thinking states:")
    for _ in range(10):
        state, anim = get_thinking_state()
        print(f"  {state} [{anim}]")
    
    print("\nContextual states:")
    prompts = [
        "Write some Python code",
        "Create a beautiful story",
        "Analyze this data",
        "Give me a recipe",
        "What's the meaning of life?"
    ]
    
    for prompt in prompts:
        state, anim = get_thinking_state(prompt, contextual=True)
        print(f"  '{prompt[:20]}...' -> {state}")