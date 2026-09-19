"""
Blueprint Demo - Shows the complete flow from Story → Blueprint → Execution
This demonstrates:
1. Story object (narrative)
2. GameBlueprint (AI output, structured JSON)
3. Validation (check safety/correctness)
4. Execution (action routing and animation sequences)
"""

import json
from memory_repository import MemoryRepository
from story_builder import StoryBuilder
from blueprint_generator import BlueprintGenerator, BlueprintValidator
from action_router import ActionRouter, ExecutionEngine, ActionSequencePlayer
from asset_library import AssetLibrary, AssetManifest
from outcome_tracker import OutcomeTracker


def main():
    print("\n" + "="*80)
    print("[BLUEPRINT DEMO] Story -> Blueprint -> Execution")
    print("="*80)
    
    # ========== STEP 1: LOAD PATIENT DATA ==========
    print("\n[1/6] Loading patient data...")
    patient_folder = "Patient_001_Lakshmi"
    repo = MemoryRepository(patient_folder)
    profile = repo.load()
    print(f"  Loaded: {profile.patient_name}")
    
    # ========== STEP 2: BUILD STORY ==========
    print("\n[2/6] Building story...")
    builder = StoryBuilder(repo)
    story = builder.build_visit_from_anu_story()
    print(f"  Story: {story.title}")
    print(f"  Scenes: {len(story.scenes)}")
    print(f"  Target: {story.cognitive_target}")
    print(f"  Chain: {' -> '.join(story.memory_chain_goal)}")
    
    # ========== STEP 3: GENERATE BLUEPRINT ==========
    print("\n[3/6] Generating blueprint...")
    asset_library = AssetLibrary()
    generator = BlueprintGenerator(repo, asset_library)
    blueprint = generator.generate_blueprint(story)
    print(f"  Blueprint: {blueprint.blueprint_id}")
    print(f"  Patient: {blueprint.patient_id}")
    print(f"  Scenes in blueprint: {len(blueprint.scenes)}")
    
    # Show first few scenes
    print("\n  Scene breakdown:")
    for i, scene_bp in enumerate(blueprint.scenes[:4]):
        print(f"    [{i}] {scene_bp.scene_id} ({scene_bp.scene_type})")
        if scene_bp.options:
            opts = ', '.join([o['text'][:20] for o in scene_bp.options])
            print(f"        Options: {opts}")
    
    # ========== STEP 4: VALIDATE BLUEPRINT ==========
    print("\n[4/6] Validating blueprint...")
    validator = BlueprintValidator(asset_library)
    is_valid = validator.validate(blueprint)
    
    if is_valid:
        print(f"  VALID - All scenes and actions are available")
    else:
        print(f"  ERRORS: {len(blueprint.validation_errors)}")
        for i, error in enumerate(blueprint.validation_errors[:5]):
            print(f"    - {error}")
    
    # ========== STEP 5: SETUP EXECUTION ENGINE ==========
    print("\n[5/6] Setting up execution engine...")
    router = ActionRouter(asset_library)
    router.load_blueprint(blueprint)
    engine = ExecutionEngine(router)
    player = ActionSequencePlayer()
    print("  Engine ready")
    
    # ========== STEP 6: SIMULATE GAMEPLAY ==========
    print("\n[6/6] Simulating gameplay...")
    print("\n" + "-"*80)
    
    # Demonstrate with available scenes
    if blueprint.scenes:
        scene_1 = blueprint.scenes[0]
        print(f"\n[SCENE 0] {scene_1.scene_id}")
        print(f"   Type: {scene_1.scene_type}")
        print(f"   Narration: {scene_1.narration}")
        if scene_1.options:
            print(f"   Options: {[o['text'] for o in scene_1.options]}")
            opt_id = scene_1.options[0]['id']
            opt_text = scene_1.options[0]['text']
            
            print(f"\n[PATIENT] Chooses: {opt_text}")
            scene_data_1 = engine.execute_scene(scene_1)
            execution_1, _ = engine.execute_action(opt_id)
            
            print(f"   Action: {execution_1['action_sequence']['id']}")
            print(f"   Result: {'✓ Correct' if execution_1['is_correct'] else 'Neutral'}")
    
    # ========== SCENE 2: KITCHEN WITH RECALL QUESTION ==========
    if len(blueprint.scenes) > 1:
        print(f"\n" + "-"*80)
        scene_2 = blueprint.scenes[1]
        print(f"\n[SCENE 1] {scene_2.scene_id}")
        print(f"   Type: {scene_2.scene_type}")
        if scene_2.question_text:
            print(f"   Question: {scene_2.question_text}")
        if scene_2.options:
            print(f"   Options: {[o['text'] for o in scene_2.options]}")
            
            if len(scene_2.options) > 0:
                opt_id = scene_2.options[0]['id']
                opt_text = scene_2.options[0]['text']
                print(f"\n[PATIENT] Chooses: {opt_text}")
                scene_data_2 = engine.execute_scene(scene_2)
                execution_2a, _ = engine.execute_action(opt_id)
                
                print(f"   Result: {'Correct' if execution_2a['is_correct'] else 'Wrong'}")
                print(f"   Action: {execution_2a['action_sequence']['id']}")
                
                # Show memory cue
                action_seq_cue = asset_library.get_action_sequence("show_memory_cue")
                if action_seq_cue:
                    playback_cue = player.play_sequence(action_seq_cue)
                    print(f"\n   [MEMORY CUE] {playback_cue['final_narration']}")
                
                # Retry with different option
                if len(scene_2.options) > 1:
                    retry_id = scene_2.options[1]['id']
                    retry_text = scene_2.options[1]['text']
                    print(f"\n[PATIENT] Retries: {retry_text}")
                    execution_2b, _ = engine.execute_action(retry_id)
                    print(f"   Result: {'Correct' if execution_2b['is_correct'] else 'Wrong'}")
                    print(f"   Hint level: {execution_2b['hint_level']}")
    if len(blueprint.scenes) > 5:
        print(f"\n" + "-"*80)
        scene_6 = blueprint.scenes[5]
        print(f"\n[SCENE 5] {scene_6.scene_id}")
        print(f"   Type: {scene_6.scene_type}")
        if scene_6.question_text:
            print(f"   Question: {scene_6.question_text}")
        
        if scene_6.options:
            opt_id = scene_6.options[0]['id']
            opt_text = scene_6.options[0]['text']
            print(f"\n[PATIENT] Chooses: {opt_text} (correct on first try)")
            scene_data_6 = engine.execute_scene(scene_6)
            execution_6, _ = engine.execute_action(opt_id)
            is_correct = execution_6.get('is_correct', False) if isinstance(execution_6, dict) else False
            hint_level = execution_6.get('hint_level', -1) if isinstance(execution_6, dict) else -1
            print(f"   Result: {'Correct' if is_correct else 'Wrong'}")
            print(f"   Hint level: {hint_level} (Independent recall)")
    
    # ========== FINAL SCENE: REWARD ==========
    if len(blueprint.scenes) > 0:
        print(f"\n" + "-"*80)
        scene_final = blueprint.scenes[-1]
        print(f"\n[FINAL SCENE] {scene_final.scene_id}")
        print(f"   Type: {scene_final.scene_type}")
        
        action_seq_reward = asset_library.get_action_sequence("final_reward")
        if action_seq_reward:
            playback_reward = player.play_sequence(action_seq_reward)
            print(f"\n   [REWARD] {playback_reward['final_narration']}")
    
    # ========== EXECUTION SUMMARY ==========
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    
    summary = engine.get_execution_summary()
    print(f"\n  Actions executed: {summary['actions_executed']}")
    print(f"  Correct: {summary['correct_count']}")
    print(f"  Wrong: {summary['wrong_count']}")
    
    print(f"\n  Action history:")
    for i, action in enumerate(summary['execution_history'], 1):
        result = "✓" if action['is_correct'] else "✗"
        print(f"    {i}. {result} {action['action_sequence_id']} (hint: {action['hint_level']})")
    
    # ========== BLUEPRINT JSON OUTPUT ==========
    print("\n" + "="*80)
    print("SAMPLE BLUEPRINT JSON (What AI Would Generate)")
    print("="*80 + "\n")
    
    # Serialize blueprint for display
    blueprint_dict = blueprint.model_dump(exclude={'scenes'})
    blueprint_dict['scenes'] = [s.model_dump() for s in blueprint.scenes[:2]]  # First 2 scenes
    
    print(json.dumps(blueprint_dict, indent=2))
    print(f"\n[... and {len(blueprint.scenes)-2} more scenes ...]")
    
    # ========== ACTION SEQUENCE EXAMPLE ==========
    print("\n" + "="*80)
    print("ACTION SEQUENCE EXAMPLE (What Unity Would Execute)")
    print("="*80 + "\n")
    
    correct_answer_seq = asset_library.get_action_sequence("correct_answer_daughter")
    action_seq_dict = {
        "id": correct_answer_seq.id,
        "description": correct_answer_seq.description,
        "animations": [
            {
                "id": a.id,
                "duration": a.duration,
                "narration": a.trigger_narration
            }
            for a in correct_answer_seq.actions
        ],
        "outcome_narration": correct_answer_seq.outcome_narration
    }
    
    print(json.dumps(action_seq_dict, indent=2))
    
    # ========== KEY INSIGHTS ==========
    print("\n" + "="*80)
    print("KEY ARCHITECTURE INSIGHTS")
    print("="*80 + "\n")
    
    print("1. SEPARATION OF CONCERNS")
    print("   Story (narrative) → Blueprint (structured) → Execution (animation)")
    print()
    
    print("2. WHAT THE AI GENERATES")
    print("   - SceneBlueprint objects with actions and questions")
    print("   - References pre-created animation IDs")
    print("   - Does NOT create animations, only the logic")
    print()
    
    print("3. WHAT UNITY RECEIVES")
    print("   - JSON blueprint with scene structure")
    print("   - Action sequences mapped to animations")
    print("   - Playback instructions with timing")
    print()
    
    print("4. WHAT ACTION ROUTER DOES")
    print("   - Maps patient button presses to action sequences")
    print("   - Looks up animations in AssetLibrary")
    print("   - Records outcomes for cognitive profile")
    print()
    
    print("5. VALIDATION LAYER")
    print("   - Ensures all action IDs exist")
    print("   - Checks scene connectivity")
    print("   - Verifies patient safety constraints")
    print()
    
    print("\n[OK] This architecture allows:")
    print("   • AI to generate stories without creating media")
    print("   • Easy updates to animation library")
    print("   • Clear separation between logic and assets")
    print("   • Safe validation before execution")
    print("   • Deterministic, testable game flow")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
