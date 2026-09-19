from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_phase2_gameplay_speak_skip_flow():
    """
    New flow: video plays → question shown → patient speaks or skips →
    interaction stored → next beat. No right/wrong feedback.
    """
    # Set up a care plan with one reminder
    care_plan = client.put(
        "/api/patients/lakshmi_001/care-plan",
        json={
            "patient_id": "lakshmi_001",
            "reminders": [
                {
                    "reminder_id": "water_0900",
                    "patient_id": "lakshmi_001",
                    "task": "Drink water",
                    "reminder_type": "water",
                    "time": "09:00",
                }
            ],
        },
    )
    assert care_plan.status_code == 200

    # Start session
    session = client.post(
        "/api/game/sessions",
        json={"patient_id": "lakshmi_001", "story_id": "jasmine_morning", "narration_language": "en"},
    ).json()
    session_id = session["session_id"]

    # Play first beat
    first = client.post(f"/api/game/sessions/{session_id}/play").json()
    assert first["beat_id"] == "jasmine_01"
    assert first["status"] == "waiting_for_speech"
    assert "question" in first
    assert first["question"]  # non-empty question
    assert first["video"]["status"] in ("no_job", "pending_provider", "waiting")
    assert first["care_reminder"] == "Drink water"

    # Acknowledge care reminder
    ack = client.post(f"/api/game/sessions/{session_id}/care-reminder/acknowledge")
    assert ack.json()["acknowledged"] is True

    # Record a spoken interaction for beat 1
    interaction = client.post(
        f"/api/game/sessions/{session_id}/interaction",
        json={
            "beat_id": "jasmine_01",
            "beat_sequence": 1,
            "question": first["question"],
            "spoken": True,
            "transcript": "She was closing the wooden door",
            "transcript_language": "en",
        },
    ).json()
    assert interaction["stored"] is True
    assert "event_id" in interaction

    # Play second beat
    second = client.post(f"/api/game/sessions/{session_id}/play").json()
    assert second["beat_id"] == "jasmine_02"
    assert second["status"] == "waiting_for_speech"
    assert second["care_reminder"] is None  # reminder already acknowledged

    # Skip (no speech) for beat 2
    skip = client.post(
        f"/api/game/sessions/{session_id}/interaction",
        json={
            "beat_id": "jasmine_02",
            "beat_sequence": 2,
            "question": second["question"],
            "spoken": False,
        },
    ).json()
    assert skip["stored"] is True

    # Play third beat
    third = client.post(f"/api/game/sessions/{session_id}/play").json()
    assert third["beat_id"] == "jasmine_03"
    assert third["status"] == "waiting_for_speech"

    # Replay works and returns question
    replay = client.post(f"/api/game/sessions/{session_id}/replay").json()
    assert replay["beat_id"] == "jasmine_03"
    assert replay["status"] == "waiting_for_speech"
    assert "question" in replay

    # Audio interaction endpoint works
    audio_interaction = client.post(
        f"/api/game/sessions/{session_id}/interaction/audio",
        data={
            "beat_id": "jasmine_03",
            "beat_sequence": "3",
            "question": third["question"],
            "transcript": "She carried the brass pot",
            "transcript_language": "en",
        },
        files={"audio": ("beat_003.wav", b"RIFF\x00\x00\x00\x00WAVE", "audio/wav")},
    )
    assert audio_interaction.status_code == 200
    assert audio_interaction.json()["stored"] is True


def test_phase2_gameplay_multilingual_question():
    """Question is served in the requested language when available."""
    session = client.post(
        "/api/game/sessions",
        json={"patient_id": "lakshmi_001", "story_id": "jasmine_morning", "narration_language": "ta"},
    ).json()
    session_id = session["session_id"]

    beat = client.post(f"/api/game/sessions/{session_id}/play").json()
    assert beat["question_language"] == "ta"
    # Tamil question should contain Tamil characters or at least be non-empty
    assert beat["question"]


def test_phase2_gameplay_end_session_generates_report():
    """End session creates session_transcript.json and a report file."""
    session = client.post(
        "/api/game/sessions",
        json={"patient_id": "lakshmi_001", "story_id": "mango_tree", "narration_language": "en"},
    ).json()
    session_id = session["session_id"]

    # Play one beat and record a spoken response
    beat = client.post(f"/api/game/sessions/{session_id}/play").json()
    client.post(
        f"/api/game/sessions/{session_id}/interaction",
        json={
            "beat_id": beat["beat_id"],
            "beat_sequence": beat["beat_sequence"],
            "question": beat["question"],
            "spoken": True,
            "transcript": "She was looking for the biggest mango in the kitchen",
            "transcript_language": "en",
        },
    )

    # End session
    result = client.post(f"/api/game/sessions/{session_id}/end").json()
    assert result["status"] == "completed"
    assert result["total_beats"] >= 1
    assert result["spoken_responses"] == 1
    assert result["skipped_responses"] == 0
    assert "download_url" in result

    # Report download endpoint exists
    report = client.get(f"/api/game/sessions/{session_id}/report")
    assert report.status_code == 200
    content_type = report.headers.get("content-type", "")
    assert "wordprocessingml" in content_type or "text/plain" in content_type
