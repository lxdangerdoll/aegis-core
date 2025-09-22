"""
CDL Integration with AI Pipeline Prompt System
"""

import logging
from typing import Dict, Optional
from pathlib import Path

from src.characters.models.character import Character
from src.characters.cdl.parser import load_character

logger = logging.getLogger(__name__)


class CDLAIPromptIntegration:
    """Integrates CDL character definitions with AI pipeline results."""

    def __init__(self, vector_memory_manager=None):
        self.memory_manager = vector_memory_manager
        self.characters_cache = {}

    async def create_character_aware_prompt(
        self,
        character_file: str,
        user_id: str,
        message_content: str,
        pipeline_result=None
    ) -> str:
        """Create a character-aware prompt."""
        try:
            character = await self.load_character(character_file)
            logger.info(f"Loaded CDL character: {character.identity.name}")

            # Build comprehensive character prompt with personality details
            personality_values = getattr(character.personality, 'values', [])
            speech_patterns = getattr(character.identity.voice, 'speech_patterns', [])
            favorite_phrases = getattr(character.identity.voice, 'favorite_phrases', [])
            quirks = getattr(character.personality, 'quirks', [])
            
            prompt = f"""You are {character.identity.name}, a {character.identity.age}-year-old {character.identity.occupation} in {character.identity.location}.

PERSONALITY:
{character.identity.description}

VOICE & COMMUNICATION STYLE:
- Tone: {getattr(character.identity.voice, 'tone', 'Natural and authentic')}
- Pace: {getattr(character.identity.voice, 'pace', 'Normal conversational pace')}
- Vocabulary: {getattr(character.identity.voice, 'vocabulary_level', 'Natural vocabulary')}"""

            if speech_patterns:
                prompt += f"\n- Speech patterns: {', '.join(speech_patterns[:3])}"
            
            if favorite_phrases:
                prompt += f"\n- Favorite phrases: {', '.join(favorite_phrases[:3])}"

            if personality_values:
                prompt += f"\n\nCORE VALUES: {', '.join(personality_values[:4])}"

            if quirks:
                prompt += f"\n\nPERSONALITY QUIRKS: {', '.join(quirks[:3])}"

            # 🎭 EMOTION INTEGRATION: Add real-time emotional intelligence to character prompt
            if pipeline_result:
                prompt += "\n\nREAL-TIME CONTEXT AWARENESS:"
                
                logger.debug("🎭 CDL EMOTION DEBUG: Processing pipeline result")
                logger.debug("  - Has emotional_state: %s", bool(pipeline_result.emotional_state))
                logger.debug("  - Has mood_assessment: %s", bool(pipeline_result.mood_assessment))
                
                # Add emotional state awareness
                if pipeline_result.emotional_state:
                    prompt += f"\n- User's current emotional state: {pipeline_result.emotional_state}"
                    logger.debug("  - Added emotional_state to prompt: %s", pipeline_result.emotional_state)
                
                # Enhanced emotion analysis integration
                if pipeline_result.mood_assessment and isinstance(pipeline_result.mood_assessment, dict):
                    mood_data = pipeline_result.mood_assessment
                    logger.debug("  - Processing mood_assessment data with keys: %s", 
                               list(mood_data.keys()) if mood_data else [])
                    
                    # Use primary emotion from comprehensive analysis
                    primary_emotion = mood_data.get('primary_emotion')
                    confidence = mood_data.get('confidence', 0)
                    
                    if primary_emotion and confidence > 0.5:
                        prompt += f"\n- Detected emotion: {primary_emotion} (confidence: {confidence:.1f})"
                        logger.debug("  - Added primary emotion to prompt: %s (%.2f)", primary_emotion, confidence)
                        
                        # Add intensity context if available
                        intensity = mood_data.get('intensity')
                        if intensity and isinstance(intensity, (int, float)) and intensity > 0.6:
                            prompt += f"\n- Emotional intensity: {intensity:.1f} (strong emotional state)"
                        
                        # Add support recommendations if needed
                        if mood_data.get('support_needed'):
                            prompt += "\n- User may need emotional support and understanding"
                        
                        # Include specific recommendations from emotion analysis
                        recommendations = mood_data.get('recommendations')
                        if recommendations and isinstance(recommendations, list) and len(recommendations) > 0:
                            # Take up to 2 most relevant recommendations
                            relevant_recs = recommendations[:2]
                            for rec in relevant_recs:
                                if isinstance(rec, str) and len(rec) < 100:  # Keep recommendations concise
                                    prompt += f"\n- Guidance: {rec}"
                        
                        # Enhanced emotion-appropriate response guidance
                        emotion_guidance = {
                            'joy': 'Share in their positive energy and enthusiasm',
                            'excitement': 'Match their enthusiasm while staying authentic to your character',
                            'happiness': 'Celebrate their positive mood with warmth',
                            'sadness': 'Show empathy and support while remaining genuine',
                            'melancholy': 'Offer gentle understanding and compassionate presence',
                            'frustration': 'Acknowledge their feelings and offer perspective',
                            'anxiety': 'Provide calm, reassuring responses',
                            'worry': 'Offer gentle reassurance and practical support',
                            'anger': 'Stay calm and avoid escalating the situation',
                            'irritation': 'Be patient and understanding',
                            'fear': 'Offer gentle reassurance and support',
                            'stress': 'Provide calming, supportive responses',
                            'overwhelmed': 'Break things down into manageable parts',
                            'neutral': 'Maintain your natural conversational style',
                            'contemplative': 'Engage thoughtfully with their reflections',
                            'curious': 'Encourage their exploration and questions'
                        }
                        
                        guidance = emotion_guidance.get(primary_emotion, 'Respond naturally and authentically')
                        prompt += f"\n- Response approach: {guidance}"
                        
                        # Add emotional intelligence context if available
                        if 'emotional_intelligence' in mood_data:
                            ei_data = mood_data['emotional_intelligence']
                            
                            # Include stress indicators for context
                            stress_indicators = ei_data.get('stress_indicators', [])
                            if stress_indicators and len(stress_indicators) > 0:
                                prompt += f"\n- Stress indicators detected: {len(stress_indicators)} signals present"
                            
                            # Include mood trend for response adaptation
                            mood_trend = ei_data.get('mood_trend', 'stable')
                            if mood_trend != 'stable':
                                trend_guidance = {
                                    'improving': 'Build on their positive momentum',
                                    'declining': 'Offer gentle support and encouragement',
                                    'fluctuating': 'Provide stable, consistent presence'
                                }
                                trend_advice = trend_guidance.get(mood_trend, 'Monitor their emotional needs')
                                prompt += f"\n- Mood trend ({mood_trend}): {trend_advice}"
                
                # Add personality context if available
                if pipeline_result.personality_profile and isinstance(pipeline_result.personality_profile, dict):
                    personality_insights = pipeline_result.personality_profile.get('personality_summary')
                    if personality_insights:
                        prompt += f"\n- User personality insights: {personality_insights[:100]}..."
                
                # Add conversation context
                if pipeline_result.enhanced_context and isinstance(pipeline_result.enhanced_context, dict):
                    conversation_mode = pipeline_result.enhanced_context.get('conversation_mode')
                    if conversation_mode:
                        prompt += f"\n- Conversation mode: {conversation_mode}"
                        
                prompt += f"\n\nADAPT your response style to be emotionally appropriate while staying true to {character.identity.name}'s personality."


            prompt += f"""

CRITICAL INSTRUCTIONS:
- You are a {character.identity.occupation}, not a poet or mystical character
- Use normal, conversational language appropriate for your profession
- Avoid overly poetic, mystical, or fantasy-style language unless it genuinely fits your character
- Be enthusiastic about your work but use authentic, professional language
- Reference topics and terminology relevant to your field and background
- Speak like a real person having a conversation

Respond as {character.identity.name}:"""

            return prompt

        except Exception as e:
            logger.error(f"CDL integration failed: {e}")
            raise

    async def load_character(self, character_file: str) -> Character:
        """Load a character from CDL file."""
        try:
            if character_file in self.characters_cache:
                return self.characters_cache[character_file]

            character_path = Path("characters") / character_file
            if not character_path.exists():
                character_path = Path(character_file)

            character = load_character(character_path)
            self.characters_cache[character_file] = character
            return character

        except Exception as e:
            logger.error(f"Failed to load character {character_file}: {e}")
            raise


async def load_character_definitions(characters_dir: str = "characters") -> Dict[str, Character]:
    """Load all character definitions from directory."""
    characters = {}
    characters_path = Path(characters_dir)

    if not characters_path.exists():
        logger.warning(f"Characters directory not found: {characters_dir}")
        return characters

    for file_path in characters_path.rglob("*.json"):
        try:
            character_name = file_path.stem
            character = load_character(file_path)
            characters[character_name] = character
            logger.info(f"Loaded character: {character_name}")
        except Exception as e:
            logger.error(f"Failed to load character from {file_path}: {e}")

    return characters