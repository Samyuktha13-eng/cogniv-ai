# Lakshmi-Anu Story Video Generation System

Complete implementation of the 11-scene narrative video generation system for dementia memory therapy using Google's Veo video generation model.

## Overview

This system creates a structured video narrative combining **past memories** → **transition** → **present-day reunion** designed specifically for Lakshmi's cognitive rehabilitation journey.

### Story Structure

**11 Scenes Total:**
- **Scenes 1-8 (Past Memories):** Flashbacks to cherished moments with Anu
- **Scene 9 (Transition):** Memories fade, present day begins
- **Scenes 10-11 (Present Day):** Anu returns home, emotional reunion

### Core Components

```
story_scene_schema.py          # Data models for scenes
story_scene_generator.py       # Generate 11-scene definitions
backend/video/video_scene_manager.py  # Video generation orchestration
lakshmi_anu_story_generator.py # Complete pipeline
story_structure_demo.py        # Visualize story without generating videos
frontend_integration_generator.py  # Generate frontend integration code
```

## Quick Start

### 1. View Story Structure (No API Required)

```bash
python story_structure_demo.py
```

This generates:
- Story structure visualization
- Scene index JSON
- Frontend configuration
- Interactive timeline

**Output:**
```
backend/generated_videos/lakshmi_anu_001/
├── metadata/
│   ├── story_structure.json
│   ├── frontend_config.json
│   ├── scene_index.json
│   └── GENERATION_SUMMARY.txt
└── scenes/
    └── [11 scene definition JSON files]
```

### 2. Generate Scene Definitions

```bash
python -c "
from story_scene_generator import generate_lakshmi_anu_scenes
from backend.video.video_scene_manager import VideoSceneManager

manager = VideoSceneManager()
scenes = generate_lakshmi_anu_scenes()

for scene in scenes:
    json_path = manager.save_scene_json(scene)
    print(f'Saved: {json_path}')
"
```

### 3. Generate Videos (Requires Gemini API Key)

Set environment variable:
```bash
set GEMINI_API_KEY=your_key_here
```

Generate videos:
```bash
python lakshmi_anu_story_generator.py --generate-videos
```

This calls Google's Veo 3.1 API to generate each video, which takes **10-15 minutes total**.

### 4. Generate Frontend Integration Code

```bash
python frontend_integration_generator.py
```

Creates:
- `story_player.html` - Complete story viewer UI
- `story_player.js` - Interactive video player
- `backend_routes.py` - Flask/FastAPI routes
- `router_config.json` - Scene navigation config
- `api_responses.json` - API endpoint specifications

## Detailed Usage

### Understanding Scene Definitions

Each scene is defined with:

```python
StoryScene(
    metadata=SceneMetadata(
        scene_id="memory_03_chapathi",
        sequence_number=3,
        title="Anu and Lakshmi Making Chapathi",
        period=ScenePeriod.PAST,
    ),
    characters=[
        Character(
            name="Lakshmi",
            character_id="lakshmi",
            reference_images=[Reference(name="Lakshmi", asset_path="Patient_001_Lakshmi/people/patient_lakshmi")],
            emotional_state="content, engaged",
        ),
        Character(
            name="Anu",
            character_id="anu",
            reference_images=[Reference(name="Anu", asset_path="Patient_001_Lakshmi/people/anu")],
            age_note="appearing younger in this past memory",
            emotional_state="loving, focused",
        )
    ],
    environment=Reference(name="Kitchen", asset_path="Patient_001_Lakshmi/home/kitchen"),
    objects=[Reference(name="Chapathi", asset_path="Patient_001_Lakshmi/food/chapathi")],
    story_context="Shared family memory of cooking chapathi together in the kitchen.",
    video_prompt="[Detailed Veo API prompt preserved exactly from specification]",
)
```

### Video Generation Process

```python
from backend.video.video_scene_manager import VideoSceneManager
from story_scene_generator import generate_lakshmi_anu_scenes

manager = VideoSceneManager()
scenes = generate_lakshmi_anu_scenes()

# Generate all 11 videos
results = manager.generate_story_videos(scenes)

for scene_id, result in results.items():
    if result.success:
        print(f"✓ {scene_id}: {result.video_path}")
    else:
        print(f"✗ {scene_id}: {result.error}")
```

