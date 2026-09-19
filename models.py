"""
Data models for the Dementia Memory Platform.
Using Pydantic for validation and serialization.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel


class MemoryEntity(BaseModel):
    """Base class for memory entities (people, places, food, etc.)"""
    id: str
    name: str
    image: str


class Person(MemoryEntity):
    """Represents a person in the patient's memory."""
    relationship: str  # "daughter", "son", "self", etc.


class Place(MemoryEntity):
    """Represents a place in the patient's memory."""
    pass


class Food(MemoryEntity):
    """Represents food in the patient's memory."""
    pass


class Home(MemoryEntity):
    """Represents a home/room in the patient's memory."""
    pass


class Object(MemoryEntity):
    """Represents an object in the patient's memory."""
    pass


class Memory(BaseModel):
    """Represents a composite memory connecting multiple entities."""
    id: str
    title: str
    people: List[str] = []  # List of person IDs
    places: List[str] = []  # List of place IDs
    home: List[str] = []  # List of home IDs
    food: List[str] = []  # List of food IDs
    objects: List[str] = []  # List of object IDs
    description: str
    image: str


class PatientProfile(BaseModel):
    """Complete patient memory profile."""
    patient_id: str
    patient_name: str
    people: List[Person] = []
    places: List[Place] = []
    home: List[Home] = []
    food: List[Food] = []
    objects: List[Object] = []
    memories: List[Memory] = []


class GameOption(BaseModel):
    """A single option in a game question."""
    id: str
    text: str
    correct: bool


class GameQuestion(BaseModel):
    """A single question in the game."""
    id: str
    question_text: str
    image: str
    options: List[GameOption]
    target_type: str  # "person", "food", "place", etc.
    target_id: str  # The ID being asked about


class GameEvent(BaseModel):
    """Records a single player interaction."""
    target_type: str  # "person_recall", "food_recall", "place_recall", etc.
    target_id: str
    target_name: str
    answer_id: str
    answer_text: str
    correct: bool
    hint_level: int = 0  # 0 = no hints, 1+ = hints used
    attempt_number: int = 1


class GameSession(BaseModel):
    """Records a complete game session."""
    patient_id: str
    session_id: str
    game_name: str
    events: List[GameEvent] = []
    
    def add_event(self, event: GameEvent):
        """Add an event to the session."""
        self.events.append(event)
    
    def get_summary(self):
        """Get summary of recall types."""
        independent_recalls = len([e for e in self.events if e.hint_level == 0 and e.correct])
        cue_assisted_recalls = len([e for e in self.events if e.hint_level > 0 and e.correct])
        incorrect = len([e for e in self.events if not e.correct])
        
        return {
            "independent_recalls": independent_recalls,
            "cue_assisted_recalls": cue_assisted_recalls,
            "incorrect_answers": incorrect,
            "total_events": len(self.events)
        }


class MemoryCue(BaseModel):
    """A memory cue to help the patient remember."""
    level: int  # 1 = visual, 2 = description, 3 = partial reveal
    image: Optional[str] = None
    text: str
    memory_associations: List[str] = []  # Related memory IDs


class SceneOption(BaseModel):
    """An option the patient can select in a scene."""
    id: str
    text: str
    narration: str  # What the narrator says when this is selected
    next_scene_id: Optional[str] = None  # Where to go after selection
    is_correct: Optional[bool] = None  # For recall questions (True/False/None for neutral)
    hint_level: int = 0  # For tracking cues


class MemoryChainLink(BaseModel):
    """Tracks the chain of memory associations in a scene."""
    entity_type: str  # "person", "place", "food", "object", "memory"
    entity_id: str
    entity_name: str
    image: str
    narration: str  # What the narrator says about this entity


class Scene(BaseModel):
    """Represents a single scene in the story."""
    id: str
    title: str
    narration: str  # Opening narration for the scene
    background_image: Optional[str] = None
    memory_chain: List[MemoryChainLink] = []  # Entities displayed in order
    question: Optional[GameQuestion] = None  # If this scene has a recall question
    options: List[SceneOption] = []  # Player choices
    animation_cue: Optional[str] = None  # e.g., "hug", "smile", "celebrate"
    outcome_tracking: bool = True  # Whether to record events from this scene


