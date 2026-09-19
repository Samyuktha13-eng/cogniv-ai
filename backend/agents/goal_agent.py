"""
Goal Agent - Parse natural language caregiver goals into structured format.

Converts: "Help Lakshmi remember her daughter Anu"
Into: {target_type: "person", target_id: "person_anu", objective: "person_recognition"}
"""

import re
from typing import Dict, Optional, List
from backend.models import PatientProfile


class GoalAgent:
    """
    Parses natural language goal statements from caregivers.
    
    Identifies:
    - What type of memory (person, place, food, association)
    - Which specific memory entity
    - What cognitive goal (recognition, association, familiarization)
    - Context clues
    """
    
    # Common keywords for different memory types
    PERSON_KEYWORDS = ["daughter", "son", "mother", "father", "sister", "brother", 
                       "grandmother", "grandfather", "wife", "husband", "grandchild",
                       "aunt", "uncle", "cousin", "friend", "person", "who", "remember"]
    
    PLACE_KEYWORDS = ["temple", "home", "house", "kitchen", "garden", "room", "place",
                      "where", "visit", "go", "school", "work", "street"]
    
    FOOD_KEYWORDS = ["chapathi", "rice", "cooking", "cook", "food", "eat", "meal",
                     "banana", "recipe", "what", "make", "dish"]
    
    FAMILY_KEYWORDS = ["family", "together", "related", "relationship", "member",
                       "relation", "connection", "bond", "relative"]
    
    def parse_goal(self, goal_text: str, patient_profile: Optional[PatientProfile] = None) -> Dict:
        """
        Parse natural language goal into structured format.
        
        Args:
            goal_text: e.g., "Help Lakshmi remember her daughter Anu"
            patient_profile: Optional patient data for entity matching
        
        Returns:
            {
                "target_type": "person" | "place" | "food" | "family" | "association",
                "target_id": "person_anu" | "place_temple" | etc.,
                "target_name": "Anu" | "Temple" | etc.,
                "objective": "person_recognition" | "place_familiarization" | etc.,
                "context": "daughter" | "cooking together" | etc.,
                "confidence": 0.0-1.0,
                "memory_chain_hint": ["home", "kitchen", "chapathi"] if available
            }
        """
        
        goal_lower = goal_text.lower()
        result = {
            "target_type": None,
            "target_id": None,
            "target_name": None,
            "objective": None,
            "context": None,
            "confidence": 0.5,
            "memory_chain_hint": []
        }
        
        # 1. Detect target type
        target_type = self._detect_target_type(goal_lower)
        result["target_type"] = target_type
        
        # 2. Extract entity name
        entity_name = self._extract_entity_name(goal_text, target_type)
        result["target_name"] = entity_name
        
        # 3. Generate target_id
        if entity_name:
            result["target_id"] = f"{target_type}_{entity_name.lower().replace(' ', '_')}"
            result["confidence"] = 0.9
        
        # 4. Determine objective
        objective = self._determine_objective(goal_lower, target_type)
        result["objective"] = objective
        
        # 5. Extract context
        context = self._extract_context(goal_text, target_type)
        result["context"] = context
        
        # 6. Build memory chain hint (if clear)
        chain = self._hint_memory_chain(goal_lower, target_type, entity_name)
        result["memory_chain_hint"] = chain
        
        return result
    
    def _detect_target_type(self, goal_lower: str) -> str:
        """Detect what type of memory this goal targets."""
        
        # Check for person
        if any(kw in goal_lower for kw in ["daughter", "son", "mother", "father"]):
            return "person"
        if any(kw in goal_lower for kw in ["sister", "brother", "grandmother", "grandfather"]):
            return "person"
        if any(kw in goal_lower for kw in ["wife", "husband", "friend"]):
            return "person"
        
        # Check for place
        if any(kw in goal_lower for kw in ["temple", "home", "house", "garden", "kitchen"]):
            return "place"
        if any(kw in goal_lower for kw in ["where", "visit", "go to", "place"]):
            return "place"
        
        # Check for food
        if any(kw in goal_lower for kw in ["chapathi", "rice", "banana", "cooking", "cook"]):
            return "food"
        if any(kw in goal_lower for kw in ["what were you making", "food", "eat", "meal"]):
            return "food"
        
        # Check for family/association
        if any(kw in goal_lower for kw in ["family", "together", "related", "connection"]):
            return "family"
        
        # Default: assume person (most common)
        return "person"
    
    def _extract_entity_name(self, goal_text: str, target_type: str) -> Optional[str]:
        """Extract the specific entity name from goal text."""
        
        # Pattern: "remember her X" or "remember X"
        patterns = [
            r"remember\s+(?:her|his|their)?\s+(\w+)",  # "remember her Anu"
            r"remember\s+(?:the)?\s+(\w+)",  # "remember the temple"
            r"remember\s+(\w+)\s+(?:who|where|what)",  # "remember Anu who..."
            r"with\s+(\w+)",  # "cooking with Anu"
            r"at\s+(?:the)?\s+(\w+)",  # "at the temple"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, goal_text, re.IGNORECASE)
            if match:
                entity_name = match.group(1)
                # Filter out common words
                if entity_name.lower() not in ["the", "a", "an", "her", "his", "their"]:
                    return entity_name
        
        return None
    
    def _determine_objective(self, goal_lower: str, target_type: str) -> str:
        """Determine the cognitive objective."""
        
        if "recognize" in goal_lower or "who is" in goal_lower or "remember who" in goal_lower:
            return "recognition"
        
        if "associate" in goal_lower or "connect" in goal_lower or "together" in goal_lower:
            return "association"
        
        if "where" in goal_lower or "familiarize" in goal_lower:
            return "place_familiarization"
        
        if "cook" in goal_lower or "make" in goal_lower:
            return "activity_recall"
        
        # Default by type
        if target_type == "person":
            return "person_recognition"
        elif target_type == "place":
            return "place_familiarization"
        elif target_type == "food":
            return "food_recognition"
        elif target_type == "family":
            return "family_association"
        
        return "general_recall"
    
    def _extract_context(self, goal_text: str, target_type: str) -> Optional[str]:
        """Extract context about how the entity is related."""
        
        if "daughter" in goal_text.lower():
            return "daughter"
        if "son" in goal_text.lower():
            return "son"
        if "mother" in goal_text.lower():
            return "mother"
        if "father" in goal_text.lower():
            return "father"
        if "cooking" in goal_text.lower():
            return "cooking_together"
        if "temple" in goal_text.lower():
            return "family_temple"
        if "kitchen" in goal_text.lower():
            return "family_kitchen"
        
        return None
    
    def _hint_memory_chain(self, goal_lower: str, target_type: str, entity_name: Optional[str]) -> List[str]:
        """Build a hint about the memory chain progression."""
        
        chain = []
        
        # Common patterns
        if "cook" in goal_lower:
            chain = ["home", "kitchen", "chapathi", target_type]
        elif "daughter" in goal_lower:
            chain = ["home", "kitchen", "chapathi", "person", "family"]
        elif "temple" in goal_lower:
            chain = ["home", "temple", "family", "worship"]
        elif "family" in goal_lower:
            chain = ["home", "family", "togetherness"]
        else:
            # Generic
            chain = ["home", "familiar", target_type]
        
        return chain
    
    def validate_goal(self, goal: Dict) -> bool:
        """Check if parsed goal is valid."""
        return (
            goal.get("target_type") is not None and
            goal.get("target_name") is not None and
            goal.get("objective") is not None and
            goal.get("confidence", 0) > 0.5
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    agent = GoalAgent()
    
    # Test cases
    goals = [
        "Help Lakshmi remember her daughter Anu",
        "Help Lakshmi remember who cooked chapathi with her",
        "Help Lakshmi associate the kitchen with family memories",
        "Help Lakshmi remember the family temple",
    ]
    
    for goal in goals:
        print(f"\nGoal: {goal}")
        result = agent.parse_goal(goal)
        print(f"  Target Type: {result['target_type']}")
        print(f"  Target Name: {result['target_name']}")
        print(f"  Target ID: {result['target_id']}")
        print(f"  Objective: {result['objective']}")
        print(f"  Context: {result['context']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Memory Chain: {result['memory_chain_hint']}")
        print(f"  Valid: {agent.validate_goal(result)}")
