"""
Game Agent - Convert narrative stories into playable game blueprints.

Takes Story objects and generates GameBlueprint with:
- Semantic action IDs (not animation filenames)
- Question flow
- Option mapping
- Correct/wrong answer branching
"""

from typing import Dict, List
from backend.models import Story, GameBlueprint, SceneBlueprint


class GameAgent:
    """
    Convert stories into game blueprints with playable scenes.
    
    Maps each story scene to:
    - UI elements (narration, questions, buttons)
    - Semantic actions (what happens when button pressed)
    - Game flow (which scene comes next)
    """
    
    def convert_story_to_blueprint(self, story: Story) -> GameBlueprint:
        """
        Convert a Story into a GameBlueprint.
        
        Args:
            story: Story object with scenes
        
        Returns:
            GameBlueprint ready for Unity execution
        """
        
        scenes = []
        
        for scene in story.scenes:
            scene_bp = self._convert_scene(scene)
            scenes.append(scene_bp)
        
        blueprint = GameBlueprint(
            blueprint_id=f"bp_{story.id}",
            game_id=f"game_{story.id}",
            story_title=story.title,
            patient_id=story.patient_id,
            cognitive_target=story.cognitive_target,
            memory_chain_goal=story.memory_chain_goal,
            scenes=scenes,
            created_by="story_agent",
            version="1.0",
            validated=False,
            validation_errors=[]
        )
        
        return blueprint
    
    def _convert_scene(self, story_scene) -> SceneBlueprint:
        """Convert a Story Scene to a SceneBlueprint."""
        
        scene_bp = SceneBlueprint(
            scene_id=story_scene.id,
            scene_type=story_scene.scene_type,
            environment=self._get_environment(story_scene),
            characters=self._get_characters(story_scene),
            memory_assets=self._get_memory_assets(story_scene),
            narration=story_scene.narration,
            question_text=story_scene.question_text,
            options=self._convert_options(story_scene),
            initial_action=story_scene.animation_cue,
            action_map=self._build_action_map(story_scene),
            next_scene_on_continue=self._get_next_scene(story_scene)
        )
        
        return scene_bp
    
    def _get_environment(self, scene) -> str:
        """Extract environment asset ID from scene."""
        
        if "kitchen" in scene.background_image.lower():
            return "family_kitchen"
        elif "temple" in scene.background_image.lower():
            return "place_temple"
        elif "house" in scene.background_image.lower():
            return "family_house_front"
        else:
            return "family_house_front"
    
    def _get_characters(self, scene) -> List[str]:
        """Extract character asset IDs from scene memory chain."""
        
        characters = []
        
        for link in scene.memory_chain:
            if link.entity_type == "person":
                if "anu" in link.entity_name.lower():
                    characters.append("daughter_anu")
                elif "rahul" in link.entity_name.lower():
                    characters.append("son_rahul")
        
        # Default: add mother
        if not characters:
            characters.append("mother_lakshmi")
        
        return characters
    
    def _get_memory_assets(self, scene) -> List[str]:
        """Extract memory/food/object asset IDs from scene."""
        
        assets = []
        
        for link in scene.memory_chain:
            if link.entity_type == "food":
                if "chapathi" in link.entity_name.lower():
                    assets.append("food_chapathi")
                elif "rice" in link.entity_name.lower():
                    assets.append("food_rice")
            elif link.entity_type == "memory":
                if "cooking" in link.entity_name.lower():
                    assets.append("memory_anu_cooking")
                elif "meal" in link.entity_name.lower():
                    assets.append("memory_family_meal")
            elif link.entity_type == "home":
                if "kitchen" in link.entity_name.lower():
                    assets.append("family_kitchen")
        
        return assets
    
    def _convert_options(self, scene) -> List[Dict[str, str]]:
        """Convert story scene options to blueprint options."""
        
        options = []
        
        for opt in scene.options:
            options.append({
                "id": opt.id,
                "text": opt.text,
                "action": self._get_semantic_action(opt, scene.scene_type),
            })
        
        return options
    
    def _build_action_map(self, scene) -> Dict[str, str]:
        """
        Build mapping from option IDs to semantic action IDs.
        
        This is KEY: it maps UI choices to semantic actions, not animation files.
        """
        
        action_map = {}
        
        for opt in scene.options:
            semantic_action = self._get_semantic_action(opt, scene.scene_type)
            action_map[opt.id] = semantic_action
        
        return action_map
    
    def _get_semantic_action(self, option, scene_type: str) -> str:
        """
        Determine the semantic action ID for a given option.
        
        Maps based on:
        - Option correctness
        - Scene type
        - Option text
        """
        
        option_lower = option.text.lower() if hasattr(option, 'text') else ""
        
        # If explicit is_correct set
        if option.is_correct is True:
            # Correct answer - what's the memory?
            if "anu" in option_lower or "daughter" in option_lower:
                return "daughter_recognition_success"
            elif "chapathi" in option_lower or "food" in option_lower:
                return "food_recognition_success"
            elif "family" in option_lower:
                return "family_recognition_success"
            else:
                return "positive_feedback"
        
        elif option.is_correct is False:
            # Wrong answer - provide cue
            return "wrong_answer_encouragement"
        
        else:
            # Neutral action - scene transition
            if "continue" in option_lower or "tell me" in option_lower:
                return "continue_to_kitchen"
            elif "try again" in option_lower:
                return "gentle_continue_to_kitchen"
            elif "thank you" in option_lower or "end" in option_lower:
                return "final_reward"
            else:
                return "positive_feedback"
    
    def _get_next_scene(self, scene) -> str:
        """Get the next scene ID from first option."""
        
        if scene.options and scene.options[0].next_scene_id:
            return scene.options[0].next_scene_id
        
        return None


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from backend.agents.goal_agent import GoalAgent
    from backend.agents.memory_agent import MemoryAgent
    from backend.agents.story_agent import StoryAgent
    
    goal_agent = GoalAgent()
    memory_agent = MemoryAgent()
    story_agent = StoryAgent()
    game_agent = GameAgent()
    
    # Test
    goal_text = "Help Lakshmi remember her daughter Anu"
    goal = goal_agent.parse_goal(goal_text)
    memories = memory_agent.get_memories("Patient_001_Lakshmi", goal)
    story = story_agent.generate_story("Patient_001_Lakshmi", "Lakshmi", goal, memories)
    blueprint = game_agent.convert_story_to_blueprint(story)
    
    print(f"Generated Blueprint: {blueprint.story_title}")
    print(f"  Blueprint ID: {blueprint.blueprint_id}")
    print(f"  Game ID: {blueprint.game_id}")
    print(f"  Patient: {blueprint.patient_id}")
    print(f"  Scenes: {len(blueprint.scenes)}")
    print(f"  Cognitive Target: {blueprint.cognitive_target}")
    print(f"  Memory Chain: {blueprint.memory_chain_goal}")
    print("\n  Scenes with Actions:")
    for scene in blueprint.scenes:
        print(f"    - {scene.scene_id}: {scene.scene_type}")
        print(f"      Actions: {list(scene.action_map.values())[:3]}...")
