# Quick Reference - Lakshmi-Anu Video Story System

## One-Minute Overview

✅ **11-scene video narrative** for dementia memory therapy  
✅ **Structured scene definitions** with video prompts  
✅ **Video generation orchestration** using Veo 3.1 API  
✅ **Frontend integration templates** (HTML/JS/Flask)  
✅ **No API required** for structure visualization  

## File Quick Reference

| File | Use Case |
|------|----------|
| `story_structure_demo.py` | **START HERE** - View story structure |
| `story_scene_schema.py` | Understand data models |
| `story_scene_generator.py` | How scenes are created |
| `lakshmi_anu_story_generator.py` | Generate everything with one command |
| `frontend_integration_generator.py` | Create frontend code |
| `VIDEO_GENERATION_GUIDE.md` | Full documentation |

## Commands

### View Story Structure (No API Needed)
```bash
python story_structure_demo.py
```
**Output:** Story timeline, scene list, frontend config

### Generate Scene Definitions
```bash
python -c "
from story_scene_generator import generate_lakshmi_anu_scenes
from backend.video.video_scene_manager import VideoSceneManager

manager = VideoSceneManager()
scenes = generate_lakshmi_anu_scenes()
for scene in scenes:
    manager.save_scene_json(scene)
    print(f'Saved: {scene.metadata.scene_id}')
"
```
**Output:** 11 JSON files in `backend/generated_videos/lakshmi_anu_001/scenes/`

### Generate Videos (Requires API Key)
```bash
# Set API key
set GEMINI_API_KEY=your_gemini_api_key

# Generate all 11 videos
python lakshmi_anu_story_generator.py --generate-videos
```
**Time:** 10-15 minutes  
**Output:** 11 MP4 files + manifests

### Generate Frontend Code
```bash
python frontend_integration_generator.py
```
**Output:** HTML, JavaScript, Flask routes in `backend/generated_videos/lakshmi_anu_001/integration/`

## 11 Scenes at a Glance

| # | Scene ID | Title | Period | Key Element |
|---|----------|-------|--------|------------|
| 1 | memory_01_home | Lakshmi at Home | Past | Home environment |
| 2 | memory_02_anu | Remembers Anu | Past | Daughter appears |
| 3 | memory_03_chapathi | Making Chapathi | Past | Cooking activity |
| 4 | memory_04_temple | Temple Visit | Past | Religious memory |
| 5 | memory_05_trip | Family Trip | Past | Multi-generational |
| 6 | memory_06_family_meal | Family Meal | Past | Dining together |
| 7 | memory_07_garden | Family Garden | Past | Peaceful nature |
| 8 | memory_08_radio | Old Radio | Past | Object memory |
| 9 | present_01_transition | Fade to Present | Transition | Memory → Reality |
| 10 | present_02_anu_enters | Anu Enters Home | Present | Daughter arrives |
| 11 | present_03_reunion_hug | Mother-Daughter Hug | Present | Emotional embrace |

## Using Generated Files

### In Python

```python
# Load story scenes
from story_scene_generator import generate_lakshmi_anu_scenes
scenes = generate_lakshmi_anu_scenes()

# Access scene data
for scene in scenes:
    print(scene.metadata.scene_id)
    print(scene.metadata.title)
    print(scene.story_context)
    print(len(scene.characters))
    print(scene.video_prompt[:100])

# Export to JSON
scene.save("scene_data.json")

# Load from JSON
from story_scene_schema import StoryScene
with open("scene_data.json") as f:
    scene = StoryScene.from_dict(json.load(f))
```

### In Flask Backend

```python
from flask import Blueprint, send_file
from backend.video.video_scene_manager import VideoSceneManager

story_bp = Blueprint('story', __name__, url_prefix='/api/story')
manager = VideoSceneManager()

@story_bp.route('/lakshmi_anu/<scene_id>/video')
def get_scene_video(scene_id):
    video_path = manager.get_scene_video_path(scene_id)
    if video_path:
        return send_file(video_path, mimetype='video/mp4')
    return {'error': 'Video not found'}, 404

app.register_blueprint(story_bp)
```

### In HTML/JavaScript

```html
<script src="story_player.js"></script>
<div id="story-player"></div>
<script>
    const player = new LakshmiAnuStoryPlayer('story-player');
    player.nextScene();      // Go to next scene
    player.previousScene();  // Go to previous scene
    player.goToScene("memory_03_chapathi");  // Jump to scene
</script>
```

## Output File Locations

```
backend/generated_videos/lakshmi_anu_001/
│
├── videos/              ← Generated MP4 files (if videos generated)
│   └── memory_01_home.mp4 ... present_03_reunion_hug.mp4
│
├── scenes/              ← Scene JSON definitions
│   └── memory_01_home.json ... present_03_reunion_hug.json
│
├── metadata/            ← Generated automatically
│   ├── story_manifest.json
│   ├── scene_index.json
│   ├── video_catalog.json
│   ├── story_structure.json
│   └── frontend_config.json
│
└── integration/         ← Generated on demand
    ├── story_player.html
    ├── story_player.js
    ├── backend_routes.py
    ├── router_config.json
    └── api_responses.json
```

## API Endpoints

