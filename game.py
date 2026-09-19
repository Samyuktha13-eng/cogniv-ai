"""
Game Logic - handles game flow, answer checking, and memory cue presentation.
"""

from typing import Optional, Dict, Tuple
from models import GameQuestion, GameEvent, MemoryCue, Memory
from game_generator import GameGenerator
from memory_repository import MemoryRepository
from outcome_tracker import OutcomeTracker


class GameFlow:
    """Manages the complete game flow including cues and retry logic."""
    
    def __init__(self, generator: GameGenerator, tracker: OutcomeTracker):
        """
        Initialize game flow.
        
        Args:
            generator: GameGenerator instance
            tracker: OutcomeTracker instance
        """
        self.generator = generator
        self.tracker = tracker
        self.repo = generator.repo
        
        self.current_question: Optional[GameQuestion] = None
        self.current_memory_cue: Optional[MemoryCue] = None
        self.attempt_count = 0
    
    def start_game_session(self, session_id: str, game_name: str = "Family Memory Game"):
        """Start a new game session."""
        self.tracker.create_session(session_id, game_name)
    
    def present_question(self, question: GameQuestion) -> Dict:
        """
        Present a question to the patient.
        
        Returns:
            Dict with question data for display
        """
        self.current_question = question
        self.attempt_count = 0
        self.current_memory_cue = None
        
        return {
            "question_text": question.question_text,
            "image": str(self.repo.resolve_image_path(question.image)),
            "options": [
                {"id": opt.id, "text": opt.text}
                for opt in question.options
            ]
        }
    
    def handle_answer(self, answer_option_id: str) -> Tuple[Dict, bool]:
        """
        Handle patient's answer to a question.
        
        Returns:
            Tuple of (response_dict, should_continue)
        """
        if not self.current_question:
            raise ValueError("No question presented yet")
        
        self.attempt_count += 1
        
        # Find the selected option
        selected_option = None
        for opt in self.current_question.options:
            if opt.id == answer_option_id:
                selected_option = opt
                break
        
        if not selected_option:
            raise ValueError(f"Invalid option: {answer_option_id}")
        
        # Check if correct
        is_correct = selected_option.correct
        
        if is_correct:
            return self._handle_correct_answer(selected_option)
        else:
            return self._handle_wrong_answer(selected_option)
    
    def _handle_correct_answer(self, option) -> Tuple[Dict, bool]:
        """Handle correct answer with reward."""
        # Record the event
        event = GameEvent(
            target_type="person_recall" if self.current_question.target_type == "person" else "food_recall",
            target_id=self.current_question.target_id,
            target_name=option.text,
            answer_id=option.id,
            answer_text=option.text,
            correct=True,
            hint_level=0 if self.attempt_count == 1 else 1,  # Independent if first try
            attempt_number=self.attempt_count
        )
        
        self.tracker.record_event(event)
        
        # Get the target entity for context
        target_entity = self.repo.get_entity_by_id(self.current_question.target_id)
        
        response = {
            "result": "correct",
            "message": f"Yes! You remembered {option.text}!",
            "reward_animation": "celebrate",
            "attempt_count": self.attempt_count,
            "hint_used": self.attempt_count > 1,
            "target_name": target_entity.name if target_entity else option.text
        }
        
        return (response, False)  # False = don't retry
    
    def _handle_wrong_answer(self, option) -> Tuple[Dict, bool]:
        """Handle wrong answer with memory cue."""
        # On first wrong attempt, offer a memory cue
        if self.attempt_count == 1:
            # Get memory cue for the correct answer
            cue, memory = self.generator.get_memory_clues_for_person(
                self.current_question.target_id
            )
            
            self.current_memory_cue = cue
            
            # Construct response with memory cue
            response = {
                "result": "wrong_with_cue",
                "message": "That's okay. Let's remember together.",
                "encouragement_animation": "gentle_encourage",
                "memory_cue": {
                    "text": cue.text,
                    "image": str(self.repo.resolve_image_path(cue.image)) if cue.image else None,
                },
                "attempt_count": self.attempt_count,
                "allow_retry": True
            }
            
            return (response, True)  # True = allow retry
        
        else:
            # After cue shown, record as failed if wrong again
            event = GameEvent(
                target_type="person_recall" if self.current_question.target_type == "person" else "food_recall",
                target_id=self.current_question.target_id,
                target_name=self.current_question.options[0].text,  # Correct answer
                answer_id=option.id,
                answer_text=option.text,
                correct=False,
                hint_level=1,
                attempt_number=self.attempt_count
            )
            
            self.tracker.record_event(event)
            
            # Get correct answer for display
            correct_option = None
            for opt in self.current_question.options:
                if opt.correct:
                    correct_option = opt
                    break
            
            response = {
                "result": "incorrect",
                "message": f"The answer is {correct_option.text}. Let's remember together.",
                "show_correct": True,
                "correct_answer": correct_option.text,
                "attempt_count": self.attempt_count,
                "allow_retry": False
            }
            
            return (response, False)  # False = don't retry
    
    def end_game(self) -> Dict:
        """End the game session and return summary."""
        summary = self.tracker.end_session()
        
        return {
            "message": "Well done! You spent time with your family memories.",
            "summary": summary,
            "performance": self.tracker.get_patient_profile()
        }


class GameScenario:
    """High-level game scenario coordinator."""
    
    def __init__(self, repo: MemoryRepository, tracker: OutcomeTracker):
        """
        Initialize game scenario.
        
        Args:
            repo: MemoryRepository instance
            tracker: OutcomeTracker instance
        """
        self.repo = repo
        self.tracker = tracker
        self.generator = GameGenerator(repo)
        self.flow = GameFlow(self.generator, tracker)
    
    def start_daughter_memory_game(self) -> Dict:
        """
        Start the "Remember My Daughter" game scenario.
        
        Returns:
            First game question
        """
        session_id = "session_001"
        self.flow.start_game_session(session_id, "Remember My Daughter")
        
        # Generate the first question: recognize the daughter
        question = self.generator.generate_person_recognition_game("daughter")
        
        return self.flow.present_question(question)
