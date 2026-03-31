import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date, timedelta
from pawpal_system import DailyPlan, Frequency, Owner, Pet, Task


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pet():
    return Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3, weight=10.5, sex="male")


@pytest.fixture
def task(pet):
    return Task(
        petId=pet.petId,
        title="Morning Walk",
        category="walk",
        frequency=Frequency.DAILY,
        duration=30,
        priority=3,
        preferredTime="morning",
        isReq=True,
    )


# ---------------------------------------------------------------------------
# Test 1 — Task Completion
# ---------------------------------------------------------------------------

def test_mark_completed_changes_status(task):
    """markCompleted() should set status to 'completed' and record lastCompleted."""
    assert task.status == "pending"
    assert task.lastCompleted is None

    task.markCompleted()

    assert task.status == "completed"
    assert task.lastCompleted is not None


# ---------------------------------------------------------------------------
# Test 2 — Task Addition
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count(pet, task):
    """addTask() should increase the pet's task list by one."""
    assert len(pet.getTasks()) == 0

    pet.addTask(task)

    assert len(pet.getTasks()) == 1


# ---------------------------------------------------------------------------
# Fixtures — shared helpers for new tests
# ---------------------------------------------------------------------------

@pytest.fixture
def owner(pet):
    o = Owner(name="Alex", email="alex@example.com", availableMinutes=120)
    o.addPet(pet)
    return o


def make_task(pet, title, frequency=Frequency.DAILY, duration=30,
              priority=2, isReq=False, scheduled_time=None):
    t = Task(
        petId=pet.petId,
        title=title,
        category="walk",
        frequency=frequency,
        duration=duration,
        priority=priority,
        preferredTime="morning",
        isReq=isReq,
    )
    t.scheduledTime = scheduled_time
    return t


# ---------------------------------------------------------------------------
# Task Scheduling & Recurrence
# ---------------------------------------------------------------------------

def test_is_due_before_created_date(pet):
    """A task is never due before its creation date."""
    task = make_task(pet, "Early Walk")
    task.createdAt = date.today() + timedelta(days=1)   # created tomorrow
    assert task.isDueOn(date.today()) is False


def test_is_due_on_created_date(pet):
    """A task is due on the day it was created."""
    task = make_task(pet, "Day-One Walk")
    assert task.isDueOn(date.today()) is True


def test_daily_not_due_after_completion(pet):
    """A DAILY task is not due again once completed today."""
    task = make_task(pet, "Daily Feed", frequency=Frequency.DAILY)
    task.markCompleted()
    assert task.isDueOn(date.today()) is False


def test_twice_daily_due_after_first_completion(pet):
    """A TWICE_DAILY task is still due after the first completion."""
    task = make_task(pet, "Morning Pill", frequency=Frequency.TWICE_DAILY)
    task.markCompleted()
    assert task.isDueOn(date.today()) is True


def test_twice_daily_not_due_after_two_completions(pet):
    """A TWICE_DAILY task is not due after two completions today."""
    task = make_task(pet, "Morning Pill", frequency=Frequency.TWICE_DAILY)
    task.markCompleted()
    task.markCompleted()
    assert task.isDueOn(date.today()) is False


def test_twice_daily_counter_resets_next_day(pet):
    """A TWICE_DAILY task resets its counter when completed on a new day."""
    task = make_task(pet, "Evening Pill", frequency=Frequency.TWICE_DAILY)
    task.lastCompleted = date.today() - timedelta(days=1)
    task.dailyCompletionCount = 2
    task.markCompleted()
    assert task.dailyCompletionCount == 1
    assert task.status == "partially_completed"


def test_weekly_due_exactly_7_days_later(pet):
    """A WEEKLY task becomes due exactly 7 days after last completion."""
    task = make_task(pet, "Bath", frequency=Frequency.WEEKLY)
    task.lastCompleted = date.today() - timedelta(days=7)
    assert task.isDueOn(date.today()) is True


def test_weekly_not_due_at_6_days(pet):
    """A WEEKLY task is not due 6 days after last completion."""
    task = make_task(pet, "Bath", frequency=Frequency.WEEKLY)
    task.lastCompleted = date.today() - timedelta(days=6)
    assert task.isDueOn(date.today()) is False


def test_weekly_due_when_never_completed(pet):
    """A WEEKLY task with no lastCompleted is always due."""
    task = make_task(pet, "Vet Visit", frequency=Frequency.WEEKLY)
    assert task.isDueOn(date.today()) is True


def test_as_needed_always_due(pet):
    """An AS_NEEDED task is always due regardless of completion history."""
    task = make_task(pet, "Extra Play", frequency=Frequency.AS_NEEDED)
    task.markCompleted()
    assert task.isDueOn(date.today()) is True


