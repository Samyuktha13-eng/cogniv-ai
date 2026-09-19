# Cognitive AI Game Backend - API Documentation

## Overview

The backend is a **FastAPI server** that orchestrates the entire game flow:

```
CAREGIVER
    ↓
POST /game/create
    ↓
AI ORCHESTRATOR
├── Goal Agent → Parse caregiver intent
├── Memory Agent → Retrieve patient memories
├── Story Agent → Generate narrative
├── Game Agent → Convert to gameplay
└── Blueprint Generator → Create JSON blueprint
    ↓
VALIDATOR → Check all actions exist
    ↓
GAME BLUEPRINT (JSON)
    ↓
UNITY
    ↓
PATIENT GAMEPLAY
    ↓
POST /game/action (button press)
    ↓
ACTION ROUTER → Semantic action ID → Animation sequence
    ↓
Unity executes locally (fast, offline)
    ↓
POST /outcome/record (after animation)
    ↓
COGNITIVE PROFILE UPDATED
```

---

## Architecture: Two Loops

### 1. Real-time Gameplay Loop (Fast, Offline)
```
Patient button press
    ↓ (instant)
Action Router (local lookup)
    ↓ (instant)
Animation plays in Unity
    ↓ (after animation)
Record outcome
```

**Note**: No waiting for backend during gameplay!

### 2. AI Personalization Loop (Asynchronous)
```
Game complete
    ↓
Outcome recorded
    ↓
Cognitive profile updated
    ↓
AI Orchestrator analyzes patterns
    ↓
Generates next game
    ↓
Caregiver starts next game
```

---

## Server Setup

### Install Backend

```bash
cd backend
pip install -r requirements.txt
```

### Start Server

```bash
# Option 1: Direct Python
python -m backend.main

# Option 2: Uvicorn with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Production
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Server

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Interactive API docs
```

---

## API Endpoints

### 1. Create Game

**Endpoint**: `POST /game/create`

**Purpose**: Caregiver provides goal → Backend creates game blueprint

**Request**:
```json
{
  "patient_id": "Patient_001_Lakshmi",
  "goal": "Help Lakshmi remember her daughter Anu"
}
```

**Response** (200 OK):
```json
{
  "blueprint_id": "bp_patient_001_1693551234",
  "game_id": "visit_from_anu_001",
  "story_title": "A Visit From Anu",
  "patient_id": "Patient_001_Lakshmi",
  "validated": true,
  "validation_errors": [],
  "first_scene": {
    "scene_id": "scene_1_welcome",
    "scene_type": "narrative",
    "narration": "Good morning. Let's spend some time with your familiar memories.",
    "options": [
      {"id": "opt_yes", "text": "Yes, I remember"},
      {"id": "opt_not_sure", "text": "I'm not sure"}
    ],
    "action_map": {
      "opt_yes": "continue_to_kitchen",
      "opt_not_sure": "gentle_continue_to_kitchen"
    },
    "initial_action": "house_intro"
  }
}
```

**Error** (500 error):
```json
{
  "detail": "Failed to generate blueprint: [error reason]"
}
```

**Flow**:
1. Goal Agent parses: "Help Lakshmi remember her daughter Anu" → `{target: "person", memory: "daughter", person_id: "person_anu"}`
2. Memory Agent queries: Patient_001_Lakshmi → retrieves people, places, foods, memories
3. Story Agent creates: 8-scene narrative "A Visit From Anu"
4. Game Agent converts: Scenes → gameplay with questions and options
5. Blueprint Generator: Creates JSON with **semantic action IDs** (not filenames)
6. Validator: Checks all action IDs exist in SemanticActionLibrary
7. Returns: First scene for Unity to display

---

### 2. Get Scene

**Endpoint**: `GET /game/scene/{game_id}/{scene_id}`

**Purpose**: Retrieve a specific scene from the blueprint

**Example**:
```bash
curl http://localhost:8000/game/scene/visit_from_anu_001/scene_2_kitchen
```

**Response** (200 OK):
```json
{
  "scene_id": "scene_2_kitchen",
  "scene_type": "recall_question",
  "environment": "family_kitchen",
  "characters": [],
  "memory_assets": ["family_kitchen", "chapathi"],
  "narration": "Someone special used to cook with you. Do you remember who?",
  "question_text": "Someone special used to cook with you. Do you remember who?",
  "options": [
    {
      "id": "person_anu",
      "text": "Anu",
      "action": "daughter_recognition_success"
    },
    {
      "id": "person_rahul",
      "text": "Rahul",
      "action": "wrong_answer_encouragement"
    },
    {
      "id": "person_lakshmi",
      "text": "Lakshmi",
      "action": "wrong_answer_encouragement"
    }
  ],
  "initial_action": "show_kitchen_memory",
  "action_map": {
    "person_anu": "daughter_recognition_success",
    "person_rahul": "wrong_answer_encouragement",
    "person_lakshmi": "wrong_answer_encouragement"
  }
}
```

