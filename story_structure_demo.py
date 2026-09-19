"""
Story Structure Demo - Visualize the complete Lakshmi-Anu story structure.

This script demonstrates the story generation system without requiring
video generation API calls. Useful for validating story structure and
testing frontend integration.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from story_scene_generator import generate_lakshmi_anu_scenes
from story_scene_schema import StoryScene


def print_story_structure(scenes: List[StoryScene]) -> None:
    """Print detailed story structure."""
    print("\n" + "=" * 100)
    print(" " * 30 + "LAKSHMI-ANU STORY STRUCTURE")
    print("=" * 100)
    
    # Group by period
    periods = {}
    for scene in scenes:
        period = scene.metadata.period.value
        if period not in periods:
            periods[period] = []
        periods[period].append(scene)
    
    for period_name in ["past", "transition", "present"]:
        period_scenes = periods.get(period_name, [])
        if not period_scenes:
            continue
        
        period_label = {
            "past": "PAST MEMORIES",
            "transition": "TRANSITION",
            "present": "PRESENT DAY",
        }.get(period_name)
        
        print(f"\n{'─' * 100}")
        print(f" {period_label}")
        print(f"{'─' * 100}")
        
        for scene in sorted(period_scenes, key=lambda s: s.metadata.sequence_number):
            print_scene_details(scene)


def print_scene_details(scene: StoryScene) -> None:
    """Print detailed information about a scene."""
    seq = scene.metadata.sequence_number
    title = scene.metadata.title
    scene_id = scene.metadata.scene_id
    
    print(f"\n  [{seq}] {title}")
    print(f"      Scene ID: {scene_id}")
    print(f"      Duration: {scene.metadata.duration_seconds}s")
    
    # Characters
    if scene.characters:
        char_names = ", ".join([c.name for c in scene.characters])
        print(f"      Characters: {char_names}")
        for char in scene.characters:
            refs = [r.asset_path.split("/")[-1] for r in char.reference_images]
            print(f"        • {char.name} ({', '.join(refs)})")
            if char.age_note:
                print(f"          Age note: {char.age_note}")
            if char.emotional_state:
                print(f"          State: {char.emotional_state}")
    
    # Environment
    if scene.environment:
        env_name = scene.environment.asset_path.split("/")[-1] if "/" in scene.environment.asset_path else scene.environment.name
        print(f"      Environment: {env_name}")
    
    # Objects
    if scene.objects:
        obj_names = ", ".join([o.name for o in scene.objects])
        print(f"      Objects: {obj_names}")
    
    # Story context
    if scene.story_context:
        print(f"      Context: {scene.story_context}")


def export_story_json(scenes: List[StoryScene], output_file: str) -> None:
    """Export complete story structure as JSON."""
    story_data = {
        "story_id": "lakshmi_anu_story_001",
        "title": "A Visit From Anu",
        "description": "11-scene narrative memory reconstruction",
        "total_scenes": len(scenes),
        "periods": {
            "past": [],
            "transition": [],
            "present": [],
        },
        "scenes": {}
    }
    
    for scene in scenes:
        period = scene.metadata.period.value
        story_data["periods"][period].append(scene.metadata.scene_id)
        
        story_data["scenes"][scene.metadata.scene_id] = {
            "sequence": scene.metadata.sequence_number,
            "title": scene.metadata.title,
            "period": period,
            "duration_seconds": scene.metadata.duration_seconds,
            "characters": [
                {
                    "name": c.name,
                    "character_id": c.character_id,
                    "reference_images": [r.asset_path for r in c.reference_images],
                    "age_note": c.age_note,
                    "emotional_state": c.emotional_state,
                }
                for c in scene.characters
            ],
            "environment": {
                "name": scene.environment.name,
                "asset_path": scene.environment.asset_path,
            } if scene.environment else None,
            "objects": [
                {"name": o.name, "asset_path": o.asset_path}
                for o in scene.objects
            ],
            "story_context": scene.story_context,
            "prompt_length": len(scene.video_prompt),
        }
    
    with open(output_file, 'w') as f:
        json.dump(story_data, f, indent=2)
    
    print(f"✓ Story structure exported to: {output_file}")


def create_frontend_config(scenes: List[StoryScene]) -> Dict[str, Any]:
    """Create configuration for frontend integration."""
    config = {
        "storyId": "lakshmi_anu_story_001",
        "patientId": "Patient_001_Lakshmi",
        "storyTitle": "A Visit From Anu",
        "videoBasePath": "/videos/lakshmi_anu_001/",
        "scenes": []
    }
    
    for scene in scenes:
        config["scenes"].append({
            "sceneId": scene.metadata.scene_id,
            "sequence": scene.metadata.sequence_number,
            "title": scene.metadata.title,
            "videoPath": f"{scene.metadata.scene_id}.mp4",
            "duration": scene.metadata.duration_seconds,
            "period": scene.metadata.period.value,
            "characters": [c.character_id for c in scene.characters],
        })
    
    return config


def create_interactive_timeline(scenes: List[StoryScene]) -> str:
    """Create ASCII timeline visualization."""
    timeline = "\n" + "=" * 100 + "\n"
    timeline += " " * 35 + "STORY TIMELINE\n"
    timeline += "=" * 100 + "\n\n"
    
    # Past memories
    timeline += "PAST MEMORIES (Patient's Flashbacks)\n"
    timeline += "│\n"
    for scene in [s for s in scenes if s.metadata.period.value == "past"]:
        timeline += f"├─ [{scene.metadata.sequence_number}] {scene.metadata.title}\n"
    
    # Transition
    timeline += "│\n"
    timeline += "└─ [9] ✨ MEMORIES FADE INTO PRESENT\n"
    
    # Present
    timeline += "        │\n"
    timeline += "        └─ [10] Anu Enters the Home\n"
    timeline += "           │\n"
    timeline += "           └─ [11] ❤️  REUNION - Mother and Daughter Embrace\n"
    
    timeline += "\n" + "=" * 100 + "\n"
    
    return timeline


def main():
    """Run story structure demo."""
    print("\n" + "█" * 100)
    print("█" + " " * 98 + "█")
    print("█" + " " * 25 + "LAKSHMI-ANU STORY STRUCTURE DEMONSTRATION" + " " * 33 + "█")
    print("█" + " " * 98 + "█")
    print("█" * 100)
    
    # Generate scenes
    print("\n[1/5] Generating story scenes...")
    scenes = generate_lakshmi_anu_scenes()
    print(f"✓ Generated {len(scenes)} scenes")
    
    # Print structure
    print("\n[2/5] Displaying story structure...")
    print_story_structure(scenes)
    
    # Export JSON
    print("\n[3/5] Exporting story structure...")
    story_json = "backend/generated_videos/lakshmi_anu_001/metadata/story_structure.json"
    Path(story_json).parent.mkdir(parents=True, exist_ok=True)
    export_story_json(scenes, story_json)
    
    # Create timeline
    print("\n[4/5] Creating interactive timeline...")
    timeline = create_interactive_timeline(scenes)
    print(timeline)
    
    # Export frontend config
    print("\n[5/5] Creating frontend configuration...")
    frontend_config = create_frontend_config(scenes)
    config_file = "backend/generated_videos/lakshmi_anu_001/metadata/frontend_config.json"
    with open(config_file, 'w') as f:
        json.dump(frontend_config, f, indent=2)
    print(f"✓ Frontend config saved to: {config_file}")
    
    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    
    periods = {
        "past": len([s for s in scenes if s.metadata.period.value == "past"]),
        "transition": len([s for s in scenes if s.metadata.period.value == "transition"]),
        "present": len([s for s in scenes if s.metadata.period.value == "present"]),
    }
    
    print(f"\nScene Breakdown:")
    print(f"  Past Memories: {periods['past']} scenes (building memory associations)")
    print(f"  Transition: {periods['transition']} scene (bridging to present)")
    print(f"  Present Day: {periods['present']} scenes (reunion with Anu)")
    
    print(f"\nCharacter Appearances:")
    all_chars = {}
    for scene in scenes:
        for char in scene.characters:
            if char.character_id not in all_chars:
                all_chars[char.character_id] = {"name": char.name, "count": 0}
            all_chars[char.character_id]["count"] += 1
    
    for char_id, char_info in sorted(all_chars.items()):
        print(f"  {char_info['name']}: {char_info['count']} scenes")
    
    print(f"\nTherapeutic Flow:")
    print(f"  1. Establish familiar home environment (Scene 1)")
    print(f"  2. Introduce memory of daughter (Scene 2)")
    print(f"  3-8. Build memory associations through activities and relationships")
    print(f"  9. Transition from past to present")
    print(f"  10-11. Present-day reunion and emotional connection")
    
    print(f"\nNext Steps:")
    print(f"  1. Review generated scene definitions in:")
    print(f"     backend/generated_videos/lakshmi_anu_001/scenes/")
    print(f"  2. Generate videos using:")
    print(f"     python lakshmi_anu_story_generator.py --generate-videos")
    print(f"  3. Integrate with frontend using config from:")
    print(f"     {config_file}")
    
    print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    main()
