# 📹 Lakshmi-Anu Video Prompt Library - Complete Summary

## ✅ All 11 Scenes Created

### 📍 Directory Location
```
c:\Users\DELL\Downloads\Cognitiveai\backend\video_prompts\
```

### 📊 Files Created (13 total)

```
✅ memory_01_home.json              (8 sec)  - Lakshmi at home remembering
✅ memory_02_anu.json               (8 sec)  - Lakshmi remembers Anu
✅ memory_03_chapathi.json          (10 sec) - Making chapathi together
✅ memory_04_temple.json            (10 sec) - Temple visit memory
✅ memory_05_trip.json              (10 sec) - Family trip with Anu & Rahul
✅ memory_06_family_meal.json       (10 sec) - Family meal together
✅ memory_07_garden.json            (10 sec) - Garden time together
✅ memory_08_radio.json             (10 sec) - Old radio listening
✅ present_01_transition.json       (8 sec)  - Memory → Present bridge
✅ present_02_anu_enters.json       (12 sec) - Anu enters home (present day)
✅ present_03_reunion_hug.json      (12 sec) - Final mother-daughter hug ❤️
✅ INDEX.json                              - Master index of all scenes
✅ README.md                               - Complete documentation
```

**Total Video Duration:** 108 seconds (~1m 48s)

---

## 🎬 Scene Timeline

```
PAST MEMORIES (8 scenes, 72 seconds)
┌─────────────────────────────────────────────────────────────┐
│ Scene 1: Lakshmi at Home              [8s]  - Alone, remembering
│ Scene 2: Lakshmi Remembers Anu        [8s]  - Sees Anu in memory
│ Scene 3: Making Chapathi              [10s] - Anu cooks, Lakshmi helps
│ Scene 4: Temple Visit                 [10s] - Walk to temple together
│ Scene 5: Family Trip                  [10s] - With Anu & Rahul
│ Scene 6: Family Meal                  [10s] - All eating together
│ Scene 7: Garden Time                  [10s] - Walk in garden
│ Scene 8: Old Radio                    [10s] - Listen to radio
└─────────────────────────────────────────────────────────────┘
                           ↓
TRANSITION (1 scene, 8 seconds)
┌─────────────────────────────────────────────────────────────┐
│ Scene 9: Memory → Present Bridge      [8s]  - Fade to present day
└─────────────────────────────────────────────────────────────┘
                           ↓
PRESENT-DAY REUNION (2 scenes, 24 seconds)
┌─────────────────────────────────────────────────────────────┐
│ Scene 10: Anu Enters Home             [12s] - Adult Anu arrives
│ Scene 11: Mother-Daughter Hug         [12s] - Final reunion ❤️
└─────────────────────────────────────────────────────────────┘

Total Story Arc: 1 minute 48 seconds
```

---

## 🎯 Therapeutic Purpose

| Scene | Therapy Focus | Memory Cue | Emotion |
|-------|---------------|-----------|---------|
| 1 | Safe environment | Familiar home | Contemplative |
| 2 | Daughter recognition | Anu's face | Recognition |
| 3 | Shared activity | Chapathi | Warmth |
| 4 | Spiritual memory | Temple | Reverence |
| 5 | Extended family | Group moment | Joy |
| 6 | Family bonding | Food/meal | Connection |
| 7 | Peaceful setting | Garden | Peace |
| 8 | Sensory memory | Radio/sound | Nostalgia |
| 9 | Time bridge | Home fade | Transition |
| 10 | Adult recognition | Present-day Anu | Anticipation |
| 11 | Emotional closure | Mother-daughter embrace | Love ❤️ |

---

## 📝 Each Scene Contains

Every `.json` file includes:

```json
{
  "scene_id": "unique_identifier",
  "sequence_number": 1-11,
  "title": "Human-readable title",
  "period": "past|transition|present",
  "duration_seconds": 8-12,
  "characters": ["who_appears"],
  "environment": "where_it_happens",
  "reference_images": ["all_asset_paths"],
  "objects": ["props_in_scene"],
  "story": "Brief narrative",
  "video_prompt": "[Complete 400-500 word Veo API prompt]"
}
```

