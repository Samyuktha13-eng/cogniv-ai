"""
Story Flow Engine - Manages narrative progression through scenes.
Handles transitions, memory cues, and detailed outcome tracking.
"""

from typing import Optional, Dict, Tuple, List
from models import (
    Story, Scene, SceneOption, GameEvent, StorySession, MemoryCue, GameQuestion
)
from game_generator import GameGenerator
from outcome_tracker import OutcomeTracker


class StoryFlowEngine:
    """Manages the complete flow through a narrative story."""
    
    def __init__(self, story: Story, generator: GameGenerator, tracker: OutcomeTracker):
        """
        Initialize the story flow engine.
        
        Args:
            story: The Story object to play through
            generator: GameGenerator for creating recall questions
            tracker: OutcomeTracker for recording events
        """
        self.story = story
        self.generator = generator
        self.tracker = tracker
        self.repo = generator.repo
        
        self.current_session: Optional[StorySession] = None
        self.current_scene: Optional[Scene] = None
        self.current_hint_level = 0
        self.current_question_attempts = 0
    
    def start_story(self, session_id: str) -> Dict:
        """
        Start a new story session.
        
        Returns:
            First scene data for display
        """
        # Create story session
        self.current_session = StorySession(
            patient_id=self.story.patient_id,
            session_id=session_id,
            story_id=self.story.id,
            story_title=self.story.title,
            current_scene_id=self.story.scenes[0].id if self.story.scenes else ""
        )
        
        # Create game session in tracker
        self.tracker.create_session(session_id, self.story.title)
        
        # Start with first scene
        return self.present_scene(self.story.scenes[0].id)
    
    def present_scene(self, scene_id: str) -> Dict:
        """
        Present a scene to the patient.
        
        Returns:
            Scene data for display including narration, images, and options
        """
        scene = self.story.get_scene_by_id(scene_id)
        if not scene:
            raise ValueError(f"Scene not found: {scene_id}")
        
        self.current_scene = scene
        self.current_session.visit_scene(scene_id)
        self.current_hint_level = 0
        self.current_question_attempts = 0
        
        # Build memory chain display
        memory_chain_display = []
        for link in scene.memory_chain:
            image_path = str(self.repo.resolve_image_path(link.image)) if link.image else None
            memory_chain_display.append({
                "entity_type": link.entity_type,
                "entity_id": link.entity_id,
                "name": link.entity_name,
                "image": image_path,
                "narration": link.narration
            })
        
        # Build options display
        options_display = []
        if scene.question:
            # Display recall question options
            options_display = [
                {"id": opt.id, "text": opt.text}
                for opt in scene.question.options
            ]
        else:
            # Display narrative choice options
            options_display = [
                {"id": opt.id, "text": opt.text}
                for opt in scene.options
            ]
        
        background_image = None
        if scene.background_image:
            background_image = str(self.repo.resolve_image_path(scene.background_image))
        
        return {
            "scene_id": scene.id,
            "title": scene.title,
            "narration": scene.narration,
            "background_image": background_image,
            "memory_chain": memory_chain_display,
            "question_text": scene.question.question_text if scene.question else None,
            "question_image": str(self.repo.resolve_image_path(scene.question.image)) if scene.question else None,
            "options": options_display,
            "animation_cue": scene.animation_cue
        }
    
    def handle_scene_choice(self, option_id: str) -> Tuple[Dict, str]:
        """
        Handle a player choice in the current scene.
        
        Args:
            option_id: The selected option ID
        
        Returns:
            Tuple of (response_dict, next_scene_id)
        """
        if not self.current_scene:
            raise ValueError("No scene presented yet")
        
        # Find the selected option
        selected_option = None
        for opt in self.current_scene.options:
            if opt.id == option_id:
                selected_option = opt
                break
        
        if not selected_option:
            raise ValueError(f"Invalid option: {option_id}")
        
        response = {
            "narration": selected_option.narration,
            "next_scene_id": selected_option.next_scene_id,
            "animation_cue": None
        }
        
        return (response, selected_option.next_scene_id)
    
    def handle_recall_answer(self, option_id: str) -> Tuple[Dict, Optional[str]]:
        """
        Handle a recall question answer with progressive cuing.
        
        Returns:
            Tuple of (response_dict, next_scene_id or None if retry needed)
        """
        if not self.current_scene or not self.current_scene.question:
            raise ValueError("No recall question in current scene")
        
        self.current_question_attempts += 1
        
        # Find the selected option in the question
        selected_option = None
        for opt in self.current_scene.question.options:
            if opt.id == option_id:
                selected_option = opt
                break
        
        if not selected_option:
            raise ValueError(f"Invalid option: {option_id}")
        
        is_correct = selected_option.correct
        
        if is_correct:
            return self._handle_correct_recall(selected_option)
        else:
            return self._handle_incorrect_recall(selected_option)
    
    def _handle_correct_recall(self, option) -> Tuple[Dict, Optional[str]]:
        """Handle correct recall answer."""
        # Find which scene option leads to next scene
        next_scene_id = None
        for scene_opt in self.current_scene.options:
            if scene_opt.is_correct:
                next_scene_id = scene_opt.next_scene_id
                break
        
        # Record event
        event = GameEvent(
            target_type=self._get_target_type(),
            target_id=self.current_scene.question.target_id,
            target_name=option.text,
            answer_id=option.id,
            answer_text=option.text,
            correct=True,
            hint_level=self.current_hint_level,
            attempt_number=self.current_question_attempts
        )
        
        self.tracker.record_event(event)
        self.current_session.add_event(event)
        
        # Record memory association
        for link in self.current_scene.memory_chain:
            self.current_session.add_association(f"{link.entity_type}:{link.entity_id}")
        
        response = {
            "result": "correct",
            "message": f"Yes! You remembered {option.text}!",
            "animation_cue": self.current_scene.animation_cue or "celebrate",
            "attempt_count": self.current_question_attempts,
            "hint_used": self.current_hint_level > 0,
            "next_scene_id": next_scene_id
        }
        
        return (response, next_scene_id)
    
    def _handle_incorrect_recall(self, option) -> Tuple[Dict, Optional[str]]:
        """Handle incorrect recall answer with progressive cueing."""
        if self.current_hint_level == 0:
            # First wrong answer: show memory cue
            cue, memory = self.generator.get_memory_clues_for_person(
                self.current_scene.question.target_id
            )
            
            self.current_hint_level = 1
            
            response = {
                "result": "incorrect_with_cue",
                "message": "That's okay. Let's remember together.",
                "animation_cue": "gentle_encourage",
                "hint_level": self.current_hint_level,
                "memory_cue": {
                    "text": cue.text,
                    "image": str(self.repo.resolve_image_path(cue.image)) if cue.image else None
                },
                "allow_retry": True
            }
            
            return (response, None)  # None = stay in scene, retry
        
        elif self.current_hint_level == 1:
            # Second wrong answer: show stronger hint
            correct_option = None
            for opt in self.current_scene.question.options:
                if opt.correct:
                    correct_option = opt
                    break
            
            self.current_hint_level = 2
            
            response = {
                "result": "incorrect_with_strong_hint",
                "message": "Let me give you another hint...",
                "animation_cue": "point_to_memory",
                "hint_level": self.current_hint_level,
                "memory_cue": {
                    "text": f"Her name starts with {correct_option.text[0].upper()}...",
                    "image": None
                },
                "allow_retry": True
            }
            
            return (response, None)  # Stay in scene, retry
        
        else:
            # Third wrong answer: reveal answer
            correct_option = None
            for opt in self.current_scene.question.options:
                if opt.correct:
                    correct_option = opt
                    break
            
            # Record as failed attempt
            event = GameEvent(
                target_type=self._get_target_type(),
                target_id=self.current_scene.question.target_id,
                target_name=correct_option.text,
                answer_id=option.id,
                answer_text=option.text,
                correct=False,
                hint_level=self.current_hint_level,
                attempt_number=self.current_question_attempts
            )
            
            self.tracker.record_event(event)
            self.current_session.add_event(event)
            
            # Find next scene (failure path)
            next_scene_id = None
            for scene_opt in self.current_scene.options:
                if not scene_opt.is_correct:
                    next_scene_id = scene_opt.next_scene_id
                    break
            
            response = {
                "result": "revealed_answer",
                "message": f"Her name is {correct_option.text}. Let's say it together.",
                "animation_cue": "gentle_encourage",
                "revealed_answer": correct_option.text,
                "allow_retry": False,
                "next_scene_id": next_scene_id
            }
            
            return (response, next_scene_id)
    
    def _get_target_type(self) -> str:
        """Determine the recall target type from current question."""
        question = self.current_scene.question
        if question.target_type == "person":
            return "person_recall"
        elif question.target_type == "food":
            return "food_recall"
        elif question.target_type == "place":
            return "place_recall"
        else:
            return f"{question.target_type}_recall"
    
    def end_story(self) -> Dict:
        """End the story session and return summary."""
        if not self.current_session:
            raise ValueError("No active session")
        
        summary = self.tracker.end_session()
        
        return {
            "message": "Well done! You spent time with your family memories.",
            "story_complete": True,
            "scenes_visited": len(self.current_session.visited_scenes),
            "associations_made": self.current_session.memory_associations_made,
            "events_count": len(self.current_session.game_events),
            "summary": summary,
            "performance": self.tracker.get_patient_profile()
        }