class Story(BaseModel):
    """Represents a complete narrative game story."""
    id: str
    title: str
    description: str
    patient_id: str
    cognitive_target: str  # e.g., "person_recall", "family_association"
    memory_chain_goal: List[str]  # The intended memory progression, e.g., ["home", "kitchen", "chapathi", "person_anu"]
    scenes: List[Scene] = []
    
    def get_scene_by_id(self, scene_id: str) -> Optional[Scene]:
        """Get a scene by its ID."""
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        return None


class StorySession(BaseModel):
    """Records a complete story playthrough."""
    patient_id: str
    session_id: str
    story_id: str
    story_title: str
    current_scene_id: str
    visited_scenes: List[str] = []
    game_events: List[GameEvent] = []
    memory_associations_made: List[str] = []  # Track which associations were successfully made
    
    def add_event(self, event: GameEvent):
        """Add an event to the session."""
        self.game_events.append(event)
    
    def visit_scene(self, scene_id: str):
        """Record visiting a scene."""
        if scene_id not in self.visited_scenes:
            self.visited_scenes.append(scene_id)
    
    def add_association(self, association: str):
        """Record a successfully made memory association."""
        if association not in self.memory_associations_made:
            self.memory_associations_made.append(association)


class AnimationAction(BaseModel):
    """Represents a single animation action in a sequence."""
    id: str  # e.g., "daughter_walk_to_mother"
    duration: float = 0.0  # Duration in seconds (0 = use default)
    trigger_narration: Optional[str] = None  # Optional narration to play during this action
    next_action: Optional[str] = None  # ID of next action in sequence


class ActionSequence(BaseModel):
    """A sequence of animation actions triggered by a patient choice."""
    id: str  # e.g., "correct_answer_daughter"
    description: str  # Human-readable description
    actions: List[AnimationAction] = []  # Ordered list of actions
    outcome_narration: str = ""  # Final narration after sequence completes
    
    def get_action_ids(self) -> List[str]:
        """Get list of action IDs in order."""
        return [a.id for a in self.actions]


class SceneBlueprint(BaseModel):
    """Blueprint for a single scene in the game."""
    scene_id: str
    scene_type: str  # "narrative", "recall_question", "reward"
    
    # Environment/visuals
    environment: Optional[str] = None  # Asset ID for background
    characters: List[str] = []  # Character asset IDs to display
    memory_assets: List[str] = []  # Memory/food/object asset IDs to show
    
    # Content
    narration: str = ""
    question_text: Optional[str] = None
    
    # Interactions
    options: List[Dict[str, str]] = []  # [{"id": "...", "text": "...", "action": "..."}]
    
    # Actions
    initial_action: Optional[str] = None  # Animation to play when scene starts
    action_map: Dict[str, str] = {}  # Maps option ID → action sequence ID
    
    # Navigation
    next_scene_on_continue: Optional[str] = None  # For non-branching scenes


class GameBlueprint(BaseModel):
    """Complete game blueprint - what AI generates, what Unity executes."""
    blueprint_id: str
    game_id: str
    story_title: str
    patient_id: str
    
    # Story info
    cognitive_target: str  # "person_recall", "family_association", etc.
    memory_chain_goal: List[str]  # Intended memory progression
    
    # All scenes
    scenes: List[SceneBlueprint] = []
    
    # Metadata
    created_by: str = "ai_generator"  # or "manual", "template"
    version: str = "1.0"
    validated: bool = False
    validation_errors: List[str] = []
    
    def get_scene(self, scene_id: str) -> Optional[SceneBlueprint]:
        """Get a scene by ID."""
        for scene in self.scenes:
            if scene.scene_id == scene_id:
                return scene
        return None
    
    def get_validation_status(self) -> Dict:
        """Get validation status."""
        return {
            "validated": self.validated,
            "errors": self.validation_errors,
            "scenes_count": len(self.scenes),
            "is_valid": self.validated and len(self.validation_errors) == 0
        }