---

### 3. Execute Patient Action

**Endpoint**: `POST /game/action?game_id=...&scene_id=...&option_id=...`

**Purpose**: Patient presses button → Get animation sequence

**Example**:
```bash
curl -X POST "http://localhost:8000/game/action?game_id=visit_from_anu_001&scene_id=scene_2_kitchen&option_id=person_anu"
```

**Response** (200 OK) - **SEMANTIC ACTION ID**:
```json
{
  "option_id": "person_anu",
  "action_id": "daughter_recognition_success",
  "action_sequence": {
    "id": "daughter_recognition_success",
    "description": "Patient correctly identifies daughter Anu",
    "actions": [
      {
        "id": "daughter_appear",
        "duration": 1.0,
        "trigger_narration": null,
        "next_action": null
      },
      {
        "id": "daughter_smile",
        "duration": 1.0,
        "trigger_narration": null,
        "next_action": null
      },
      {
        "id": "daughter_walk_to_mother",
        "duration": 2.0,
        "trigger_narration": null,
        "next_action": null
      },
      {
        "id": "daughter_hug_mother",
        "duration": 2.0,
        "trigger_narration": null,
        "next_action": null
      },
      {
        "id": "reward_celebrate",
        "duration": 2.0,
        "trigger_narration": null,
        "next_action": null
      }
    ],
    "outcome_narration": "Yes! That's Anu, your daughter. She always cooked with you."
  },
  "is_correct": true,
  "hint_level": 0,
  "duration": 8.0
}
```

**What Unity Does**:
1. Receive `action_sequence` (list of semantic action IDs with durations)
2. For each action ID, look up animation file in local AssetLibrary
3. Play animations in sequence with timing
4. After all animations complete, display outcome_narration
5. Send outcome to `/outcome/record`

**Key Point**: Action ID is **semantic** ("daughter_recognition_success"), not a filename. Unity maps it to actual animation files.

---

### 4. Get Full Blueprint

**Endpoint**: `GET /game/blueprint/{blueprint_id}`

**Purpose**: Get complete game structure (all 8 scenes)

**Example**:
```bash
curl http://localhost:8000/game/blueprint/bp_patient_001_1693551234
```

**Response** (200 OK) - Contains all scenes:
```json
{
  "blueprint_id": "bp_patient_001_1693551234",
  "game_id": "visit_from_anu_001",
  "story_title": "A Visit From Anu",
  "patient_id": "Patient_001_Lakshmi",
  "cognitive_target": "person_recall",
  "memory_chain_goal": ["home", "kitchen", "chapathi", "person_anu", "family"],
  "created_by": "ai_generator",
  "version": "1.0",
  "validated": true,
  "validation_errors": [],
  "scenes": [
    { ... scene_1_welcome ... },
    { ... scene_2_kitchen ... },
    { ... scene_3a_correct ... },
    { ... scene_3b_wrong ... },
    { ... scene_6_food ... },
    { ... scene_7_family ... },
    { ... scene_8_reward ... }
  ]
}
```

---

### 5. Record Outcome

**Endpoint**: `POST /outcome/record`

**Purpose**: Record patient action result (after animation)

**Request**:
```json
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
```

**Response** (200 OK):
```json
{
  "outcome_id": "outcome_Patient_001_Lakshmi_2026-09-01T10:30:45.123456",
  "recorded": true,
  "cognitive_profile_updated": true
}
```

**Backend does**:
1. Store outcome in database
2. Update cognitive profile (aggregate stats)
3. Analyze memory associations
4. Prepare data for next AI game generation

---

### 6. Get Cognitive Profile

**Endpoint**: `GET /outcome/patient/{patient_id}/profile`

**Purpose**: Get patient's memory recall patterns

**Example**:
```bash
curl http://localhost:8000/outcome/patient/Patient_001_Lakshmi/profile
```

