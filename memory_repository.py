"""
Memory Repository - loads and manages patient memory data.
"""

import json
from pathlib import Path
from typing import Optional, List
from models import (
    PatientProfile, Person, Place, Food, Home, Object, Memory
)


class MemoryRepository:
    """Loads and manages patient memories from memories.json."""
    
    def __init__(self, patient_folder: Path):
        """
        Initialize the repository.
        
        Args:
            patient_folder: Path to the patient's folder (e.g., Patient_001_Lakshmi)
        """
        self.patient_folder = Path(patient_folder)
        self.memories_file = self.patient_folder / "memories.json"
        self.profile = None
        
    def load(self) -> PatientProfile:
        """Load patient profile from memories.json."""
        if not self.memories_file.exists():
            raise FileNotFoundError(f"memories.json not found at {self.memories_file}")
        
        with open(self.memories_file, 'r') as f:
            data = json.load(f)
        
        # Parse the JSON into Pydantic models
        people = [Person(**p) for p in data.get("people", [])]
        places = [Place(**p) for p in data.get("places", [])]
        home = [Home(**h) for h in data.get("home", [])]
        food = [Food(**f) for f in data.get("food", [])]
        objects = [Object(**o) for o in data.get("objects", [])]
        memories = [Memory(**m) for m in data.get("memories", [])]
        
        self.profile = PatientProfile(
            patient_id=data["patient_id"],
            patient_name=data["patient_name"],
            people=people,
            places=places,
            home=home,
            food=food,
            objects=objects,
            memories=memories
        )
        
        return self.profile
    
    def get_person_by_relationship(self, relationship: str) -> Optional[Person]:
        """Find a person by relationship (e.g., 'daughter', 'son')."""
        if not self.profile:
            raise ValueError("Profile not loaded. Call load() first.")
        
        for person in self.profile.people:
            if person.relationship == relationship:
                return person
        return None
    
    def get_memories_for_person(self, person_id: str) -> List[Memory]:
        """Get all memories associated with a person."""
        if not self.profile:
            raise ValueError("Profile not loaded. Call load() first.")
        
        return [m for m in self.profile.memories if person_id in m.people]
    
    def get_entity_by_id(self, entity_id: str):
        """Get any entity (person, place, food, etc.) by its ID."""
        if not self.profile:
            raise ValueError("Profile not loaded. Call load() first.")
        
        # Search in all entity lists
        for person in self.profile.people:
            if person.id == entity_id:
                return person
        for place in self.profile.places:
            if place.id == entity_id:
                return place
        for home in self.profile.home:
            if home.id == entity_id:
                return home
        for food in self.profile.food:
            if food.id == entity_id:
                return food
        for obj in self.profile.objects:
            if obj.id == entity_id:
                return obj
        return None
    
    def resolve_image_path(self, relative_path: str) -> Path:
        """Convert relative image path to absolute path."""
        return self.patient_folder / relative_path
    
    def get_all_people(self) -> List[Person]:
        """Get all people in the patient's profile."""
        if not self.profile:
            raise ValueError("Profile not loaded. Call load() first.")
        return self.profile.people
    
    def get_all_memories(self) -> List[Memory]:
        """Get all memories."""
        if not self.profile:
            raise ValueError("Profile not loaded. Call load() first.")
        return self.profile.memories
