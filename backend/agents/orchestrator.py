"""
AI Orchestrator - Coordinate all agents to generate game blueprints.

Main entry point: async create_blueprint(patient_id, goal_text)
Flow:
  1. Goal Agent: Parse goal
  2. Memory Agent: Retrieve memories
  3. Story Agent: Generate narrative
  4. Game Agent: Create blueprint
  5. Blueprint Validator: Validate
  6. Return blueprint
"""

import asyncio
from typing import Dict, Optional, Tuple
from backend.agents.goal_agent import GoalAgent
from backend.agents.memory_agent import MemoryAgent
from backend.agents.story_agent import StoryAgent
from backend.agents.game_agent import GameAgent
from backend.models import GameBlueprint


class AIOrchestrator:
    """
    Orchestrates AI agent pipeline to generate game blueprints.
    
    Manages:
    - Agent initialization
    - Data flow between agents
    - Error handling
    - Blueprint validation
    - Caching
    """
    
    def __init__(self):
        self.goal_agent = GoalAgent()
        self.memory_agent = MemoryAgent()
        self.story_agent = StoryAgent()
        self.game_agent = GameAgent()
        
        # Cache for faster regeneration
        self._goal_cache = {}
        self._story_cache = {}
        self._blueprint_cache = {}
    
    async def create_blueprint(self, patient_id: str, goal_text: str, 
                              use_cache: bool = True) -> Tuple[GameBlueprint, Dict]:
        """
        Generate a game blueprint from patient ID and goal text.
        
        Args:
            patient_id: e.g., "Patient_001_Lakshmi"
            goal_text: e.g., "Help Lakshmi remember her daughter Anu"
            use_cache: Whether to use cached results if available
        
        Returns:
            (blueprint, metadata) where metadata contains:
            {
                "status": "success" | "error",
                "steps": {
                    "goal_parsing": {...},
                    "memory_retrieval": {...},
                    "story_generation": {...},
                    "blueprint_generation": {...},
                    "validation": {...}
                },
                "total_scenes": int,
                "generation_time_ms": float,
                "errors": [...]
            }
        """
        
        import time
        start_time = time.time()
        
        metadata = {
            "status": "in_progress",
            "steps": {},
            "errors": []
        }
        
        try:
            # ===== STEP 1: Goal Agent - Parse natural language =====
            step1_start = time.time()
            
            cache_key = f"goal_{patient_id}_{goal_text}"
            if use_cache and cache_key in self._goal_cache:
                goal = self._goal_cache[cache_key]
                metadata["steps"]["goal_parsing"] = {
                    "status": "success",
                    "cached": True,
                    "time_ms": time.time() - step1_start,
                    "target": goal.get("target_id"),
                    "objective": goal.get("objective")
                }
            else:
                goal = await self._async_run(
                    self.goal_agent.parse_goal,
                    goal_text
                )
                
                if not self.goal_agent.validate_goal(goal):
                    raise ValueError("Goal validation failed")
                
                self._goal_cache[cache_key] = goal
                metadata["steps"]["goal_parsing"] = {
                    "status": "success",
                    "cached": False,
                    "time_ms": time.time() - step1_start,
                    "target": goal.get("target_id"),
                    "objective": goal.get("objective"),
                    "confidence": goal.get("confidence")
                }
            
            # ===== STEP 2: Memory Agent - Retrieve memories =====
            step2_start = time.time()
            
            memories = await self._async_run(
                self.memory_agent.get_memories,
                patient_id,
                goal
            )
            
            if "error" in memories:
                raise ValueError(f"Memory retrieval failed: {memories['error']}")
            
            metadata["steps"]["memory_retrieval"] = {
                "status": "success",
                "time_ms": time.time() - step2_start,
                "patient_name": memories.get("patient_name"),
                "entities_found": len(memories.get("all_entities", {})),
                "relevant_memories": len(memories.get("composite_memories", []))
            }
            
            # ===== STEP 3: Story Agent - Generate narrative =====
            step3_start = time.time()
            
            story = await self._async_run(
                self.story_agent.generate_story,
                patient_id,
                memories.get("patient_name", "patient"),
                goal,
                memories
            )
            
            metadata["steps"]["story_generation"] = {
                "status": "success",
                "time_ms": time.time() - step3_start,
                "story_id": story.id,
                "story_title": story.title,
                "scenes": len(story.scenes),
                "memory_chain": story.memory_chain_goal
            }
            
            # ===== STEP 4: Game Agent - Convert to blueprint =====
            step4_start = time.time()
            
            blueprint = await self._async_run(
                self.game_agent.convert_story_to_blueprint,
                story
            )
            
            metadata["steps"]["blueprint_generation"] = {
                "status": "success",
                "time_ms": time.time() - step4_start,
                "blueprint_id": blueprint.blueprint_id,
                "scenes": len(blueprint.scenes),
                "semantic_actions": self._count_unique_actions(blueprint)
            }
            
            # ===== STEP 5: Validation =====
            step5_start = time.time()
            
            validation_result = self._validate_blueprint(blueprint)
            
            metadata["steps"]["validation"] = {
                "status": "success" if validation_result["valid"] else "warning",
                "time_ms": time.time() - step5_start,
                "valid": validation_result["valid"],
                "warnings": validation_result["warnings"],
                "checks_passed": validation_result["checks_passed"]
            }
            
            blueprint.validated = validation_result["valid"]
            blueprint.validation_errors = validation_result["warnings"]
            
            # ===== CACHE RESULT =====
            self._blueprint_cache[f"bp_{patient_id}_{goal_text}"] = blueprint
            
            # ===== FINAL STATUS =====
            metadata["status"] = "success"
            metadata["total_scenes"] = len(blueprint.scenes)
            metadata["generation_time_ms"] = (time.time() - start_time) * 1000
            
            return blueprint, metadata
        
        except Exception as e:
            metadata["status"] = "error"
            metadata["errors"].append(str(e))
            metadata["generation_time_ms"] = (time.time() - start_time) * 1000
            
            # Log error but don't crash
            print(f"Blueprint generation error: {str(e)}")
            
            # Return None with error metadata
            return None, metadata
    
    async def _async_run(self, func, *args, **kwargs):
        """Run synchronous function as async."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    def _count_unique_actions(self, blueprint: GameBlueprint) -> int:
        """Count unique semantic action IDs in blueprint."""
        actions = set()
        for scene in blueprint.scenes:
            for action_id in scene.action_map.values():
                actions.add(action_id)
        return len(actions)
    
    def _validate_blueprint(self, blueprint: GameBlueprint) -> Dict:
        """
        Validate blueprint structure and content.
        
        Returns:
        {
            "valid": bool,
            "checks_passed": int,
            "checks_total": int,
            "warnings": [...]
        }
        """
        
        warnings = []
        checks_passed = 0
        checks_total = 0
        
        # Check 1: Has scenes
        checks_total += 1
        if blueprint.scenes and len(blueprint.scenes) > 0:
            checks_passed += 1
        else:
            warnings.append("Blueprint has no scenes")
        
        # Check 2: Scenes have semantic actions
        checks_total += 1
        has_actions = all(
            scene.action_map and len(scene.action_map) > 0
            for scene in blueprint.scenes
        )
        if has_actions:
            checks_passed += 1
        else:
            warnings.append("Some scenes missing semantic actions")
        
        # Check 3: Questions have options
        checks_total += 1
        question_scenes = [s for s in blueprint.scenes if "question" in s.scene_type]
        if all(s.options and len(s.options) > 1 for s in question_scenes):
            checks_passed += 1
        else:
            warnings.append("Some question scenes have insufficient options")
        
        # Check 4: Memory chain coherence
        checks_total += 1
        if blueprint.memory_chain_goal and len(blueprint.memory_chain_goal) > 0:
            checks_passed += 1
        else:
            warnings.append("Memory chain goal not defined")
        
        # Check 5: Cognitive target specified
        checks_total += 1
        if blueprint.cognitive_target:
            checks_passed += 1
        else:
            warnings.append("Cognitive target not specified")
        
        return {
            "valid": checks_passed >= (checks_total - 1),  # Allow 1 warning
            "checks_passed": checks_passed,
            "checks_total": checks_total,
            "warnings": warnings
        }
    
    def get_cached_blueprint(self, patient_id: str, goal_text: str) -> Optional[GameBlueprint]:
        """Retrieve cached blueprint if exists."""
        cache_key = f"bp_{patient_id}_{goal_text}"
        return self._blueprint_cache.get(cache_key)
    
    def clear_cache(self):
        """Clear all caches."""
        self._goal_cache.clear()
        self._story_cache.clear()
        self._blueprint_cache.clear()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_orchestrator():
        orchestrator = AIOrchestrator()
        
        # Test
        patient_id = "Patient_001_Lakshmi"
        goal_text = "Help Lakshmi remember her daughter Anu"
        
        print(f"Generating blueprint for: {goal_text}")
        print()
        
        blueprint, metadata = await orchestrator.create_blueprint(patient_id, goal_text)
        
        if blueprint:
            print(f"✓ Blueprint Generated: {blueprint.story_title}")
            print(f"  Blueprint ID: {blueprint.blueprint_id}")
            print(f"  Scenes: {len(blueprint.scenes)}")
            print(f"  Validated: {blueprint.validated}")
            print()
            print("Pipeline Steps:")
            for step_name, step_data in metadata["steps"].items():
                status = "✓" if step_data.get("status") == "success" else "✗"
                time_ms = step_data.get("time_ms", 0)
                print(f"  {status} {step_name}: {time_ms:.1f}ms")
            print()
            print(f"Total generation time: {metadata['generation_time_ms']:.1f}ms")
        else:
            print("✗ Blueprint generation failed")
            for error in metadata.get("errors", []):
                print(f"  Error: {error}")
    
    # Run async test
    asyncio.run(test_orchestrator())
