from pydantic import BaseModel, Field


class CarePlanReminder(BaseModel):
    reminder_id: str
    patient_id: str
    task: str
    reminder_type: str
    time: str | None = None
    enabled: bool = True
    source: str = "care_plan"


class CarePlan(BaseModel):
    patient_id: str
    reminders: list[CarePlanReminder] = Field(default_factory=list)
