import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import Frequency, Pet, Task


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