# ---------------------------------------------------------------------------
# Recurrence — daily task creates next-day occurrence
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_task(pet):
    """Marking a DAILY task complete appends a new task for tomorrow."""
    task = make_task(pet, "Morning Walk", frequency=Frequency.DAILY, isReq=True)
    pet.addTask(task)
    before = len(pet.getTasks())
    pet.markTaskCompleted(task.taskId)
    after = len(pet.getTasks())
    assert after == before + 1


def test_daily_recurrence_scheduled_for_tomorrow(pet):
    """The next occurrence created for a DAILY task has createdAt == tomorrow."""
    task = make_task(pet, "Evening Run", frequency=Frequency.DAILY, isReq=True)
    pet.addTask(task)
    pet.markTaskCompleted(task.taskId)
    tomorrow = date.today() + timedelta(days=1)
    new_task = pet.getTasks()[-1]
    assert new_task.createdAt == tomorrow


def test_twice_daily_no_next_occurrence(pet):
    """getNextOccurrence returns None for TWICE_DAILY tasks."""
    task = make_task(pet, "Insulin", frequency=Frequency.TWICE_DAILY)
    assert task.getNextOccurrence() is None


def test_biweekly_no_next_occurrence(pet):
    """getNextOccurrence returns None for BIWEEKLY tasks."""
    task = make_task(pet, "Flea Treatment", frequency=Frequency.BIWEEKLY)
    assert task.getNextOccurrence() is None


# ---------------------------------------------------------------------------
# Plan Generation — DailyPlan
# ---------------------------------------------------------------------------

def test_required_tasks_always_included_over_time_budget(pet, owner):
    """Required tasks are included even when they exceed availableMinutes."""
    owner.availableMinutes = 10
    req = make_task(pet, "Must-Do Walk", duration=60, isReq=True)
    pet.addTask(req)
    plan = DailyPlan(plan_date=date.today(), ownerId=owner.ownerId)
    plan.generatePlan(owner, owner.pets, owner.getAllTasks())
    assert any(t.taskId == req.taskId for t in plan.tasks)


def test_optional_task_excluded_when_over_budget(pet, owner):
    """An optional task that would exceed availableMinutes is excluded."""
    owner.availableMinutes = 20
    big_optional = make_task(pet, "Long Hike", duration=30, isReq=False, priority=3)
    pet.addTask(big_optional)
    plan = DailyPlan(plan_date=date.today(), ownerId=owner.ownerId)
    plan.generatePlan(owner, owner.pets, owner.getAllTasks())
    assert not any(t.taskId == big_optional.taskId for t in plan.tasks)


def test_optional_task_fits_exactly(pet, owner):
    """An optional task that fills the budget exactly is included."""
    owner.availableMinutes = 30
    exact = make_task(pet, "Exact Fit", duration=30, isReq=False, priority=2)
    pet.addTask(exact)
    plan = DailyPlan(plan_date=date.today(), ownerId=owner.ownerId)
    plan.generatePlan(owner, owner.pets, owner.getAllTasks())
    assert any(t.taskId == exact.taskId for t in plan.tasks)


def test_zero_available_minutes_only_required(pet, owner):
    """With 0 availableMinutes, only required tasks are scheduled."""
    owner.availableMinutes = 0
    req = make_task(pet, "Required Med", duration=5, isReq=True)
    opt = make_task(pet, "Optional Play", duration=5, isReq=False)
    pet.addTask(req)
    pet.addTask(opt)
    plan = DailyPlan(plan_date=date.today(), ownerId=owner.ownerId)
    plan.generatePlan(owner, owner.pets, owner.getAllTasks())
    task_ids = [t.taskId for t in plan.tasks]
    assert req.taskId in task_ids
    assert opt.taskId not in task_ids


# ---------------------------------------------------------------------------
# Sorting Correctness — sortByPriority and sortByTime
# ---------------------------------------------------------------------------

def test_sort_by_priority_required_first(pet):
    """sortByPriority puts required tasks before optional ones."""
    opt  = make_task(pet, "Optional",  priority=3, isReq=False)
    req  = make_task(pet, "Required",  priority=1, isReq=True)
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [opt, req]
    plan.sortByPriority()
    assert plan.tasks[0].isReq is True


def test_sort_by_time_chronological_order(pet):
    """sortByTime returns tasks in ascending chronological order."""
    t1 = make_task(pet, "Breakfast",   scheduled_time="08:00")
    t2 = make_task(pet, "Lunch Walk",  scheduled_time="12:30")
    t3 = make_task(pet, "Dinner Feed", scheduled_time="18:00")
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t3, t1, t2]   # intentionally shuffled
    plan.sortByTime()
    assert [t.scheduledTime for t in plan.tasks] == ["08:00", "12:30", "18:00"]


def test_sort_by_time_none_goes_to_end(pet):
    """Tasks with no scheduledTime sort to the end of the list."""
    t_timed   = make_task(pet, "Walk",  scheduled_time="09:00")
    t_untimed = make_task(pet, "Groom", scheduled_time=None)
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t_untimed, t_timed]
    plan.sortByTime()
    assert plan.tasks[-1].scheduledTime is None


