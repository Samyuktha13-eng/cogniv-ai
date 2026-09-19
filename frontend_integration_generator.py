"""
Frontend Integration Guide - Connect Lakshmi-Anu Story to Frontend.

This script generates configuration and integration code for connecting
the story video system to the frontend application.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from story_scene_generator import generate_lakshmi_anu_scenes


class FrontendIntegration:
    """Generate frontend integration artifacts."""
    
    def __init__(self, base_url: str = "http://localhost:8081"):
        """Initialize frontend integration."""
        self.base_url = base_url
        self.scenes = generate_lakshmi_anu_scenes()
    
    def generate_scene_router_config(self) -> Dict[str, Any]:
        """Generate scene routing configuration for frontend."""
        routes = {
            "story_id": "lakshmi_anu_story_001",
            "base_route": "/story/lakshmi_anu",
            "scenes": {}
        }
        
        for scene in self.scenes:
            scene_id = scene.metadata.scene_id
            next_scene = None
            prev_scene = None
            
            # Find next/prev
            for other in self.scenes:
                if other.metadata.sequence_number == scene.metadata.sequence_number + 1:
                    next_scene = other.metadata.scene_id
                if other.metadata.sequence_number == scene.metadata.sequence_number - 1:
                    prev_scene = other.metadata.scene_id
            
            routes["scenes"][scene_id] = {
                "route": f"/story/lakshmi_anu/{scene_id}",
                "next": next_scene,
                "prev": prev_scene,
                "sequence": scene.metadata.sequence_number,
            }
        
        return routes
    
    def generate_scene_data_api(self) -> Dict[str, Any]:
        """Generate scene data API responses."""
        api_data = {
            "endpoints": {
                "/api/story/lakshmi_anu": "GET - Fetch complete story",
                "/api/story/lakshmi_anu/{scene_id}": "GET - Fetch scene details",
                "/api/story/lakshmi_anu/{scene_id}/video": "GET - Get video stream",
            },
            "story": {
                "id": "lakshmi_anu_story_001",
                "title": "A Visit From Anu",
                "patient_id": "Patient_001_Lakshmi",
                "total_scenes": len(self.scenes),
                "scenes": {}
            }
        }
        
        for scene in self.scenes:
            api_data["story"]["scenes"][scene.metadata.scene_id] = {
                "id": scene.metadata.scene_id,
                "sequence": scene.metadata.sequence_number,
                "title": scene.metadata.title,
                "period": scene.metadata.period.value,
                "duration": scene.metadata.duration_seconds,
                "description": scene.story_context,
                "characters": [
                    {
                        "id": c.character_id,
                        "name": c.name,
                    }
                    for c in scene.characters
                ],
                "video_path": f"/videos/lakshmi_anu_001/{scene.metadata.scene_id}.mp4",
            }
        
        return api_data
    
    def generate_html_template(self) -> str:
        """Generate HTML template for story player."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lakshmi-Anu Story - Memory Theater</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .story-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 1000px;
            width: 100%;
            overflow: hidden;
        }
        
        .story-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .story-header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .story-header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .scene-viewer {
            padding: 40px;
        }
        
        .video-container {
            position: relative;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 30px;
            aspect-ratio: 16 / 9;
        }
        
        .video-container video {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        .scene-info {
            margin-bottom: 30px;
        }
        
        .scene-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 10px;
        }
        
        .scene-period {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-bottom: 15px;
        }
        
        .scene-period.past {
            background: #f5e6d3;
            color: #8b6f47;
        }
        
        .scene-period.transition {
            background: #e6d9f5;
            color: #6b47a1;
        }
        
        .scene-period.present {
            background: #d9f5e6;
            color: #2d7d5f;
        }
        
        .scene-description {
            color: #666;
            font-size: 1.1em;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        
        .scene-characters {
            margin-bottom: 20px;
        }
        
        .scene-characters h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .character-list {
            list-style: none;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .character-item {
            background: #f5f5f5;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 0.95em;
        }
        
        .character-item .char-name {
            font-weight: 600;
            color: #333;
        }
        
        .character-item .char-role {
            color: #999;
            font-size: 0.9em;
        }
        
        .navigation {
            display: flex;
            gap: 20px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        
        .nav-button {
            flex: 1;
            padding: 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: white;
            color: #333;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .nav-button:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .nav-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #eee;
            border-radius: 2px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        
        .scene-counter {
            text-align: center;
            color: #999;
            font-size: 0.95em;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="story-container">
        <div class="story-header">
            <h1>A Visit From Anu</h1>
            <p>A Memory Journey for Lakshmi</p>
        </div>
        
        <div class="scene-viewer">
            <!-- Progress -->
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill" style="width: 9%"></div>
            </div>
            
            <div class="scene-counter">
                <span id="sceneCounter">Scene 1 of 11</span>
            </div>
            
            <!-- Scene Content -->
            <div class="scene-info">
                <div class="scene-period past" id="scenePeriod">Past Memory</div>
                <h2 class="scene-title" id="sceneTitle">Lakshmi at Home</h2>
                <p class="scene-description" id="sceneDescription">
                    Lakshmi sits peacefully in her familiar home, beginning to remember her daughter.
                </p>
            </div>
            
            <!-- Video -->
            <div class="video-container">
                <video id="sceneVideo" controls>
                    <source src="/videos/lakshmi_anu_001/memory_01_home.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            
            <!-- Characters -->
            <div class="scene-characters">
                <h3>Characters</h3>
                <ul class="character-list" id="characterList">
                    <li class="character-item">
                        <div class="char-name">Lakshmi</div>
                        <div class="char-role">Elderly mother</div>
                    </li>
                </ul>
            </div>
            
            <!-- Navigation -->
            <div class="navigation">
                <button class="nav-button" id="prevBtn" onclick="previousScene()">
                    ← Previous
                </button>
                <button class="nav-button" id="nextBtn" onclick="nextScene()">
                    Next →
                </button>
            </div>
        </div>
    </div>
    
    <script>
        // Scene data loaded from API
        const storyData = window.storyData || {};
        let currentScene = 0;
        
        function updateScene(sceneIndex) {
            currentScene = sceneIndex;
            // Update DOM elements with scene data
            // This would typically fetch from the API
            updateNavigation();
        }
        
        function updateNavigation() {
            const isFirst = currentScene === 0;
            const isLast = currentScene === 10; // 11 scenes total
            
            document.getElementById('prevBtn').disabled = isFirst;
            document.getElementById('nextBtn').disabled = isLast;
        }
        
        function previousScene() {
            if (currentScene > 0) {
                updateScene(currentScene - 1);
            }
        }
        
        function nextScene() {
            if (currentScene < 10) {
                updateScene(currentScene + 1);
            }
        }
        
        // Initialize
        updateScene(0);
    </script>
</body>
</html>"""
        return html
    
    def generate_javascript_player(self) -> str:
        """Generate JavaScript player code."""
        js = """// Lakshmi-Anu Story Player
// Manages scene transitions, video playback, and therapeutic context

class LakshmiAnuStoryPlayer {
    constructor(containerId = 'story-player', apiBase = '/api') {
        this.container = document.getElementById(containerId);
        this.apiBase = apiBase;
        this.currentSceneIndex = 0;
        this.storyData = null;
        this.scenes = [];
        
        this.init();
    }
    
    async init() {
        // Fetch story data from API
        try {
            const response = await fetch(`${this.apiBase}/story/lakshmi_anu`);
            this.storyData = await response.json();
            this.scenes = Object.values(this.storyData.scenes);
            
            this.renderScene(0);
        } catch (error) {
            console.error('Failed to load story:', error);
            this.showError('Unable to load story data');
        }
    }
    
    async renderScene(index) {
        if (index < 0 || index >= this.scenes.length) return;
        
        this.currentSceneIndex = index;
        const scene = this.scenes[index];
        
        // Update scene title and info
        this.updateSceneInfo(scene);
        
        // Update video
        await this.updateVideo(scene);
        
        // Update navigation buttons
        this.updateNavigation();
        
        // Update progress
        this.updateProgress();
    }
    
    updateSceneInfo(scene) {
        document.getElementById('sceneTitle').textContent = scene.title;
        document.getElementById('sceneDescription').textContent = scene.description;
        
        const periodEl = document.getElementById('scenePeriod');
        periodEl.textContent = scene.period.charAt(0).toUpperCase() + scene.period.slice(1);
        periodEl.className = `scene-period ${scene.period}`;
        
        document.getElementById('sceneCounter').textContent = 
            `Scene ${scene.sequence} of ${this.scenes.length}`;
        
        // Update characters
        const charList = document.getElementById('characterList');
        charList.innerHTML = scene.characters
            .map(char => `
                <li class="character-item">
                    <div class="char-name">${char.name}</div>
                </li>
            `)
            .join('');
    }
    
    async updateVideo(scene) {
        const video = document.getElementById('sceneVideo');
        video.src = scene.video_path;
        video.load();
    }
    
    updateNavigation() {
        const isFirst = this.currentSceneIndex === 0;
        const isLast = this.currentSceneIndex === this.scenes.length - 1;
        
        document.getElementById('prevBtn').disabled = isFirst;
        document.getElementById('nextBtn').disabled = isLast;
    }
    
    updateProgress() {
        const progress = ((this.currentSceneIndex + 1) / this.scenes.length) * 100;
        document.getElementById('progressFill').style.width = progress + '%';
    }
    
    nextScene() {
        if (this.currentSceneIndex < this.scenes.length - 1) {
            this.renderScene(this.currentSceneIndex + 1);
        }
    }
    
    previousScene() {
        if (this.currentSceneIndex > 0) {
            this.renderScene(this.currentSceneIndex - 1);
        }
    }
    
    goToScene(sceneId) {
        const index = this.scenes.findIndex(s => s.id === sceneId);
        if (index !== -1) {
            this.renderScene(index);
        }
    }
    
    showError(message) {
        const container = document.getElementById('sceneDescription');
        container.textContent = message;
        container.style.color = 'red';
    }
}

// Initialize player when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.player = new LakshmiAnuStoryPlayer('story-container');
});
"""
        return js
    
    def generate_backend_routes(self) -> str:
        """Generate Flask/FastAPI backend route code."""
        code = '''"""
Backend routes for Lakshmi-Anu story videos.
Add these routes to your Flask or FastAPI application.
"""

from flask import Blueprint, jsonify, send_file, request
from pathlib import Path
import json

story_bp = Blueprint('story', __name__, url_prefix='/api/story')

# Load story metadata
STORY_DIR = Path('backend/generated_videos/lakshmi_anu_001')
METADATA_FILE = STORY_DIR / 'metadata' / 'story_manifest.json'

with open(METADATA_FILE) as f:
    STORY_MANIFEST = json.load(f)


@story_bp.route('/lakshmi_anu', methods=['GET'])
def get_story():
    """Get complete story with all scenes."""
    return jsonify(STORY_MANIFEST)


@story_bp.route('/lakshmi_anu/<scene_id>', methods=['GET'])
def get_scene(scene_id):
    """Get specific scene details."""
    scene = next(
        (s for s in STORY_MANIFEST['scenes'] if s['scene_id'] == scene_id),
        None
    )
    if scene:
        return jsonify(scene)
    return jsonify({'error': 'Scene not found'}), 404


@story_bp.route('/lakshmi_anu/<scene_id>/video', methods=['GET'])
def get_scene_video(scene_id):
    """Stream scene video file."""
    scene = next(
        (s for s in STORY_MANIFEST['scenes'] if s['scene_id'] == scene_id),
        None
    )
    if scene and scene.get('video_path'):
        video_path = Path(scene['video_path'])
        if video_path.exists():
            return send_file(video_path, mimetype='video/mp4')
    return jsonify({'error': 'Video not found'}), 404


@story_bp.route('/lakshmi_anu/progress', methods=['POST'])
def track_progress():
    """Track patient progress through story."""
    data = request.json
    scene_id = data.get('scene_id')
    completed = data.get('completed', False)
    
    # Log to patient outcomes
    # TODO: Save to outcome_tracker
    
    return jsonify({'status': 'ok', 'scene_id': scene_id})


# Register blueprint in your Flask app:
# app.register_blueprint(story_bp)
'''
        return code
    
    def generate_all_integration_files(self, output_dir: str = "backend/generated_videos/lakshmi_anu_001/integration") -> Dict[str, Path]:
        """Generate all integration files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Router config
        router = self.generate_scene_router_config()
        router_file = output_dir / "router_config.json"
        with open(router_file, 'w') as f:
            json.dump(router, f, indent=2)
        files["router_config"] = router_file
        
        # API config
        api_config = self.generate_scene_data_api()
        api_file = output_dir / "api_responses.json"
        with open(api_file, 'w') as f:
            json.dump(api_config, f, indent=2)
        files["api_config"] = api_file
        
        # HTML template
        html_file = output_dir / "story_player.html"
        with open(html_file, 'w') as f:
            f.write(self.generate_html_template())
        files["html_template"] = html_file
        
        # JavaScript player
        js_file = output_dir / "story_player.js"
        with open(js_file, 'w') as f:
            f.write(self.generate_javascript_player())
        files["javascript_player"] = js_file
        
        # Backend routes
        routes_file = output_dir / "backend_routes.py"
        with open(routes_file, 'w') as f:
            f.write(self.generate_backend_routes())
        files["backend_routes"] = routes_file
        
        return files


def main():
    """Generate all frontend integration files."""
    print("\n" + "=" * 100)
    print(" " * 30 + "FRONTEND INTEGRATION GENERATOR")
    print("=" * 100)
    
    integration = FrontendIntegration()
    
    print("\nGenerating frontend integration files...")
    files = integration.generate_all_integration_files()
    
    print("\nGenerated Files:")
    for file_type, file_path in files.items():
        print(f"  ✓ {file_type:20} → {file_path.relative_to(Path.cwd())}")
    
    print("\n" + "=" * 100)
    print("INTEGRATION COMPLETE")
    print("=" * 100)
    print("\nNext Steps:")
    print("  1. Copy story_player.html to your frontend")
    print("  2. Register backend_routes.py in your Flask/FastAPI app")
    print("  3. Include story_player.js in your HTML")
    print("  4. Update video paths in configuration files")
    print("  5. Test video playback in browser")


if __name__ == "__main__":
    main()
