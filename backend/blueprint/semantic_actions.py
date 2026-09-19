"""
Semantic Action Library
Maps semantic action IDs to animation sequences.
This is the single source of truth for all game animations.
"""

from typing import Dict, Optional
from backend.models import ActionSequence, AnimationAction


class SemanticActionLibrary:
    """
    Central repository of all semantic actions and their animation sequences.
    
    Semantic Action = Meaning-based ID that describes what happens
    Examples:
        - "daughter_recognition_success" (not "animation_01.mp4")
        - "wrong_answer_encouragement" (not "clip_005.mp4")
        - "show_memory_cue" (not "vid_23.mp4")
    """
    
    def __init__(self):
        self.actions: Dict[str, ActionSequence] = {}
        self._initialize_actions()
    
    def _initialize_actions(self):
        """Initialize all semantic actions."""
        
        # =====================================================================
        # SCENE TRANSITIONS
        # =====================================================================
        
        self.actions["house_intro"] = ActionSequence(
            id="house_intro",
            description="Introduce patient to familiar house environment",
            actions=[
                AnimationAction(id="house_camera_pan", duration=2.0),
                AnimationAction(id="mother_idle", duration=1.0),
            ],
            outcome_narration=""
        )
        
        self.actions["continue_to_kitchen"] = ActionSequence(
            id="continue_to_kitchen",
            description="Transition to kitchen - patient clicks Yes",
            actions=[
                AnimationAction(id="fade_transition", duration=1.0),
                AnimationAction(id="kitchen_camera_transition", duration=2.0),
                AnimationAction(id="show_chapathi", duration=1.0),
                AnimationAction(id="mother_looks_at_food", duration=1.0),
            ],
            outcome_narration="Here's the kitchen where you spent so much time..."
        )
        
        self.actions["gentle_continue_to_kitchen"] = ActionSequence(
            id="gentle_continue_to_kitchen",
            description="Transition to kitchen - patient unsure, gentle approach",
            actions=[
                AnimationAction(id="fade_transition", duration=1.0),
                AnimationAction(id="gentle_narration_play", duration=2.0),
                AnimationAction(id="kitchen_camera_transition", duration=2.0),
                AnimationAction(id="show_chapathi", duration=1.0),
            ],
            outcome_narration="That's okay. Let me help you remember."
        )
        
        # =====================================================================
        # CORRECT ANSWERS - PERSON RECOGNITION
        # =====================================================================
        
        self.actions["daughter_recognition_success"] = ActionSequence(
            id="daughter_recognition_success",
            description="Patient correctly identifies daughter Anu",
            actions=[
                AnimationAction(id="daughter_appear", duration=1.0),
                AnimationAction(id="daughter_smile", duration=1.0),
                AnimationAction(id="daughter_walk_to_mother", duration=2.0),
                AnimationAction(id="daughter_hug_mother", duration=2.0),
                AnimationAction(id="reward_celebrate", duration=2.0),
            ],
            outcome_narration="Yes! That's Anu, your daughter. She always cooked with you."
        )
        
        # =====================================================================
        # WRONG ANSWERS - ENCOURAGEMENT & MEMORY CUES
        # =====================================================================
        
        self.actions["wrong_answer_encouragement"] = ActionSequence(
            id="wrong_answer_encouragement",
            description="Patient selected wrong answer, gentle encouragement",
            actions=[
                AnimationAction(id="daughter_encourage", duration=1.5),
                AnimationAction(id="narration_cue_play", duration=2.0),
            ],
            outcome_narration="That's okay. Let's remember together..."
        )
        
        self.actions["show_memory_cue"] = ActionSequence(
            id="show_memory_cue",
            description="Show visual memory cue - kitchen and chapathi",
            actions=[
                AnimationAction(id="show_anu_cooking", duration=2.0),
                AnimationAction(id="show_chapathi_highlight", duration=2.0),
                AnimationAction(id="memory_hint_narration", duration=2.0),
            ],
            outcome_narration="She used to cook chapathi with you here in the kitchen."
        )
        
        self.actions["stronger_hint_daughter"] = ActionSequence(
            id="stronger_hint_daughter",
            description="Stronger hint - show daughter's face with name hint",
            actions=[
                AnimationAction(id="show_anu_face", duration=1.5),
                AnimationAction(id="narration_hint_name", duration=2.0),
                AnimationAction(id="show_anu_name_partial", duration=2.0),
            ],
            outcome_narration="Her name starts with A... Do you remember?"
        )
        
        self.actions["reveal_answer_fully"] = ActionSequence(
            id="reveal_answer_fully",
            description="Full reveal of correct answer with context",
            actions=[
                AnimationAction(id="show_daughter_full_image", duration=1.5),
                AnimationAction(id="show_anu_name_full", duration=1.0),
                AnimationAction(id="show_family_together", duration=2.0),
                AnimationAction(id="narration_full_reveal", duration=3.0),
            ],
            outcome_narration="This is your daughter Anu. She loved cooking with you."
        )
        
        # =====================================================================
        # FOOD RECOGNITION
        # =====================================================================
        
        self.actions["food_recognition_success"] = ActionSequence(
            id="food_recognition_success",
            description="Patient correctly identifies food (chapathi)",
            actions=[
                AnimationAction(id="show_chapathi_success", duration=1.5),
                AnimationAction(id="anu_cooking_animation", duration=2.0),
                AnimationAction(id="food_smell_animation", duration=1.5),
                AnimationAction(id="family_meal", duration=2.0),
            ],
            outcome_narration="Yes! Chapathi - Anu made this so well. You two cooked together."
        )
        
        self.actions["show_food_chapathi"] = ActionSequence(
            id="show_food_chapathi",
            description="Display chapathi as memory anchor",
            actions=[
                AnimationAction(id="show_chapathi_closeup", duration=2.0),
                AnimationAction(id="show_chapathi_cooking", duration=2.0),
            ],
            outcome_narration="Remember this? Chapathi, fresh from the pan."
        )
        
        # =====================================================================
        # FAMILY ASSOCIATION
        # =====================================================================
        
        self.actions["family_recognition_success"] = ActionSequence(
            id="family_recognition_success",
            description="Patient recognizes family member correctly",
            actions=[
                AnimationAction(id="show_family_member", duration=1.5),
                AnimationAction(id="family_warmth_animation", duration=1.5),
                AnimationAction(id="family_together_animation", duration=2.0),
                AnimationAction(id="family_meal_animation", duration=2.0),
            ],
            outcome_narration="Yes! Family is so important. These are your precious memories."
        )
        
        # =====================================================================
        # GENERAL TRANSITIONS & UTILITY
        # =====================================================================
        
        self.actions["enter_kitchen"] = ActionSequence(
            id="enter_kitchen",
            description="Enter the kitchen scene",
            actions=[
                AnimationAction(id="kitchen_camera_pan", duration=2.0),
                AnimationAction(id="show_kitchen_objects", duration=1.5),
            ],
            outcome_narration="Look, the kitchen..."
        )
        
        self.actions["positive_feedback"] = ActionSequence(
            id="positive_feedback",
            description="General positive feedback after correct answer",
            actions=[
                AnimationAction(id="celebration_animation", duration=2.0),
                AnimationAction(id="positive_narration", duration=1.5),
            ],
            outcome_narration="Wonderful! You remembered!"
        )
        
        self.actions["final_reward"] = ActionSequence(
            id="final_reward",
            description="Final reward animation for end of game",
            actions=[
                AnimationAction(id="family_gathering", duration=2.0),
                AnimationAction(id="celebration_lights", duration=2.0),
                AnimationAction(id="happy_music_play", duration=3.0),
                AnimationAction(id="narration_proud", duration=2.0),
            ],
            outcome_narration="You did so well today! Your family is proud of you."
        )
        
        self.actions["reward_celebrate"] = ActionSequence(
            id="reward_celebrate",
            description="Celebration for correct recognition",
            actions=[
                AnimationAction(id="celebration_animation", duration=2.0),
                AnimationAction(id="positive_sound", duration=1.0),
            ],
            outcome_narration="Wonderful!"
        )
        
        self.actions["positive_feedback_animation"] = ActionSequence(
            id="positive_feedback_animation",
            description="Short positive feedback",
            actions=[
                AnimationAction(id="smile_animation", duration=1.0),
                AnimationAction(id="positive_sound", duration=0.5),
            ],
            outcome_narration="Great!"
        )
    
    def get_action_sequence(self, action_id: str) -> Optional[ActionSequence]:
        """Get action sequence by semantic ID."""
        return self.actions.get(action_id)
    
    def validate_action_sequence(self, action_id: str) -> bool:
        """Check if action sequence exists."""
        return action_id in self.actions
    
    def list_all_actions(self):
        """Return list of all available action IDs."""
        return list(self.actions.keys())
    
    def get_action_description(self, action_id: str) -> Optional[str]:
        """Get human-readable description of an action."""
        action = self.get_action_sequence(action_id)
        return action.description if action else None