# ---------------------------------------------------------------------------
# Highest-Risk Bug — sortByTime with non-zero-padded single-digit hours
# ---------------------------------------------------------------------------

def test_sort_by_time_single_digit_hour_sorts_correctly(pet):
    """'9:00' must sort before '10:00' — fails if compared lexicographically without zero-padding."""
    t9  = make_task(pet, "Early Walk",  scheduled_time="9:00")
    t10 = make_task(pet, "Late Walk",   scheduled_time="10:00")
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t10, t9]   # 10:00 first — sort must fix this
    plan.sortByTime()
    # Lexicographic comparison puts "9:00" > "10:00", so this test will FAIL
    # until times are zero-padded (e.g. "09:00") or parsed as actual time objects.
    assert plan.tasks[0].scheduledTime == "9:00", (
        "BUG: '9:00' sorted after '10:00' due to lexicographic string comparison. "
        "Fix: zero-pad hours or parse scheduledTime as datetime.time."
    )


# ---------------------------------------------------------------------------
# Conflict Detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_pet_same_time(pet):
    """Two tasks for the same pet at the same time generate a warning."""
    t1 = make_task(pet, "Walk",  scheduled_time="09:00")
    t2 = make_task(pet, "Groom", scheduled_time="09:00")
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t1, t2]
    warnings = plan.detectConflicts()
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]


def test_detect_conflicts_different_pets_same_time():
    """Two tasks for different pets at the same time generate a cross-pet warning."""
    pet_a = Pet(name="Mochi", species="dog", breed="Shiba", age=2, weight=9.0, sex="male")
    pet_b = Pet(name="Luna",  species="cat", breed="Tabby", age=3, weight=4.5, sex="female")
    t1 = make_task(pet_a, "Walk",     scheduled_time="10:00")
    t2 = make_task(pet_b, "Feeding",  scheduled_time="10:00")
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t1, t2]
    pets_map = {pet_a.petId: pet_a, pet_b.petId: pet_b}
    warnings = plan.detectConflicts(pets=pets_map)
    assert len(warnings) == 1
    assert "Mochi" in warnings[0] and "Luna" in warnings[0]


def test_detect_conflicts_three_tasks_same_slot(pet):
    """Three tasks in the same slot produce a warning for every pair (3 warnings)."""
    t1 = make_task(pet, "Walk",   scheduled_time="07:00")
    t2 = make_task(pet, "Feed",   scheduled_time="07:00")
    t3 = make_task(pet, "Groom",  scheduled_time="07:00")
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t1, t2, t3]
    warnings = plan.detectConflicts()
    assert len(warnings) == 3


def test_detect_no_conflicts_when_times_differ(pet):
    """Tasks at different times produce no conflict warnings."""
    t1 = make_task(pet, "Walk",  scheduled_time="08:00")
    t2 = make_task(pet, "Feed",  scheduled_time="12:00")
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t1, t2]
    assert plan.detectConflicts() == []


def test_detect_no_conflicts_for_unscheduled_tasks(pet):
    """Tasks with no scheduledTime are excluded from conflict detection."""
    t1 = make_task(pet, "Walk",  scheduled_time=None)
    t2 = make_task(pet, "Feed",  scheduled_time=None)
    plan = DailyPlan(plan_date=date.today(), ownerId="owner-1")
    plan.tasks = [t1, t2]
    assert plan.detectConflicts() == []


# ---------------------------------------------------------------------------
# Pet & Owner — guard rails
# ---------------------------------------------------------------------------

def test_add_duplicate_task_raises(pet, task):
    """Adding the same task twice to a pet raises ValueError."""
    pet.addTask(task)
    with pytest.raises(ValueError):
        pet.addTask(task)


def test_add_task_wrong_pet_raises(task):
    """Adding a task whose petId doesn't match the pet raises ValueError."""
    other_pet = Pet(name="Biscuit", species="cat", breed="Tabby", age=1, weight=4.0, sex="female")
    with pytest.raises(ValueError):
        other_pet.addTask(task)


def test_remove_nonexistent_task_raises(pet):
    """Removing a taskId that doesn't exist raises KeyError."""
    with pytest.raises(KeyError):
        pet.removeTask("nonexistent-id")


def test_update_priority_invalid_value_raises(task):
    """updatePriority with a value outside 1–3 raises ValueError."""
    with pytest.raises(ValueError):
        task.updatePriority(0)
    with pytest.raises(ValueError):
        task.updatePriority(4)


def test_update_task_protected_field_raises(task):
    """updateTask with a protected field like 'taskId' raises KeyError."""
    with pytest.raises(KeyError):
        task.updateTask({"taskId": "hacked-id"})


def test_update_pet_protected_field_raises(pet):
    """updateInfo with 'petId' raises KeyError."""
    with pytest.raises(KeyError):
        pet.updateInfo({"petId": "hacked-id"})
