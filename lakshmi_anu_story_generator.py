"""
Lakshmi-Anu Story Generator - Complete pipeline for generating the 11-scene narrative.

This script:
1. Generates all 11 scene definitions from patient memories
2. Saves scene JSON for reference and validation
3. Generates video files using Veo API
4. Creates a story manifest for frontend integration
5. Organizes videos in structured output directory
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from story_scene_schema import StoryScene
from story_scene_generator import generate_lakshmi_anu_scenes
from backend.video.video_scene_manager import VideoSceneManager, VideoGenerationResult


class LakshmiAnuStoryGenerator:
    """Complete pipeline for generating the Lakshmi-Anu narrative."""
    
    def __init__(self, 
                 output_base: str = "backend/generated_videos/lakshmi_anu_001",
                 patient_id: str = "Patient_001_Lakshmi"):
        """
        Initialize the story generator.
        
        Args:
            output_base: Base output directory for all artifacts
            patient_id: Patient identifier
        """
        self.output_base = Path(output_base)
        self.patient_id = patient_id
        
        # Create subdirectories
        self.videos_dir = self.output_base / "videos"
        self.scenes_dir = self.output_base / "scenes"
        self.metadata_dir = self.output_base / "metadata"
        
        for d in [self.videos_dir, self.scenes_dir, self.metadata_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Initialize manager
        self.manager = VideoSceneManager(
            output_dir=str(self.videos_dir),
            cache_dir=str(self.metadata_dir),
        )
    
    def generate_complete_story(self, generate_videos: bool = False) -> Dict[str, Any]:
        """
        Generate complete story artifacts.
        
        Args:
            generate_videos: Whether to generate actual video files (requires API)
        
        Returns:
            Story generation summary
        """
        print("=" * 70)
        print("LAKSHMI-ANU STORY GENERATOR")
        print("=" * 70)
        
        # Step 1: Generate scene definitions
        print("\n[STEP 1] Generating scene definitions...")
        scenes = generate_lakshmi_anu_scenes()
        print(f"✓ Generated {len(scenes)} scenes")
        
        # Step 2: Save scene JSON files
        print("\n[STEP 2] Saving scene definitions as JSON...")
        scene_files = {}
        for scene in scenes:
            scene_path = self.manager.save_scene_json(scene, str(self.scenes_dir))
            scene_files[scene.metadata.scene_id] = str(scene_path)
            print(f"  ✓ {scene.metadata.scene_id}")
        
        # Step 3: Generate videos (if enabled)
        video_results = {}
        if generate_videos:
            print("\n[STEP 3] Generating videos via Veo API...")
            print("         (This may take 10-15 minutes)")
            video_results = self.manager.generate_story_videos(scenes)
            
            for scene_id, result in video_results.items():
                if result.success:
                    print(f"  ✓ {scene_id}")
                else:
                    print(f"  ✗ {scene_id}: {result.error}")
        else:
            print("\n[STEP 3] Video generation skipped (generate_videos=False)")
            print("         Run with generate_videos=True to create videos")
        
        # Step 4: Create frontend-ready manifest
        print("\n[STEP 4] Creating story manifest...")
        manifest = self._create_story_manifest(scenes, video_results)
        manifest_file = self.metadata_dir / "story_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"  ✓ Manifest saved to {manifest_file}")
        
        # Step 5: Create scene index
        print("\n[STEP 5] Creating scene index...")
        scene_index = self._create_scene_index(scenes)
        index_file = self.metadata_dir / "scene_index.json"
        with open(index_file, 'w') as f:
            json.dump(scene_index, f, indent=2)
        print(f"  ✓ Index saved to {index_file}")
        
        # Step 6: Create video catalog
        print("\n[STEP 6] Creating video catalog...")
        video_catalog = self._create_video_catalog(scenes, video_results)
        catalog_file = self.metadata_dir / "video_catalog.json"
        with open(catalog_file, 'w') as f:
            json.dump(video_catalog, f, indent=2)
        print(f"  ✓ Catalog saved to {catalog_file}")
        
        # Step 7: Generate summary report
        print("\n[STEP 7] Generating summary report...")
        summary = self._generate_summary(scenes, video_results)
        summary_file = self.metadata_dir / "GENERATION_SUMMARY.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        print(f"  ✓ Summary saved to {summary_file}")
        
        # Final summary
        print("\n" + "=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nOutput Directory: {self.output_base}")
        print(f"  Videos: {self.videos_dir}")
        print(f"  Scenes: {self.scenes_dir}")
        print(f"  Metadata: {self.metadata_dir}")
        print(f"\nArtifacts Created:")
        print(f"  - {len(scenes)} scene definition JSON files")
        print(f"  - story_manifest.json (frontend integration)")
        print(f"  - scene_index.json (scene navigation)")
        print(f"  - video_catalog.json (video metadata)")
        print(f"  - GENERATION_SUMMARY.txt (this report)")
        
        if generate_videos:
            successful = sum(1 for r in video_results.values() if r.success)
            print(f"\nVideo Generation Results:")
            print(f"  - {successful}/{len(video_results)} videos generated successfully")
            if successful < len(video_results):
                print(f"  - {len(video_results) - successful} videos failed")
        
        return {
            "success": True,
            "scenes_count": len(scenes),
            "scene_definitions": scene_files,
            "manifest": manifest,
            "video_results": video_results,
            "output_base": str(self.output_base),
        }
    
    def _create_story_manifest(self, 
                               scenes: List[StoryScene],
                               video_results: Dict[str, VideoGenerationResult]) -> Dict[str, Any]:
        """Create frontend-ready story manifest."""
        return {
            "story_id": "lakshmi_anu_story_001",
            "patient_id": self.patient_id,
            "title": "A Visit From Anu - Complete Story",
            "description": "11-scene narrative memory reconstruction with video sequences",
            "total_scenes": len(scenes),
            "scenes": [
                {
                    "scene_id": scene.metadata.scene_id,
                    "sequence": scene.metadata.sequence_number,
                    "title": scene.metadata.title,
                    "period": scene.metadata.period.value,
                    "characters": [c.character_id for c in scene.characters],
                    "video_path": (
                        str(video_results[scene.metadata.scene_id].video_path)
                        if scene.metadata.scene_id in video_results 
                        and video_results[scene.metadata.scene_id].success
                        else None
                    ),
                    "story_context": scene.story_context,
                    "duration_seconds": scene.metadata.duration_seconds,
                }
                for scene in scenes
            ],
        }
    
    def _create_scene_index(self, scenes: List[StoryScene]) -> Dict[str, Any]:
        """Create scene navigation index."""
        return {
            "story_id": "lakshmi_anu_story_001",
            "scenes": {
                scene.metadata.scene_id: {
                    "sequence": scene.metadata.sequence_number,
                    "title": scene.metadata.title,
                    "period": scene.metadata.period.value,
                    "characters": [c.character_id for c in scene.characters],
                    "next_scene_id": (
                        scenes[scenes.index(scene) + 1].metadata.scene_id
                        if scenes.index(scene) + 1 < len(scenes)
                        else None
                    ),
                    "prev_scene_id": (
                        scenes[scenes.index(scene) - 1].metadata.scene_id
                        if scenes.index(scene) - 1 >= 0
                        else None
                    ),
                }
                for scene in scenes
            },
        }
    
    def _create_video_catalog(self, 
                              scenes: List[StoryScene],
                              video_results: Dict[str, VideoGenerationResult]) -> Dict[str, Any]:
        """Create video metadata catalog."""
        catalog = {
            "story_id": "lakshmi_anu_story_001",
            "total_videos": len(scenes),
            "videos": [],
        }
        
        for scene in scenes:
            result = video_results.get(scene.metadata.scene_id)
            catalog["videos"].append({
                "scene_id": scene.metadata.scene_id,
                "title": scene.metadata.title,
                "sequence": scene.metadata.sequence_number,
                "period": scene.metadata.period.value,
                "duration_seconds": scene.metadata.duration_seconds,
                "status": "generated" if result and result.success else "pending",
                "video_path": str(result.video_path) if result and result.success else None,
                "generated_at": result.generated_at if result and result.success else None,
                "reference_images": [
                    {"name": c.name, "count": len(c.reference_images)}
                    for c in scene.characters
                ],
            })
        
        return catalog
    
    def _generate_summary(self, 
                         scenes: List[StoryScene],
                         video_results: Dict[str, VideoGenerationResult]) -> str:
        """Generate human-readable summary report."""
        lines = [
            "=" * 80,
            "LAKSHMI-ANU STORY GENERATION SUMMARY",
            "=" * 80,
            "",
            f"Patient ID: {self.patient_id}",
            f"Story ID: lakshmi_anu_story_001",
            f"Generated Scenes: {len(scenes)}",
            "",
            "SCENE BREAKDOWN BY PERIOD:",
            "-" * 80,
        ]
        
        # Group by period
        from story_scene_schema import ScenePeriod
        for period in [ScenePeriod.PAST, ScenePeriod.TRANSITION, ScenePeriod.PRESENT]:
            period_scenes = [s for s in scenes if s.metadata.period == period]
            if period_scenes:
                lines.append(f"\n{period.value.upper()} ({len(period_scenes)} scenes):")
                for scene in sorted(period_scenes, key=lambda s: s.metadata.sequence_number):
                    chars = ", ".join([c.name for c in scene.characters])
                    lines.append(f"  [{scene.metadata.sequence_number}] {scene.metadata.title}")
                    lines.append(f"      Characters: {chars}")
                    lines.append(f"      Scene ID: {scene.metadata.scene_id}")
        
        lines.extend([
            "",
            "=" * 80,
            "VIDEO GENERATION STATUS:",
            "-" * 80,
        ])
        
        if video_results:
            successful = sum(1 for r in video_results.values() if r.success)
            failed = len(video_results) - successful
            lines.append(f"Total Videos Generated: {successful}/{len(video_results)}")
            if failed > 0:
                lines.append(f"Failed Videos: {failed}")
                for scene_id, result in video_results.items():
                    if not result.success:
                        lines.append(f"  - {scene_id}: {result.error}")
        else:
            lines.append("Video generation not yet performed")
        
        lines.extend([
            "",
            "=" * 80,
            "STORY FLOW:",
            "-" * 80,
            "",
            "1. PAST MEMORIES (Scenes 1-8):",
            "   - Scene 1: Lakshmi at Home (establishes familiar environment)",
            "   - Scene 2: Remembers Anu (memory visualization begins)",
            "   - Scenes 3-8: Series of shared memories (cooking, temple, trips, meals, garden, radio)",
            "",
            "2. TRANSITION (Scene 9):",
            "   - Memories fade into present day",
            "   - Anu approaching the house",
            "",
            "3. PRESENT DAY (Scenes 10-11):",
            "   - Scene 10: Anu enters the home",
            "   - Scene 11: Emotional reunion - final mother-daughter embrace",
            "",
            "THERAPEUTIC GOALS:",
            "- Establish visual familiarity with daughter (Anu)",
            "- Reinforce positive memories through multiple sensory contexts",
            "- Create emotional connection and recognition",
            "- Bridge past memories to present-day reunion",
            "- Support person recognition therapy for dementia care",
            "",
            "=" * 80,
        ])
        
        return "\n".join(lines)


def main():
    """Run the complete story generation pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Lakshmi-Anu story videos")
    parser.add_argument(
        "--generate-videos",
        action="store_true",
        help="Generate actual video files (requires Gemini API key)"
    )
    parser.add_argument(
        "--output",
        default="backend/generated_videos/lakshmi_anu_001",
        help="Output directory for generated files"
    )
    
    args = parser.parse_args()
    
    generator = LakshmiAnuStoryGenerator(output_base=args.output)
    result = generator.generate_complete_story(generate_videos=args.generate_videos)
    
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