**Response** (200 OK):
```json
{
  "patient_id": "Patient_001_Lakshmi",
  "patient_name": "Lakshmi",
  "independent_recalls": {
    "daughter": 3,
    "chapathi": 2,
    "family": 1
  },
  "cue_assisted_recalls": {
    "son": 1,
    "temple": 1
  },
  "associations": {
    "Anu→Kitchen": true,
    "Anu→Chapathi": true,
    "Anu→Cooking": true,
    "Anu→Family": true
  },
  "summary": {
    "games_played": 3,
    "total_correct": 8,
    "total_attempts": 12,
    "accuracy": 0.667,
    "last_updated": "2026-09-01T14:30:00",
    "trend": "improving",
    "recommendation": "Continue with family-related memories. Strong recognition of Anu."
  }
}
```

**How AI uses this**:
- Next game focuses on weak associations (e.g., temple)
- Adjusts difficulty based on accuracy
- Reinforces successful memory chains

---

### 7. List Patient Games

**Endpoint**: `GET /outcome/patient/{patient_id}/games`

**Purpose**: Show all games patient has played

**Example**:
```bash
curl http://localhost:8000/outcome/patient/Patient_001_Lakshmi/games
```

**Response** (200 OK):
```json
{
  "patient_id": "Patient_001_Lakshmi",
  "games_count": 3,
  "games": [
    {
      "game_id": "visit_from_anu_001",
      "date": "2026-09-01T10:30:00",
      "outcomes_recorded": 8,
      "correct_answers": 5,
      "wrong_answers": 3,
      "accuracy": 0.625
    },
    {
      "game_id": "temple_visit_001",
      "date": "2026-09-01T14:20:00",
      "outcomes_recorded": 6,
      "correct_answers": 4,
      "wrong_answers": 2,
      "accuracy": 0.667
    },
    {
      "game_id": "morning_routine_001",
      "date": "2026-09-02T09:15:00",
      "outcomes_recorded": 5,
      "correct_answers": 5,
      "wrong_answers": 0,
      "accuracy": 1.0
    }
  ]
}
```

---

## Semantic Action IDs

Instead of filenames, blueprints use **semantic action IDs** (meaning-based):

### Person Recognition
- `daughter_recognition_success` → Daughter appears, walks, hugs, celebration
- `wrong_answer_encouragement` → Gentle encouragement, memory cue
- `show_memory_cue` → Show visual/contextual hint
- `stronger_hint_daughter` → Show face with name hint
- `reveal_answer_fully` → Full reveal with context

### Food Recognition
- `food_recognition_success` → Show food, person cooking, family meal
- `show_food_chapathi` → Display chapathi as memory anchor

### Family Association
- `family_recognition_success` → Show family, together, warmth

### Transitions
- `house_intro` → Camera pan, mother idle
- `continue_to_kitchen` → Fade transition, show kitchen, chapathi
- `gentle_continue_to_kitchen` → Gentle approach to next scene

### Rewards
- `final_reward` → Family gathering, celebration, music
- `positive_feedback` → Short celebration
- `reward_celebrate` → Brief celebration

**Key Benefit**: AI doesn't generate animations, only references them. The same animation library works for all games.

---

## How Unity Uses This

### Unity Flow

```
1. GET /game/create
   ↓ receive blueprint_id and first_scene
   
2. Display scene
   - Show narration
   - Display question
   - Show buttons
   
3. Patient presses button
   - Send POST /game/action
   
4. Receive action_sequence
   - For each action ID:
     * Look up animation file locally
     * Play animation with timing
   - After all actions: Show outcome narration
   
5. After animation
   - Send POST /outcome/record
   
6. Move to next scene
   - GET /game/scene/...
   - Repeat from step 2
```

### Example C# Code (Unity)

```csharp
// When patient presses button
async void OnButtonPressed(string optionId)
{
    // Get action sequence from backend
    var response = await apiClient.ExecuteAction(
        gameId: "visit_from_anu_001",
        sceneId: "scene_2_kitchen",
        optionId: "person_anu"
    );
    
    // Play animation sequence locally
    foreach (var action in response.ActionSequence.Actions)
    {
        string animFile = AssetLibrary.GetAnimationPath(action.Id);
        animator.PlayAnimation(animFile);
        await Task.Delay((int)(action.Duration * 1000));
    }
    
    // Show final narration
    narrator.Speak(response.ActionSequence.OutcomeNarration);
    
    // Record outcome
    await apiClient.RecordOutcome(new OutcomeRequest
    {
        PatientId = "Patient_001_Lakshmi",
        GameId = "visit_from_anu_001",
        SceneId = "scene_2_kitchen",
        OptionId: "person_anu",
        ActionId: response.ActionId,
        IsCorrect: response.IsCorrect,
        HintLevel: response.HintLevel,
        ResponseTime: stopwatch.ElapsedMilliseconds / 1000.0
    });
}
```

