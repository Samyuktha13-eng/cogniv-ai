# File Generation Locations - Lakshmi-Anu Video Story System

## 📁 Directory Structure & File Locations

### Base Output Directory
All files are created under:
```
backend/generated_videos/lakshmi_anu_001/
```

### 1️⃣ VIDEOS Directory
**Location:** `backend/generated_videos/lakshmi_anu_001/videos/`

Generated when: Running `python lakshmi_anu_story_generator.py --generate-videos`

**Files created (11 MP4 videos):**
```
backend/generated_videos/lakshmi_anu_001/videos/
├── memory_01_home.mp4                    ← Scene 1
├── memory_02_anu.mp4                     ← Scene 2
├── memory_03_chapathi.mp4                ← Scene 3
├── memory_04_temple.mp4                  ← Scene 4
├── memory_05_trip.mp4                    ← Scene 5
├── memory_06_family_meal.mp4             ← Scene 6
├── memory_07_garden.mp4                  ← Scene 7
├── memory_08_radio.mp4                   ← Scene 8
├── present_01_transition.mp4             ← Scene 9
├── present_02_anu_enters.mp4             ← Scene 10
└── present_03_reunion_hug.mp4            ← Scene 11
```

**Created by:** `VideoSceneManager.generate_scene_video()`  
**Manager instance:** `LakshmiAnuStoryGenerator.manager`  
**Code location:** [lakshmi_anu_story_generator.py](./lakshmi_anu_story_generator.py#L43)  
**Details:** `self.videos_dir = self.output_base / "videos"`

---

### 2️⃣ SCENES Directory
**Location:** `backend/generated_videos/lakshmi_anu_001/scenes/`

Generated when: Running `python story_structure_demo.py` or any script that calls `manager.save_scene_json()`

**Files created (11 JSON files):**
```
backend/generated_videos/lakshmi_anu_001/scenes/
├── memory_01_home.json                   ← Scene 1 definition
├── memory_02_anu.json                    ← Scene 2 definition
├── memory_03_chapathi.json               ← Scene 3 definition
├── memory_04_temple.json                 ← Scene 4 definition
├── memory_05_trip.json                   ← Scene 5 definition
├── memory_06_family_meal.json            ← Scene 6 definition
├── memory_07_garden.json                 ← Scene 7 definition
├── memory_08_radio.json                  ← Scene 8 definition
├── present_01_transition.json            ← Scene 9 definition
├── present_02_anu_enters.json            ← Scene 10 definition
└── present_03_reunion_hug.json           ← Scene 11 definition
```

**Each JSON file contains:**
```json
{
  "metadata": {
    "scene_id": "memory_01_home",
    "sequence_number": 1,
    "title": "Lakshmi at Home / Beginning",
    "period": "past",
    "duration_seconds": 8
  },
  "characters": [
    {
      "name": "Lakshmi",
      "character_id": "lakshmi",
      "reference_images": [
        {"name": "Lakshmi", "asset_path": "Patient_001_Lakshmi/people/patient_lakshmi"}
      ],
      "age_note": "",
      "emotional_state": "thoughtful, peaceful"
    }
  ],
  "environment": {
    "name": "Living Room",
    "asset_path": "Patient_001_Lakshmi/home/living_room"
  },
  "objects": [...],
  "story_context": "...",
  "video_prompt": "[Full Veo API prompt - 400+ words]",
  "notes": "..."
}
```

**Created by:** `VideoSceneManager.save_scene_json()`  
**Code location:** [backend/video/video_scene_manager.py](./backend/video/video_scene_manager.py#L168)  
**Details:**
```python
def save_scene_json(self, scene: StoryScene, output_dir: Optional[str] = None) -> Path:
    save_dir = Path(output_dir) if output_dir else self.cache_dir
    filepath = save_dir / f"{scene.metadata.scene_id}.json"
    scene.save(str(filepath))
    return filepath
```

---

### 3️⃣ METADATA Directory
**Location:** `backend/generated_videos/lakshmi_anu_001/metadata/`

Generated when: Running `python story_structure_demo.py`

**Files created:**
```
backend/generated_videos/lakshmi_anu_001/metadata/
├── story_structure.json                  ← Scene structure export
├── scene_index.json                      ← Scene navigation index
├── video_catalog.json                    ← Video metadata (if videos generated)
├── story_manifest.json                   ← Complete story manifest
├── frontend_config.json                  ← Frontend configuration
├── scenes_manifest.json                  ← Video generation manifest
└── GENERATION_SUMMARY.txt                ← Summary report (text)
```

**Each file details:**

| File | Purpose | Created By | Triggers |
|------|---------|-----------|----------|
| `story_structure.json` | Complete scene structure as JSON | `story_structure_demo.py` | `export_story_json()` |
| `scene_index.json` | Scene navigation mapping | `story_structure_demo.py` | `create_scene_index()` |
| `video_catalog.json` | Video metadata catalog | `lakshmi_anu_story_generator.py` | `_create_video_catalog()` |
| `story_manifest.json` | Frontend-ready story manifest | `lakshmi_anu_story_generator.py` | `_create_story_manifest()` |
| `frontend_config.json` | Frontend app configuration | `story_structure_demo.py` | `create_frontend_config()` |
| `scenes_manifest.json` | Video generation cache | `VideoSceneManager` | Auto-created, auto-updated |
| `GENERATION_SUMMARY.txt` | Human-readable summary | `lakshmi_anu_story_generator.py` | `_generate_summary()` |

**Created by:** Multiple functions in generator classes  
**Code locations:**
- [lakshmi_anu_story_generator.py](./lakshmi_anu_story_generator.py#L107) - Step 4-6 (manifests)
- [story_structure_demo.py](./story_structure_demo.py#L190) - Step 3-5 (structure exports)
- [backend/video/video_scene_manager.py](./backend/video/video_scene_manager.py#L62) - cache manifest

---

### 4️⃣ INTEGRATION Directory
**Location:** `backend/generated_videos/lakshmi_anu_001/integration/`

Generated when: Running `python frontend_integration_generator.py`

**Files created:**
```
backend/generated_videos/lakshmi_anu_001/integration/
├── story_player.html                     ← Complete HTML UI
├── story_player.js                       ← JavaScript video player
├── backend_routes.py                     ← Flask/FastAPI routes
├── router_config.json                    ← Scene routing configuration
└── api_responses.json                    ← API endpoint specifications
```

**File details:**

| File | Purpose | Size | Usage |
|------|---------|------|-------|
| `story_player.html` | Complete video player UI with CSS | ~2KB | Copy to frontend |
| `story_player.js` | Interactive video controller | ~3KB | Include in HTML |
| `backend_routes.py` | Flask blueprint with 4 endpoints | ~2KB | Import in main app |
| `router_config.json` | Scene navigation routes | ~1KB | Frontend config |
| `api_responses.json` | API spec and example responses | ~2KB | Documentation |

**Created by:** `FrontendIntegration.generate_all_integration_files()`  
**Code location:** [frontend_integration_generator.py](./frontend_integration_generator.py#L584)  
**Details:**
```python
def generate_all_integration_files(self, 
                                   output_dir: str = "backend/generated_videos/lakshmi_anu_001/integration") -> Dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Creates 5 files in this directory
    files = {
        "router_config": output_dir / "router_config.json",
        "api_config": output_dir / "api_responses.json",
        "html_template": output_dir / "story_player.html",
        "javascript_player": output_dir / "story_player.js",
        "backend_routes": output_dir / "backend_routes.py",
    }
```

---

## 🔄 File Creation Flow

```
┌─────────────────────────────────────────────────────────────┐
│               USER RUNS SCRIPT                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ├─ python story_structure_demo.py
                          │  ├─ Creates metadata/story_structure.json
                          │  ├─ Creates metadata/scene_index.json
                          │  ├─ Creates metadata/frontend_config.json
                          │  └─ Creates scenes/*.json (11 files)
                          │
                          ├─ python lakshmi_anu_story_generator.py --generate-videos
                          │  ├─ Creates videos/*.mp4 (11 files)
                          │  ├─ Creates metadata/story_manifest.json
                          │  ├─ Creates metadata/video_catalog.json
                          │  └─ Updates metadata/scenes_manifest.json
                          │
                          └─ python frontend_integration_generator.py
                             ├─ Creates integration/story_player.html
                             ├─ Creates integration/story_player.js
                             ├─ Creates integration/backend_routes.py
                             ├─ Creates integration/router_config.json
                             └─ Creates integration/api_responses.json
```

---

## 📍 Exact File Paths in Code

### VideoSceneManager
**File:** `backend/video/video_scene_manager.py`

```python
# Line 37-47: Constructor
def __init__(self, 
             output_dir: str = "backend/generated_videos",
             cache_dir: str = "backend/generated_videos/cache"):
    self.output_dir = Path(output_dir)              # Videos go here
    self.cache_dir = Path(cache_dir)                # Metadata cached here
    self.output_dir.mkdir(parents=True, exist_ok=True)
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    self.cache_file = self.cache_dir / "scenes_manifest.json"

# Line 168-177: Save scene JSON
def save_scene_json(self, scene: StoryScene, output_dir: Optional[str] = None) -> Path:
    save_dir = Path(output_dir) if output_dir else self.cache_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    filepath = save_dir / f"{scene.metadata.scene_id}.json"
    scene.save(str(filepath))
    return filepath
```

### LakshmiAnuStoryGenerator
**File:** `lakshmi_anu_story_generator.py`

```python
# Line 16-33: Constructor
def __init__(self, 
             output_base: str = "backend/generated_videos/lakshmi_anu_001",
             patient_id: str = "Patient_001_Lakshmi"):
    self.output_base = Path(output_base)
    
    # Create subdirectories
    self.videos_dir = self.output_base / "videos"          # Videos → here
    self.scenes_dir = self.output_base / "scenes"          # Scenes → here
    self.metadata_dir = self.output_base / "metadata"      # Metadata → here
    
    for d in [self.videos_dir, self.scenes_dir, self.metadata_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Initialize manager
    self.manager = VideoSceneManager(
        output_dir=str(self.videos_dir),
        cache_dir=str(self.metadata_dir),
    )
```

### FrontendIntegration
**File:** `frontend_integration_generator.py`

```python
# Line 584: Generate integration files
def generate_all_integration_files(self, 
                                   output_dir: str = "backend/generated_videos/lakshmi_anu_001/integration") -> Dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    router_file = output_dir / "router_config.json"
    api_file = output_dir / "api_responses.json"
    html_file = output_dir / "story_player.html"
    js_file = output_dir / "story_player.js"
    routes_file = output_dir / "backend_routes.py"
```

---

## 🎯 Quick Reference - Where Each File Goes

```
Your workspace root (C:\Users\DELL\Downloads\Cognitiveai\)
│
└── backend/
    └── generated_videos/
        └── lakshmi_anu_001/
            │
            ├── videos/                          ← 11 MP4 files (if generated)
            │   ├── memory_01_home.mp4
            │   ├── memory_02_anu.mp4
            │   ├── ... (9 more)
            │
            ├── scenes/                          ← 11 JSON scene definitions
            │   ├── memory_01_home.json
            │   ├── memory_02_anu.json
            │   ├── ... (9 more)
            │
            ├── metadata/                        ← Manifests & config
            │   ├── story_structure.json
            │   ├── scene_index.json
            │   ├── frontend_config.json
            │   ├── story_manifest.json
            │   ├── video_catalog.json
            │   ├── scenes_manifest.json
            │   └── GENERATION_SUMMARY.txt
            │
            └── integration/                     ← Frontend code templates
                ├── story_player.html
                ├── story_player.js
                ├── backend_routes.py
                ├── router_config.json
                └── api_responses.json
```

---

## 📋 Complete Checklist - What Gets Created When

### After: `python story_structure_demo.py`
✅ `backend/generated_videos/lakshmi_anu_001/scenes/*.json` (11 files)  
✅ `backend/generated_videos/lakshmi_anu_001/metadata/story_structure.json`  
✅ `backend/generated_videos/lakshmi_anu_001/metadata/scene_index.json`  
✅ `backend/generated_videos/lakshmi_anu_001/metadata/frontend_config.json`  

### After: `python lakshmi_anu_story_generator.py --generate-videos`
✅ `backend/generated_videos/lakshmi_anu_001/videos/*.mp4` (11 files)  
✅ `backend/generated_videos/lakshmi_anu_001/metadata/story_manifest.json`  
✅ `backend/generated_videos/lakshmi_anu_001/metadata/video_catalog.json`  
✅ `backend/generated_videos/lakshmi_anu_001/metadata/GENERATION_SUMMARY.txt`  
✅ `backend/generated_videos/lakshmi_anu_001/metadata/scenes_manifest.json` (updated)  

### After: `python frontend_integration_generator.py`
✅ `backend/generated_videos/lakshmi_anu_001/integration/story_player.html`  
✅ `backend/generated_videos/lakshmi_anu_001/integration/story_player.js`  
✅ `backend/generated_videos/lakshmi_anu_001/integration/backend_routes.py`  
✅ `backend/generated_videos/lakshmi_anu_001/integration/router_config.json`  
✅ `backend/generated_videos/lakshmi_anu_001/integration/api_responses.json`  

---

## 🔗 Accessing Files After Generation

### In Python Code
```python
# Scenes directory
scenes_dir = Path("backend/generated_videos/lakshmi_anu_001/scenes")
for scene_file in scenes_dir.glob("*.json"):
    print(scene_file)

# Videos directory
videos_dir = Path("backend/generated_videos/lakshmi_anu_001/videos")
for video_file in videos_dir.glob("*.mp4"):
    print(video_file)

# Metadata directory
metadata_dir = Path("backend/generated_videos/lakshmi_anu_001/metadata")
manifest = json.load(open(metadata_dir / "story_manifest.json"))

# Integration directory
integration_dir = Path("backend/generated_videos/lakshmi_anu_001/integration")
with open(integration_dir / "story_player.html") as f:
    html_content = f.read()
```

### In Flask Backend
```python
from flask import send_file

@app.route('/videos/lakshmi_anu_001/<filename>')
def serve_video(filename):
    video_path = Path("backend/generated_videos/lakshmi_anu_001/videos") / filename
    return send_file(video_path, mimetype='video/mp4')
```

### In Frontend (HTML)
```html
<video src="/videos/lakshmi_anu_001/memory_01_home.mp4" controls></video>
```

---

## ✅ Verify Files Exist

After running scripts, verify with:

```powershell
# Check videos
Get-ChildItem "backend\generated_videos\lakshmi_anu_001\videos\" -Filter "*.mp4"

# Check scenes
Get-ChildItem "backend\generated_videos\lakshmi_anu_001\scenes\" -Filter "*.json"

# Check metadata
Get-ChildItem "backend\generated_videos\lakshmi_anu_001\metadata\" -Filter "*.json"

# Check integration
Get-ChildItem "backend\generated_videos\lakshmi_anu_001\integration\"
```

---

**Summary:** All files are organized under `backend/generated_videos/lakshmi_anu_001/` with clear subdirectories for videos, scene definitions, metadata, and frontend integration templates.
