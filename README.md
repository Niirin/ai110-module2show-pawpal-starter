# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The `pawpal_system.py` module adds several features that make the planner more realistic:

- **Flexible frequencies** — Tasks support `DAILY`, `TWICE_DAILY`, `WEEKLY`, `BIWEEKLY`, and `AS_NEEDED` schedules. `isDueOn()` checks each task against its history so it only appears on the right days.
- **Time-budget fitting** — `DailyPlan._fitToTimeWindow()` always includes required tasks, then fills remaining available minutes with optional tasks ordered by priority. Nothing optional gets scheduled if it would exceed the owner's time budget.
- **Auto-scheduling next occurrences** — When a `DAILY` or `WEEKLY` task is marked completed, `markTaskCompleted()` automatically creates a new task instance for the next due date so the plan stays continuous.
- **Conflict detection** — `detectConflicts()` flags any two tasks assigned to the same time slot, calling out same-pet and cross-pet overlaps separately.
- **Filtered views** — `filterBy()` lets the UI show only tasks matching a given status (e.g. `"pending"`) or a specific pet, making it easy to build progress-tracking dashboards.
- **Rich summaries** — `getTaskSummary()` and `getPlanSummary()` return structured dicts ready for display or export, and `getReason()` generates a plain-English explanation of why the plan looks the way it does.
