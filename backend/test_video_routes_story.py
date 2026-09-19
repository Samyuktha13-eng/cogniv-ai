from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_get_story_route_uses_definition_not_generation(monkeypatch):
    def fake_get_story_definition(scene_limit=None):
        return {
            "story_id": "lakshmi-anu",
            "title": "Lakshmi Memories",
            "scenes": [{"id": "intro", "title": "intro", "video": "/videos/memory_01_home.mp4"}],
        }

    def fake_generate_story_videos(*args, **kwargs):
        raise AssertionError("GET /video/story/lakshmi-anu should not trigger generation")

    monkeypatch.setattr("backend.api.video_routes.get_story_definition", fake_get_story_definition)
    monkeypatch.setattr("backend.api.video_routes.generate_story_videos", fake_generate_story_videos)

    response = client.get("/video/story/lakshmi-anu?limit=4")

    assert response.status_code == 200
    body = response.json()
    assert body["story_id"] == "lakshmi-anu"
    assert body["scenes"][0]["video"] == "/videos/memory_01_home.mp4"


def test_get_story_definition_uses_existing_generated_video(monkeypatch, tmp_path):
    monkeypatch.setattr("backend.story_video_service.build_lakshmi_memory_journey", lambda: {
        "story_id": "lakshmi_anu_memory_journey",
        "title": "Lakshmi's Memories",
        "patient": "Lakshmi",
        "main_character": "Anu",
        "scenes": [{"id": "intro", "title": "Lakshmi's Memories", "image": "home/family_house_front.png"}],
    })
    monkeypatch.setattr("backend.story_video_service.resolve_scene_image", lambda scene: tmp_path / "home.png")
    monkeypatch.setattr("backend.story_video_service.VIDEO_DIR", tmp_path)
    monkeypatch.setattr("backend.story_video_service.VIDEO_FILENAMES", {"intro": "memory_01_home.mp4"})
    (tmp_path / "memory_01_home.mp4").write_bytes(b"video")

    result = __import__("backend.story_video_service", fromlist=["get_story_definition"]).get_story_definition(scene_limit=1)

    assert result["scenes"][0]["video"] == "/videos/memory_01_home.mp4"