---

## 🔑 Key Features of Prompts

### ✅ Facial Identity Preservation
Each prompt specifies exact preservation requirements:
- "preserve her facial appearance, grey hair, saree, bindi, jewelry, age"
- "recognizable facial characteristics and overall appearance"
- Prevents AI from changing faces or making unrecognizable versions

### ✅ Environmental Consistency
References actual patient assets:
- "Use the provided living-room reference to preserve actual architecture"
- "closely resemble the provided reference image"
- Ensures recognizable home environment

### ✅ Memory vs. Present Distinction
Clear temporal markers:
- Past scenes: "Anu may appear younger while remaining recognizable"
- Present scenes: "current facial appearance, age, hairstyle, clothing"
- Transition: "clearly feel different from earlier younger-memory scenes"

### ✅ Natural Motion
Specifies realistic physics:
- "natural alternating leg movement, natural arm movement"
- "blinking, breathing, gentle head movement"
- "physically natural: arms move around each other naturally"

### ✅ Therapeutic Tone
Sets emotional context:
- "gentle autobiographical memory, not dramatic"
- "communicate recognition and emotional familiarity"
- "warm, love, relief and emotional connection"

### ✅ Clarity & Exclusions
Prevents unintended artifacts:
- "No text, no captions, no logos, no watermark"
- "Do not invent a different house"
- "Do not add unrelated people"

---

## 🎬 Ready for Video Generation

### How to Use These Prompts

```python
# Load any scene
import json
scene = json.load(open("backend/video_prompts/memory_03_chapathi.json"))

# Access video prompt
veo_prompt = scene["video_prompt"]

# Collect reference images
refs = scene["reference_images"]
# e.g., ["people/anu", "people/patient_lakshmi", "home/kitchen", "food/chapathi"]

# Use with Veo 3.1 API
# response = veo_api.generate(prompt=veo_prompt, reference_images=refs)
```

### Batch Generation Script
```python
import json
from pathlib import Path

index = json.load(open("backend/video_prompts/INDEX.json"))

for scene_info in index["scenes"]:
    scene = json.load(open(f"backend/video_prompts/{scene_info['file']}"))
    # Generate video with scene["video_prompt"] + scene["reference_images"]
    # Save to backend/generated_videos/lakshmi_anu_001/videos/[scene_id].mp4
```

---

## 📊 INDEX.json Structure

Master index file includes:

```json
{
  "story_id": "lakshmi_anu_001",
  "total_scenes": 11,
  "periods": {
    "past": {"count": 8, "scenes": [...]},
    "transition": {"count": 1, "scenes": [...]},
    "present": {"count": 2, "scenes": [...]}
  },
  "scenes": [
    {
      "file": "memory_01_home.json",
      "scene_id": "memory_01_home",
      "sequence": 1,
      "title": "...",
      "therapeutic_focus": "..."
    },
    ...
  ],
  "asset_requirements": {
    "people": ["patient_lakshmi", "anu", "rahul"],
    "places": ["family_temple", "family_garden", "family_trip"],
    "home": ["house", "living_room", "kitchen"],
    "food": ["chapathi", "rice", "banana"],
    "objects": ["old_radio"]
  }
}
```

---

## 📦 Asset Paths

All prompts reference these patient assets:

### People
- `Patient_001_Lakshmi/people/patient_lakshmi`
- `Patient_001_Lakshmi/people/anu`
- `Patient_001_Lakshmi/people/rahul`

### Home
- `Patient_001_Lakshmi/home/house`
- `Patient_001_Lakshmi/home/living_room`
- `Patient_001_Lakshmi/home/kitchen`

### Places
- `Patient_001_Lakshmi/places/family_temple`
- `Patient_001_Lakshmi/places/family_garden`
- `Patient_001_Lakshmi/places/family_trip`

