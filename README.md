# Dementia Memory Platform - Core Game Engine

A Python-based cognitive engagement system for dementia patients, built around familiar personal memories. Features a narrative story flow engine that creates personalized interactive experiences through connected memory associations.

## 📁 Project Structure

```
Cognitiveai/
├── Patient_001_Lakshmi/          # Patient data folder
│   ├── people/                   # Images of family members
│   ├── home/                     # Home/room images
│   ├── food/                     # Food images
│   ├── places/                   # Location images
│   ├── memories/                 # Combined memory images
│   ├── objects/                  # Object images
│   ├── memories.json             # Memory database (metadata)
│   └── outcomes/                 # Game session recordings
│
├── models.py                     # Pydantic data models
├── memory_repository.py          # Loads and manages patient memories
├── game_generator.py             # Creates game scenarios
├── game.py                       # Basic game flow and logic
├── outcome_tracker.py            # Records and analyzes results
├── story_builder.py              # Builds narrative stories from memories
├── story_flow.py                 # Manages narrative progression through scenes
├── demo.py                       # Basic CLI game demo
├── story_demo.py                 # Full narrative story demo
└── requirements.txt              # Python dependencies
```

## 🎮 Core Components

### 1. **models.py** — Complete Data Models

Core entities:
- `Memory entities`: Person, Place, Food, Home, Object
- `Memory`: Composite memories linking multiple entities
- `PatientProfile`: Complete patient data
- `GameQuestion`: Question with options
- `GameEvent`: Player interaction record
- `GameSession`: Game session tracking

**New Story Models:**
- `Scene`: Individual scene in a narrative
- `StoryOption`: Dialogue/narrative choices
- `MemoryChainLink`: Connections between memory entities
- `Story`: Complete narrative with multiple scenes
- `StorySession`: Tracks playthrough of a story

### 2. **memory_repository.py** — Data Loader
```python
repo = MemoryRepository(patient_folder_path)
profile = repo.load()

# Access memories
daughter = repo.get_person_by_relationship("daughter")
memories = repo.get_memories_for_person(daughter.id)
entity = repo.get_entity_by_id("person_anu")
```

### 3. **game_generator.py** — Game Creation
```python
generator = GameGenerator(repo)

# Generate recall questions
question = generator.generate_person_recognition_game("daughter")
question = generator.generate_food_recognition_game("food_chapathi")

# Get progressive memory cues
cue, memory = generator.get_memory_clues_for_person(person_id)
```

### 4. **story_builder.py** — Narrative Constructor

Builds multi-scene interactive stories from patient data:

```python
builder = StoryBuilder(repo)
story = builder.build_visit_from_anu_story()
```

**Creates narrative structures with:**
- Multiple interconnected scenes
- Progressive memory cues
- Branching paths (correct/wrong answers)
- Emotional rewards
- Memory association tracking

### 5. **story_flow.py** — Narrative Engine

Manages progression through story scenes:

```python
flow = StoryFlowEngine(story, generator, tracker)

# Start story
scene_data = flow.start_story("session_001")

# Present scenes
scene_data = flow.present_scene(scene_id)

# Handle choices
response, next_scene = flow.handle_scene_choice(option_id)

# Handle recall questions with progressive cuing
response, next_scene = flow.handle_recall_answer(option_id)

# End story
summary = flow.end_story()
```

**Response types:**
- `correct` — Independent or cue-assisted recall
- `incorrect_with_cue` — Show memory cue, allow retry
- `incorrect_with_strong_hint` — Stronger hint, allow retry
- `revealed_answer` — Show answer after multiple attempts

### 6. **outcome_tracker.py** — Performance Analytics
```python
tracker = OutcomeTracker(patient_id, patient_folder)

# Record interactions
tracker.create_session("session_001", "A Visit From Anu")
tracker.record_event(event)
summary = tracker.end_session()

# Build cognitive profile
profile = tracker.get_patient_profile()
print(tracker.get_performance_summary())
```

## 🎭 The Complete Story: "A Visit From Anu"

An 8-scene narrative experience that helps Lakshmi recognize her daughter Anu through familiar visual associations.

### Memory Chain Goal
```
HOME → KITCHEN → CHAPATHI → ANU → FAMILY
```

### Scene Progression

**Scene 1: Welcome Home**
- Show family house
- Gentle introduction
- Navigation choice (no wrong answers)

**Scene 2: The Kitchen**
- Show kitchen and chapathi
- First recall question: "Who used to cook with you?"
- Options: Anu, Rahul, Lakshmi

**Scene 3: Correct Answer Path**
- Celebration with Anu
- Emotional reward

**Scene 3B: Wrong Answer Path**
- Gentle encouragement
- Progressive memory cues with images
- Retry mechanism (up to 3 attempts)

**Scene 4: Memory Cue**
- Show Anu cooking
- Additional context clues

**Scene 6: Food Recognition**
- Second recall question: "What were you making?"
- Options: Chapathi, Rice, Banana

**Scene 7: Family Memory**
- Show family meal image
- Third recall question: "Who else is there?"
- Options: Anu, Rahul, Lakshmi

**Scene 8: Emotional Reward**
- Final celebration
- Affirmation
- Session summary

## 📊 Cognitive Tracking

The system tracks three types of recall:

```
Independent Recall
└─ Patient recalls correctly on first attempt
   (hint_level = 0)

Cue-Assisted Recall
└─ Patient needs memory cues but succeeds
   (hint_level = 1 or 2)

Failed Recall
└─ Patient unable to recall even with cues
   (incorrect = true)
```