---

## Complete Game Flow Example

### Step 1: Caregiver Creates Game

```bash
curl -X POST http://localhost:8000/game/create \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "Patient_001_Lakshmi",
    "goal": "Help Lakshmi remember her daughter Anu"
  }'
```

**Response**: Blueprint with first scene

### Step 2: Unity Displays First Scene

```
Good morning. Let's spend some time with your familiar memories.

┌──────────────┐  ┌──────────────┐
│ Yes, I       │  │ I'm not      │
│ remember     │  │ sure         │
└──────────────┘  └──────────────┘
```

### Step 3: Patient Presses "Yes, I remember"

```bash
curl -X POST "http://localhost:8000/game/action?game_id=visit_from_anu_001&scene_id=scene_1_welcome&option_id=opt_yes"
```

**Response**: Action sequence with semantic IDs

### Step 4: Unity Plays Animation Sequence Locally

```
Action ID: "continue_to_kitchen"
├─ fade_transition (1.0s)
├─ kitchen_camera_transition (2.0s)
├─ show_chapathi (1.0s)
└─ mother_looks_at_food (1.0s)
```

### Step 5: Outcome Recorded

```bash
curl -X POST http://localhost:8000/outcome/record \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "Patient_001_Lakshmi",
    "game_id": "visit_from_anu_001",
    "scene_id": "scene_1_welcome",
    "option_id": "opt_yes",
    "action_id": "continue_to_kitchen",
    "is_correct": null,
    "hint_level": 0,
    "response_time": 0.5,
    "recall_type": "neutral"
  }'
```

### Step 6: Next Scene

```bash
curl http://localhost:8000/game/scene/visit_from_anu_001/scene_2_kitchen
```

**Scene 2 appears**: Kitchen with question about daughter

### Steps 7-8: Patient Presses "Anu" (Correct Answer)

```bash
curl -X POST "http://localhost:8000/game/action?game_id=visit_from_anu_001&scene_id=scene_2_kitchen&option_id=person_anu"
```

**Response**: Action sequence for "daughter_recognition_success"
- Daughter appears, walks to mother, hug, celebration

### Step 9: Record Correct Answer

```bash
curl -X POST http://localhost:8000/outcome/record \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "Patient_001_Lakshmi",
    "game_id": "visit_from_anu_001",
    "scene_id": "scene_2_kitchen",
    "option_id": "person_anu",
    "action_id": "daughter_recognition_success",
    "is_correct": true,
    "hint_level": 0,
    "response_time": 3.2,
    "recall_type": "independent"
  }'
```

### Step 10: Game Continues

All 8 scenes follow the same pattern...

### Step 11: Check Cognitive Profile

```bash
curl http://localhost:8000/outcome/patient/Patient_001_Lakshmi/profile
```

**Shows**: Progress, associations, recommendations for next game

---

## Error Handling

### 404 - Not Found
```json
{
  "detail": "Game visit_from_anu_001 not found"
}
```

### 400 - Bad Request
```json
{
  "detail": "Option person_anu not in action_map"
}
```

### 500 - Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# List available actions
curl http://localhost:8000/game/actions

# Create game
curl -X POST http://localhost:8000/game/create \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"Patient_001","goal":"Remember daughter"}'

# Execute action
curl -X POST "http://localhost:8000/game/action?game_id=game_1&scene_id=scene_1&option_id=opt_1"

# Record outcome
curl -X POST http://localhost:8000/outcome/record \
  -H "Content-Type: application/json" \
  -d '{...outcome data...}'

# Get profile
curl http://localhost:8000/outcome/patient/Patient_001/profile
```

---

## Next Steps

1. **Implement AI Orchestrator** (backend/agents/)
   - Goal Agent, Memory Agent, Story Agent, Game Agent
   
2. **Database Integration** (backend/memory/)
   - Store blueprints, outcomes, cognitive profiles
   - FAISS embeddings for memory retrieval
   
3. **Unity Integration**
   - C# API client in Unity
   - Asset library mapping
   - Animation playback logic
   
4. **Production Deployment**
   - Docker containerization
   - Cloud hosting (AWS, Google Cloud, etc.)
   - Database (MongoDB, Firebase, PostgreSQL)
