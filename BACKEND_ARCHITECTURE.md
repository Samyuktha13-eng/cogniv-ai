# Backend Architecture - Complete System

## Project Structure

```
Cognitiveai/
│
├── backend/                          # FastAPI Backend Server
│   ├── __init__.py
│   ├── main.py                       # ← Start here (uvicorn main:app)
│   ├── requirements.txt               # Backend dependencies
│   │
│   ├── api/                          # FastAPI Endpoints
│   │   ├── __init__.py
│   │   ├── game_routes.py            # POST /game/create, /game/action, GET /game/scene
│   │   └── outcome_routes.py         # POST /outcome/record, GET /patient/{id}/profile
│   │
│   ├── agents/                       # AI Orchestration Layer
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Main AI Orchestrator
│   │   ├── goal_agent.py             # Parse natural language goal
│   │   ├── memory_agent.py           # Retrieve patient memories with FAISS
│   │   ├── story_agent.py            # Generate narrative
│   │   └── game_agent.py             # Convert story to gameplay
│   │
│   ├── blueprint/                    # Blueprint Generation & Validation
│   │   ├── __init__.py
│   │   ├── semantic_actions.py       # Semantic action library & asset manifest
│   │   ├── generator.py              # Story → Blueprint converter
│   │   └── validator.py              # Validate blueprint before execution
│   │
│   ├── memory/                       # Patient Memory Management
│   │   ├── __init__.py
│   │   ├── memory_repository.py      # Load patient memories from JSON
│   │   ├── embeddings.py             # FAISS embeddings for memory retrieval
│   │   └── retrieval.py              # Memory search & ranking
│   │
│   ├── outcomes/                     # Outcome & Profile Management
│   │   ├── __init__.py
│   │   ├── tracker.py                # Track individual game events
│   │   └── aggregator.py             # Build cognitive profiles
│   │
│   └── models/                       # Pydantic Data Models
│       └── __init__.py               # All data model classes
│
├── Patient_001_Lakshmi/              # Patient Data
│   ├── people/
│   ├── home/
│   ├── places/
│   ├── food/
│   ├── memories/
│   ├── objects/
│   └── memories.json                 # Patient memory profile
│
├── assets/                           # Animation & Image Library
│   ├── animations/                   # .mp4, .mp3 files
│   ├── characters/                   # .png character images
│   ├── environments/                 # .png environment images
│   ├── food/                         # .png food images
│   └── memories/                     # .png memory images
│
├── unity/                            # Unity Game Client (future)
│   └── CognitiveGame/
│       ├── Scenes/
│       ├── Scripts/
│       │   ├── APIClient.cs          # Calls backend API
│       │   ├── SceneManager.cs       # Loads scenes from blueprint
│       │   ├── ActionRouter.cs       # Routes animations
│       │   ├── AnimationManager.cs   # Plays local animations
│       │   └── OutcomeManager.cs     # Records outcomes
│       ├── Animations/
│       └── UI/
│
├── ARCHITECTURE.md                   # High-level architecture
├── API_DOCUMENTATION.md              # Complete API reference
└── README.md                         # Project overview

```

---

## Data Flow: Complete Pipeline

### 1. Game Creation Flow

```
CAREGIVER UI
     │
     └─ POST /game/create
        {
          "patient_id": "Patient_001_Lakshmi",
          "goal": "Help Lakshmi remember her daughter Anu"
        }
            ↓
    ┌─────────────────────────────────────┐
    │  BACKEND - AI ORCHESTRATOR          │
    ├─────────────────────────────────────┤
    │                                     │
    │  1. Goal Agent                      │
    │     "daughter Anu"                  │
    │     ↓                               │
    │     {target: person, id: person_anu}│
    │                                     │
    │  2. Memory Agent                    │
    │     Query: Patient_001_Lakshmi      │
    │     ↓                               │
    │     Retrieve: people, places, foods │
    │     + memories connections          │
    │                                     │
    │  3. Story Agent                     │
    │     Generate: 8-scene narrative     │
    │     "A Visit From Anu"              │
    │     ├─ Scene 0: Welcome home        │
    │     ├─ Scene 1: Kitchen             │
    │     ├─ Scene 2: Question (who?)     │
    │     └─ ...                          │
    │                                     │
    │  4. Game Agent                      │
    │     Convert to gameplay             │
    │     ├─ Options                      │
    │     ├─ Semantic actions             │
    │     └─ Flow logic                   │
    │                                     │
    │  5. Blueprint Generator             │
    │     Story → JSON GameBlueprint      │
    │     with semantic action IDs        │
    │     (not animation filenames!)      │
    │                                     │
    │  6. Validator                       │
    │     Check: All action IDs exist?    │
    │     ↓ YES ✓                         │
    │     validated=true                  │
    │                                     │
    └─────────────────────────────────────┘
            ↓
    GameBlueprint (JSON)
        ├─ blueprint_id
        ├─ scenes[]
        │   └─ action_map {option→action_id}
        └─ validated=true
            ↓
    Response: First scene + metadata
            ↓
    UNITY displays scene to patient
```

