"""
Video Scene Manager - Generate and manage videos for narrative scenes.

Orchestrates the creation of video files from scene definitions,
caches results, and tracks generation progress.
"""

import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from story_scene_schema import StoryScene
from backend.video.veo_generator import VeoVideoGenerator


@dataclass
class VideoGenerationResult:
    """Result of a video generation attempt."""
    scene_id: str
    success: bool
    video_path: Optional[Path] = None
    error: Optional[str] = None
    generated_at: Optional[str] = None


class VideoSceneManager:
    """
    Manage video generation for narrative story scenes.
    
    Handles:
    - Converting scene definitions to video prompts
    - Generating videos via Veo API
    - Caching video files
    - Tracking generation progress
    """
    
    def __init__(self, 
                 output_dir: str = "backend/generated_videos",
                 cache_dir: str = "backend/generated_videos/cache"):
        """
        Initialize the video scene manager.
        
        Args:
            output_dir: Directory for generated video files
            cache_dir: Directory for metadata cache
        """
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize video generator
        self.video_gen = VeoVideoGenerator()
        
        # Load existing cache
        self.cache_file = self.cache_dir / "scenes_manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load scene generation manifest from cache."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {"scenes": {}, "metadata": {}}
    
    def _save_manifest(self) -> None:
        """Save scene generation manifest to cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def generate_scene_video(self, scene: StoryScene) -> VideoGenerationResult:
        """
        Generate or retrieve cached video for a scene.
        
        Args:
            scene: StoryScene object with video prompt and references
        
        Returns:
            VideoGenerationResult with path and status
        """
        scene_id = scene.metadata.scene_id
        
        # Check if already generated
        cached = self.manifest["scenes"].get(scene_id)
        if cached and Path(cached["path"]).exists():
            return VideoGenerationResult(
                scene_id=scene_id,
                success=True,
                video_path=Path(cached["path"]),
            )
        
        try:
            # Build reference image paths
            reference_images = []
            
            # Add character references
            for char in scene.characters:
                for ref in char.reference_images:
                    if Path(ref.asset_path).exists():
                        reference_images.append(ref.asset_path)
            
            # Add environment reference
            if scene.environment and Path(scene.environment.asset_path).exists():
                reference_images.append(scene.environment.asset_path)
            
            # Add object references
            for obj in scene.objects:
                if Path(obj.asset_path).exists():
                    reference_images.append(obj.asset_path)
            
            # Generate output filename
            output_filename = f"{scene_id}.mp4"
            output_path = self.output_dir / output_filename
            
            # Generate video using Veo API
            print(f"Generating video for {scene_id}: {scene.metadata.title}")
            video_path = self.video_gen.ensure_video(
                action_name=scene_id,
                prompt=scene.video_prompt,
                reference_images=reference_images,
            )
            
            # Track in manifest
            self.manifest["scenes"][scene_id] = {
                "title": scene.metadata.title,
                "path": str(video_path),
                "sequence": scene.metadata.sequence_number,
                "period": scene.metadata.period.value,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self._save_manifest()
            
            return VideoGenerationResult(
                scene_id=scene_id,
                success=True,
                video_path=video_path,
                generated_at=self.manifest["scenes"][scene_id]["generated_at"],
            )
        
        except Exception as e:
            error_msg = f"Failed to generate video for {scene_id}: {str(e)}"
            print(f"ERROR: {error_msg}")
            return VideoGenerationResult(
                scene_id=scene_id,
                success=False,
                error=error_msg,
            )
    
    def generate_story_videos(self, scenes: List[StoryScene]) -> Dict[str, VideoGenerationResult]:
        """
        Generate videos for a complete story sequence.
        
        Args:
            scenes: List of StoryScene objects
        
        Returns:
            Dictionary mapping scene_id to VideoGenerationResult
        """
        results = {}
        
        for i, scene in enumerate(scenes, 1):
            print(f"\n[{i}/{len(scenes)}] Processing {scene.metadata.title}")
            result = self.generate_scene_video(scene)
            results[scene.metadata.scene_id] = result
            
            # Add small delay between requests to respect API rate limits
            if i < len(scenes):
                time.sleep(2)
        
        return results
    
    def save_scene_json(self, scene: StoryScene, output_dir: Optional[str] = None) -> Path:
        """
        Save scene definition to JSON file.
        
        Args:
            scene: StoryScene to save
            output_dir: Directory to save to (uses cache_dir if not specified)
        
        Returns:
            Path to saved JSON file
        """
        save_dir = Path(output_dir) if output_dir else self.cache_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = save_dir / f"{scene.metadata.scene_id}.json"
        scene.save(str(filepath))
        return filepath
    
    def export_story_manifest(self, 
                              story_id: str,
                              output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Export complete story manifest with all scene info.
        
        Args:
            story_id: Story identifier
            output_file: Optional file to save manifest to
        
        Returns:
            Story manifest dictionary
        """
        manifest = {
            "story_id": story_id,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scenes": [],
        }
        
        # Sort by sequence number
        sorted_scenes = sorted(
            self.manifest["scenes"].items(),
            key=lambda x: x[1].get("sequence", 0)
        )
        
        for scene_id, scene_info in sorted_scenes:
            manifest["scenes"].append({
                "scene_id": scene_id,
                "title": scene_info.get("title"),
                "sequence": scene_info.get("sequence"),
                "period": scene_info.get("period"),
                "video_path": scene_info.get("path"),
                "generated_at": scene_info.get("generated_at"),
            })
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=2)
        
        return manifest
    
    def get_scene_video_path(self, scene_id: str) -> Optional[Path]:
        """
        Get path to generated video for a scene.
        
        Args:
            scene_id: Scene identifier
        
        Returns:
            Path if video exists, None otherwise
        """
        cached = self.manifest["scenes"].get(scene_id)
        if cached:
            path = Path(cached["path"])
            if path.exists():
                return path
        return None
    
    def list_generated_videos(self) -> List[Dict[str, Any]]:
        """
        List all generated videos with metadata.
        
        Returns:
            List of video info dictionaries
        """
        videos = []
        for scene_id, info in sorted(
            self.manifest["scenes"].items(),
            key=lambda x: x[1].get("sequence", 0)
        ):
            video_path = Path(info.get("path", ""))
            videos.append({
                "scene_id": scene_id,
                "title": info.get("title"),
                "sequence": info.get("sequence"),
                "path": str(video_path),
                "exists": video_path.exists(),
                "generated_at": info.get("generated_at"),
            })
        return videos


if __name__ == "__main__":
    # Example usage
    from story_scene_generator import generate_lakshmi_anu_scenes
    
    print("Initializing Video Scene Manager...")
    manager = VideoSceneManager()
    
    print("Generating Lakshmi-Anu story scenes...")
    scenes = generate_lakshmi_anu_scenes()
    
    # Save scene definitions as JSON for reference
    print(f"\nSaving {len(scenes)} scene definitions...")
    for scene in scenes:
        json_path = manager.save_scene_json(scene)
        print(f"  Saved: {json_path}")
    
    # Note: Video generation requires Gemini API key and will call the API
    # Uncomment to generate actual videos:
    # print("\nGenerating videos (this may take a while)...")
    # results = manager.generate_story_videos(scenes)
    # for scene_id, result in results.items():
    #     if result.success:
    #         print(f"✓ {scene_id}: {result.video_path}")
    #     else:
    #         print(f"✗ {scene_id}: {result.error}")
    
    # Export manifest
    manifest = manager.export_story_manifest("lakshmi_anu_story_001")
    print(f"\nGenerated manifest with {len(manifest['scenes'])} scenes")
