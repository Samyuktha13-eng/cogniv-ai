"""
Asset Library - Defines all available animations and action sequences.
This is the "pre-created" animation library that Unity uses.
"""

from typing import Dict, Optional, List
from models import ActionSequence, AnimationAction


class AssetLibrary:
    """Manages all animation assets and action sequences."""
    
    def __init__(self):
        """Initialize the asset library with all "A Visit From Anu" animations."""
        self.action_sequences: Dict[str, ActionSequence] = {}
        self._initialize_animations()
    
    def _initialize_animations(self):
        """Define all animation sequences for "A Visit From Anu"."""
        
        # ==== SCENE INTRO ANIMATIONS ====
        
        self.action_sequences["house_intro"] = ActionSequence(
            id="house_intro",
            description="House intro with slow pan and mother idle",
            actions=[
                AnimationAction(id="house_camera_slow_pan", duration=3.0),
                AnimationAction(id="mother_idle", duration=2.0)
            ],
            outcome_narration="This is your home."
        )
        
        self.action_sequences["enter_kitchen"] = ActionSequence(
            id="enter_kitchen",
            description="Transition into kitchen and show chapathi",
            actions=[
                AnimationAction(id="camera_enter_kitchen", duration=2.5),
                AnimationAction(id="mother_look_around", duration=1.5),
                AnimationAction(id="show_food_chapathi", duration=1.0)
            ],
            outcome_narration="This is the kitchen where you made chapathi."
        )
        
        # ==== CORRECT ANSWER ANIMATIONS ====
        
        self.action_sequences["correct_answer_daughter"] = ActionSequence(
            id="correct_answer_daughter",
            description="Daughter recognizes mother, walks, hugs, celebration",
            actions=[
                AnimationAction(id="daughter_appear", duration=1.0),
                AnimationAction(id="daughter_smile", duration=1.0),
                AnimationAction(id="daughter_walk_to_mother", duration=2.0),
                AnimationAction(id="daughter_hug_mother", duration=2.0),
                AnimationAction(id="reward_celebrate", duration=2.0)
            ],
            outcome_narration="Yes! You remembered Anu. She is your daughter."
        )
        
        # ==== WRONG ANSWER ANIMATIONS ====
        
        self.action_sequences["wrong_answer_encouragement"] = ActionSequence(
            id="wrong_answer_encouragement",
            description="Gentle encouragement when patient gives wrong answer",
            actions=[
                AnimationAction(id="daughter_appear", duration=1.0),
                AnimationAction(id="daughter_smile", duration=1.0),
                AnimationAction(id="daughter_gentle_gesture_to_kitchen", duration=1.5)
            ],
            outcome_narration="That's okay. Let's remember together."
        )
        
        self.action_sequences["show_memory_cue"] = ActionSequence(
            id="show_memory_cue",
            description="Show memory cue with Anu cooking",
            actions=[
                AnimationAction(id="fade_to_memory", duration=1.0),
                AnimationAction(id="show_anu_cooking_image", duration=2.0)
            ],
            outcome_narration="She used to cook chapathi with you here."
        )
        
        # ==== STRONGER HINT ANIMATIONS ====
        
        self.action_sequences["stronger_hint_daughter"] = ActionSequence(
            id="stronger_hint_daughter",
            description="Stronger hint - show Anu cooking with name clue",
            actions=[
                AnimationAction(id="daughter_appear", duration=1.0),
                AnimationAction(id="daughter_cooking", duration=2.0),
                AnimationAction(id="daughter_turn_and_smile", duration=1.0),
                AnimationAction(id="show_name_hint", duration=1.5)
            ],
            outcome_narration="You and Anu used to cook together. Her name starts with A..."
        )
        
        # ==== FOOD RECOGNITION ANIMATIONS ====
        
        self.action_sequences["correct_answer_food"] = ActionSequence(
            id="correct_answer_food",
            description="Food recognition correct - chapathi with reward",
            actions=[
                AnimationAction(id="show_food_chapathi", duration=1.0),
                AnimationAction(id="food_recognition_correct", duration=1.5),
                AnimationAction(id="daughter_smile", duration=1.0),
                AnimationAction(id="positive_feedback_animation", duration=1.5)
            ],
            outcome_narration="Yes! Chapathi."
        )
        
        # ==== FAMILY RECOGNITION ANIMATIONS ====
        
        self.action_sequences["correct_answer_family"] = ActionSequence(
            id="correct_answer_family",
            description="Family member recognition correct - Rahul",
            actions=[
                AnimationAction(id="show_family_meal_image", duration=1.5),
                AnimationAction(id="family_meal_animation", duration=2.0),
                AnimationAction(id="anu_and_rahul_smile", duration=1.0),
                AnimationAction(id="positive_feedback_animation", duration=1.5)
            ],
            outcome_narration="Yes. Rahul is with Anu."
        )
        
        # ==== FINAL REWARD ANIMATIONS ====
        
        self.action_sequences["final_reward"] = ActionSequence(
            id="final_reward",
            description="Final emotional reward - mother and daughter together",
            actions=[
                AnimationAction(id="daughter_appear", duration=1.0),
                AnimationAction(id="daughter_walk_to_mother", duration=2.0),
                AnimationAction(id="mother_and_daughter_smile", duration=1.0),
                AnimationAction(id="daughter_hug_mother", duration=2.0),
                AnimationAction(id="final_celebration", duration=3.0)
            ],
            outcome_narration="You remembered many familiar things today. It was nice spending time with your family memories."
        )
        
        # ==== REWARD/CELEBRATION ANIMATIONS ====
        
        self.action_sequences["reward_celebrate"] = ActionSequence(
            id="reward_celebrate",
            description="Celebration and reward animation",
            actions=[
                AnimationAction(id="daughter_smile", duration=1.0),
                AnimationAction(id="final_celebration", duration=2.0)
            ],
            outcome_narration="Wonderful!"
        )
        
        self.action_sequences["positive_feedback_animation"] = ActionSequence(
            id="positive_feedback_animation",
            description="Positive feedback animation",
            actions=[
                AnimationAction(id="positive_feedback", duration=1.5)
            ],
            outcome_narration="Great job!"
        )
        
        # ==== NEUTRAL TRANSITIONS (no wrong answer) ====
        
        self.action_sequences["continue_to_kitchen"] = ActionSequence(
            id="continue_to_kitchen",
            description="Positive transition to kitchen",
            actions=[
                AnimationAction(id="camera_transition", duration=1.5)
            ],
            outcome_narration="Good. Let's look inside."
        )
        
        self.action_sequences["gentle_continue_to_kitchen"] = ActionSequence(
            id="gentle_continue_to_kitchen",
            description="Gentle transition to kitchen",
            actions=[
                AnimationAction(id="mother_nod", duration=1.0),
                AnimationAction(id="camera_transition", duration=1.5)
            ],
            outcome_narration="That's okay. Let's explore together."
        )
    
    def get_action_sequence(self, action_id: str) -> Optional[ActionSequence]:
        """Get an action sequence by ID."""
        return self.action_sequences.get(action_id)
    
    def get_action_sequence_ids(self) -> List[str]:
        """Get all available action sequence IDs."""
        return list(self.action_sequences.keys())
    
    def validate_action_sequence(self, action_id: str) -> bool:
        """Check if an action sequence exists."""
        return action_id in self.action_sequences
    
    def get_all_action_ids_for_sequence(self, sequence_id: str) -> List[str]:
        """Get all animation action IDs in a sequence."""
        seq = self.get_action_sequence(sequence_id)
        if seq:
            return seq.get_action_ids()
        return []