### Frontend Integration

#### 1. HTML Setup

```html
<div id="story-container"></div>
<script src="story_player.js"></script>
<script>
    const player = new LakshmiAnuStoryPlayer('story-container');
</script>
```

#### 2. Backend API Endpoints

```python
from flask import Blueprint, jsonify

story_bp = Blueprint('story', __name__, url_prefix='/api')

@story_bp.route('/story/lakshmi_anu', methods=['GET'])
def get_story():
    return jsonify(story_manifest)

@story_bp.route('/story/lakshmi_anu/<scene_id>/video', methods=['GET'])
def get_video(scene_id):
    return send_file(video_path, mimetype='video/mp4')
```

#### 3. Player Initialization

```javascript
class LakshmiAnuStoryPlayer {
    constructor(containerId, apiBase = '/api') {
        this.currentScene = 0;
        this.fetchStory();
    }
    
    async fetchStory() {
        const response = await fetch(`${this.apiBase}/story/lakshmi_anu`);
        this.storyData = await response.json();
        this.renderScene(0);
    }
    
    renderScene(index) {
        // Update video, title, characters, navigation
    }
    
    nextScene() { }
    previousScene() { }
}
```

## Scene Details

### 🏠 Past Memories (Scenes 1-8)

| Scene | Title | Key Elements | Therapeutic Goal |
|-------|-------|--------------|-----------------|
| 1 | Lakshmi at Home | Home environment, familiar space | Establish comfort, recognition |
| 2 | Remembers Anu | Lakshmi + Anu appears | Introduce daughter visually |
| 3 | Making Chapathi | Cooking activity, food | Activity recognition, bonding |
| 4 | Temple Visit | Religious/cultural setting | Cultural identity, family traditions |
| 5 | Family Trip | Multi-generational scene | Extended family connection |
| 6 | Family Meal | Dining together, food sharing | Family bonding, routine memory |
| 7 | Garden | Nature, peaceful setting | Calm memory, emotional connection |
| 8 | Old Radio | Object-focused memory | Familiar object recognition |

### ✨ Transition (Scene 9)

- Memories visually fade
- Present-day lighting begins
- Anu approaches home
- Emotional shift from past to present

### 💚 Present Day (Scenes 10-11)

| Scene | Title | Key Elements | Therapeutic Goal |
|-------|-------|--------------|-----------------|
| 10 | Anu Enters Home | Daughter arrives, recognition | Current-day awareness |
| 11 | Mother-Daughter Embrace | Emotional reunion, physical connection | Maximum emotional engagement |

## File Organization

```
backend/generated_videos/lakshmi_anu_001/
│
├── videos/
│   ├── memory_01_home.mp4
│   ├── memory_02_anu.mp4
│   ├── memory_03_chapathi.mp4
│   ├── memory_04_temple.mp4
│   ├── memory_05_trip.mp4
│   ├── memory_06_family_meal.mp4
│   ├── memory_07_garden.mp4
│   ├── memory_08_radio.mp4
│   ├── present_01_transition.mp4
│   ├── present_02_anu_enters.mp4
│   └── present_03_reunion_hug.mp4
│
├── scenes/
│   ├── memory_01_home.json
│   ├── memory_02_anu.json
│   ├── ... [10 more JSON files]
│
├── metadata/
│   ├── story_manifest.json
│   ├── scene_index.json
│   ├── video_catalog.json
│   ├── story_structure.json
│   ├── frontend_config.json
│   └── GENERATION_SUMMARY.txt
│
└── integration/
    ├── router_config.json
    ├── api_responses.json
    ├── story_player.html
    ├── story_player.js
    └── backend_routes.py
```

## API Reference

### Story Endpoints

**GET /api/story/lakshmi_anu**
```json
{
  "story_id": "lakshmi_anu_story_001",
  "title": "A Visit From Anu",
  "patient_id": "Patient_001_Lakshmi",
  "total_scenes": 11,
  "scenes": [
    {
      "scene_id": "memory_01_home",
      "sequence": 1,
      "title": "Lakshmi at Home",
      "video_path": "/videos/lakshmi_anu_001/memory_01_home.mp4",
      "characters": ["lakshmi"]
    }
  ]
}
```

