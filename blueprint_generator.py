"""
Blueprint Generator - Converts Story objects into executable GameBlueprints.
This is what the AI generates (as JSON), what gets validated, and what Unity executes.
"""

from typing import Optional, Dict, List
from models import (
    Story, Scene, GameBlueprint, SceneBlueprint, AnimationAction, ActionSequence
)
from memory_repository import MemoryRepository
from asset_library import AssetLibrary, AssetManifest


class BlueprintGenerator:
    """Generates executable game blueprints from narrative stories."""
    
    def __init__(self, repo: MemoryRepository, asset_library: AssetLibrary):
        """
        Initialize the blueprint generator.
        
        Args:
            repo: MemoryRepository with loaded patient data
            asset_library: AssetLibrary with available animations
        """
        self.repo = repo
        self.asset_library = asset_library
        self.manifest = AssetManifest()
    
    def generate_blueprint(self, story: Story) -> GameBlueprint:
        """
        Convert a Story into a GameBlueprint.
        
        This generates the structured JSON that:
        1. AI can produce
        2. Validator can check
        3. Unity can execute
        
        Args:
            story: The Story object to convert
        
        Returns:
            GameBlueprint ready for validation and execution
        """
        blueprint = GameBlueprint(
            blueprint_id=f"bp_{story.id}",
            game_id=story.id,
            story_title=story.title,
            patient_id=story.patient_id,
            cognitive_target=story.cognitive_target,
            memory_chain_goal=story.memory_chain_goal
        )
        
        # Convert each scene to a blueprint scene
        for scene in story.scenes:
            scene_bp = self._convert_scene_to_blueprint(scene)
            blueprint.scenes.append(scene_bp)
        
        return blueprint
    
    def _convert_scene_to_blueprint(self, scene: Scene) -> SceneBlueprint:
        """Convert a Story Scene into a SceneBlueprint."""
        
        # Determine scene type
        if scene.question:
            scene_type = "recall_question"
        elif "reward" in scene.id.lower():
            scene_type = "reward"
        else:
            scene_type = "narrative"
        
        # Gather environment
        environment = None
        if scene.background_image:
            # Extract asset ID from path
            environment = self._extract_asset_id(scene.background_image)
        
        # Gather characters and memory assets
        characters = []
        memory_assets = []
        
        for link in scene.memory_chain:
            asset_id = self._extract_asset_id(link.image)
            if link.entity_type == "person":
                characters.append(asset_id)
            else:
                memory_assets.append(asset_id)
        
        # Build options with action mappings
        options = []
        action_map = {}
        
        if scene.question:
            # Question-based scene: options are answers
            for opt in scene.question.options:
                option_data = {
                    "id": opt.id,
                    "text": opt.text,
                    "type": "answer"
                }
                options.append(option_data)
                
                # Map option to action sequence
                if opt.correct:
                    action_id = self._get_correct_answer_action(scene.question.target_type)
                else:
                    action_id = self._get_wrong_answer_action(scene.question.target_type)
                
                action_map[opt.id] = action_id
        
        else:
            # Narrative scene: options are choices
            for opt in scene.options:
                option_data = {
                    "id": opt.id,
                    "text": opt.text,
                    "type": "choice"
                }
                options.append(option_data)
                
                # Map option to action sequence
                if opt.text.lower() in ["yes, i remember", "yes"]:
                    action_id = "continue_to_kitchen"
                elif opt.text.lower() in ["i'm not sure", "not sure"]:
                    action_id = "gentle_continue_to_kitchen"
                else:
                    action_id = self._get_narrative_action(opt.id)
                
                action_map[opt.id] = action_id
        
        # Initial action when scene starts
        initial_action = None
        if scene.animation_cue:
            initial_action = self._map_animation_cue_to_action(scene.animation_cue)
        
        scene_bp = SceneBlueprint(
            scene_id=scene.id,
            scene_type=scene_type,
            environment=environment,
            characters=characters,
            memory_assets=memory_assets,
            narration=scene.narration,
            question_text=scene.question.question_text if scene.question else None,
            options=options,
            initial_action=initial_action,
            action_map=action_map,
            next_scene_on_continue=None  # Will be set by story flow
        )
        
        return scene_bp
    
    def _extract_asset_id(self, image_path: str) -> str:
        """Extract asset ID from image path."""
        # Convert "people/daughter_anu.png" → "daughter_anu"
        return image_path.split("/")[-1].split(".")[0]
    
    def _get_correct_answer_action(self, target_type: str) -> str:
        """Get correct answer action sequence ID."""
        if target_type == "person":
            return "correct_answer_daughter"
        elif target_type == "food":
            return "correct_answer_food"
        elif target_type == "family":
            return "correct_answer_family"
        else:
            return "positive_feedback"
    
    def _get_wrong_answer_action(self, target_type: str) -> str:
        """Get wrong answer action sequence ID."""
        if target_type == "person":
            return "wrong_answer_encouragement"
        else:
            return "positive_feedback"
    
    def _get_narrative_action(self, option_id: str) -> str:
        """Get narrative choice action sequence ID."""
        # Default transitions
        return "continue_to_kitchen"
    
    def _map_animation_cue_to_action(self, animation_cue: str) -> Optional[str]:
        """Map animation cue to action sequence ID."""
        cue_mapping = {
            "celebrate": "reward_celebrate",
            "gentle_encourage": "wrong_answer_encouragement",
            "camera_pan": "house_intro",
            "show_image": "show_food_chapathi",
            "point_to_memory": "show_memory_cue",
            "hug": "daughter_hug_mother",
            "smile": "daughter_smile"
        }
        return cue_mapping.get(animation_cue)


