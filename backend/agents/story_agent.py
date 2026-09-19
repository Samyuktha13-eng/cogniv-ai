"""
Story Agent - Generate narrative stories from patient memories.

Takes parsed goal + retrieved memories and creates an 8-scene narrative
that progressively guides the patient through memory associations.
"""

from typing import Dict, List, Optional
from backend.models import Story, Scene, MemoryChainLink, GameQuestion, GameOption, SceneOption


class StoryAgent:
    """
    Generate game narratives from goals and memories.
    
    Creates an 8-scene story arc that:
    1. Establishes familiar environment
    2. Introduces context/setting
    3. Presents initial question/memory
    4. Provides memory cues if needed
    5. Reinforces associations
    6. Combines multiple memories
    7. Rewards correct recalls
    8. Closes with positive reinforcement
    """
    
    def generate_story(self, patient_id: str, patient_name: str, goal: Dict, 
                      memories: Dict) -> Story:
        """
        Generate a complete story.
        
        Args:
            patient_id: e.g., "Patient_001_Lakshmi"
            patient_name: e.g., "Lakshmi"
            goal: Parsed goal {target_type, target_id, target_name, objective, ...}
            memories: Retrieved memories {target_entity, related_entities, associations, ...}
        
        Returns:
            Story object with 8 scenes
        """
        
        target_type = goal.get("target_type")
        target_name = goal.get("target_name", "friend")
        context = goal.get("context", "")
        chain_hint = goal.get("memory_chain_hint", [])
        
        # Build 8-scene story
        scenes = []
        
        # Scene 0: Welcome - Establish familiar environment
        scenes.append(self._scene_welcome(patient_name))
        
        # Scene 1: Location setup - Introduce the setting
        scenes.append(self._scene_location_setup(target_type, memories))
        
        # Scene 2: Question - Main recall question
        scenes.append(self._scene_question(target_type, target_name, memories))
        
        # Scene 3: Positive path - If correct, show success
        scenes.append(self._scene_correct_answer(target_type, target_name, memories))
        
        # Scene 4: Alternative path - If wrong, provide cue
        scenes.append(self._scene_memory_cue(target_type, target_name, memories))
        
        # Scene 5: Reinforcement - Build stronger memory connection
        scenes.append(self._scene_reinforcement(target_type, target_name, memories))
        
        # Scene 6: Association - Connect to related memories
        scenes.append(self._scene_association(target_type, target_name, memories))
        
        # Scene 7: Reward - Celebrate and close
        scenes.append(self._scene_reward(patient_name, target_name))
        
        # Create story object
        story = Story(
            id=f"story_{patient_id}_{target_type}_{target_name.lower()}",
            title=f"A Visit From {target_name}" if target_type == "person" else f"Remembering {target_name}",
            description=f"Help {patient_name} remember {target_name}",
            patient_id=patient_id,
            cognitive_target=goal.get("objective", "recall"),
            memory_chain_goal=chain_hint or ["home", "memory", "target", "family"],
            scenes=scenes
        )
        
        return story
    
    def _scene_welcome(self, patient_name: str) -> Scene:
        """Scene 0: Welcome - greet patient, establish comfort."""
        
        return Scene(
            id="scene_0_welcome",
            scene_id="scene_0_welcome",
            scene_type="narrative",
            title="Good Morning",
            narration=f"Good morning, {patient_name}! Let's spend some time together with your memories today.",
            background_image="assets/environments/house_front.png",
            memory_chain=[],
            question=None,
            options=[
                SceneOption(
                    id="opt_yes",
                    text="Yes, I'd like that",
                    narration="Wonderful!",
                    next_scene_id="scene_1_setup",
                    is_correct=None
                ),
                SceneOption(
                    id="opt_ready",
                    text="I'm ready",
                    narration="Let's begin!",
                    next_scene_id="scene_1_setup",
                    is_correct=None
                )
            ],
            animation_cue="house_intro"
        )
    
    def _scene_location_setup(self, target_type: str, memories: Dict) -> Scene:
        """Scene 1: Setup - Introduce location/context."""
        
        if target_type == "person":
            narration = "Let me take you somewhere special. Somewhere you spent so much time with your family."
            memory_chain = [
                MemoryChainLink(
                    entity_type="home",
                    entity_id="home_kitchen",
                    entity_name="Kitchen",
                    image="assets/environments/kitchen.png",
                    narration="The kitchen... such happy memories here."
                )
            ]
            next_scene = "scene_2_question"
        elif target_type == "place":
            narration = "Let's visit a place that was important to you and your family."
            memory_chain = [
                MemoryChainLink(
                    entity_type="place",
                    entity_id="place_temple",
                    entity_name="Temple",
                    image="assets/environments/temple.png",
                    narration="The family temple..."
                )
            ]
            next_scene = "scene_2_question"
        else:
            narration = "Let's explore a familiar memory together."
            memory_chain = []
            next_scene = "scene_2_question"
        
        return Scene(
            id="scene_1_setup",
            scene_id="scene_1_setup",
            scene_type="narrative",
            title="Setting the Scene",
            narration=narration,
            background_image=memory_chain[0].image if memory_chain else "assets/environments/house_front.png",
            memory_chain=memory_chain,
            question=None,
            options=[
                SceneOption(
                    id="opt_continue",
                    text="Tell me more",
                    narration="Of course...",
                    next_scene_id=next_scene,
                    is_correct=None
                )
            ],
            animation_cue="enter_kitchen"
        )
    
    def _scene_question(self, target_type: str, target_name: str, memories: Dict) -> Scene:
        """Scene 2: The main question - test recall."""
        
        if target_type == "person":
            question_text = f"Who is this special person you remember so well?"
            narration = "Someone important to you was here. Someone who loved spending time with you."
            image_key = "target_entity"
        elif target_type == "food":
            question_text = f"What was this food you loved making and eating?"
            narration = "This was your favorite to make. Such wonderful flavors..."
            image_key = "target_entity"
        else:
            question_text = "What is this place?"
            narration = "This place holds so many memories..."
            image_key = "target_entity"
        
        # Get related people for distractors
        related_people = memories.get("all_entities", {}).get("people", [])
        
        # Create options
        options = []
        correct_id = f"option_{target_name.lower()}"
        
        # Correct answer
        options.append(
            SceneOption(
                id=correct_id,
                text=target_name,
                narration=f"Yes! That's right, {target_name}!",
                is_correct=True
            )
        )
        
        # Add distractors
        for person in related_people:
            if person["name"] != target_name:
                options.append(
                    SceneOption(
                        id=f"option_{person['name'].lower()}",
                        text=person["name"],
                        narration=f"No, that's not who we're remembering today...",
                        is_correct=False
                    )
                )
        
        # Ensure at least 3 options
        while len(options) < 3:
            options.append(
                SceneOption(
                    id=f"option_other_{len(options)}",
                    text=f"Someone else",
                    narration="That's not the memory we're exploring...",
                    is_correct=False
                )
            )
        
        return Scene(
            id="scene_2_question",
            scene_id="scene_2_question",
            scene_type="recall_question",
            title="The Question",
            narration=narration,
            question_text=question_text,
            background_image="assets/environments/kitchen.png",
            memory_chain=[],
            options=options,
            animation_cue="show_target"
        )
    
    def _scene_correct_answer(self, target_type: str, target_name: str, memories: Dict) -> Scene:
        """Scene 3: Correct answer path - celebrate recognition."""
        
        narration = f"Yes! That's {target_name}! You remembered! What wonderful memories you share."
        
        return Scene(
            id="scene_3_correct",
            scene_id="scene_3_correct",
            scene_type="narrative",
            title="You Remember!",
            narration=narration,
            background_image="assets/environments/kitchen.png",
            memory_chain=[],
            question=None,
            options=[
                SceneOption(
                    id="opt_next",
                    text="Continue",
                    narration="Let's explore more...",
                    next_scene_id="scene_6_association",
                    is_correct=None
                )
            ],
            animation_cue="positive_feedback_animation"
        )
    
    def _scene_memory_cue(self, target_type: str, target_name: str, memories: Dict) -> Scene:
        """Scene 4: Wrong answer path - provide memory cue."""
        
        narration = f"That's okay. Let me help you remember {target_name}. Let's think about what you did together..."
        
        return Scene(
            id="scene_4_cue",
            scene_id="scene_4_cue",
            scene_type="narrative",
            title="A Little Help",
            narration=narration,
            background_image="assets/environments/kitchen.png",
            memory_chain=[
                MemoryChainLink(
                    entity_type="food",
                    entity_id="food_chapathi",
                    entity_name="Chapathi",
                    image="assets/food/chapathi.png",
                    narration="You two made this together..."
                )
            ],
            question=None,
            options=[
                SceneOption(
                    id="opt_try_again",
                    text="Try again",
                    narration="Let me guess again...",
                    next_scene_id="scene_2_question",
                    is_correct=None
                )
            ],
            animation_cue="show_memory_cue"
        )
    
    def _scene_reinforcement(self, target_type: str, target_name: str, memories: Dict) -> Scene:
        """Scene 5: Reinforce the memory connection."""
        
        narration = f"{target_name} was such an important part of your life. You spent so much time together, creating memories."
        
        return Scene(
            id="scene_5_reinforce",
            scene_id="scene_5_reinforce",
            scene_type="narrative",
            title="Strong Memories",
            narration=narration,
            background_image="assets/environments/kitchen.png",
            memory_chain=[
                MemoryChainLink(
                    entity_type="memory",
                    entity_id="mem_anu_cooking",
                    entity_name="Cooking Together",
                    image="assets/memories/anu_cooking.png",
                    narration="Cooking in the kitchen together..."
                )
            ],
            question=None,
            options=[
                SceneOption(
                    id="opt_continue",
                    text="I remember",
                    narration="Yes, those were wonderful times...",
                    next_scene_id="scene_6_association",
                    is_correct=None
                )
            ],
            animation_cue="daughter_walk_to_mother"
        )
    
    def _scene_association(self, target_type: str, target_name: str, memories: Dict) -> Scene:
        """Scene 6: Build associations - connect to related memories."""
        
        narration = f"And {target_name} was part of your whole family. You all shared wonderful moments together."
        
        return Scene(
            id="scene_6_association",
            scene_id="scene_6_association",
            scene_type="narrative",
            title="Family Connections",
            narration=narration,
            background_image="assets/environments/kitchen.png",
            memory_chain=[
                MemoryChainLink(
                    entity_type="memory",
                    entity_id="mem_family_meal",
                    entity_name="Family Meal",
                    image="assets/memories/family_meal.png",
                    narration="The whole family together at the table..."
                )
            ],
            question=None,
            options=[
                SceneOption(
                    id="opt_finish",
                    text="That was beautiful",
                    narration="It truly was...",
                    next_scene_id="scene_7_reward",
                    is_correct=None
                )
            ],
            animation_cue="family_recognition_success"
        )
    
    def _scene_reward(self, patient_name: str, target_name: str) -> Scene:
        """Scene 7: Final reward - celebrate and close."""
        
        narration = f"You did wonderfully today, {patient_name}! Your memories of {target_name} are alive and strong. That's beautiful."
        
        return Scene(
            id="scene_7_reward",
            scene_id="scene_7_reward",
            scene_type="reward",
            title="Well Done!",
            narration=narration,
            background_image="assets/environments/house_front.png",
            memory_chain=[
                MemoryChainLink(
                    entity_type="celebration",
                    entity_id="celebration",
                    entity_name="Celebration",
                    image="assets/memories/family_together.png",
                    narration="A beautiful moment of connection..."
                )
            ],
            question=None,
            options=[
                SceneOption(
                    id="opt_end",
                    text="Thank you",
                    narration="You're welcome. Come back whenever you'd like to remember.",
                    next_scene_id=None,
                    is_correct=None
                )
            ],
            animation_cue="final_reward"
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from backend.agents.goal_agent import GoalAgent
    from backend.agents.memory_agent import MemoryAgent
    
    goal_agent = GoalAgent()
    memory_agent = MemoryAgent()
    story_agent = StoryAgent()
    
    # Test
    goal_text = "Help Lakshmi remember her daughter Anu"
    goal = goal_agent.parse_goal(goal_text)
    memories = memory_agent.get_memories("Patient_001_Lakshmi", goal)
    story = story_agent.generate_story("Patient_001_Lakshmi", "Lakshmi", goal, memories)
    
    print(f"Generated Story: {story.title}")
    print(f"  Patient: {story.patient_id}")
    print(f"  Scenes: {len(story.scenes)}")
    print(f"  Memory Chain Goal: {story.memory_chain_goal}")
    print("\n  Scenes:")
    for scene in story.scenes:
        print(f"    - {scene.scene_id}: {scene.title}")