# ============================================================================
# ASSET MANIFEST - Maps semantic IDs to file paths
# ============================================================================

class AssetManifest:
    """
    Maps semantic asset IDs to actual file paths.
    This allows separating logic (blueprint with semantic IDs) from
    media (actual animation/image files).
    """
    
    # Character assets
    CHARACTER_ASSETS = {
        "daughter_anu": "assets/characters/anu.png",
        "son_rahul": "assets/characters/rahul.png",
        "mother_lakshmi": "assets/characters/mother.png",
    }
    
    # Environment assets
    ENVIRONMENT_ASSETS = {
        "family_house_front": "assets/environments/house_front.png",
        "family_kitchen": "assets/environments/kitchen.png",
        "family_temple": "assets/environments/temple.png",
    }
    
    # Memory/food assets
    MEMORY_ASSETS = {
        "chapathi": "assets/food/chapathi.png",
        "rice": "assets/food/rice.png",
        "banana": "assets/food/banana.png",
        "family_meal": "assets/memories/family_meal.png",
        "anu_cooking": "assets/memories/anu_cooking.png",
    }
    
    # Animation files
    ANIMATION_ASSETS = {
        "daughter_appear": "assets/animations/daughter_appear.mp4",
        "daughter_smile": "assets/animations/daughter_smile.mp4",
        "daughter_walk_to_mother": "assets/animations/daughter_walk_to_mother.mp4",
        "daughter_hug_mother": "assets/animations/daughter_hug_mother.mp4",
        "celebration_animation": "assets/animations/celebration.mp4",
        "happy_music_play": "assets/animations/happy_music.mp3",
    }
    
    @classmethod
    def get_asset_path(cls, asset_type: str, asset_id: str) -> Optional[str]:
        """Get file path for an asset."""
        asset_maps = {
            "character": cls.CHARACTER_ASSETS,
            "environment": cls.ENVIRONMENT_ASSETS,
            "memory": cls.MEMORY_ASSETS,
            "animation": cls.ANIMATION_ASSETS,
        }
        
        if asset_type in asset_maps:
            return asset_maps[asset_type].get(asset_id)
        return None
