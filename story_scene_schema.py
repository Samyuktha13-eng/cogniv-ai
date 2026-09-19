"""
Story Scene Schema - Define video scene structure for narrative generation.

Each scene is a JSON-serializable object that contains:
- Scene metadata (id, period, sequence)
- Character references (with reference images)
- Environment (with reference images)
- Objects and visual elements
- Story context
- Video generation prompt
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class ScenePeriod(Enum):
    """Time period for the scene."""
    PAST = "past"           # Memory/flashback scenes
    PRESENT = "present"      # Current day scenes
    TRANSITION = "transition" # Transition from past to present


@dataclass
class Reference:
    """A reference image or object."""
    name: str
    asset_path: str
    type: str = "image"  # "image", "object", "environment"
    description: str = ""


@dataclass
class Character:
    """Character in the scene."""
    name: str
    character_id: str  # e.g., "lakshmi", "anu"
    reference_images: List[Reference] = field(default_factory=list)
    age_note: str = ""  # e.g., "younger in this past memory"
    emotional_state: str = ""  # e.g., "thoughtful", "warm", "emotional"


@dataclass
class SceneMetadata:
    """Metadata about the scene."""
    scene_id: str
    sequence_number: int
    title: str
    period: ScenePeriod
    duration_seconds: int = 8  # Default video duration


@dataclass
class StoryScene:
    """Complete scene definition for video generation."""
    
    metadata: SceneMetadata
    characters: List[Character] = field(default_factory=list)
    environment: Optional[Reference] = None
    objects: List[Reference] = field(default_factory=list)
    story_context: str = ""  # Brief description of what's happening
    video_prompt: str = ""    # Full detailed prompt for video generator
    notes: str = ""           # Implementation notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}
        
        # Metadata
        if self.metadata:
            result["metadata"] = {
                "scene_id": self.metadata.scene_id,
                "sequence_number": self.metadata.sequence_number,
                "title": self.metadata.title,
                "period": self.metadata.period.value,
                "duration_seconds": self.metadata.duration_seconds,
            }
        
        # Characters
        if self.characters:
            result["characters"] = []
            for char in self.characters:
                char_dict = {
                    "name": char.name,
                    "character_id": char.character_id,
                }
                if char.age_note:
                    char_dict["age_note"] = char.age_note
                if char.emotional_state:
                    char_dict["emotional_state"] = char.emotional_state
                if char.reference_images:
                    char_dict["reference_images"] = [
                        {"name": ref.name, "asset_path": ref.asset_path}
                        for ref in char.reference_images
                    ]
                result["characters"].append(char_dict)
        
        # Environment
        if self.environment:
            result["environment"] = {
                "name": self.environment.name,
                "asset_path": self.environment.asset_path
            }
        
        # Objects
        if self.objects:
            result["objects"] = [
                {"name": obj.name, "asset_path": obj.asset_path}
                for obj in self.objects
            ]
        
        # Story and prompts
        result["story_context"] = self.story_context
        result["video_prompt"] = self.video_prompt
        
        if self.notes:
            result["notes"] = self.notes
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save(self, filepath: str) -> None:
        """Save scene to JSON file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StoryScene':
        """Create from dictionary."""
        meta_data = data.get("metadata", {})
        metadata = SceneMetadata(
            scene_id=meta_data.get("scene_id", ""),
            sequence_number=meta_data.get("sequence_number", 0),
            title=meta_data.get("title", ""),
            period=ScenePeriod(meta_data.get("period", "past")),
            duration_seconds=meta_data.get("duration_seconds", 8),
        )
        
        characters = []
        for char_data in data.get("characters", []):
            refs = [
                Reference(
                    name=ref.get("name", ""),
                    asset_path=ref.get("asset_path", "")
                )
                for ref in char_data.get("reference_images", [])
            ]
            characters.append(Character(
                name=char_data.get("name", ""),
                character_id=char_data.get("character_id", ""),
                reference_images=refs,
                age_note=char_data.get("age_note", ""),
                emotional_state=char_data.get("emotional_state", ""),
            ))
        
        env_data = data.get("environment")
        environment = Reference(
            name=env_data.get("name", ""),
            asset_path=env_data.get("asset_path", "")
        ) if env_data else None
        
        objects = [
            Reference(name=obj.get("name", ""), asset_path=obj.get("asset_path", ""))
            for obj in data.get("objects", [])
        ]
        
        return StoryScene(
            metadata=metadata,
            characters=characters,
            environment=environment,
            objects=objects,
            story_context=data.get("story_context", ""),
            video_prompt=data.get("video_prompt", ""),
            notes=data.get("notes", ""),
        )
