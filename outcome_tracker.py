"""
Outcome Tracker - records and analyzes game session results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from models import GameSession, GameEvent


class OutcomeTracker:
    """Tracks patient performance across game sessions."""
    
    def __init__(self, patient_id: str, patient_folder: Path):
        """
        Initialize the outcome tracker.
        
        Args:
            patient_id: The patient's ID
            patient_folder: Path to patient folder for storing outcomes
        """
        self.patient_id = patient_id
        self.patient_folder = Path(patient_folder)
        self.outcomes_folder = self.patient_folder / "outcomes"
        self.outcomes_folder.mkdir(exist_ok=True)
        
        self.current_session: Optional[GameSession] = None
    
    def create_session(self, session_id: str, game_name: str) -> GameSession:
        """Create a new game session."""
        self.current_session = GameSession(
            patient_id=self.patient_id,
            session_id=session_id,
            game_name=game_name,
            events=[]
        )
        return self.current_session
    
    def record_event(self, event: GameEvent):
        """Record a single game event in the current session."""
        if not self.current_session:
            raise ValueError("No active session. Call create_session() first.")
        self.current_session.add_event(event)
    
    def end_session(self) -> Dict:
        """End the current session and save results."""
        if not self.current_session:
            raise ValueError("No active session.")
        
        summary = self.current_session.get_summary()
        
        # Save session to file
        session_file = self.outcomes_folder / f"session_{self.current_session.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump({
                "patient_id": self.current_session.patient_id,
                "session_id": self.current_session.session_id,
                "game_name": self.current_session.game_name,
                "timestamp": datetime.now().isoformat(),
                "events": [e.model_dump() for e in self.current_session.events],
                "summary": summary
            }, f, indent=2)
        
        self.current_session = None
        return summary
    
    def get_patient_profile(self) -> Dict:
        """
        Analyze all sessions to build patient's cognitive profile.
        
        Returns:
            Dict with performance metrics by category
        """
        profile = {
            "person_recall": {"independent": 0, "cue_assisted": 0, "failed": 0},
            "food_recall": {"independent": 0, "cue_assisted": 0, "failed": 0},
            "place_recall": {"independent": 0, "cue_assisted": 0, "failed": 0},
            "object_recall": {"independent": 0, "cue_assisted": 0, "failed": 0},
            "total_sessions": 0
        }
        
        # Read all session files
        if not self.outcomes_folder.exists():
            return profile
        
        for session_file in self.outcomes_folder.glob("session_*.json"):
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            profile["total_sessions"] += 1
            
            for event in session_data["events"]:
                target_type = event["target_type"]
                
                # Map target_type to category
                if "person" in target_type:
                    category = "person_recall"
                elif "food" in target_type:
                    category = "food_recall"
                elif "place" in target_type:
                    category = "place_recall"
                elif "object" in target_type:
                    category = "object_recall"
                else:
                    continue
                
                if event["correct"]:
                    if event["hint_level"] == 0:
                        profile[category]["independent"] += 1
                    else:
                        profile[category]["cue_assisted"] += 1
                else:
                    profile[category]["failed"] += 1
        
        return profile
    
    def get_performance_summary(self) -> str:
        """Get a readable summary of patient performance."""
        profile = self.get_patient_profile()
        
        lines = [
            "\n" + "="*50,
            "PATIENT COGNITIVE PROFILE",
            "="*50,
            f"\nTotal Sessions: {profile['total_sessions']}\n"
        ]
        
        for category in ["person_recall", "food_recall", "place_recall", "object_recall"]:
            data = profile[category]
            total = data["independent"] + data["cue_assisted"] + data["failed"]
            
            if total == 0:
                continue
            
            category_name = category.replace("_", " ").title()
            success_rate = ((data["independent"] + data["cue_assisted"]) / total) * 100
            independent_rate = (data["independent"] / total) * 100 if total > 0 else 0
            
            lines.append(f"\n{category_name}:")
            lines.append(f"  Independent Recall:   {data['independent']}")
            lines.append(f"  Cue-Assisted Recall:  {data['cue_assisted']}")
            lines.append(f"  Failed:               {data['failed']}")
            lines.append(f"  Success Rate:         {success_rate:.1f}%")
            lines.append(f"  Independent Rate:     {independent_rate:.1f}%")
        
        lines.append("\n" + "="*50)
        return "\n".join(lines)