### 2. Gameplay Execution Flow

```
PATIENT (in Unity)
     │
     ├─ Sees Scene 1: Kitchen
     │   "Who cooked with you?"
     │   [Anu] [Rahul] [Lakshmi]
     │
     └─ Presses "Anu"
            ↓
    UNITY → POST /game/action
    {
      game_id: "visit_from_anu_001",
      scene_id: "scene_2_kitchen",
      option_id: "person_anu"
    }
            ↓
    ┌──────────────────────────────┐
    │  BACKEND - ACTION ROUTER     │
    ├──────────────────────────────┤
    │                              │
    │  1. Look up scene            │
    │  2. Get action_map           │
    │  3. Find: option_id → action │
    │     "person_anu"             │
    │     ↓                         │
    │     "daughter_recognition_success"
    │  4. Query Semantic Action    │
    │     Library                  │
    │  5. Return ActionSequence:   │
    │     [                         │
    │       daughter_appear (1s),  │
    │       daughter_smile (1s),   │
    │       daughter_walk (2s),    │
    │       daughter_hug (2s),     │
    │       reward (2s)            │
    │     ]                         │
    │     + is_correct=true         │
    │     + hint_level=0            │
    │                              │
    └──────────────────────────────┘
            ↓
    Response: ActionSequence
    (semantic IDs, not animation filenames)
            ↓
    UNITY (local execution)
    ├─ For each action in sequence:
    │  ├─ Look up file in AssetLibrary
    │  │  "daughter_appear" → "assets/animations/daughter_appear.mp4"
    │  ├─ Play animation for X seconds
    │  └─ Wait for duration
    │
    ├─ Play outcome narration
    │  "Yes! That's Anu, your daughter..."
    │
    └─ Send POST /outcome/record
            ↓
    ┌──────────────────────────────────┐
    │ BACKEND - OUTCOME TRACKING       │
    ├──────────────────────────────────┤
    │                                  │
    │ 1. Store outcome                 │
    │ 2. Update cognitive profile      │
    │    ├─ Independent recalls count  │
    │    ├─ Cue-assisted recalls count │
    │    ├─ Memory associations        │
    │    └─ Accuracy metrics           │
    │ 3. Analyze patterns              │
    │ 4. Prepare for next game         │
    │                                  │
    └──────────────────────────────────┘
            ↓
    Cognitive Profile Updated
    → Used for next game generation
```

---

## Key Architectural Decisions

### 1. Separation of Concerns

```
┌─────────────────────────┐
│ What AI Generates       │
├─────────────────────────┤
│ Blueprints (logic)      │
│ - Scene flow            │
│ - Questions             │
│ - Semantic action IDs   │
│ (NOT animation files!)  │
└─────────────────────────┘

┌─────────────────────────┐
│ What Humans Create      │
├─────────────────────────┤
│ Animation sequences     │
│ - Character animations  │
│ - Environment videos    │
│ - Audio narration       │
│ (Pre-generated, reusable)
└─────────────────────────┘

┌─────────────────────────┐
│ What Connects Them      │
├─────────────────────────┤
│ Semantic Action Library │
│ "daughter_recognition" →
│ → "assets/animations/..." 
└─────────────────────────┘
```

### 2. Two Execution Loops

```
PERSONALIZATION LOOP (asynchronous)      GAMEPLAY LOOP (real-time)
┌─────────────────────────────────┐     ┌──────────────────────────┐
│ Patient completes game          │     │ Patient presses button   │
│ ↓                               │     │ ↓                        │
│ Outcome recorded                │     │ Action Router (local)    │
│ ↓                               │     │ ↓                        │
│ Profile updated                 │     │ Animation plays (local)  │
│ ↓                               │     │ ↓                        │
│ AI Orchestrator analyzes        │     │ Outcome recorded         │
│ ↓                               │     │                          │
│ Next game generated             │     │ (No backend latency!)    │
│ ↓                               │     │                          │
│ Caregiver sees recommendation   │     │ Instant feedback         │
│ ↓                               │     │                          │
│ Starts next game                │     │ Patient engaged!         │
└─────────────────────────────────┘     └──────────────────────────┘
```

### 3. Semantic Action IDs (Not Filenames)

```
WRONG APPROACH:
┌──────────────────────────────────┐
│ Blueprint contains:              │
│ "animation_01.mp4"              │  ← Filename!
│ "animation_02.mp4"              │
│ "animation_03.mp4"              │
│                                  │
│ Problem:                          │
│ - Hard to understand meaning     │
│ - Changes require blueprint edit │
│ - Can't reuse across games       │
└──────────────────────────────────┘

CORRECT APPROACH:
┌──────────────────────────────────┐
│ Blueprint contains:              │
│ "daughter_recognition_success"  │  ← Semantic ID!
│   ├─ What it means               │
│   ├─ Reusable across games       │
│   ├─ Easy to understand          │
│   └─ Maps to animation files     │
│       in AssetLibrary            │
│                                  │
│ Asset manifest:                  │
│ "daughter_recognition_success"  │
│ → assets/animations/daughter_walk
│ → assets/animations/daughter_hug
│ → assets/animations/celebration
└──────────────────────────────────┘
```

