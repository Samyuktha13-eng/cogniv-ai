from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..data.narrations import NARRATIONS
from ..models.care_plan import CarePlan
from ..models.game_session import GameSession, SessionStatus
from ..models.video_job import VideoJobStatus
from .story_playback import StoryAgent


class VideoProvider(Protocol):
    def request(self, story_id: str, beat_id: str) -> tuple[str, str]: ...


@dataclass(frozen=True)
class PendingVideo:
    status: str
    request_id: str | None
    video_url: str | None


class LibraryVideoProvider:
    """Looks up a completed VideoJob for the beat and returns its served URL."""

    def request(self, story_id: str, beat_id: str) -> tuple[str, str | None]:
        from ..services.patient_library import VIDEO_JOBS
        for job in VIDEO_JOBS.values():
            if job.story_id == story_id and job.scene_id == beat_id:
                if job.status == VideoJobStatus.COMPLETED and job.output_path:
                    output = Path(job.output_path)
                    try:
                        from ..services.patient_library import PATIENT_LIBRARY_ROOT
                        rel = output.relative_to(PATIENT_LIBRARY_ROOT)
                        return "completed", "/patient-library/" + rel.as_posix()
                    except ValueError:
                        return "completed", None
                return job.status.value, None
        return "no_job", None


class DeferredVideoProvider:
    """Fallback: returns a submit URL when no completed job exists yet."""

    def request(self, story_id: str, beat_id: str) -> tuple[str, str]:
        return "pending_provider", f"/api/generation/story/{story_id}/beat/{beat_id}/submit"


class GamePlayService:
    def __init__(
        self,
        session: GameSession,
        story_agent: StoryAgent,
        care_plan: CarePlan | None = None,
        video_provider: VideoProvider | None = None,
    ):
        self.session = session
        self.story_agent = story_agent
        self.care_plan = care_plan or CarePlan(patient_id=session.patient_id)
        self.video_provider = video_provider or LibraryVideoProvider()

    def play_next(self) -> dict[str, object]:
        beats = self.story_agent.beats()
        next_beats = [b for b in beats if b.id not in self.session.completed_beat_ids]
        if not next_beats:
            self.session.status = SessionStatus.COMPLETED
            return {"status": self.session.status.value}

        beat = next_beats[0]
        self.session.current_beat_id = beat.id
        self.session.current_beat_sequence = beat.sequence
        self.session.status = SessionStatus.PLAYING

        try:
            self.session.video_status, video_url = self.video_provider.request(
                self.session.story_id, beat.id
            )
            self.session.video_request_id = None
            self.session.video_url = video_url
            self.session.video_error = None
        except Exception as error:
            self.session.video_status = "failed"
            self.session.video_request_id = None
            self.session.video_url = None
            self.session.video_error = str(error)

        # Narration
        requested_language = self.session.narration_language or "en"
        narration_data = NARRATIONS.get(beat.id, {})
        narration_by_language = beat.narration_by_language or {"en": beat.narration or narration_data.get("opening", "")}
        selected_language = requested_language if requested_language in narration_by_language else "en"
        self.session.narration_language = selected_language
        self.session.narration_text = narration_by_language.get(selected_language, beat.narration)

        # Question — multilingual
        question_by_language = narration_data.get("question_by_language", {})
        question = question_by_language.get(requested_language) or narration_data.get("question", "")
        self.session.current_question = question

        # Mark beat played and move to waiting-for-speech
        self.session.completed_beat_ids.append(beat.id)
        self.session.status = SessionStatus.WAITING_FOR_SPEECH

        # Care reminder
        reminder = self._active_care_reminder()
        self.session.care_reminder_id = reminder.reminder_id if reminder else None
        self.session.care_reminder = reminder.task if reminder else None

        return {
            "status": self.session.status.value,
            "beat_id": beat.id,
            "beat_sequence": beat.sequence,
            "action": beat.action,
            "motion_sequence": beat.motion_sequence,
            "video": PendingVideo(self.session.video_status, self.session.video_request_id, self.session.video_url),
            "video_error": self.session.video_error,
            "narration": {
                "language": self.session.narration_language,
                "text": self.session.narration_text,
                "fallback_used": requested_language != self.session.narration_language,
            },
            "question": question,
            "question_language": requested_language,
            "care_reminder": self.session.care_reminder,
        }

    def replay(self) -> dict[str, object]:
        if not self.session.current_beat_id:
            raise RuntimeError("There is no current beat to replay.")
        self.session.status = SessionStatus.PLAYING
        try:
            self.session.video_status, video_url = self.video_provider.request(
                self.session.story_id, self.session.current_beat_id
            )
            self.session.video_url = video_url
            self.session.video_request_id = None
            self.session.video_error = None
        except Exception as error:
            self.session.video_status = "failed"
            self.session.video_request_id = None
            self.session.video_url = None
            self.session.video_error = str(error)
        self.session.status = SessionStatus.WAITING_FOR_SPEECH
        return {
            "status": self.session.status.value,
            "beat_id": self.session.current_beat_id,
            "question": self.session.current_question,
            "video": PendingVideo(self.session.video_status, self.session.video_request_id, self.session.video_url),
            "video_error": self.session.video_error,
        }

    def acknowledge_care_reminder(self) -> bool:
        reminder_id = self.session.care_reminder_id
        if not reminder_id:
            return False
        if reminder_id not in self.session.acknowledged_care_reminder_ids:
            self.session.acknowledged_care_reminder_ids.append(reminder_id)
        self.session.care_reminder = None
        self.session.care_reminder_id = None
        return True

    def _active_care_reminder(self):
        for item in self.care_plan.reminders:
            if item.enabled and item.reminder_id not in self.session.presented_care_reminder_ids:
                self.session.presented_care_reminder_ids.append(item.reminder_id)
                return item
        return None
