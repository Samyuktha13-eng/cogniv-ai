# Cognitive AI Game Architecture: Action Router Pattern

## Overview

This architecture implements a **separation of concerns** for cognitive games:
- **AI generates logic/structure** (blueprints, scene routing)
- **Pre-made animations/images** (asset library, no generation)
- **Action router** (maps patient choices to animations)
- **Validation layer** (ensures safety before execution)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ STORY BUILDING PHASE                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Patient Data (memories.json)                                    │
│        ↓                                                          │
│  Story Generator → 8-Scene Narrative                             │
│        ↓                                                          │
│  Each Scene: {narration, question, options, target_memory}       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ BLUEPRINT GENERATION PHASE (What AI Creates)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  BlueprintGenerator converts Story → GameBlueprint               │
│        ↓                                                          │
│  For each Scene:                                                 │
│    • Convert to SceneBlueprint (JSON structure)                  │
│    • Map options to ACTION IDs (strings)                         │
│    • Set initial_action for animations                           │
│                                                                   │
│  SceneBlueprint Structure:                                       │
│  {                                                               │
│    "scene_id": "scene_2_kitchen",                                │
│    "question_text": "Who cooked with you?",                      │
│    "options": [                                                  │
│      {"id": "person_anu", "text": "Anu"},                        │
│      {"id": "person_rahul", "text": "Rahul"}                     │
│    ],                                                            │
│    "action_map": {                                               │
│      "person_anu": "correct_answer_daughter",      ← ACTION ID   │
│      "person_rahul": "wrong_answer_encouragement"  ← ACTION ID   │
│    },                                                            │
│    "initial_action": "show_kitchen_memory"         ← ACTION ID   │
│  }                                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ VALIDATION PHASE (Safety Check)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  BlueprintValidator checks:                                      │
│    ✓ All ACTION IDs exist in AssetLibrary                        │
│    ✓ All required scene fields present                           │
│    ✓ Option IDs match action_map keys                            │
│    ✓ No null/undefined action references                         │
│                                                                   │
│  Result: validated=true/false + error_list                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ EXECUTION PHASE (Runtime)                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ExecutionEngine loads scenes and executes scene flow            │
│                                                                   │
│  When patient selects option (e.g., "Anu"):                      │
│    1. Look up option_id in action_map                            │
│    2. Get ACTION ID: "correct_answer_daughter"                   │
│    3. Call ActionRouter.route_action(option_id)                  │
│       └─→ ActionRouter fetches from AssetLibrary                 │
│           └─→ Get ActionSequence object                          │
│    4. Return animation sequence + metadata                       │
│       {                                                          │
│         "action_sequence": {...},                                │
│         "is_correct": true,                                      │
│         "hint_level": 0,                                         │
│         "duration": 8.5                                          │
│       }                                                          │
│    5. Unity receives animation frames + timing                   │
│       └─→ Execute: daughter appears → walks → hugs              │
│       └─→ Play narration: "Yes! That's Anu."                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Story → Blueprint → Execution

### 1. Story Phase
```python
story = StoryBuilder.build_story(patient)
# Creates:
#   - scene_1_welcome: narration + continue button
#   - scene_2_kitchen: question "Who cooked with you?" + 3 options
#   - ...
#   - scene_8_reward: congratulations
# Total: 8 scenes with structured scenes
```

### 2. Blueprint Phase
```python
blueprint = BlueprintGenerator.generate_blueprint(story)
# Converts to:
# {
#   "scene_2_kitchen": {
#     "options": [
#       {"id": "person_anu", "text": "Anu"},
#       {"id": "person_rahul", "text": "Rahul"}
#     ],
#     "action_map": {
#       "person_anu": "correct_answer_daughter",     ← ACTION ID
#       "person_rahul": "wrong_answer_encouragement" ← ACTION ID
#     }
#   }
# }
```

### 3. Validation Phase
```python
validator = BlueprintValidator()
report = validator.validate(blueprint)
# Checks: "Are all these ACTION IDs in AssetLibrary?"
# 
# If action_map references "show_food_chapathi" but it's not in
# AssetLibrary, validation fails with:
#   "ERROR: Scene scene_2_kitchen: Action 'show_food_chapathi' not found"
```

### 4. Execution Phase
```python
engine = ExecutionEngine(blueprint, asset_library)
scene = blueprint.scenes[0]
action_seq, response = engine.execute_action("person_anu")
# Returns:
# action_seq = ActionSequence {
#   id: "correct_answer_daughter",
#   animations: [
#     {id: "daughter_appear", duration: 1.0},
#     {id: "daughter_walk_to_mother", duration: 2.0},
#     ...
#   ]
# }
# response = {
#   "is_correct": true,
#   "hint_level": 0,
#   "duration": 8.5
# }
```