---

## API Endpoints Summary

### Game Creation & Execution
```
POST   /game/create                Create new game blueprint
GET    /game/blueprint/{id}         Get full blueprint
GET    /game/scene/{game}/{scene}   Get specific scene
POST   /game/action                 Execute patient action (button press)
```

### Outcome & Profile
```
POST   /outcome/record              Record game outcome
GET    /outcome/patient/{id}/profile Get cognitive profile
GET    /outcome/patient/{id}/games   List patient's games
```

### Debug
```
GET    /game/actions                List all semantic actions
GET    /game/blueprints             List all blueprints
GET    /outcome/debug/outcomes/{id} Debug outcomes
```

---

## Agent Responsibilities

### Goal Agent
```
Input: Natural language goal
       "Help Lakshmi remember her daughter Anu"
        ↓
Process: Parse intent
        ├─ Target type: person
        ├─ Target ID: person_anu
        └─ Goal type: recognition
        ↓
Output: Structured goal object
        {
          target_type: "person",
          target_id: "person_anu",
          objective: "person_recognition",
          context: "daughter"
        }
```

### Memory Agent
```
Input: Patient ID, structured goal
       "Patient_001_Lakshmi", goal
        ↓
Process: Query patient memories
        1. Load memories.json
        2. FAISS embedding search
        3. Rank by relevance
        4. Build memory context
        ↓
Output: Relevant memories
        {
          people: [Anu, Rahul, Lakshmi],
          places: [Kitchen, Temple],
          foods: [Chapathi, Rice],
          memories: [Anu cooking, Family meal, ...],
          associations: {Anu→Kitchen, Anu→Chapathi}
        }
```

### Story Agent
```
Input: Memories, goal
       memories, goal
        ↓
Process: Generate narrative
        1. Define memory chain goal
           [home → kitchen → chapathi → person → family]
        2. Create 8-scene story arc
        3. Place memories in scenes
        4. Define scene transitions
        ↓
Output: Story object
        {
          scenes: [
            {id: scene_1, narration: "..."},
            {id: scene_2, question: "Who cooked with you?"},
            ...
          ],
          memory_chain_goal: [home, kitchen, chapathi, person, family]
        }
```

### Game Agent
```
Input: Story, memories
       story, memories
        ↓
Process: Convert to gameplay
        1. For each scene:
           - Define question (if any)
           - Create options with answers
           - Map to semantic actions
        2. Choose answer flow:
           - Correct → celebration
           - Wrong → encouragement + cue
        ↓
Output: Gameplay structure
        {
          scenes: [
            {
              question_text: "Who cooked?",
              options: [
                {text: "Anu", correct: true, action: "..."},
                {text: "Rahul", correct: false, action: "..."}
              ],
              action_map: {...}
            }
          ]
        }
```

---

## Data Models

### Request Models (API Input)
```python
GameCreateRequest
├─ patient_id: str
└─ goal: str

OutcomeRequest
├─ patient_id: str
├─ game_id: str
├─ scene_id: str
├─ option_id: str
├─ action_id: str
├─ is_correct: bool
├─ hint_level: int
├─ response_time: float
└─ recall_type: str
```

### Response Models (API Output)
```python
GameCreateResponse
├─ blueprint_id: str
├─ game_id: str
├─ story_title: str
├─ validated: bool
├─ validation_errors: List[str]
└─ first_scene: SceneBlueprint

ActionResponse
├─ option_id: str
├─ action_id: str (SEMANTIC!)
├─ action_sequence: ActionSequence
├─ is_correct: bool
├─ hint_level: int
└─ duration: float

CognitiveProfileResponse
├─ patient_id: str
├─ independent_recalls: Dict
├─ cue_assisted_recalls: Dict
├─ associations: Dict
└─ summary: Dict
```

---

## Running the Backend

### Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start server
python -m backend.main

# OR with auto-reload:
uvicorn backend.main:app --reload

# 3. Check API
curl http://localhost:8000/docs
```

### With Docker (future)

```dockerfile
FROM python:3.11
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

---

## Next Steps

### Immediate (Week 1)
1. ✅ Backend folder structure
2. ✅ FastAPI routes
3. ✅ Semantic action library
4. ⚙️ Implement Goal Agent
5. ⚙️ Implement Memory Agent
6. ⚙️ Implement Story Agent
7. ⚙️ Implement Game Agent

### Short-term (Week 2-3)
1. Database integration (MongoDB/Firebase)
2. FAISS memory embeddings
3. LLM integration (Gemini + LangGraph)
4. Blueprint validation
5. Outcome tracking & aggregation

### Medium-term (Week 4+)
1. Unity game client
2. API client for Unity (C#)
3. Animation playback system
4. User interface (Caregiver + Patient)
5. Testing & refinement

### Long-term (Production)
1. Deployment (Cloud)
2. Multi-patient system
3. Multi-game scenarios
4. Offline synchronization
5. Analytics dashboard