class AssetManifest:
    """Describes all static assets used in the game."""
    
    ENVIRONMENT_ASSETS = {
        "house": "environments/house.jpg",
        "kitchen": "environments/kitchen.jpg",
    }
    
    CHARACTER_ASSETS = {
        "mother": "characters/mother.png",
        "daughter_anu": "characters/daughter_anu.png",
        "son_rahul": "characters/rahul.png",
    }
    
    MEMORY_ASSETS = {
        "anu_cooking": "memories/anu_cooking_with_lakshmi.jpg",
        "family_meal": "memories/family_meal.jpg",
        "chapathi": "food/chapathi.jpg",
        "kitchen_memory": "home/family_kitchen.jpg",
    }
    
    ANIMATION_ASSETS = {
        # Scene intros
        "house_camera_slow_pan": "animations/house_intro.mp4",
        "mother_idle": "animations/mother_idle.mp4",
        "camera_enter_kitchen": "animations/enter_kitchen.mp4",
        "mother_look_around": "animations/mother_look_around.mp4",
        
        # Correct answer - daughter recognition
        "daughter_appear": "animations/daughter_appear.mp4",
        "daughter_smile": "animations/daughter_smile.mp4",
        "daughter_walk_to_mother": "animations/daughter_walk_to_mother.mp4",
        "daughter_hug_mother": "animations/daughter_hug_mother.mp4",
        "reward_celebrate": "animations/reward_celebrate.mp4",
        
        # Wrong answer
        "daughter_gentle_gesture_to_kitchen": "animations/daughter_gesture_kitchen.mp4",
        "fade_to_memory": "animations/fade_to_memory.mp4",
        "show_anu_cooking_image": "animations/show_cooking.mp4",
        
        # Stronger hints
        "daughter_cooking": "animations/daughter_cooking.mp4",
        "daughter_turn_and_smile": "animations/daughter_turn_smile.mp4",
        "show_name_hint": "animations/show_name_hint.mp4",
        
        # Food recognition
        "show_food_chapathi": "animations/show_food.mp4",
        "food_recognition_correct": "animations/food_correct.mp4",
        "positive_feedback": "animations/positive_feedback.mp4",
        "positive_feedback_animation": "animations/positive_feedback.mp4",
        
        # Family recognition
        "show_family_meal_image": "animations/show_family_meal.mp4",
        "family_meal_animation": "animations/family_meal_together.mp4",
        "anu_and_rahul_smile": "animations/family_smile.mp4",
        
        # Final reward
        "mother_and_daughter_smile": "animations/mother_daughter_smile.mp4",
        "final_celebration": "animations/final_celebration.mp4",
        
        # Transitions
        "camera_transition": "animations/camera_transition.mp4",
        "mother_nod": "animations/mother_nod.mp4",
    }
    
    @classmethod
    def get_asset(cls, asset_type: str, asset_id: str) -> Optional[str]:
        """Get asset path by type and ID."""
        assets = getattr(cls, f"{asset_type.upper()}_ASSETS", {})
        return assets.get(asset_id)
    
    @classmethod
    def validate_animation(cls, animation_id: str) -> bool:
        """Check if animation exists in manifest."""
        return animation_id in cls.ANIMATION_ASSETS