class BlueprintValidator:
    """Validates blueprints for safety and correctness before execution."""
    
    def __init__(self, asset_library: AssetLibrary):
        """
        Initialize the validator.
        
        Args:
            asset_library: AssetLibrary to validate against
        """
        self.asset_library = asset_library
    
    def validate(self, blueprint: GameBlueprint) -> bool:
        """
        Validate a blueprint for safety and completeness.
        
        Returns:
            True if blueprint is valid, False otherwise
        """
        errors = []
        
        # Check basic structure
        if not blueprint.blueprint_id:
            errors.append("Blueprint ID is required")
        if not blueprint.game_id:
            errors.append("Game ID is required")
        if not blueprint.patient_id:
            errors.append("Patient ID is required")
        
        # Check scenes
        if not blueprint.scenes:
            errors.append("Blueprint must have at least one scene")
        
        # Validate each scene
        for scene in blueprint.scenes:
            scene_errors = self._validate_scene(scene)
            errors.extend(scene_errors)
        
        # Update blueprint validation status
        blueprint.validated = len(errors) == 0
        blueprint.validation_errors = errors
        
        return len(errors) == 0
    
    def _validate_scene(self, scene: SceneBlueprint) -> List[str]:
        """Validate a single scene."""
        errors = []
        
        if not scene.scene_id:
            errors.append(f"Scene missing ID")
        
        if not scene.narration:
            errors.append(f"Scene {scene.scene_id}: Missing narration")
        
        # Check all action sequences exist
        for option_id, action_id in scene.action_map.items():
            if not self.asset_library.validate_action_sequence(action_id):
                errors.append(
                    f"Scene {scene.scene_id}: Action '{action_id}' not found in asset library"
                )
        
        # Check initial action
        if scene.initial_action:
            if not self.asset_library.validate_action_sequence(scene.initial_action):
                errors.append(
                    f"Scene {scene.scene_id}: Initial action '{scene.initial_action}' not found"
                )
        
        # Check question has options
        if scene.scene_type == "recall_question" and not scene.question_text:
            errors.append(f"Scene {scene.scene_id}: Recall question missing question text")
        
        if scene.options and not scene.action_map:
            errors.append(f"Scene {scene.scene_id}: Options defined but no action mapping")
        
        return errors
    
    def get_report(self, blueprint: GameBlueprint) -> Dict:
        """Get a detailed validation report."""
        return {
            "blueprint_id": blueprint.blueprint_id,
            "valid": blueprint.validated,
            "errors_count": len(blueprint.validation_errors),
            "errors": blueprint.validation_errors,
            "scenes_count": len(blueprint.scenes),
            "story_title": blueprint.story_title,
            "cognitive_target": blueprint.cognitive_target
        }
