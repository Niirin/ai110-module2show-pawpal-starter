from dataclasses import dataclass, field
from datetime import date
from typing import Optional


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    taskId: str
    petId: str
    title: str
    category: str          # e.g. "walk", "feeding", "medication", "grooming"
    duration: int          # minutes
    priority: int          # 1 (low) – 3 (high)
    frequency: str         # e.g. "daily", "weekly"
    preferredTime: str     # e.g. "morning", "evening"
    isReq: bool            # required task (cannot be skipped)
    notes: str = ""
    status: str = "pending"  # "pending" | "completed" | "skipped"

    def markCompleted(self):
        pass

    def markSkipped(self):
        pass

    def updatePriority(self, _priority: int):
        pass

    def updateTask(self, _info: dict):
        pass

    def isDueOn(self, _check_date: date) -> bool:
        pass

    def getTaskSummary(self) -> dict:
        pass


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    petId: str
    name: str
    species: str
    breed: str
    age: int
    weight: float
    sex: str
    medicalNotes: str = ""
    activityLevel: str = "moderate"   # "low" | "moderate" | "high"
    feeding: dict = field(default_factory=dict)
    specialNeeds: str = ""
    tasks: list[Task] = field(default_factory=list)

    def addTask(self, _task: Task):
        pass

    def removeTask(self, _taskId: str):
        pass

    def updateInfo(self, _info: dict):
        pass

    def getTasks(self) -> list[Task]:
        pass

    def getTasksForDate(self, _check_date: date) -> list[Task]:
        pass

    def getImportantInfo(self) -> dict:
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        ownerId: str,
        name: str,
        email: str,
        preferences: Optional[dict] = None,
    ):
        self.ownerId = ownerId
        self.name = name
        self.email = email
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def addPet(self, _pet: Pet):
        pass

    def removePet(self, _petId: str):
        pass

    def updatePet(self, _petId: str, _info: dict):
        pass

    def getPet(self, _petId: str) -> Optional[Pet]:
        pass

    def getAvailableTime(self) -> int:
        """Return available minutes for the day based on preferences."""
        pass


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

class DailyPlan:
    def __init__(self, planId: str, plan_date: date, ownerId: str):
        self.planId = planId
        self.date = plan_date
        self.ownerId = ownerId
        self.tasks: list[Task] = []
        self.totalEstTime: int = 0
        self.explanation: str = ""

    def generatePlan(self, _owner: Owner, _pets: list[Pet], _tasks: list[Task]):
        pass

    def sortByPriority(self):
        pass

    def getPlanSummary(self) -> dict:
        pass

    def getReason(self) -> str:
        pass