```
GET  /api/story/lakshmi_anu
     → Returns complete story with all 11 scenes

GET  /api/story/lakshmi_anu/{scene_id}
     → Returns specific scene metadata

GET  /api/story/lakshmi_anu/{scene_id}/video
     → Streams MP4 video file

POST /api/story/lakshmi_anu/progress
     → Track patient progress through story
```

## Therapeutic Journey

```
Patient Views Story:

[1-8] PAST MEMORIES
  ↓ Flashback through shared moments
  ├─ Recognizes familiar places (home, kitchen)
  ├─ Recalls activities (cooking, temple visit)
  ├─ Sees daughter (Anu) multiple times
  └─ Strengthens memory associations

[9] TRANSITION
  ↓ Memories fade away
  └─ Present day begins

[10-11] PRESENT DAY REUNION
  ↓ Emotional reunion
  ├─ Anu returns home
  └─ Final embrace with mother ❤️

OUTCOME: 
  ✓ Person recognition (Anu)
  ✓ Memory associations (activities → people → emotions)
  ✓ Emotional engagement (positive reunion)
```

## Data Model Quick Reference

### SceneMetadata
```python
SceneMetadata(
    scene_id="memory_01_home",           # Unique identifier
    sequence_number=1,                   # 1-11
    title="Lakshmi at Home",             # Human-readable
    period=ScenePeriod.PAST,             # PAST/TRANSITION/PRESENT
    duration_seconds=8,                  # Video length
)
```

### Character
```python
Character(
    name="Lakshmi",                      # Display name
    character_id="lakshmi",              # Unique ID
    reference_images=[...],              # Asset paths
    age_note="elderly",                  # Context
    emotional_state="thoughtful",        # Emotional tone
)
```

### StoryScene
```python
StoryScene(
    metadata=SceneMetadata(...),
    characters=[...],                    # Character list
    environment=Reference(...),          # Setting
    objects=[...],                       # Props/objects
    story_context="...",                 # Brief description
    video_prompt="...",                  # Full Veo API prompt
)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "GEMINI_API_KEY is not set" | Run: `set GEMINI_API_KEY=your_key` |
| "Reference image not found" | Check asset paths in `Patient_001_Lakshmi/` |
| Video generation times out | Veo API is rate-limited; wait and retry |
| Scene JSON won't serialize | Use `scene.to_dict()` or `scene.to_json()` |
| Frontend video won't play | Verify video path matches manifest |

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| View story structure | <1s | No API calls needed |
| Generate scene definitions | <5s | Local file I/O only |
| Generate 11 videos | 10-15 min | Veo API is rate-limited |
| Frontend load time | 5-30s/video | Depends on bandwidth |

## Next Steps After Implementation

1. ✅ Review story structure (`python story_structure_demo.py`)
2. ✅ Generate scene JSON definitions
3. 🔲 Generate videos (with API key)
4. 🔲 Integrate frontend templates
5. 🔲 Connect outcome tracking
6. 🔲 Deploy to production
7. 🔲 Create additional story variations

## Getting Help

**For documentation:**
- [VIDEO_GENERATION_GUIDE.md](./VIDEO_GENERATION_GUIDE.md) - Complete technical guide
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - What was built
- Code comments in each Python file

**For specific issues:**
1. Check output from `story_structure_demo.py`
2. Review scene JSON files in `backend/generated_videos/lakshmi_anu_001/scenes/`
3. Check manifests in `backend/generated_videos/lakshmi_anu_001/metadata/`
4. Run diagnostic: `python -c "from story_scene_generator import generate_lakshmi_anu_scenes; print(f'✓ Generated {len(generate_lakshmi_anu_scenes())} scenes')"`

## Example: Building a Frontend Component

```python
# Backend Flask app
from flask import Flask, jsonify, send_file
from backend.video.video_scene_manager import VideoSceneManager

app = Flask(__name__)
manager = VideoSceneManager()

@app.route('/api/story/lakshmi_anu')
def get_story():
    manifest = manager.export_story_manifest("lakshmi_anu_story_001")
    return jsonify(manifest)

@app.route('/api/story/lakshmi_anu/<scene_id>/video')
def get_video(scene_id):
    video_path = manager.get_scene_video_path(scene_id)
    if video_path:
        return send_file(video_path, mimetype='video/mp4')
    return jsonify({'error': 'Not found'}), 404

# Frontend JavaScript
class StoryPlayer {
    async loadStory() {
        const response = await fetch('/api/story/lakshmi_anu');
        this.story = await response.json();
        this.currentScene = 0;
        this.render();
    }
    
    async render() {
        const scene = this.story.scenes[this.currentScene];
        const video = document.querySelector('video');
        video.src = scene.video_path;
        document.querySelector('h1').textContent = scene.title;
    }
    
    nextScene() {
        if (this.currentScene < this.story.scenes.length - 1) {
            this.currentScene++;
            this.render();
        }
    }
}

// Usage
const player = new StoryPlayer();
player.loadStory();
```

---

**Status:** ✅ Ready to use  
**Last Updated:** January 2024  
**For full details:** See [VIDEO_GENERATION_GUIDE.md](./VIDEO_GENERATION_GUIDE.md)