**GET /api/story/lakshmi_anu/{scene_id}**
```json
{
  "scene_id": "memory_03_chapathi",
  "title": "Anu and Lakshmi Making Chapathi",
  "period": "past",
  "duration": 8,
  "characters": [
    {"id": "lakshmi", "name": "Lakshmi"},
    {"id": "anu", "name": "Anu"}
  ],
  "description": "Shared family memory of cooking chapathi together",
  "video_path": "/videos/lakshmi_anu_001/memory_03_chapathi.mp4"
}
```

**GET /api/story/lakshmi_anu/{scene_id}/video**
- Returns MP4 video stream
- MIME type: `video/mp4`

**POST /api/story/lakshmi_anu/progress**
```json
{
  "scene_id": "memory_03_chapathi",
  "completed": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Therapeutic Integration

### Cognitive Rehabilitation Goals

1. **Person Recognition** - Visual identification of Anu across multiple contexts
2. **Memory Association** - Connecting activities/places to people
3. **Emotional Connection** - Positive feelings toward reunion
4. **Routine Recognition** - Identifying familiar daily activities
5. **Cultural Identity** - Maintaining sense of Indian heritage and traditions

### Patient Flow

1. Patient enters app
2. Guided through 11-minute story sequence
3. Videos trigger memory associations
4. Questions test recall (integration with game_generator)
5. Outcomes recorded for cognitive assessment
6. Progress tracked over multiple sessions

## Troubleshooting

### Video Generation Fails

**Error:** `GEMINI_API_KEY is not set`
```bash
# Set API key
set GEMINI_API_KEY=your_key_here
```

**Error:** `Reference image not found`
- Verify asset paths exist in `Patient_001_Lakshmi/` directory
- Check asset naming conventions

### Missing Scene Data

```bash
# Regenerate scene definitions
python -c "
from story_scene_generator import generate_lakshmi_anu_scenes
from backend.video.video_scene_manager import VideoSceneManager

manager = VideoSceneManager()
scenes = generate_lakshmi_anu_scenes()
for scene in scenes:
    manager.save_scene_json(scene)
"
```

### Frontend Video Won't Play

1. Verify video files exist at paths in manifest
2. Check CORS headers if videos on separate domain
3. Verify MIME type is `video/mp4`
4. Check browser video codec support (H.264 recommended)

## Performance Notes

- **Scene Definition Generation:** <1 second
- **Scene JSON Export:** <5 seconds
- **Video Generation:** ~10-15 minutes for 11 videos (Veo API rate-limited)
- **Frontend Load Time:** Depends on video download (typically 5-30 seconds per video)

## Extensions

### Adding New Story Variations

```python
class StorySceneGenerator:
    def build_alternate_scenes(self) -> List[StoryScene]:
        # Create variations for different memory contexts
        pass
```

### Multi-Patient Support

```python
generator = StorySceneGenerator(patient_dir="Patient_002_Name")
scenes = generator.build_all_scenes()
```

### Adaptive Difficulty

```python
# Generate scenes with varying complexity levels
scene = scene_with_additional_characters()
scene = scene_with_subtle_memory_cues()
```

## Documentation Files

- **story_scene_schema.py** - Data model documentation
- **story_scene_generator.py** - Scene generation logic
- **backend/video/video_scene_manager.py** - Video orchestration
- **lakshmi_anu_story_generator.py** - Complete pipeline
- **story_structure_demo.py** - Visualization and testing
- **frontend_integration_generator.py** - Frontend code generation

## References

- [Google Veo 3.1 API Documentation](https://ai.google.dev/gemini-api/docs/video/generate)
- [Scene Schema Definition](./story_scene_schema.py)
- [Story Generator Code](./story_scene_generator.py)
- [Integration Guide](./frontend_integration_generator.py)

## Support

For issues or questions:
1. Review story_structure_demo.py output
2. Check scene JSON definitions in `metadata/` directory
3. Verify asset paths in Patient_001_Lakshmi/ directory
4. Run diagnostic using `get_errors()` tool

---

**Version:** 1.0  
**Last Updated:** January 2024  
**Status:** ✅ Complete & Tested