---

## Key Components

### 1. **AssetLibrary** (`asset_library.py`)
**Purpose**: Central source of truth for all animation sequences

**Contains**:
- 25+ pre-created ActionSequence objects
- Each has: id, duration, animation frames, narration
- Immutable collection (loaded once at startup)

**Responsibilities**:
```python
library = AssetLibrary()
action_seq = library.get_action_sequence("correct_answer_daughter")
# Returns ActionSequence with: daughter appear → walk → hug → celebrate
```

### 2. **BlueprintGenerator** (`blueprint_generator.py`)
**Purpose**: Convert Story objects into executable GameBlueprint JSON

**Process**:
1. Takes Story (from StoryBuilder)
2. For each Scene → SceneBlueprint
3. Maps options to action IDs via _get_*_action() methods
4. Returns GameBlueprint (serializable JSON)

**Key Methods**:
```python
def generate_blueprint(story: Story) → GameBlueprint
def _convert_scene_to_blueprint(scene: Scene) → SceneBlueprint
def _get_correct_answer_action(target_type: str) → str  # action ID
def _get_wrong_answer_action(target_type: str) → str    # action ID
```

### 3. **BlueprintValidator** (`blueprint_generator.py`)
**Purpose**: Verify blueprint before sending to Unity

**Checks**:
- All action_map values exist in AssetLibrary
- All scene references are valid
- No null/None action IDs
- Scene connectivity OK

**Result**: Validation report with error list

### 4. **ActionRouter** (`action_router.py`)
**Purpose**: Map patient button press → ActionSequence

**Flow**:
```
Patient presses "Anu" button
    ↓
ActionRouter.route_action("person_anu")
    ↓
Look up in current scene's action_map
    ↓
Get action ID: "correct_answer_daughter"
    ↓
Fetch from AssetLibrary
    ↓
Return ActionSequence + metadata
    ↓
ActionSequencePlayer generates playback frames
```

### 5. **ExecutionEngine** (`action_router.py`)
**Purpose**: Orchestrate scene loading and action execution

**Manages**:
- Current scene
- Patient action history
- Correct/wrong counts
- Integration with ActionRouter

**Interface**:
```python
engine = ExecutionEngine(blueprint, asset_library)
engine.load_scene(scene_id)
action_seq, response = engine.execute_action(option_id)
summary = engine.get_execution_summary()
```

### 6. **ActionSequencePlayer** (`action_router.py`)
**Purpose**: Convert ActionSequence into playback keyframes

**Generates**:
- Frame-by-frame animation data
- Timing information
- Narration cues
- Output format ready for Unity

---

## Data Models

### Story Scene (from StoryBuilder)
```python
class Scene:
    scene_id: str
    scene_type: "narrative" | "recall_question"
    narration: str
    question: Optional[GameQuestion]
    options: List[GameOption]  # Unstructured, randomized
```

### Blueprint Scene (JSON-serializable)
```python
class SceneBlueprint:
    scene_id: str
    scene_type: str
    environment: str
    characters: List[str]
    narration: str
    question_text: Optional[str]
    options: List[Dict]  # Structured, with id + text
    initial_action: str  # ACTION ID
    action_map: Dict[str, str]  # option_id → ACTION ID
```

### Action Sequence
```python
class ActionSequence:
    id: str
    description: str
    animations: List[AnimationAction]
    outcome_narration: str
    
class AnimationAction:
    id: str
    duration: float
    narration: Optional[str]
    next_action: Optional[str]
```

### Execution Response
```python
{
    "is_correct": bool,
    "hint_level": int,  # 0=independent, 1=cue, 2=strong hint, 3=reveal
    "duration": float,
    "action_sequence": ActionSequence,
    "narration": str
}
```

---

## Example Flow: Patient Plays Game

### Setup
```
1. Load patient: Lakshmi
2. Build story: "A Visit From Anu" (8 scenes)
3. Generate blueprint: Convert to JSON with action mappings
4. Validate blueprint: Check all action IDs exist
5. Create execution engine: Load blueprint + asset library
```