### Example Session Outcome
```json
{
  "events": [
    {
      "target_name": "Anu",
      "correct": true,
      "hint_level": 1,     // Cue-assisted
      "attempt_number": 2  // Second try
    },
    {
      "target_name": "Chapathi",
      "correct": true,
      "hint_level": 0,     // Independent
      "attempt_number": 1  // First try
    }
  ],
  "associations_made": [
    "home:home_kitchen",
    "food:food_chapathi",
    "memory:memory_anu_cooking",
    "memory:family_meal"
  ]
}
```

### Cognitive Profile Building

After multiple games, the system generates:

```
Person Recall
  Anu               → Cue-assisted (70% success)
  Rahul             → Independent (90% success)

Food Recall
  Chapathi          → Independent (100% success)
  Rice              → Cue-assisted (60% success)

Family Associations
  Anu + Kitchen     → Cue-assisted (80% success)
  Anu + Rahul       → Independent (95% success)
```

This profile guides the **AI Orchestrator** to generate the next personalized experience.

## 🚀 Running the Demos

### Basic Game Demo
```bash
python demo.py
```
Tests core game logic with static questions.

### Full Story Demo
```bash
python story_demo.py
```
Plays through the complete 8-scene "A Visit From Anu" narrative with:
- Scene transitions
- Memory chains
- Progressive cuing
- Outcome tracking
- Cognitive profile generation

## 📝 memories.json Format

Your patient data file (`Patient_001_Lakshmi/memories.json`) contains:

```json
{
  "patient_id": "patient_001",
  "patient_name": "Lakshmi",
  
  "people": [
    {
      "id": "person_anu",
      "name": "Anu",
      "relationship": "daughter",
      "image": "people/daughter_anu.png"
    }
  ],
  
  "home": [
    {
      "id": "home_kitchen",
      "name": "Family Kitchen",
      "image": "home/family_kitchen.jpg"
    }
  ],
  
  "food": [
    {
      "id": "food_chapathi",
      "name": "Chapathi",
      "image": "food/chapathi.jpg"
    }
  ],
  
  "memories": [
    {
      "id": "memory_anu_cooking",
      "title": "Cooking with Anu",
      "people": ["person_anu"],
      "home": ["home_kitchen"],
      "food": ["food_chapathi"],
      "image": "memories/anu_cooking_with_lakshmi.jpg",
      "description": "Anu used to cook chapathi with Lakshmi."
    }
  ]
}
```

## 🎯 Design Principles

- **Emotional Safety** — No punishment for wrong answers; only gentle encouragement
- **Progressive Cuing** — Visual → Description → Name hints  
- **Memory Chain** — Each scene connects to the last through familiar associations
- **Personalization** — Outcomes drive the selection of next experience
- **Dignity** — Respectful, calm interactions throughout
- **Recall Distinction** — Tracks independent vs. cue-assisted success

## 🔄 Next Steps in Architecture

```
Current:  Story + Outcome Tracking ✅
    ↓
Next:    Connect to Unity for visual gameplay
    ↓
Then:    AI Agents generate stories dynamically
    ↓
Final:   Full closed loop: Play → Analyze → Generate personalized next experience
```

## 🎬 Story Generation (Future: LLM Integration)

Once this engine is stable, the AI pipeline will be:

```
Caregiver Goal
"Help Lakshmi remember her daughter"
    ↓
Goal Analyzer
Structures the intent
    ↓
Memory Agent
Retrieves relevant memories
    ↓
Story Agent
Writes narrative
    ↓
Game Agent
Defines interactions
    ↓
Blueprint Generator
Creates Story JSON
    ↓
Validator
Ensures safety
    ↓
Story Flow Engine (This system)
Executes the story
    ↓
Outcome Tracker
Records results
    ↓
Patient Profile
Guides next story
```

## 📋 Key Features

✅ **Narrative Game Engine** — Multi-scene interactive stories  
✅ **Memory Associations** — Tracks connections between entities  
✅ **Progressive Cuing** — Multiple levels of memory support  
✅ **Detailed Outcome Tracking** — Independent vs. assisted recall  
✅ **Cognitive Profiling** — Aggregate patient performance  
✅ **Personalization Ready** — Architecture supports AI-driven next-game selection  
✅ **No Punishment** — All interactions are supportive  
✅ **Real Patient Data** — Works with actual memories and images  

## 🎯 For SIH Demo

Show the judges:

```
CAREGIVER
"Help Lakshmi remember her daughter"
    ↓
System generates "A Visit From Anu"
    ↓
👵 PLAYS THE GAME
    ├─ Wrong answer on first try
    ├─ Sees memory cue (Anu cooking)
    ├─ Tries again
    ├─ Correct! (Cue-assisted)
    ├─ Continues to next memory
    └─ Completes story
    ↓
OUTCOMES RECORDED
Person recognition: Cue-assisted
Food recognition: Independent
Family association: Independent
    ↓
COGNITIVE PROFILE UPDATED
Person memories: 60% independent
Food memories: 90% independent
    ↓
NEXT GAME SELECTED
"A Visit to the Temple with Anu"
(Focuses on places since person recognition needs more cues)
```

---

**Built for the SIH 2024 Innovation Challenge**

*Transforming dementia care through personalized, AI-driven cognitive engagement.*

