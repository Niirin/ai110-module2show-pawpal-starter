from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
from uuid import uuid4


# ---------------------------------------------------------------------------
# Frequency Enum
# ---------------------------------------------------------------------------

class Frequency(Enum):
    DAILY       = "daily"
    TWICE_DAILY = "twice_daily"
    WEEKLY      = "weekly"
    BIWEEKLY    = "biweekly"
    AS_NEEDED   = "as_needed"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    petId: str
    title: str
    category: str               # e.g. "walk", "feeding", "medication", "grooming"
    frequency: Frequency
    duration: int               # minutes
    priority: int               # 1 (low) – 3 (high)
    preferredTime: str          # e.g. "morning", "evening"
    isReq: bool                 # required task (cannot be skipped)
    taskId: str                 = field(default_factory=lambda: str(uuid4()))
    notes: str                  = ""
    status: str                 = "pending"     # "pending" | "partially_completed" | "completed" | "skipped"
    createdAt: date             = field(default_factory=date.today)
    scheduledTime: Optional[str]= None          # assigned slot, e.g. "9:00 AM"
    lastCompleted: Optional[date] = None        # set when markCompleted() is called
    dailyCompletionCount: int   = 0             # tracks completions today (used by TWICE_DAILY)

    def markCompleted(self):
        """Mark the task done; handles TWICE_DAILY counter and sets lastCompleted."""
        today = date.today()
        if self.frequency == Frequency.TWICE_DAILY:
            # Reset counter if this is a new day
            if self.lastCompleted != today:
                self.dailyCompletionCount = 0
            self.dailyCompletionCount += 1
            self.lastCompleted = today
            self.status = "completed" if self.dailyCompletionCount >= 2 else "partially_completed"
        else:
            self.status = "completed"
            self.lastCompleted = today

    def markSkipped(self):
        """Set the task status to 'skipped' without recording a completion."""
        self.status = "skipped"

    def updatePriority(self, priority: int):
        """Validate and update the task priority (1=low, 2=medium, 3=high)."""
        if priority not in (1, 2, 3):
            raise ValueError("Priority must be 1 (low), 2 (medium), or 3 (high).")
        self.priority = priority

    def updateTask(self, info: dict):
        """Update allowed task fields from a dict; raises KeyError for protected fields."""
        allowed = {
            "title", "category", "frequency", "duration",
            "priority", "preferredTime", "isReq", "notes",
        }
        for key, value in info.items():
            if key not in allowed:
                raise KeyError(f"'{key}' is not an editable Task field.")
            setattr(self, key, value)

    def isDueOn(self, check_date: date) -> bool:
        """Return True if the task is due on check_date based on its frequency and completion history."""
        # Task cannot be due before it was created
        if check_date < self.createdAt:
            return False

        if self.frequency == Frequency.AS_NEEDED:
            return True

        # Already completed today — not due again (except TWICE_DAILY handled below)
        completed_today = self.lastCompleted == check_date

        if self.frequency == Frequency.DAILY:
            return not completed_today

        if self.frequency == Frequency.TWICE_DAILY:
            # Due if completed fewer than 2 times today
            if self.lastCompleted == check_date:
                return self.dailyCompletionCount < 2
            return True

        days_since = (
            (check_date - self.lastCompleted).days
            if self.lastCompleted
            else float("inf")
        )

        if self.frequency == Frequency.WEEKLY:
            return days_since >= 7

        if self.frequency == Frequency.BIWEEKLY:
            return days_since >= 14

        return False

    def getTaskSummary(self) -> dict:
        """Return a flat dict of the task's key fields for display or plan output."""
        return {
            "taskId":        self.taskId,
            "title":         self.title,
            "category":      self.category,
            "frequency":     self.frequency.value,
            "duration_min":  self.duration,
            "priority":      self.priority,
            "preferredTime": self.preferredTime,
            "isReq":         self.isReq,
            "status":        self.status,
            "lastCompleted":        str(self.lastCompleted) if self.lastCompleted else None,
            "dailyCompletionCount": self.dailyCompletionCount,
            "scheduledTime":        self.scheduledTime,
            "notes":                self.notes,
        }


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    weight: float
    sex: str
    petId: str                  = field(default_factory=lambda: str(uuid4()))
    medicalNotes: str           = ""
    activityLevel: str          = "moderate"    # "low" | "moderate" | "high"
    feeding: dict               = field(default_factory=dict)
    specialNeeds: str           = ""
    tasks: list[Task]           = field(default_factory=list)

    def addTask(self, task: Task):
        """Append a task to this pet, validating petId and rejecting duplicates."""
        if task.petId != self.petId:
            raise ValueError(f"Task petId '{task.petId}' does not match this pet's id '{self.petId}'.")
        if any(t.taskId == task.taskId for t in self.tasks):
            raise ValueError(f"Task '{task.taskId}' is already added to {self.name}.")
        self.tasks.append(task)

    def removeTask(self, taskId: str):
        """Remove a task by taskId; raises KeyError if not found."""
        task = next((t for t in self.tasks if t.taskId == taskId), None)
        if task is None:
            raise KeyError(f"No task with id '{taskId}' found for {self.name}.")
        self.tasks.remove(task)

    def updateInfo(self, info: dict):
        """Update allowed pet fields from a dict; raises KeyError for protected fields."""
        allowed = {
            "name", "species", "breed", "age", "weight",
            "sex", "medicalNotes", "activityLevel", "feeding", "specialNeeds",
        }
        for key, value in info.items():
            if key not in allowed:
                raise KeyError(f"'{key}' is not an editable Pet field.")
            setattr(self, key, value)

    def getTasks(self) -> list[Task]:
        """Return a copy of all tasks belonging to this pet."""
        return list(self.tasks)

    def getTasksForDate(self, check_date: date) -> list[Task]:
        """Return all tasks due on check_date by delegating to each task's isDueOn."""
        return [t for t in self.tasks if t.isDueOn(check_date)]

    def getImportantInfo(self) -> dict:
        """Return a flat dict of the pet's key details including task count."""
        return {
            "petId":         self.petId,
            "name":          self.name,
            "species":       self.species,
            "breed":         self.breed,
            "age":           self.age,
            "weight":        self.weight,
            "sex":           self.sex,
            "activityLevel": self.activityLevel,
            "feeding":       self.feeding,
            "medicalNotes":  self.medicalNotes,
            "specialNeeds":  self.specialNeeds,
            "taskCount":     len(self.tasks),
        }


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        name: str,
        email: str,
        availableMinutes: int = 60,
        preferences: Optional[dict] = None,
        ownerId: Optional[str] = None,
    ):
        self.ownerId = ownerId or str(uuid4())
        self.name = name
        self.email = email
        self.availableMinutes = availableMinutes   # e.g. 90 for 1.5 hours
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def addPet(self, pet: Pet):
        """Register a pet to this owner, rejecting duplicates."""
        if any(p.petId == pet.petId for p in self.pets):
            raise ValueError(f"Pet '{pet.name}' is already registered to this owner.")
        self.pets.append(pet)

    def removePet(self, petId: str):
        """Remove a pet by petId; raises KeyError if not found."""
        pet = next((p for p in self.pets if p.petId == petId), None)
        if pet is None:
            raise KeyError(f"No pet with id '{petId}' found for {self.name}.")
        self.pets.remove(pet)

    def updatePet(self, petId: str, info: dict):
        """Look up a pet by petId and delegate field updates to pet.updateInfo."""
        pet = self.getPet(petId)
        if pet is None:
            raise KeyError(f"No pet with id '{petId}' found for {self.name}.")
        pet.updateInfo(info)

    def getPet(self, petId: str) -> Optional[Pet]:
        """Return the Pet matching petId, or None if not found."""
        return next((p for p in self.pets if p.petId == petId), None)

    def getAllTasks(self) -> list[Task]:
        """Return every task across all pets."""
        return [task for pet in self.pets for task in pet.getTasks()]

    def getAllTasksForDate(self, check_date: date) -> list[Task]:
        """Return all tasks due on check_date across every pet."""
        return [task for pet in self.pets for task in pet.getTasksForDate(check_date)]

    def getAvailableTime(self) -> int:
        """Return available minutes for the day."""
        return self.availableMinutes


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

