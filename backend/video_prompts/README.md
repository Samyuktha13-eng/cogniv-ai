# Video Prompts - Lakshmi & Anu Memory Therapy Narrative

Complete 11-scene video prompt library for Google Veo 3.1 API video generation.

## 📁 Directory Structure

```
backend/video_prompts/
├── INDEX.json                      # Master index of all 11 scenes
├── README.md                       # This file
│
├── PAST MEMORIES (8 scenes)
├── memory_01_home.json            # Lakshmi at home - beginning
├── memory_02_anu.json             # Lakshmi remembers Anu
├── memory_03_chapathi.json        # Making chapathi together
├── memory_04_temple.json          # Temple visit memory
├── memory_05_trip.json            # Family trip memory
├── memory_06_family_meal.json     # Family meal together
├── memory_07_garden.json          # Family garden time
├── memory_08_radio.json           # Listening to old radio
│
├── TRANSITION (1 scene)
├── present_01_transition.json     # Memory → present-day bridge
│
└── PRESENT-DAY REUNION (2 scenes)
    ├── present_02_anu_enters.json # Anu enters the home
    └── present_03_reunion_hug.json # Final mother-daughter hug
```

## 🎯 Story Structure

### Period 1: PAST (8 scenes, ~72 seconds)
Establishes familiar memories with younger Anu and Rahul, family connections, and emotional anchors:

| # | Scene | Duration | Focus |
|---|-------|----------|-------|
| 1 | **Lakshmi at Home** | 8s | Establish safe, familiar environment |
| 2 | **Lakshmi Remembers Anu** | 8s | Introduce Anu's face and daughter role |
| 3 | **Making Chapathi** | 10s | Shared activity and cultural memory |
| 4 | **Temple Memory** | 10s | Spiritual moment and special occasion |
| 5 | **Family Trip** | 10s | Extended family and positive experiences |
| 6 | **Family Meal** | 10s | Shared meals and togetherness |
| 7 | **Garden Time** | 10s | Peaceful, familiar environment |
| 8 | **Old Radio** | 10s | Sensory cues and comfort objects |

**Therapeutic Goal**: Build visual familiarity and emotional anchors

### Period 2: TRANSITION (1 scene, ~8 seconds)
Bridge from memory to present-day reality:

| # | Scene | Duration | Focus |
|---|-------|----------|-------|
| 9 | **Memory → Present Bridge** | 8s | Fade memories, introduce present day |

**Therapeutic Goal**: Prepare for recognition of adult Anu

### Period 3: PRESENT (2 scenes, ~24 seconds)
Present-day reunion with adult Anu:

| # | Scene | Duration | Focus |
|---|-------|----------|-------|
| 10 | **Anu Enters the Home** | 12s | Recognize adult daughter arriving |
| 11 | **Mother-Daughter Hug** | 12s | Emotional closure and affirmation |

**Therapeutic Goal**: Real-time recognition and emotional reconnection

---

## 📄 JSON File Format

Each scene file follows this structure:

```json
{
  "scene_id": "memory_01_home",
  "sequence_number": 1,
  "title": "Lakshmi at Home / Beginning",
  "period": "past|transition|present",
  "duration_seconds": 8,
  "characters": ["people/patient_lakshmi"],
  "environment": "home/living_room",
  "reference_images": [
    "people/patient_lakshmi",
    "home/living_room",
    "home/house"
  ],
  "objects": [],
  "story": "Brief narrative description",
  "video_prompt": "Complete Veo API prompt..."
}
```

### Field Descriptions

| Field | Type | Purpose |
|-------|------|---------|
| `scene_id` | String | Unique identifier for the scene |
| `sequence_number` | Integer | Order in 11-scene narrative (1-11) |
| `title` | String | Human-readable scene title |
| `period` | Enum | "past", "transition", or "present" |
| `duration_seconds` | Integer | Target video length |
| `characters` | Array | Character references from Patient_001_Lakshmi/ |
| `environment` | String | Main environment reference |
| `reference_images` | Array | All asset paths for facial/environmental identity |
| `objects` | Array | Important prop/visual references |
| `story` | String | 1-2 sentence narrative summary |
| `video_prompt` | String | Complete Veo API prompt (400-500 words) |

---

## 🎬 Using These Prompts with Google Veo 3.1

### Setup
```python
import os
import json
from google.generativeai import genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Load a scene
with open("backend/video_prompts/memory_01_home.json") as f:
    scene = json.load(f)

# Extract video prompt
veo_prompt = scene["video_prompt"]
```

### Generate Video
```python
def generate_veo_video(scene: dict, reference_images: list) -> str:
    """
    Generate Veo video for a single scene.
    
    Args:
        scene: Scene JSON object with video_prompt
        reference_images: List of reference image file paths
    
    Returns:
        Video URL from Veo API
    """
    # Prepare file paths
    files = []
    for ref_path in scene["reference_images"]:
        abs_path = f"Patient_001_Lakshmi/{ref_path}"
        files.append(genai.upload_file(abs_path))
    
    # Generate video with reference images + prompt
    response = genai.models.generate_content(
        model="models/gemini-2.0-flash",  # Veo 3.1 via Gemini
        contents=[
            *files,
            scene["video_prompt"]
        ]
    )
    
    return response.video_url
```

### Batch Generation
```python
import json
from pathlib import Path

scenes_dir = Path("backend/video_prompts")
index = json.load(open(scenes_dir / "INDEX.json"))

for scene_info in index["scenes"]:
    scene_file = scenes_dir / scene_info["file"]
    scene = json.load(open(scene_file))
    
    video_url = generate_veo_video(scene, scene["reference_images"])
    
    # Save video
    output_path = f"backend/generated_videos/lakshmi_anu_001/videos/{scene['scene_id']}.mp4"
    # Download and save...
```

