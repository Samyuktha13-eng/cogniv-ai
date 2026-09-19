"""
Game Generator - creates game scenarios from patient memories.
"""

import random
from typing import List, Tuple
from models import (
    GameQuestion, GameOption, Memory, Person, Food, MemoryCue
)
from memory_repository import MemoryRepository


class GameGenerator:
    """Generates game scenarios from patient memory data."""
    
    def __init__(self, repo: MemoryRepository):
        """
        Initialize the game generator.
        
        Args:
            repo: MemoryRepository instance with loaded memories
        """
        self.repo = repo
        if not self.repo.profile:
            raise ValueError("Repository profile not loaded. Call repo.load() first.")
    
    def generate_person_recognition_game(self, target_relationship: str) -> GameQuestion:
        """
        Generate a person recognition game.
        
        Example: "Remember My Daughter"
        
        Args:
            target_relationship: The relationship to target (e.g., "daughter")
        
        Returns:
            GameQuestion with image and options
        """
        target_person = self.repo.get_person_by_relationship(target_relationship)
        if not target_person:
            raise ValueError(f"No person found with relationship: {target_relationship}")
        
        # Get all other people to create wrong options
        all_people = self.repo.get_all_people()
        wrong_people = [p for p in all_people if p.id != target_person.id]
        
        if len(wrong_people) < 2:
            # Need at least 2 wrong options
            wrong_people = [
                Person(id="f_priya", name="Priya", relationship="other", image=""),
                Person(id="f_radha", name="Radha", relationship="other", image="")
            ]
        
        # Select 2 random wrong options
        selected_wrong = random.sample(wrong_people, min(2, len(wrong_people)))
        
        # Create options
        options = [
            GameOption(id=target_person.id, text=target_person.name, correct=True),
            GameOption(id=selected_wrong[0].id, text=selected_wrong[0].name, correct=False),
            GameOption(id=selected_wrong[1].id, text=selected_wrong[1].name, correct=False)
        ]
        
        # Shuffle options
        random.shuffle(options)
        
        # Create the question
        question = GameQuestion(
            id="q_person_recognition",
            question_text="Who is this?",
            image=target_person.image,
            options=options,
            target_type="person",
            target_id=target_person.id
        )
        
        return question
    
    def generate_food_recognition_game(self, target_food_id: str) -> GameQuestion:
        """
        Generate a food recognition game.
        
        Args:
            target_food_id: The food ID to target
        
        Returns:
            GameQuestion
        """
        target_food = None
        for food in self.repo.profile.food:
            if food.id == target_food_id:
                target_food = food
                break
        
        if not target_food:
            raise ValueError(f"Food not found: {target_food_id}")
        
        # Get other foods for wrong options
        other_foods = [f for f in self.repo.profile.food if f.id != target_food_id]
        selected_wrong = random.sample(other_foods, min(2, len(other_foods)))
        
        options = [
            GameOption(id=target_food.id, text=target_food.name, correct=True),
            GameOption(id=selected_wrong[0].id, text=selected_wrong[0].name, correct=False),
            GameOption(id=selected_wrong[1].id, text=selected_wrong[1].name, correct=False)
        ]
        
        random.shuffle(options)
        
        question = GameQuestion(
            id="q_food_recognition",
            question_text="What food is this?",
            image=target_food.image,
            options=options,
            target_type="food",
            target_id=target_food_id
        )
        
        return question
    
    def generate_memory_cues(self, memory: Memory, hint_level: int = 1) -> List[MemoryCue]:
        """
        Generate progressive memory cues for a specific memory.
        
        Args:
            memory: The memory to create cues for
            hint_level: How many hint levels to generate
        
        Returns:
            List of MemoryCue objects with increasing strength
        """
        cues = []
        
        # Level 1: Visual cue - show the memory image
        if hint_level >= 1:
            cues.append(MemoryCue(
                level=1,
                image=memory.image,
                text="Look at this memory.",
                memory_associations=memory.people + memory.food
            ))
        
        # Level 2: Description cue
        if hint_level >= 2:
            cues.append(MemoryCue(
                level=2,
                text=memory.description,
                memory_associations=memory.people + memory.food
            ))
        
        # Level 3: Strong association cue with person name
        if hint_level >= 3 and memory.people:
            person = self.repo.get_entity_by_id(memory.people[0])
            if person:
                cues.append(MemoryCue(
                    level=3,
                    text=f"Her name starts with {person.name[0].upper()}...",
                    memory_associations=[person.id]
                ))
        
        return cues
    
    def get_memory_clues_for_person(self, person_id: str) -> Tuple[MemoryCue, Memory]:
        """
        Get a memory clue to help patient recall a person.
        
        Args:
            person_id: The person to get clues for
        
        Returns:
            Tuple of (MemoryCue, associated Memory)
        """
        memories = self.repo.get_memories_for_person(person_id)
        
        if not memories:
            person = self.repo.get_entity_by_id(person_id)
            if person:
                return (
                    MemoryCue(level=1, text=f"Think about {person.name}"),
                    None
                )
            raise ValueError(f"No memories found for person: {person_id}")
        
        # Select the first memory as a clue
        selected_memory = memories[0]
        cue = MemoryCue(
            level=1,
            image=selected_memory.image,
            text=selected_memory.description,
            memory_associations=selected_memory.people
        )
        
        return (cue, selected_memory)
