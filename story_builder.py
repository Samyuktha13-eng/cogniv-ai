"""
Story Builder - Constructs the "A Visit From Anu" narrative from patient memories.
"""

from typing import Optional, List
from models import (
    Story, Scene, SceneOption, GameQuestion, GameOption, MemoryChainLink
)
from memory_repository import MemoryRepository


class StoryBuilder:
    """Builds narrative stories from patient memory data."""
    
    def __init__(self, repo: MemoryRepository):
        """
        Initialize the story builder.
        
        Args:
            repo: MemoryRepository with loaded patient data
        """
        self.repo = repo
        if not self.repo.profile:
            raise ValueError("Repository not loaded. Call repo.load() first.")
    
    def build_visit_from_anu_story(self) -> Story:
        """
        Build the complete "A Visit From Anu" story.
        
        This 8-scene narrative helps the patient recognize their daughter Anu
        through familiar visual associations: home → kitchen → chapathi → Anu → family.
        
        Returns:
            Complete Story object with all 8 scenes
        """
        story = Story(
            id="visit_from_anu_001",
            title="A Visit From Anu",
            description="A gentle memory journey through familiar places and people",
            patient_id=self.repo.profile.patient_id,
            cognitive_target="person_recall",
            memory_chain_goal=["home", "kitchen", "chapathi", "person_anu", "family"]
        )
        
        # SCENE 1 — Welcome Home
        scene_1 = self._build_scene_1_welcome()
        
        # SCENE 2 — The Kitchen
        scene_2 = self._build_scene_2_kitchen()
        
        # SCENE 3A — Correct Answer (Anu)
        scene_3a = self._build_scene_3a_correct_anu()
        
        # SCENE 3B — Wrong Answer (Return to memory)
        scene_3b = self._build_scene_3b_wrong_answer()
        
        # SCENE 4 — Memory Cue (Kitchen + Cooking)
        scene_4 = self._build_scene_4_memory_cue()
        
        # SCENE 6 — Food Recognition
        scene_6 = self._build_scene_6_food_recognition()
        
        # SCENE 7 — Family Memory
        scene_7 = self._build_scene_7_family_memory()
        
        # SCENE 8 — Emotional Reward
        scene_8 = self._build_scene_8_reward()
        
        story.scenes = [scene_1, scene_2, scene_3a, scene_3b, scene_4, scene_6, scene_7, scene_8]
        
        return story
    
    def _build_scene_1_welcome(self) -> Scene:
        """Scene 1: Welcome to familiar home."""
        home = self.repo.get_entity_by_id("home_house")
        if not home:
            # Fallback
            home = self.repo.profile.home[0] if self.repo.profile.home else None
        
        scene = Scene(
            id="scene_1_welcome",
            title="A Familiar Home",
            narration="Good morning. Let's spend some time with your familiar memories.",
            background_image=home.image if home else None,
            memory_chain=[
                MemoryChainLink(
                    entity_type="home",
                    entity_id=home.id if home else "home_house",
                    entity_name=home.name if home else "Family House",
                    image=home.image if home else "home/family_house_front.png",
                    narration="This is your home."
                )
            ],
            options=[
                SceneOption(
                    id="opt_remember_yes",
                    text="Yes, I remember",
                    narration="Good. Let's look inside.",
                    next_scene_id="scene_2_kitchen",
                    is_correct=None
                ),
                SceneOption(
                    id="opt_remember_not_sure",
                    text="I'm not sure",
                    narration="That's okay. Let's explore together.",
                    next_scene_id="scene_2_kitchen",
                    is_correct=None
                )
            ],
            animation_cue="camera_pan"
        )
        
        return scene
    
    def _build_scene_2_kitchen(self) -> Scene:
        """Scene 2: Enter the kitchen, introduce chapathi."""
        kitchen = self.repo.get_entity_by_id("home_kitchen")
        chapathi = self.repo.get_entity_by_id("food_chapathi")
        
        memory_chain = [
            MemoryChainLink(
                entity_type="home",
                entity_id=kitchen.id if kitchen else "home_kitchen",
                entity_name=kitchen.name if kitchen else "Kitchen",
                image=kitchen.image if kitchen else "home/family_kitchen.jpg",
                narration="This is the kitchen."
            ),
            MemoryChainLink(
                entity_type="food",
                entity_id=chapathi.id if chapathi else "food_chapathi",
                entity_name=chapathi.name if chapathi else "Chapathi",
                image=chapathi.image if chapathi else "food/chapathi.jpg",
                narration="You used to make chapathi here."
            )
        ]
        
        # Get the daughter for the question
        daughter = self.repo.get_person_by_relationship("daughter")
        wrong_people = [p for p in self.repo.profile.people if p.id != daughter.id]
        selected_wrong = wrong_people[:2] if len(wrong_people) >= 2 else [
            type('obj', (object,), {'id': 'f_priya', 'name': 'Priya'})(),
            type('obj', (object,), {'id': 'f_radha', 'name': 'Radha'})()
        ]
        
        options = [
            GameOption(id=daughter.id, text=daughter.name, correct=True),
            GameOption(id=selected_wrong[0].id, text=selected_wrong[0].name, correct=False),
            GameOption(id=selected_wrong[1].id, text=selected_wrong[1].name, correct=False)
        ]
        
        import random
        random.shuffle(options)
        
        question = GameQuestion(
            id="q_daughter_recognition",
            question_text="Someone special used to cook with you. Do you remember who?",
            image=daughter.image,
            options=options,
            target_type="person",
            target_id=daughter.id
        )
        
        scene = Scene(
            id="scene_2_kitchen",
            title="The Kitchen",
            narration="Someone special used to cook with you. Do you remember who?",
            background_image=kitchen.image if kitchen else "home/family_kitchen.jpg",
            memory_chain=memory_chain,
            question=question,
            options=[
                SceneOption(
                    id="opt_correct_anu",
                    text=daughter.name,
                    narration=f"Yes! You remembered {daughter.name}.",
                    next_scene_id="scene_3a_correct",
                    is_correct=True
                ),
                SceneOption(
                    id="opt_wrong_answer",
                    text="Wrong answer",
                    narration="Let's remember together.",
                    next_scene_id="scene_3b_wrong",
                    is_correct=False
                )
            ],
            animation_cue="show_image"
        )
        
        return scene
    
    def _build_scene_3a_correct_anu(self) -> Scene:
        """Scene 3A: Correct answer - Celebrate finding Anu."""
        daughter = self.repo.get_person_by_relationship("daughter")
        
        scene = Scene(
            id="scene_3a_correct",
            title="Found Anu!",
            narration=f"Yes! You remembered {daughter.name}. She is your daughter.",
            background_image=None,
            memory_chain=[
                MemoryChainLink(
                    entity_type="person",
                    entity_id=daughter.id,
                    entity_name=daughter.name,
                    image=daughter.image,
                    narration=f"Your daughter, {daughter.name}."
                )
            ],
            options=[
                SceneOption(
                    id="opt_continue_to_food",
                    text="Continue",
                    narration="Let's remember more about Anu.",
                    next_scene_id="scene_6_food",
                    is_correct=True
                )
            ],
            animation_cue="celebrate"
        )
        
        return scene
    
    def _build_scene_3b_wrong_answer(self) -> Scene:
        """Scene 3B: Wrong answer - Show memory cue."""
        daughter = self.repo.get_person_by_relationship("daughter")
        memory = self.repo.get_memories_for_person(daughter.id)[0] if self.repo.get_memories_for_person(daughter.id) else None
        kitchen = self.repo.get_entity_by_id("home_kitchen")
        
        memory_chain = []
        if memory:
            memory_chain.append(
                MemoryChainLink(
                    entity_type="memory",
                    entity_id=memory.id,
                    entity_name=memory.title,
                    image=memory.image,
                    narration=memory.description
                )
            )
        
        scene = Scene(
            id="scene_3b_wrong",
            title="Memory Cue",
            narration="That's okay. Let's remember together.",
            background_image=kitchen.image if kitchen else "home/family_kitchen.jpg",
            memory_chain=memory_chain,
            options=[
                SceneOption(
                    id="opt_retry",
                    text="Try again",
                    narration="Let's try again.",
                    next_scene_id="scene_2_kitchen",
                    is_correct=None
                )
            ],
            animation_cue="gentle_encourage"
        )
        
        return scene
    
    def _build_scene_4_memory_cue(self) -> Scene:
        """Scene 4: Stronger memory cue with cooking association."""
        daughter = self.repo.get_person_by_relationship("daughter")
        memory = self.repo.get_memories_for_person(daughter.id)[0] if self.repo.get_memories_for_person(daughter.id) else None
        chapathi = self.repo.get_entity_by_id("food_chapathi")
        
        memory_chain = []
        if memory:
            memory_chain.append(
                MemoryChainLink(
                    entity_type="memory",
                    entity_id=memory.id,
                    entity_name=memory.title,
                    image=memory.image,
                    narration=f"You and {daughter.name} used to cook together."
                )
            )
        
        scene = Scene(
            id="scene_4_memory_cue",
            title="Cooking Memory",
            narration=f"You and {daughter.name} used to cook chapathi together. Her name starts with {daughter.name[0]}...",
            background_image=memory.image if memory else "memories/anu_cooking_with_lakshmi.jpg",
            memory_chain=memory_chain,
            options=[
                SceneOption(
                    id="opt_continue_food",
                    text="Continue",
                    narration="Let's continue.",
                    next_scene_id="scene_6_food",
                    is_correct=None
                )
            ],
            animation_cue="point_to_memory"
        )
        
        return scene
    
    def _build_scene_6_food_recognition(self) -> Scene:
        """Scene 6: Food recognition - What were you making?"""
        memory = self.repo.get_memories_for_person(
            self.repo.get_person_by_relationship("daughter").id
        )[0] if self.repo.get_memories_for_person(
            self.repo.get_person_by_relationship("daughter").id
        ) else None
        
        target_food = self.repo.get_entity_by_id("food_chapathi")
        other_foods = [f for f in self.repo.profile.food if f.id != target_food.id]
        selected_wrong = other_foods[:2] if len(other_foods) >= 2 else []
        
        options = [
            GameOption(id=target_food.id, text=target_food.name, correct=True),
        ]
        for food in selected_wrong:
            options.append(GameOption(id=food.id, text=food.name, correct=False))
        
        import random
        random.shuffle(options)
        
        question = GameQuestion(
            id="q_food_recognition",
            question_text="What were you making together?",
            image=memory.image if memory else "memories/anu_cooking_with_lakshmi.jpg",
            options=options,
            target_type="food",
            target_id=target_food.id
        )
        
        scene = Scene(
            id="scene_6_food",
            title="Food Memory",
            narration="What were you making together?",
            background_image=memory.image if memory else "memories/anu_cooking_with_lakshmi.jpg",
            memory_chain=[
                MemoryChainLink(
                    entity_type="memory",
                    entity_id=memory.id if memory else "memory_cooking",
                    entity_name=memory.title if memory else "Cooking",
                    image=memory.image if memory else "memories/anu_cooking_with_lakshmi.jpg",
                    narration="You were cooking together."
                )
            ],
            question=question,
            options=[
                SceneOption(
                    id="opt_food_correct",
                    text=target_food.name,
                    narration=f"Yes! Chapathi!",
                    next_scene_id="scene_7_family",
                    is_correct=True
                ),
                SceneOption(
                    id="opt_food_wrong",
                    text="Wrong food",
                    narration="Let me show you again.",
                    next_scene_id="scene_6_food",
                    is_correct=False
                )
            ],
            animation_cue="show_image"
        )
        
        return scene
    
    def _build_scene_7_family_memory(self) -> Scene:
        """Scene 7: Family memory - Who else is there?"""
        family_meal_memory = None
        for memory in self.repo.profile.memories:
            if "family_meal" in memory.id:
                family_meal_memory = memory
                break
        
        daughter = self.repo.get_person_by_relationship("daughter")
        son = self.repo.get_person_by_relationship("son")
        
        target = son if son else daughter
        wrong_options = [p for p in self.repo.profile.people if p.id != target.id]
        selected_wrong = wrong_options[:2] if len(wrong_options) >= 2 else []
        
        options = [
            GameOption(id=target.id, text=target.name, correct=True),
        ]
        for person in selected_wrong:
            options.append(GameOption(id=person.id, text=person.name, correct=False))
        
        import random
        random.shuffle(options)
        
        question = GameQuestion(
            id="q_family_recognition",
            question_text="Who else is in this family memory?",
            image=family_meal_memory.image if family_meal_memory else "memories/family_meal.jpg",
            options=options,
            target_type="person",
            target_id=target.id
        )
        
        scene = Scene(
            id="scene_7_family",
            title="Family Memory",
            narration="Look at this family memory. Who else is there?",
            background_image=family_meal_memory.image if family_meal_memory else "memories/family_meal.jpg",
            memory_chain=[
                MemoryChainLink(
                    entity_type="memory",
                    entity_id=family_meal_memory.id if family_meal_memory else "memory_meal",
                    entity_name=family_meal_memory.title if family_meal_memory else "Family Meal",
                    image=family_meal_memory.image if family_meal_memory else "memories/family_meal.jpg",
                    narration="Your family gathered for a meal."
                )
            ],
            question=question,
            options=[
                SceneOption(
                    id="opt_family_correct",
                    text=target.name,
                    narration=f"Yes! {target.name} is there with Anu.",
                    next_scene_id="scene_8_reward",
                    is_correct=True
                ),
                SceneOption(
                    id="opt_family_wrong",
                    text="Wrong person",
                    narration="Let me show you again.",
                    next_scene_id="scene_7_family",
                    is_correct=False
                )
            ],
            animation_cue="show_image"
        )
        
        return scene
    
    def _build_scene_8_reward(self) -> Scene:
        """Scene 8: Final reward and celebration."""
        daughter = self.repo.get_person_by_relationship("daughter")
        
        scene = Scene(
            id="scene_8_reward",
            title="Well Remembered!",
            narration=f"You remembered many things about {daughter.name} and your family. Well done!",
            background_image=None,
            memory_chain=[
                MemoryChainLink(
                    entity_type="person",
                    entity_id=daughter.id,
                    entity_name=daughter.name,
                    image=daughter.image,
                    narration=f"You spent time with memories of {daughter.name}."
                )
            ],
            options=[
                SceneOption(
                    id="opt_finish",
                    text="Finish",
                    narration="Thank you for spending time with your memories.",
                    next_scene_id=None,
                    is_correct=None
                )
            ],
            animation_cue="celebrate"
        )
        
        return scene