### Gameplay
```
SCENE 0: Welcome Screen
  [Narration] "Good morning. Let's spend time with memories."
  [Button 1] "Yes, I remember" → action: continue_to_kitchen
  [Button 2] "I'm not sure" → action: gentle_continue_to_kitchen
  
  Patient clicks: "Yes, I remember"
  → ActionRouter.route_action("opt_remember_yes")
  → Returns ActionSequence: continue_to_kitchen
  → Unity plays: fade transition to kitchen
  → Execution logs: {action: continue_to_kitchen, is_correct: null}

SCENE 1: Kitchen Question
  [Narration] "Someone special used to cook with you. Who?"
  [Button 1] "Anu" → action: correct_answer_daughter
  [Button 2] "Rahul" → action: wrong_answer_encouragement
  [Button 3] "Lakshmi" → action: wrong_answer_encouragement
  
  Patient clicks: "Anu"
  → ActionRouter.route_action("person_anu")
  → Look up action_map["person_anu"] = "correct_answer_daughter"
  → Fetch AssetLibrary["correct_answer_daughter"]
  → Return ActionSequence with:
     * daughter_appear (1s)
     * daughter_smile (1s)
     * daughter_walk_to_mother (2s)
     * daughter_hug_mother (2s)
     * reward_celebrate (2s)
  → Response: {is_correct: true, hint_level: 0, duration: 8s}
  → Unity plays all animations with narration
  → Execution logs: {action: correct_answer_daughter, is_correct: true}
```

---

## Why This Architecture?

### 1. **AI Generation ≠ Media Creation**
- AI generates structure (blueprints, logic)
- Humans create animations (pre-made sequences)
- AI only references, never generates

### 2. **Validation Before Execution**
- Check all action IDs exist before game starts
- Prevent runtime crashes
- Clear error messages for debugging

### 3. **Easy to Scale**
- Add new animation sequences to AssetLibrary
- AI automatically can reference them
- No code changes needed

### 4. **Reusable Components**
- Same ActionRouter for all patient games
- Same ExecutionEngine for all story types
- Same ValidationEngine for all blueprints

### 5. **Clear Separation**
```
AI Work:          Story → Blueprint (logic, structure)
Media Work:       Animation sequences (hand-created)
Integration Work: AssetLibrary (references)
```

---

## Files in This Architecture

| File | Purpose | Status |
|------|---------|--------|
| `models.py` | Pydantic data models | ✅ Complete |
| `asset_library.py` | Animation library + metadata | ✅ Complete (25+ sequences) |
| `blueprint_generator.py` | Story→Blueprint conversion | ✅ Complete |
| `blueprint_generator.py` | Blueprint validation | ✅ Complete |
| `action_router.py` | Patient action→animation routing | ✅ Complete |
| `blueprint_demo.py` | End-to-end demonstration | ✅ Complete |

---

## Next Steps: Unity Integration

Once blueprints are validated:

1. **REST API Layer**
   - POST /game/blueprint → Unity receives GameBlueprint JSON
   - GET /game/scene/{id} → Request specific scene
   - POST /game/action → Send patient choice, get ActionSequence

2. **JSON Protocol**
   - Request: `{"scene_id": "scene_2_kitchen", "option_id": "person_anu"}`
   - Response: `{"action_sequence": {...}, "is_correct": true, "duration": 8.5}`

3. **Asset Delivery**
   - Store animation files in `/assets/animations/`
   - Reference in ActionSequence: `{"id": "daughter_appear", "file": "assets/animations/daughter_01.fbx"}`

4. **Execution Flow in Unity**
   - Receive blueprint scene
   - Display narration and buttons
   - Detect patient click
   - Send to API
   - Receive action sequence
   - Play animations in sequence
   - Record outcome

---

## Quick Reference: Action ID Naming

Patterns used in AssetLibrary:

```
Correct answers:
  - correct_answer_daughter
  - correct_answer_food
  - correct_answer_family

Wrong answers:
  - wrong_answer_encouragement
  - wrong_answer_encouragement_2
  - wrong_answer_encouragement_3

Memory cues:
  - show_memory_cue
  - stronger_hint_daughter
  - reveal_answer_fully

Transitions:
  - continue_to_kitchen
  - gentle_continue_to_kitchen
  - enter_kitchen
  - enter_home

Rewards:
  - final_reward
  - reward_celebrate
  - positive_feedback_animation
```

---

## Troubleshooting

### Error: "Action 'show_food_chapathi' not found"
- Solution: Add to AssetLibrary or update BlueprintGenerator mapping

### Error: "KeyError 'is_correct' in execution response"
- Solution: Ensure ActionRouter._build_response() includes all keys

### Validation passes but execution fails
- Solution: Check ActionSequence animation IDs exist in file system

### Patient sees wrong animations
- Solution: Check action_map in SceneBlueprint matches logic

---

## Architecture Success Metrics

✅ **Achieved**:
- Story → Blueprint conversion works
- JSON serialization complete
- Validation layer functioning
- Action routing logic correct
- 8-scene demo runs without crashes
- Clear separation of concerns

🎯 **In Progress**:
- Add missing action sequences to AssetLibrary
- REST API for Unity communication
- Integration testing with animations

---

Generated: Blueprint Architecture v1.0
Demonstrated with: "A Visit From Anu" (Patient 001 Lakshmi)
