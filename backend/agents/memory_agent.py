"""
Memory Agent - Retrieve patient memories based on goal.

Loads patient memory data and returns relevant entities based on goal.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from backend.models import PatientProfile, Person, Place, Food, Home, Object, Memory


class MemoryRepository:
    """Load and manage patient memory data."""
    
    def __init__(self, patient_data_dir: str = "Patient_001_Lakshmi"):
        self.patient_data_dir = patient_data_dir
        self.memories_file = os.path.join(patient_data_dir, "memories.json")
    
    def load_patient_profile(self, patient_id: str) -> Optional[PatientProfile]:
        """
        Load patient profile from JSON file.
        
        Args:
            patient_id: e.g., "Patient_001_Lakshmi"
        
        Returns:
            PatientProfile object or None if not found
        """
        
        # For demo: hardcode the known patient
        if "Lakshmi" in patient_id:
            return self._load_lakshmi_profile()
        
        return None
    
    def _load_lakshmi_profile(self) -> PatientProfile:
        """Load Lakshmi's hardcoded memory profile."""
        
        # People
        people = [
            Person(id="person_anu", name="Anu", image="assets/characters/anu.png", 
                   relationship="daughter"),
            Person(id="person_rahul", name="Rahul", image="assets/characters/rahul.png",
                   relationship="son"),
            Person(id="person_lakshmi", name="Lakshmi", image="assets/characters/mother.png",
                   relationship="self"),
        ]
        
        # Places
        places = [
            Place(id="place_temple", name="Family Temple", image="assets/environments/temple.png"),
            Place(id="place_garden", name="Family Garden", image="assets/environments/garden.png"),
        ]
        
        # Home/Rooms
        homes = [
            Home(id="home_kitchen", name="Kitchen", image="assets/environments/kitchen.png"),
            Home(id="home_living_room", name="Living Room", image="assets/environments/living_room.png"),
            Home(id="home_front", name="House Front", image="assets/environments/house_front.png"),
        ]
        
        # Food
        foods = [
            Food(id="food_chapathi", name="Chapathi", image="assets/food/chapathi.png"),
            Food(id="food_rice", name="Rice", image="assets/food/rice.png"),
            Food(id="food_banana", name="Banana", image="assets/food/banana.png"),
        ]
        
        # Objects
        objects = [
            Object(id="obj_cooking_pot", name="Cooking Pot", image="assets/objects/pot.png"),
            Object(id="obj_dining_table", name="Dining Table", image="assets/objects/table.png"),
        ]
        
        # Composite Memories
        memories = [
            Memory(
                id="mem_anu_cooking",
                title="Anu cooking in kitchen",
                people=["person_anu"],
                home=["home_kitchen"],
                food=["food_chapathi"],
                description="Anu and you cooking chapathi together",
                image="assets/memories/anu_cooking.png"
            ),
            Memory(
                id="mem_family_meal",
                title="Family meal together",
                people=["person_anu", "person_rahul"],
                home=["home_kitchen"],
                food=["food_chapathi", "food_rice"],
                description="The family eating together",
                image="assets/memories/family_meal.png"
            ),
            Memory(
                id="mem_temple_visit",
                title="Temple visit with family",
                people=["person_anu", "person_rahul"],
                places=["place_temple"],
                description="Family visiting the temple together",
                image="assets/memories/temple_visit.png"
            ),
        ]
        
        return PatientProfile(
            patient_id="Patient_001_Lakshmi",
            patient_name="Lakshmi",
            people=people,
            places=places,
            home=homes,
            food=foods,
            objects=objects,
            memories=memories
        )


