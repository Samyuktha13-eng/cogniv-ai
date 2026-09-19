"""
Outcome Routes - FastAPI endpoints for tracking game results and cognitive profiles.

Flow:
1. POST /outcome → Record single patient action outcome
2. GET /patient/{patient_id}/profile → Get cognitive profile from accumulated results
3. POST /patient/{patient_id}/games → List all games played
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime

from backend.models import (
    OutcomeRequest,
    OutcomeResponse,
    CognitiveProfileResponse,
)

router = APIRouter(prefix="/outcome", tags=["outcomes"])

# Global storage (in production: use database)
_outcomes: Dict[str, list] = {}  # patient_id → list of outcomes
_cognitive_profiles: Dict[str, dict] = {}  # patient_id → profile


# ============================================================================
# OUTCOME RECORDING ENDPOINT
# ============================================================================

@router.post("/record", response_model=OutcomeResponse)
async def record_outcome(request: OutcomeRequest):
    """
    Record a single game outcome.
    
    Called by Unity after patient completes an action.
    This updates the patient's cognitive profile.
    
    Flow:
    1. Store outcome
    2. Update cognitive profile
    3. Analyze memory associations
    4. Return confirmation
    
    Example request:
    {
        "patient_id": "Patient_001_Lakshmi",
        "game_id": "visit_from_anu_001",
        "scene_id": "scene_2_kitchen",
        "option_id": "person_anu",
        "action_id": "daughter_recognition_success",
        "is_correct": true,
        "hint_level": 0,
        "response_time": 3.2,
        "recall_type": "independent"
    }
    
    Example response:
    {
        "outcome_id": "outcome_001_20260901_001",
        "recorded": true,
        "cognitive_profile_updated": true
    }
    """
    
    try:
        outcome_id = f"outcome_{request.patient_id}_{datetime.now().isoformat()}"
        
        # Store outcome
        if request.patient_id not in _outcomes:
            _outcomes[request.patient_id] = []
        
        outcome_data = {
            "outcome_id": outcome_id,
            "timestamp": datetime.now().isoformat(),
            **request.dict()
        }
        
        _outcomes[request.patient_id].append(outcome_data)
        
        # Update cognitive profile
        _update_cognitive_profile(request.patient_id)
        
        return OutcomeResponse(
            outcome_id=outcome_id,
            recorded=True,
            cognitive_profile_updated=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COGNITIVE PROFILE ENDPOINT
# ============================================================================

@router.get("/patient/{patient_id}/profile", response_model=CognitiveProfileResponse)
async def get_cognitive_profile(patient_id: str):
    """
    Get patient's cognitive profile from all accumulated outcomes.
    
    Shows:
    - Independent recalls (no hints)
    - Cue-assisted recalls (with hints)
    - Memory associations made
    - Overall pattern
    
    Example:
    GET /outcome/patient/Patient_001_Lakshmi/profile
    
    Response:
    {
        "patient_id": "Patient_001_Lakshmi",
        "patient_name": "Lakshmi",
        "independent_recalls": {
            "daughter_anu": 3,
            "chapathi": 2
        },
        "cue_assisted_recalls": {
            "son_rahul": 1,
            "temple": 1
        },
        "associations": {
            "Anu→Kitchen": true,
            "Anu→Chapathi": true,
            "Anu→Cooking": true,
            "Anu→Family": true,
            "Rahul→Sons": true
        },
        "summary": {
            "games_played": 3,
            "total_correct": 8,
            "total_attempts": 12,
            "accuracy": 0.667,
            "progress": "improving",
            "recommendation": "Continue with family-related memories"
        }
    }
    """
    
    if patient_id not in _cognitive_profiles:
        return CognitiveProfileResponse(
            patient_id=patient_id,
            patient_name="Unknown",
            independent_recalls={},
            cue_assisted_recalls={},
            associations={},
            summary={}
        )
    
    profile = _cognitive_profiles[patient_id]
    return CognitiveProfileResponse(**profile)


@router.get("/patient/{patient_id}/games")
async def list_patient_games(patient_id: str):
    """
    List all games played by a patient.
    
    Example:
    GET /outcome/patient/Patient_001_Lakshmi/games
    
    Response:
    {
        "patient_id": "Patient_001_Lakshmi",
        "games": [
            {
                "game_id": "visit_from_anu_001",
                "title": "A Visit From Anu",
                "date": "2026-09-01T10:30:00",
                "scenes_completed": 8,
                "correct_answers": 5,
                "wrong_answers": 3
            },
            {
                "game_id": "temple_visit_001",
                "title": "A Visit to the Temple",
                "date": "2026-09-01T14:20:00",
                "scenes_completed": 6,
                "correct_answers": 4,
                "wrong_answers": 2
            }
        ]
    }
    """
    
    if patient_id not in _outcomes:
        return {
            "patient_id": patient_id,
            "games": []
        }
    
    # Group outcomes by game_id
    games_dict = {}
    for outcome in _outcomes[patient_id]:
        game_id = outcome.get("game_id")
        if game_id not in games_dict:
            games_dict[game_id] = {
                "game_id": game_id,
                "date": outcome.get("timestamp"),
                "outcomes": []
            }
        games_dict[game_id]["outcomes"].append(outcome)
    
    # Summarize each game
    games_list = []
    for game_data in games_dict.values():
        outcomes = game_data["outcomes"]
        correct = sum(1 for o in outcomes if o.get("is_correct"))
        wrong = sum(1 for o in outcomes if not o.get("is_correct"))
        
        games_list.append({
            "game_id": game_data["game_id"],
            "date": game_data["date"],
            "outcomes_recorded": len(outcomes),
            "correct_answers": correct,
            "wrong_answers": wrong,
            "accuracy": correct / len(outcomes) if outcomes else 0
        })
    
    return {
        "patient_id": patient_id,
        "games_count": len(games_list),
        "games": games_list
    }


# ============================================================================
# INTERNAL HELPER FUNCTIONS
# ============================================================================

def _update_cognitive_profile(patient_id: str):
    """
    Update patient's cognitive profile based on accumulated outcomes.
    
    Calculates:
    - Independent recalls (hint_level == 0)
    - Cue-assisted recalls (hint_level > 0)
    - Memory associations
    - Overall progress
    """
    
    if patient_id not in _outcomes:
        return
    
    outcomes = _outcomes[patient_id]
    
    # Initialize profile
    profile = {
        "patient_id": patient_id,
        "patient_name": patient_id.split("_")[-1],  # Extract name from ID
        "independent_recalls": {},
        "cue_assisted_recalls": {},
        "associations": {},
        "summary": {}
    }
    
    # Analyze outcomes
    total_correct = 0
    total_attempts = 0
    association_success = {}
    
    for outcome in outcomes:
        action_id = outcome.get("action_id", "")
        is_correct = outcome.get("is_correct", False)
        hint_level = outcome.get("hint_level", 0)
        
        total_attempts += 1
        if is_correct:
            total_correct += 1
        
        # Track independent vs. cued recalls
        target_key = action_id.split("_")[0] if "_" in action_id else action_id
        
        if is_correct and hint_level == 0:
            profile["independent_recalls"][target_key] = \
                profile["independent_recalls"].get(target_key, 0) + 1
        elif is_correct and hint_level > 0:
            profile["cue_assisted_recalls"][target_key] = \
                profile["cue_assisted_recalls"].get(target_key, 0) + 1
        
        # Track associations (e.g., Anu→Kitchen, Anu→Chapathi)
        if is_correct:
            association_success[action_id] = True
    
    # Calculate summary statistics
    accuracy = total_correct / total_attempts if total_attempts > 0 else 0
    
    profile["associations"] = association_success
    profile["summary"] = {
        "games_played": len(set(o.get("game_id") for o in outcomes)),
        "total_correct": total_correct,
        "total_attempts": total_attempts,
        "accuracy": round(accuracy, 2),
        "last_updated": datetime.now().isoformat(),
        "trend": "improving" if len(outcomes) > 3 and \
                 outcomes[-1].get("is_correct") else "stable"
    }
    
    # Store profile
    _cognitive_profiles[patient_id] = profile


@router.get("/debug/outcomes/{patient_id}")
async def debug_outcomes(patient_id: str):
    """Debug endpoint - see all outcomes for a patient."""
    return {
        "patient_id": patient_id,
        "outcomes_count": len(_outcomes.get(patient_id, [])),
        "outcomes": _outcomes.get(patient_id, [])
    }