class DailyPlan:
    def __init__(
        self,
        plan_date: date,
        ownerId: str,
        planId: Optional[str] = None,
    ):
        self.planId = planId or str(uuid4())
        self.date = plan_date
        self.ownerId = ownerId
        self.petIds: list[str] = []
        self.tasks: list[Task] = []
        self.totalEstTime: int = 0
        self.explanation: str = ""

    def generatePlan(self, owner: Owner, pets: list[Pet], tasks: list[Task]):
        """Build a daily plan: filter due tasks, fit to available time, sort."""
        due = self._filterDueTasks(tasks, self.date)
        fitted = self._fitToTimeWindow(due, owner.getAvailableTime())
        self.tasks = fitted
        self.sortByPriority()
        self.petIds = list({t.petId for t in fitted})
        self.totalEstTime = sum(t.duration for t in fitted)
        self.explanation = self.getReason()

    def _filterDueTasks(self, tasks: list[Task], check_date: date) -> list[Task]:
        """Return only tasks that are due on check_date."""
        return [t for t in tasks if t.isDueOn(check_date)]

    def _fitToTimeWindow(self, tasks: list[Task], availableMinutes: int) -> list[Task]:
        """Fill the time window with tasks: required tasks first (always kept),
        then optional tasks sorted highest priority first until time runs out."""
        required  = [t for t in tasks if t.isReq]
        optional  = sorted(
            [t for t in tasks if not t.isReq],
            key=lambda t: t.priority,
            reverse=True,
        )

        scheduled: list[Task] = []
        time_used = 0

        # Required tasks are always included regardless of time
        for task in required:
            scheduled.append(task)
            time_used += task.duration

        # Fill remaining time with optional tasks
        for task in optional:
            if time_used + task.duration <= availableMinutes:
                scheduled.append(task)
                time_used += task.duration

        return scheduled

    def sortByPriority(self):
        """Sort scheduled tasks: required first, then by priority descending."""
        self.tasks.sort(key=lambda t: (not t.isReq, -t.priority))

    def getTasksByPet(self) -> dict[str, list[Task]]:
        """Return scheduled tasks grouped by petId."""
        grouped: dict[str, list[Task]] = {}
        for task in self.tasks:
            grouped.setdefault(task.petId, []).append(task)
        return grouped

    def getPlanSummary(self) -> dict:
        """Return a full snapshot of the plan including all task summaries."""
        return {
            "planId":        self.planId,
            "date":          str(self.date),
            "ownerId":       self.ownerId,
            "petIds":        self.petIds,
            "totalEstTime":  self.totalEstTime,
            "taskCount":     len(self.tasks),
            "tasks":         [t.getTaskSummary() for t in self.tasks],
            "explanation":   self.explanation,
        }

    def getReason(self) -> str:
        """Build a plain-English explanation of the plan."""
        if not self.tasks:
            return "No tasks were scheduled — either none are due today or no time is available."

        req_titles = [t.title for t in self.tasks if t.isReq]
        opt_titles = [t.title for t in self.tasks if not t.isReq]

        lines = [f"Plan for {self.date} - estimated {self.totalEstTime} min total."]

        if req_titles:
            lines.append(f"Required tasks (always included): {', '.join(req_titles)}.")
        if opt_titles:
            lines.append(
                f"Optional tasks scheduled by priority: {', '.join(opt_titles)}."
            )

        skipped_count = len([t for t in self.tasks if t.status == "skipped"])
        if skipped_count:
            lines.append(f"{skipped_count} task(s) were skipped today.")

        return " ".join(lines)