class MemoryAgent:
    """
    Retrieve patient memories relevant to a goal.
    
    Takes a parsed goal (from Goal Agent) and returns relevant
    memory entities that can be used to build a story.
    """
    
    def __init__(self):
        self.repository = MemoryRepository()
    
    def get_memories(self, patient_id: str, goal: Dict) -> Dict:
        """
        Retrieve memories relevant to the goal.
        
        Args:
            patient_id: e.g., "Patient_001_Lakshmi"
            goal: Parsed goal from Goal Agent
                {
                    target_type: "person",
                    target_id: "person_anu",
                    target_name: "Anu",
                    objective: "person_recognition",
                    memory_chain_hint: ["home", "kitchen", "chapathi", "person", "family"]
                }
        
        Returns:
            {
                "target_entity": {...},  # The entity being focused on
                "related_entities": {...},  # People, places, foods related to it
                "composite_memories": [...],  # Multi-entity memories
                "associations": {entity_id: [related_ids]},  # Connections
                "recommended_chain": [...]  # Suggested memory progression
            }
        """
        
        # Load patient profile
        profile = self.repository.load_patient_profile(patient_id)
        if not profile:
            return {"error": f"Patient {patient_id} not found"}
        
        # Extract from goal
        target_type = goal.get("target_type")
        target_id = goal.get("target_id")
        target_name = goal.get("target_name")
        chain_hint = goal.get("memory_chain_hint", [])
        
        # Get the target entity
        target_entity = self._get_entity(profile, target_type, target_id)
        
        # Get related entities
        related = self._get_related_entities(profile, target_entity, target_type)
        
        # Get relevant memories
        relevant_memories = self._get_relevant_memories(profile, target_id, chain_hint)
        
        # Build associations
        associations = self._build_associations(profile, target_id)
        
        # Recommend memory chain
        recommended_chain = self._recommend_chain(target_type, chain_hint, associations)
        
        return {
            "patient_id": patient_id,
            "patient_name": profile.patient_name,
            "target_entity": target_entity.dict() if target_entity else None,
            "related_entities": related,
            "composite_memories": [m.dict() for m in relevant_memories],
            "associations": associations,
            "recommended_chain": recommended_chain,
            "all_entities": {
                "people": [p.dict() for p in profile.people],
                "places": [p.dict() for p in profile.places],
                "homes": [h.dict() for h in profile.home],
                "foods": [f.dict() for f in profile.food],
                "objects": [o.dict() for o in profile.objects],
            }
        }
    
    def _get_entity(self, profile: PatientProfile, entity_type: str, entity_id: str) -> Optional[object]:
        """Get a specific entity by type and ID."""
        
        if entity_type == "person":
            for p in profile.people:
                if p.id == entity_id:
                    return p
        elif entity_type == "place":
            for p in profile.places:
                if p.id == entity_id:
                    return p
        elif entity_type == "food":
            for f in profile.food:
                if f.id == entity_id:
                    return f
        elif entity_type == "home":
            for h in profile.home:
                if h.id == entity_id:
                    return h
        
        return None
    
    def _get_related_entities(self, profile: PatientProfile, target_entity: object, 
                             target_type: str) -> Dict:
        """Get entities related to the target entity."""
        
        related = {
            "people": [],
            "places": [],
            "homes": [],
            "foods": [],
            "objects": []
        }
        
        if not target_entity:
            return related
        
        # If target is a person, find memories with them
        if target_type == "person" and hasattr(target_entity, "id"):
            target_id = target_entity.id
            
            for mem in profile.memories:
                if target_id in mem.people:
                    # Add all entities from this memory
                    for person_id in mem.people:
                        person = self._get_entity(profile, "person", person_id)
                        if person and person.id != target_id:
                            related["people"].append(person.dict())
                    
                    for place_id in mem.places:
                        place = self._get_entity(profile, "place", place_id)
                        if place:
                            related["places"].append(place.dict())
                    
                    for home_id in mem.home:
                        home = self._get_entity(profile, "home", home_id)
                        if home:
                            related["homes"].append(home.dict())
                    
                    for food_id in mem.food:
                        food = self._get_entity(profile, "food", food_id)
                        if food:
                            related["foods"].append(food.dict())
        
        return related
    
    def _get_relevant_memories(self, profile: PatientProfile, target_id: str, 
                              chain_hint: List[str]) -> List[Memory]:
        """Get composite memories involving the target."""
        
        relevant = []
        
        for mem in profile.memories:
            # If target is in this memory, include it
            if target_id in mem.people or target_id in mem.places or \
               target_id in mem.food or target_id in mem.home:
                relevant.append(mem)
        
        # If no direct matches, return all memories (good context)
        if not relevant and chain_hint:
            return profile.memories[:2]  # Return top 2
        
        return relevant
    
    def _build_associations(self, profile: PatientProfile, target_id: str) -> Dict[str, List[str]]:
        """Build a map of what entities are associated with the target."""
        
        associations = {}
        
        for mem in profile.memories:
            if target_id in mem.people:
                associations[target_id] = []
                
                # Add other people
                for p_id in mem.people:
                    if p_id != target_id:
                        associations[target_id].append(p_id)
                
                # Add places
                for place_id in mem.places:
                    associations[target_id].append(place_id)
                
                # Add food
                for food_id in mem.food:
                    associations[target_id].append(food_id)
                
                # Add homes
                for home_id in mem.home:
                    associations[target_id].append(home_id)
        
        return associations
    
    def _recommend_chain(self, target_type: str, hint: List[str], 
                        associations: Dict) -> List[str]:
        """Recommend a memory chain for story progression."""
        
        # If hint provided, use it
        if hint:
            return hint
        
        # Default chains by type
        if target_type == "person":
            return ["home", "kitchen", "food", "person", "family"]
        elif target_type == "place":
            return ["home", "journey", "arrival", "place", "family"]
        elif target_type == "food":
            return ["home", "kitchen", "ingredients", "cooking", "food", "family"]
        else:
            return ["home", "memory", "association", "family"]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from backend.agents.goal_agent import GoalAgent
    
    goal_agent = GoalAgent()
    memory_agent = MemoryAgent()
    
    # Test
    goal_text = "Help Lakshmi remember her daughter Anu"
    goal = goal_agent.parse_goal(goal_text)
    
    print(f"Goal: {goal_text}")
    print(f"Parsed Goal: {goal}\n")
    
    memories = memory_agent.get_memories("Patient_001_Lakshmi", goal)
    
    print("Retrieved Memories:")
    print(f"  Patient: {memories.get('patient_name')}")
    print(f"  Target Entity: {memories.get('target_entity')}")
    print(f"  Related People: {len(memories.get('related_entities', {}).get('people', []))}")
    print(f"  Composite Memories: {len(memories.get('composite_memories', []))}")
    print(f"  Recommended Chain: {memories.get('recommended_chain')}")