---

## 🎨 Prompt Engineering Principles

All prompts follow these key principles:

### 1. **Facial Identity Preservation**
```
"Use the provided Lakshmi reference image to preserve her facial appearance, 
grey hair, saree, bindi, jewelry, age and overall identity."
```
✅ Specifies exact identity elements to preserve
❌ Avoids vague descriptions like "looks like her"

### 2. **Environmental Consistency**
```
"Use the provided living-room and house reference images to preserve the 
actual architecture, furniture, colors, layout and atmosphere."
```
✅ References actual patient assets
❌ Leaves room for artistic interpretation that breaks consistency

### 3. **Memory Context**
```
"Because this is a past memory, Anu may appear younger while still remaining 
recognizable as the same person."
```
✅ Acknowledges temporal context
❌ Demands identical appearance across decades

### 4. **Emotional Authenticity**
```
"The scene should feel like a gentle autobiographical memory, not a 
dramatic movie scene."
```
✅ Sets emotional tone
❌ Risks over-dramatization

### 5. **Natural Motion**
```
"Natural subtle movement: blinking, breathing, gentle head movement 
and natural hand movement."
```
✅ Specifies realistic physicality
❌ Risks unnatural or exaggerated motion

### 6. **Clear Exclusions**
```
"No text, no captions, no logos, no watermark."
```
✅ Prevents unwanted artifacts
❌ Allows model to add overlays

---

## 📦 Asset Requirements

### People
- `Patient_001_Lakshmi/people/patient_lakshmi` - Elderly Lakshmi (present-day)
- `Patient_001_Lakshmi/people/anu` - Adult Anu (both past younger & present)
- `Patient_001_Lakshmi/people/rahul` - Son (past memory)

### Homes
- `Patient_001_Lakshmi/home/house` - Exterior/overall house
- `Patient_001_Lakshmi/home/living_room` - Living room interior
- `Patient_001_Lakshmi/home/kitchen` - Kitchen for cooking scene

### Places
- `Patient_001_Lakshmi/places/family_temple` - Temple for spiritual memory
- `Patient_001_Lakshmi/places/family_garden` - Garden for peaceful memory
- `Patient_001_Lakshmi/places/family_trip` - Any available trip location

### Food
- `Patient_001_Lakshmi/food/chapathi` - Bread for cooking scene
- `Patient_001_Lakshmi/food/rice` - Grain for meal scene
- `Patient_001_Lakshmi/food/banana` - Fruit for meal scene

### Objects
- `Patient_001_Lakshmi/objects/old_radio` - Vintage radio for listening scene

---

## ✅ Checklist: Before Generating Videos

- [ ] All reference images exist in `Patient_001_Lakshmi/`
- [ ] GEMINI_API_KEY environment variable is set
- [ ] Google Veo 3.1 access is enabled in Gemini API console
- [ ] Output directory exists: `backend/generated_videos/lakshmi_anu_001/videos/`
- [ ] All 11 JSON files are present in this directory
- [ ] Read INDEX.json to verify scene order
- [ ] Understand temporal shift: past (younger Anu) → present (adult Anu)
- [ ] Have API quota available for 11 video generations (~10-15 minutes wall time)

---

## 🎯 Therapeutic Outcomes

### Memory Recognition
- Scenes 1-8 establish visual familiarity
- Patient recognizes home, familiar faces, activities
- Emotional anchors strengthen recognition pathways

### Temporal Orientation
- Scene 9 bridges past/present
- Patient understands adult Anu is present-day person
- Reduces confusion from younger appearance in memories

### Emotional Reconnection
- Scenes 10-11 enable real-time recognition
- Mother-daughter interaction reaffirms relationship
- Physical contact (hug) provides emotional validation

### Activity & Engagement
- 11 scenes = ~2 minutes total viewing
- Digestible for attention span limitations
- Can be repeated, paused, or segmented

---

## 📝 Documentation

- **INDEX.json** - Complete scene metadata and asset requirements
- **[filename].json** - Individual scene prompt and configuration
- **VIDEO_GENERATION_GUIDE.md** - Technical guide for API integration
- **QUICK_REFERENCE.md** - One-page prompt summary

---

## 🔗 Integration Points

### Frontend
Frontend reads from `backend/generated_videos/lakshmi_anu_001/metadata/frontend_config.json` to map:
- Scene ID → Video file
- Scene → Therapeutic questions
- User response → Next scene

### Backend
Backend reads INDEX.json and individual scene files to:
- Batch-generate all 11 videos
- Track generation progress
- Cache video URLs
- Store scene metadata

### Therapist Dashboard
Displays:
- Video generation status
- Scene content summaries
- Patient engagement metrics
- Memory recognition tracking

---

## 🚀 Next Steps

1. **Verify Assets** - Confirm all reference images exist
2. **Test Single Scene** - Generate one video with Veo to validate prompt quality
3. **Batch Generate** - Run full 11-scene generation
4. **Validate Output** - Check facial consistency, environmental accuracy
5. **Frontend Integration** - Connect videos to interactive questions
6. **Clinical Trial** - Test with Lakshmi and track therapeutic outcomes

---

**Created:** 2026-09-03  
**System:** Lakshmi-Anu Memory Therapy Prototype  
**API:** Google Veo 3.1 via Gemini  
**Patient:** Patient_001_Lakshmi  
**Status:** ✅ Ready for video generation
