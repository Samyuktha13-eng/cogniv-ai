"""
Game Routes - FastAPI endpoints for game creation and execution.

Flow:
1. POST /game/create → AI Orchestrator creates blueprint → returns first scene
2. POST /game/action → Patient presses button → Action Router returns animation sequence
3. POST /game/outcome → Record outcome → update cognitive profile
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import json
from datetime import datetime

from backend.models import (
    GameCreateRequest,
    GameCreateResponse,
    ActionResponse,
    OutcomeRequest,
    OutcomeResponse,
    CognitiveProfileResponse,
    GameBlueprint,
    SceneBlueprint,
)
from backend.agents import AIOrchestrator


router = APIRouter(prefix="/game", tags=["game"])

# Global storage (in production: use database)
_game_blueprints: dict = {}
_game_sessions: dict = {}
_orchestrator = AIOrchestrator()  # Initialize orchestrator


# ============================================================================
# GAME CREATION ENDPOINT
# ============================================================================

@router.post("/create", response_model=GameCreateResponse)
async def create_game(request: GameCreateRequest):
    """
    Create a new game for a patient.
    
    Flow:
    1. Goal Agent: Parse natural language goal
    2. Memory Agent: Retrieve patient memories
    3. Story Agent: Generate narrative
    4. Game Agent: Convert to gameplay
    5. Blueprint Generator: Create JSON blueprint
    6. Validator: Check all actions exist
    7. Return: First scene (if valid)
    
    Example request:
    {
        "patient_id": "Patient_001_Lakshmi",
        "goal": "Help Lakshmi remember her daughter Anu"
    }
    
    Example response:
    {
        "blueprint_id": "bp_visit_from_anu_001",
        "game_id": "visit_from_anu_001",
        "story_title": "A Visit From Anu",
        "patient_id": "Patient_001_Lakshmi",
        "validated": true,
        "validation_errors": [],
        "first_scene": { ... SceneBlueprint ... }
    }
    """
    
    try:
        # Call AI Orchestrator to generate blueprint
        blueprint, metadata = await _orchestrator.create_blueprint(
            patient_id=request.patient_id,
            goal_text=request.goal
        )
        
        if not blueprint or metadata.get("status") != "success":
            errors = metadata.get("errors", ["Unknown error during blueprint generation"])
            raise HTTPException(
                status_code=500,
                detail=f"Blueprint generation failed: {errors[0] if errors else 'Unknown error'}"
            )
        
        # Store blueprint for later reference
        _game_blueprints[blueprint.blueprint_id] = blueprint
        
        first_scene = blueprint.scenes[0] if blueprint.scenes else None
        
        return GameCreateResponse(
            blueprint_id=blueprint.blueprint_id,
            game_id=blueprint.game_id,
            story_title=blueprint.story_title,
            patient_id=blueprint.patient_id,
            validated=blueprint.validated,
            validation_errors=blueprint.validation_errors,
            first_scene=first_scene
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SCENE RETRIEVAL ENDPOINT
# ============================================================================

@router.get("/scene/{game_id}/{scene_id}")
async def get_scene(game_id: str, scene_id: str):
    """
    Get a specific scene from a game blueprint.
    
    Example:
    GET /game/scene/visit_from_anu_001/scene_2_kitchen
    
    Response:
    {
        "scene_id": "scene_2_kitchen",
        "scene_type": "recall_question",
        "narration": "Someone special used to cook with you...",
        "question_text": "Do you remember who?",
        "options": [
            {"id": "person_anu", "text": "Anu", "action": "daughter_recognition_success"},
            {"id": "person_rahul", "text": "Rahul", "action": "wrong_answer_encouragement"}
        ],
        "action_map": {...}
    }
    """
    
    try:
        # Find blueprint by game_id
        blueprint = None
        for bp in _game_blueprints.values():
            if bp.game_id == game_id:
                blueprint = bp
                break
        
        if not blueprint:
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
        
        scene = blueprint.get_scene(scene_id)
        if not scene:
            raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
        
        return scene
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ACTION EXECUTION ENDPOINT
# ============================================================================

@router.post("/action", response_model=ActionResponse)
async def execute_action(
    game_id: str,
    scene_id: str,
    option_id: str
):
    """
    Execute a patient action (button press).
    
    This is called when patient taps a button in Unity.
    Should return immediately with animation sequence.
    
    Flow:
    1. Look up scene in blueprint
    2. Find action_map[option_id] → get semantic action ID
    3. Action Router: Map action ID → ActionSequence
    4. Return animation frames + timing
    
    Example:
    POST /game/action?game_id=visit_from_anu_001&scene_id=scene_2_kitchen&option_id=person_anu
    
    Response:
    {
        "option_id": "person_anu",
        "action_id": "daughter_recognition_success",
        "action_sequence": {
            "id": "daughter_recognition_success",
            "description": "...",
            "actions": [
                {"id": "daughter_appear", "duration": 1.0},
                {"id": "daughter_walk_to_mother", "duration": 2.0},
                ...
            ],
            "outcome_narration": "Yes! That's Anu..."
        },
        "is_correct": true,
        "hint_level": 0,
        "duration": 8.5
    }
    """
    
    try:
        # Find blueprint
        blueprint = None
        for bp in _game_blueprints.values():
            if bp.game_id == game_id:
                blueprint = bp
                break
        
        if not blueprint:
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
        
        # Get scene
        scene = blueprint.get_scene(scene_id)
        if not scene:
            raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
        
        # Get action ID from action_map
        action_id = scene.action_map.get(option_id)
        if not action_id:
            raise HTTPException(status_code=400, detail=f"Option {option_id} not in action_map")
        
        # TODO: Call Action Router to get ActionSequence from SemanticActionLibrary
        # action_seq = action_router.get_action_sequence(action_id)
        
        # For now, return mock
        from backend.blueprint.semantic_actions import SemanticActionLibrary
        library = SemanticActionLibrary()
        action_seq = library.get_action_sequence(action_id)
        
        if not action_seq:
            raise HTTPException(status_code=404, detail=f"Action {action_id} not found in library")
        
        # Determine if answer is correct (for recall questions)
        is_correct = None
        hint_level = 0
        
        if scene.options:
            for opt in scene.options:
                if opt.get("id") == option_id and opt.get("correct"):
                    is_correct = True
                    hint_level = 0
                    break
            if is_correct is None and opt.get("id") == option_id:
                is_correct = False
                hint_level = 1
        
        # Calculate total duration
        total_duration = sum(a.duration for a in action_seq.actions)
        
        return ActionResponse(
            option_id=option_id,
            action_id=action_id,
            action_sequence=action_seq,
            is_correct=is_correct,
            hint_level=hint_level,
            duration=total_duration
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BLUEPRINT ENDPOINT - Get full blueprint JSON
# ============================================================================

@router.get("/blueprint/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """
    Get complete game blueprint.
    
    Used by Unity to load entire game structure.
    This blueprint is what the AI generated and the validator approved.
    
    Example:
    GET /game/blueprint/bp_visit_from_anu_001
    
    Response:
    {
        "blueprint_id": "bp_visit_from_anu_001",
        "game_id": "visit_from_anu_001",
        "story_title": "A Visit From Anu",
        "patient_id": "Patient_001_Lakshmi",
        "cognitive_target": "person_recall",
        "memory_chain_goal": ["home", "kitchen", "chapathi", "person_anu", "family"],
        "scenes": [...8 scenes...],
        "validated": true,
        "validation_errors": []
    }
    """
    
    if blueprint_id not in _game_blueprints:
        raise HTTPException(status_code=404, detail=f"Blueprint {blueprint_id} not found")
    
    blueprint = _game_blueprints[blueprint_id]
    return blueprint


# ============================================================================
# DEBUG ENDPOINTS
# ============================================================================

@router.get("/blueprints")
async def list_blueprints():
    """List all loaded blueprints (debug)."""
    return {
        "count": len(_game_blueprints),
        "blueprints": [
            {
                "id": bp.blueprint_id,
                "title": bp.story_title,
                "patient": bp.patient_id,
                "scenes": len(bp.scenes),
                "validated": bp.validated
            }
            for bp in _game_blueprints.values()
        ]
    }


@router.get("/actions")
async def list_actions():
    """List all available semantic actions (debug)."""
    from backend.blueprint.semantic_actions import SemanticActionLibrary
    library = SemanticActionLibrary()
    return {
        "count": len(library.list_all_actions()),
        "actions": [
            {
                "id": action_id,
                "description": library.get_action_description(action_id)
            }
            for action_id in library.list_all_actions()
        ]
    }