### Food
- `Patient_001_Lakshmi/food/chapathi`
- `Patient_001_Lakshmi/food/rice`
- `Patient_001_Lakshmi/food/banana`

### Objects
- `Patient_001_Lakshmi/objects/old_radio`

---

## 🚀 Next Steps

### 1. Verify Assets Exist
```powershell
# Check each reference image
Test-Path "Patient_001_Lakshmi/people/patient_lakshmi"
Test-Path "Patient_001_Lakshmi/people/anu"
# ... etc
```

### 2. Set Up API Key
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

### 3. Test Single Scene Generation
```bash
python generate_single_video.py --scene memory_01_home
```

### 4. Batch Generate All 11 Videos
```bash
python lakshmi_anu_story_generator.py --generate-videos
# Outputs: backend/generated_videos/lakshmi_anu_001/videos/*.mp4
```

### 5. Verify Videos Created
```powershell
Get-ChildItem "backend/generated_videos/lakshmi_anu_001/videos" -Filter "*.mp4"
# Should see 11 files:
# - memory_01_home.mp4
# - memory_02_anu.mp4
# - ... through present_03_reunion_hug.mp4
```

### 6. Integrate with Frontend
- Map scene IDs to video paths
- Create interactive timeline
- Add therapeutic questions between scenes
- Track patient responses

---

## 📋 File Organization

```
Cognitiveai/
└── backend/
    └── video_prompts/                    ← YOU ARE HERE
        ├── INDEX.json                    ← Master index
        ├── README.md                     ← Documentation
        ├── memory_01_home.json
        ├── memory_02_anu.json
        ├── memory_03_chapathi.json
        ├── memory_04_temple.json
        ├── memory_05_trip.json
        ├── memory_06_family_meal.json
        ├── memory_07_garden.json
        ├── memory_08_radio.json
        ├── present_01_transition.json
        ├── present_02_anu_enters.json
        └── present_03_reunion_hug.json
```

---

## 🎁 What You Have

✅ **11 Detailed Video Prompts** - Each 400-500 words, optimized for Veo 3.1  
✅ **Scene-Based Organization** - Clear file naming: `[period]_[sequence]_[title].json`  
✅ **Master Index** - Single reference for all scenes and metadata  
✅ **Complete Documentation** - README with usage examples  
✅ **Therapeutic Architecture** - 8 memories + 1 transition + 2 present-day scenes  
✅ **Asset Mapping** - All reference images specified  
✅ **Identity Preservation** - Prompts enforce facial/environmental consistency  

---

## 💡 Design Highlights

### Narrative Arc
- **Build** (Past): Establish memories with younger Anu/Rahul
- **Bridge** (Transition): Move from past to present  
- **Reconnect** (Present): Adult Anu returns, emotional reunion

### Memory Cues
Each scene includes distinct visual/sensory anchors:
- Chapathi (food memory)
- Temple (spiritual memory)  
- Radio (sound memory)
- Garden (sensory memory)

### Emotional Progression
- Contemplative → Joyful → Peaceful → Nostalgic → Hopeful → Loving

### Temporal Shift
- Clear visual difference between past (younger) and present (adult)
- Helps patient understand "this is NOW" for present-day recognition

---

## ✨ Ready to Generate Videos

All prompts are **production-ready** for Google Veo 3.1 API.

- Prompts follow best practices for video generation
- Reference images are specified exactly
- Identity preservation is explicit
- Motion and emotion are well-defined
- Artifacts (text, logos) are excluded

**Estimated Generation Time:** 10-15 minutes for all 11 videos  
**API Cost:** Depends on Veo 3.1 pricing  
**Output Size:** ~2-3 GB for 11 MP4 files (depends on resolution)

---

**Created:** September 3, 2026  
**System:** Lakshmi-Anu Memory Therapy Prototype  
**Status:** ✅ COMPLETE - Ready for Video Generation  
**Next:** Run video generation pipeline
