from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_patient_library_build_and_video_registry():
    # Reset folder state so this test is independent of prior runs
    from backend.app.services.patient_library import FOLDERS, VIDEO_JOBS
    if "lakshmi_001" in FOLDERS:
        FOLDERS["lakshmi_001"].story_status = "not_built"
        FOLDERS["lakshmi_001"].generation_status = "not_started"
        FOLDERS["lakshmi_001"].documents.clear()
        FOLDERS["lakshmi_001"].image_assets.clear()
        FOLDERS["lakshmi_001"].voice_story = None
    # Clear any existing video jobs for this patient
    for jid in [k for k, v in VIDEO_JOBS.items() if v.patient_id == "lakshmi_001"]:
        del VIDEO_JOBS[jid]

    before = client.get("/api/patients/lakshmi_001/folder")
    assert before.status_code == 200

    blocked = client.post("/api/patients/lakshmi_001/videos/generate")
    assert blocked.status_code == 409

    document = client.post(
        "/api/patients/lakshmi_001/folder/story-document",
        files={"document": ("Story 01 - The Jasmine Morning.docx", b"story", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert document.status_code == 200
    assert document.json()["type"] == "story_document"

    images = client.post(
        "/api/patients/lakshmi_001/folder/images",
        files=[
            ("images", ("jasmine_01.jpg", b"image-one", "image/jpeg")),
            ("images", ("jasmine_02.jpg", b"image-two", "image/jpeg")),
            ("relative_paths", (None, "jasmine/jasmine_01.jpg")),
            ("relative_paths", (None, "jasmine/jasmine_02.jpg")),
        ],
    )
    assert images.status_code == 200
    assert [item["relative_path"] for item in images.json()] == [
        "jasmine/jasmine_01.jpg",
        "jasmine/jasmine_02.jpg",
    ]

    voice = client.post(
        "/api/patients/lakshmi_001/folder/voice",
        files={"audio": ("lakshmi_story_recording.wav", b"audio", "audio/wav")},
    )
    assert voice.status_code == 200
    assert voice.json()["transcript_status"] == "queued"

    build = client.post("/api/patients/lakshmi_001/story/build")
    assert build.status_code == 200
    assert build.json()["status"] == "completed"
    # chapters_found = len(get_all_stories()) = 5 stories in the registry
    assert build.json()["chapters_found"] == 5
    assert build.json()["narration_prepared"] == 25  # 5 stories x 5 beats each

    jobs = client.post("/api/patients/lakshmi_001/videos/generate")
    assert jobs.status_code == 200
    assert len(jobs.json()) == 25
    assert all(job["status"] == "waiting" for job in jobs.json())

    status = client.get("/api/patients/lakshmi_001/videos/status")
    assert status.json()["total"] == 25
    assert status.json()["waiting"] == 25
