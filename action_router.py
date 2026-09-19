"""
Action Router - Maps patient actions to animation sequences and executes them.
This is what processes player choices and drives the game forward.
"""

from typing import Optional, Dict, List, Tuple
from models import (
    GameBlueprint, SceneBlueprint, ActionSequence, AnimationAction
)
from asset_library import AssetLibrary


class ActionRouter:
    """Routes patient actions to animation sequences."""
    
    def __init__(self, asset_library: AssetLibrary):
        """
        Initialize the action router.
        
        Args:
            asset_library: AssetLibrary containing all animation sequences
        """
        self.asset_library = asset_library
        self.current_blueprint: Optional[GameBlueprint] = None
        self.current_scene: Optional[SceneBlueprint] = None
        self.action_history: List[str] = []
    
    def load_blueprint(self, blueprint: GameBlueprint):
        """Load a blueprint for execution."""
        self.current_blueprint = blueprint
    
    def set_current_scene(self, scene: SceneBlueprint):
        """Set the current scene being displayed."""
        self.current_scene = scene
    
    def route_action(self, option_id: str) -> Tuple[Optional[ActionSequence], Dict]:
        """
        Route a patient action and get the animation sequence to play.
        
        Args:
            option_id: The option/button the patient pressed
        
        Returns:
            Tuple of (ActionSequence, metadata_dict)
            - ActionSequence: The animations to play
            - metadata_dict: Response info (success, hint_level, outcome, etc.)
        """
        
        if not self.current_scene:
            return None, {"error": "No scene loaded"}
        
        # Check if option exists in action map
        if option_id not in self.current_scene.action_map:
            return None, {"error": f"Invalid option: {option_id}"}
        
        # Get the action sequence ID
        action_seq_id = self.current_scene.action_map[option_id]
        
        # Get the action sequence from asset library
        action_sequence = self.asset_library.get_action_sequence(action_seq_id)
        
        if not action_sequence:
            return None, {"error": f"Action sequence not found: {action_seq_id}"}
        
        # Record action
        self.action_history.append(action_seq_id)
        
        # Determine response metadata
        response = self._build_response(option_id, action_seq_id, action_sequence)
        
        return action_sequence, response
    
    def _build_response(self, option_id: str, action_id: str, 
                       action_seq: ActionSequence) -> Dict:
        """Build response metadata."""
        
        # Determine if this was correct or wrong based on action ID
        is_correct = "correct" in action_id
        hint_level = self._get_hint_level(action_id)
        
        response = {
            "success": True,
            "option_id": option_id,
            "action_sequence_id": action_id,
            "animation_count": len(action_seq.actions),
            "animations": [a.id for a in action_seq.actions],
            "narration": action_seq.outcome_narration,
            "is_correct": is_correct,
            "hint_level": hint_level,
            "duration_seconds": sum(a.duration for a in action_seq.actions)
        }
        
        return response
    
    def _get_hint_level(self, action_id: str) -> int:
        """Determine hint level from action ID."""
        if "stronger_hint" in action_id or "hint_2" in action_id:
            return 2
        elif "wrong" in action_id or "cue" in action_id:
            return 1
        elif "correct" in action_id or "independent" in action_id:
            return 0
        else:
            return -1  # Unknown


class ExecutionEngine:
    """Executes blueprints by routing actions through the action router."""
    
    def __init__(self, action_router: ActionRouter):
        """
        Initialize the execution engine.
        
        Args:
            action_router: ActionRouter to use for routing
        """
        self.action_router = action_router
        self.execution_log: List[Dict] = []
    
    def execute_scene(self, scene: SceneBlueprint) -> Dict:
        """
        Prepare a scene for execution.
        
        Returns scene data that Unity should display.
        """
        self.action_router.set_current_scene(scene)
        
        scene_data = {
            "scene_id": scene.scene_id,
            "scene_type": scene.scene_type,
            "environment": scene.environment,
            "characters": scene.characters,
            "memory_assets": scene.memory_assets,
            "narration": scene.narration,
            "question_text": scene.question_text,
            "options": scene.options,
            "initial_action": scene.initial_action
        }
        
        return scene_data
    
    def execute_action(self, option_id: str) -> Tuple[Dict, Optional[str]]:
        """
        Execute a player action and return the animation + next scene.
        
        Args:
            option_id: The option the patient selected
        
        Returns:
            Tuple of (execution_result, next_scene_id)
            - execution_result: Animation sequence and metadata
            - next_scene_id: Which scene to show next (or None if retry)
        """
        
        action_sequence, response = self.action_router.route_action(option_id)
        
        if not action_sequence:
            return response, None
        
        # Log execution
        self.execution_log.append({
            "option_id": option_id,
            "action_sequence_id": response.get("action_sequence_id"),
            "is_correct": response.get("is_correct"),
            "hint_level": response.get("hint_level")
        })
        
        # Build execution result
        execution_result = {
            "success": True,
            "action_sequence": {
                "id": action_sequence.id,
                "description": action_sequence.description,
                "animations": [
                    {
                        "id": a.id,
                        "duration": a.duration,
                        "narration": a.trigger_narration
                    }
                    for a in action_sequence.actions
                ],
                "outcome_narration": action_sequence.outcome_narration
            },
            **response
        }
        
        # Determine next scene
        # For now, return None (story flow will handle progression)
        next_scene_id = None
        
        return execution_result, next_scene_id
    
    def get_execution_summary(self) -> Dict:
        """Get summary of execution so far."""
        return {
            "actions_executed": len(self.execution_log),
            "correct_count": sum(1 for e in self.execution_log if e["is_correct"]),
            "wrong_count": sum(1 for e in self.execution_log if not e["is_correct"]),
            "execution_history": self.execution_log
        }


class ActionSequencePlayer:
    """Simplified utility for playing back animation sequences."""
    
    def __init__(self):
        """Initialize the player."""
        pass
    
    @staticmethod
    def play_sequence(action_sequence: ActionSequence) -> Dict:
        """
        Generate playback data for an action sequence.
        
        This is what would be sent to Unity to actually play the animations.
        
        Returns:
            Dict with animation playback instructions
        """
        
        playback_data = {
            "sequence_id": action_sequence.id,
            "sequence_description": action_sequence.description,
            "total_duration": sum(a.duration for a in action_sequence.actions),
            "keyframes": []
        }
        
        current_time = 0.0
        for i, action in enumerate(action_sequence.actions):
            keyframe = {
                "index": i,
                "animation_id": action.id,
                "start_time": current_time,
                "duration": action.duration,
                "end_time": current_time + action.duration
            }
            
            if action.trigger_narration:
                keyframe["narration"] = action.trigger_narration
            
            playback_data["keyframes"].append(keyframe)
            current_time += action.duration
        
        playback_data["final_narration"] = action_sequence.outcome_narration
        
        return playback_data
