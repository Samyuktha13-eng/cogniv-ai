# 🎬 QUICK START - Video Prompts

## 📁 Location
```
c:\Users\DELL\Downloads\Cognitiveai\backend\video_prompts\
```

## 📊 What's Inside (14 files)

### 11 Scene JSON Files
```
✅ PAST MEMORIES (8 scenes)
   memory_01_home.json              (8 sec)
   memory_02_anu.json               (8 sec)
   memory_03_chapathi.json          (10 sec)
   memory_04_temple.json            (10 sec)
   memory_05_trip.json              (10 sec)
   memory_06_family_meal.json       (10 sec)
   memory_07_garden.json            (10 sec)
   memory_08_radio.json             (10 sec)

✅ TRANSITION (1 scene)
   present_01_transition.json       (8 sec)

✅ PRESENT-DAY (2 scenes)
   present_02_anu_enters.json       (12 sec)
   present_03_reunion_hug.json      (12 sec)
```

### 3 Documentation Files
```
📄 INDEX.json              - Master index of all scenes
📄 README.md               - Complete technical guide
📄 COMPLETE_SUMMARY.md     - Executive summary
```

## 🎯 Quick Usage

### Load a Scene
```python
import json
scene = json.load(open("backend/video_prompts/memory_03_chapathi.json"))
print(scene["video_prompt"])  # Get Veo API prompt
print(scene["reference_images"])  # Get asset paths
```

### Generate Video
```python
# Use Veo 3.1 API with:
# - scene["video_prompt"]
# - scene["reference_images"]

# Output to:
# backend/generated_videos/lakshmi_anu_001/videos/[scene_id].mp4
```

### Batch Generation
```bash
python lakshmi_anu_story_generator.py --generate-videos
```

## 📋 File Structure

Each scene JSON:
```json
{
  "scene_id": "memory_03_chapathi",
  "sequence_number": 3,
  "title": "Anu and Lakshmi Making Chapathi",
  "period": "past",
  "duration_seconds": 10,
  "characters": ["people/anu", "people/patient_lakshmi"],
  "environment": "home/kitchen",
  "reference_images": ["people/anu", "people/patient_lakshmi", "home/kitchen", "food/chapathi"],
  "objects": ["food/chapathi"],
  "story": "A warm nostalgic memory of making chapathi together",
  "video_prompt": "[Complete 400-500 word Veo prompt with identity preservation instructions]"
}
```

## 🔑 Key Features

✅ **Facial Identity Preserved** - Exact instructions for facial preservation  
✅ **Environmental Consistency** - References real patient assets  
✅ **Memory → Present Timeline** - Clear temporal progression  
✅ **Therapeutic Design** - Emotional arc optimized for dementia memory therapy  
✅ **Natural Motion** - Realistic physicality specified  
✅ **Ready for API** - Production-ready prompts for Google Veo 3.1  

## 📊 Timeline

```
PAST (72s) → TRANSITION (8s) → PRESENT (24s)
Total: 108 seconds (1m 48s)
```

## 🚀 Next Steps

1. Verify reference assets exist:
   ```powershell
   Test-Path "Patient_001_Lakshmi/people/patient_lakshmi"
   ```

2. Set API key:
   ```powershell
   $env:GEMINI_API_KEY = "your-key"
   ```

3. Test single scene:
   ```bash
   python generate_single_video.py --scene memory_01_home
   ```

4. Generate all 11 videos:
   ```bash
   python lakshmi_anu_story_generator.py --generate-videos
   ```

5. Check output:
   ```powershell
   Get-ChildItem "backend/generated_videos/lakshmi_anu_001/videos"
   # Should show 11 .mp4 files
   ```

## 📖 Documentation

- **README.md** - Full technical guide with examples
- **INDEX.json** - Master scene index and asset requirements
- **COMPLETE_SUMMARY.md** - Detailed overview with all details

## ⏱️ Estimated Time

- Single video: 1-2 minutes
- All 11 videos: 10-15 minutes
- Depends on Veo API queue

## 📦 Output Location

```
backend/generated_videos/lakshmi_anu_001/
├── videos/                 ← 11 MP4 files (after generation)
├── scenes/                 ← 11 JSON scene definitions
├── metadata/               ← Manifests & config
└── integration/            ← Frontend templates
```

## ✅ Checklist

- [ ] Reference images exist in Patient_001_Lakshmi/
- [ ] GEMINI_API_KEY is set
- [ ] Google Veo 3.1 access is enabled
- [ ] All 14 files present in backend/video_prompts/
- [ ] INDEX.json readable and complete
- [ ] Output directory exists
- [ ] API quota available

## 💡 Remember

Each prompt includes:
- ✅ Facial identity preservation (won't change faces)
- ✅ Environmental reference (uses actual patient home)
- ✅ Temporal context (past younger, present adult)
- ✅ Natural motion (realistic physicality)
- ✅ Therapeutic focus (memory/emotion target)
- ✅ Clear exclusions (no text/logos/watermarks)

---

**Status:** ✅ READY FOR VIDEO GENERATION  
**Created:** 2026-09-03  
**System:** Lakshmi-Anu Memory Therapy Prototype
