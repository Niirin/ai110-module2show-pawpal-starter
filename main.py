from datetime import date
from pawpal_system import DailyPlan, Frequency, Owner, Pet, Task


# ---------------------------------------------------------------------------
# Helper — pretty print
# ---------------------------------------------------------------------------

PRIORITY_LABEL = {1: "Low", 2: "Medium", 3: "High"}
SEP = "-" * 52


def print_schedule(plan: DailyPlan, owner: Owner, pets: dict[str, Pet]):
    print(f"\n{'=' * 52}")
    print(f"  PawPal+  |  Today's Schedule  |  {plan.date}")
    print(f"{'=' * 52}")
    print(f"  Owner   : {owner.name}")
    print(f"  Time    : {owner.getAvailableTime()} min available")
    print(f"  Est.    : {plan.totalEstTime} min scheduled")
    print(f"  Tasks   : {len(plan.tasks)}")
    print(SEP)

    grouped = plan.getTasksByPet()
    for petId, tasks in grouped.items():
        pet = pets.get(petId)
        pet_label = f"{pet.name} ({pet.species})" if pet else petId
        print(f"\n  {pet_label}")
        print(f"  {'-' * 46}")
        for task in tasks:
            req_flag  = "[REQ]" if task.isReq else "     "
            priority  = PRIORITY_LABEL[task.priority]
            freq      = task.frequency.value.replace("_", " ")
            time_slot = task.preferredTime.capitalize()
            print(f"  {req_flag} {task.title:<22} {task.duration:>3} min  |  {time_slot:<9}  |  P: {priority}  |  {freq}")

    print(f"\n{SEP}")
    print(f"  Why this plan?")
    print(f"  {plan.explanation}")
    print(f"{'=' * 52}\n")


# ---------------------------------------------------------------------------
# Setup — Owner
# ---------------------------------------------------------------------------

jordan = Owner(
    name="Jordan",
    email="jordan@email.com",
    availableMinutes=120,
    preferences={"morning_person": True},
)

# ---------------------------------------------------------------------------
# Setup — Pets
# ---------------------------------------------------------------------------

mochi = Pet(
    name="Mochi",
    species="dog",
    breed="Shiba Inu",
    age=3,
    weight=10.5,
    sex="male",
    activityLevel="high",
    feeding={"times": ["7:00 AM", "6:00 PM"], "amount": "1 cup"},
    medicalNotes="Allergic to chicken-based treats.",
)

luna = Pet(
    name="Luna",
    species="cat",
    breed="Domestic Shorthair",
    age=5,
    weight=4.2,
    sex="female",
    activityLevel="low",
    feeding={"times": ["8:00 AM", "5:00 PM"], "amount": "half cup"},
    specialNeeds="Indoor only. Stress-sensitive.",
)

jordan.addPet(mochi)
jordan.addPet(luna)

# ---------------------------------------------------------------------------
# Setup — Tasks for Mochi (added out of order)
# ---------------------------------------------------------------------------

mochi.addTask(Task(
    petId=mochi.petId,
    title="Fetch & Play",
    category="enrichment",
    frequency=Frequency.DAILY,
    duration=20,
    priority=2,
    preferredTime="afternoon",
    isReq=False,
    scheduledTime="14:00",
))

mochi.addTask(Task(
    petId=mochi.petId,
    title="Flea Medication",
    category="medication",
    frequency=Frequency.BIWEEKLY,
    duration=5,
    priority=3,
    preferredTime="morning",
    isReq=True,
    notes="Apply between shoulder blades.",
    scheduledTime="08:30",
))

mochi.addTask(Task(
    petId=mochi.petId,
    title="Morning Walk",
    category="walk",
    frequency=Frequency.DAILY,
    duration=30,
    priority=3,
    preferredTime="morning",
    isReq=True,
    notes="At least 20 min brisk walk.",
    scheduledTime="07:00",
))

# ---------------------------------------------------------------------------
# Setup — Tasks for Luna (added out of order)
# ---------------------------------------------------------------------------

luna.addTask(Task(
    petId=luna.petId,
    title="Brushing",
    category="grooming",
    frequency=Frequency.WEEKLY,
    duration=15,
    priority=2,
    preferredTime="evening",
    isReq=False,
    notes="Helps reduce shedding.",
    scheduledTime="19:00",
))

luna.addTask(Task(
    petId=luna.petId,
    title="Feeding",
    category="feeding",
    frequency=Frequency.TWICE_DAILY,
    duration=10,
    priority=3,
    preferredTime="morning",
    isReq=True,
    scheduledTime="08:00",
))

luna.addTask(Task(
    petId=luna.petId,
    title="Litter Box Clean",
    category="grooming",
    frequency=Frequency.DAILY,
    duration=5,
    priority=3,
    preferredTime="morning",
    isReq=True,
    notes="Scoop daily, full change weekly.",
    scheduledTime="09:00",
))

# ---------------------------------------------------------------------------
# Generate today's plan
# ---------------------------------------------------------------------------

today = date.today()
all_tasks = jordan.getAllTasksForDate(today)

plan = DailyPlan(plan_date=today, ownerId=jordan.ownerId)
plan.generatePlan(owner=jordan, pets=jordan.pets, tasks=all_tasks)

# ---------------------------------------------------------------------------
# Print schedule
# ---------------------------------------------------------------------------

pet_lookup = {p.petId: p for p in jordan.pets}
print_schedule(plan, jordan, pet_lookup)

# ---------------------------------------------------------------------------
# Demo — sortByTime()
# ---------------------------------------------------------------------------

print(f"{'=' * 52}")
print("  sortByTime() — tasks sorted by scheduledTime")
print(f"{'=' * 52}")
plan.sortByTime()
for t in plan.tasks:
    print(f"  {t.scheduledTime or 'No time':>6}  |  {t.title}")
print()

# ---------------------------------------------------------------------------
# Demo — filterBy()
# ---------------------------------------------------------------------------

print(f"{'=' * 52}")
print("  filterBy(status='pending')")
print(f"{'=' * 52}")
pending = plan.filterBy(status="pending")
for t in pending:
    print(f"  [{t.status}]  {t.title}")
print()

print(f"{'=' * 52}")
print("  filterBy(pet_name='Mochi')")
print(f"{'=' * 52}")
mochi_tasks = plan.filterBy(pet_name="Mochi", pets=pet_lookup)
for t in mochi_tasks:
    print(f"  {t.scheduledTime or 'No time':>6}  |  {t.title}")
print()

print(f"{'=' * 52}")
print("  filterBy(status='pending', pet_name='Luna')")
print(f"{'=' * 52}")
luna_pending = plan.filterBy(status="pending", pet_name="Luna", pets=pet_lookup)
for t in luna_pending:
    print(f"  [{t.status}]  {t.title}")
print()

# ---------------------------------------------------------------------------
# Demo — markTaskCompleted() auto-schedules next occurrence
# ---------------------------------------------------------------------------

print(f"{'=' * 52}")
print("  Auto-scheduling next occurrence on completion")
print(f"{'=' * 52}")

# pick the two tasks we want to demonstrate
walk_task  = next(t for t in mochi.tasks if t.title == "Morning Walk")   # DAILY
brush_task = next(t for t in luna.tasks  if t.title == "Brushing")        # WEEKLY

print(f"\n  Before completing tasks:")
print(f"  Mochi tasks : {len(mochi.tasks)}")
print(f"  Luna tasks  : {len(luna.tasks)}")

mochi.markTaskCompleted(walk_task.taskId)   # DAILY  → spawns tomorrow's task
luna.markTaskCompleted(brush_task.taskId)   # WEEKLY → spawns next-week's task

print(f"\n  After completing '{walk_task.title}' (daily) and '{brush_task.title}' (weekly):")
print(f"  Mochi tasks : {len(mochi.tasks)}")
print(f"  Luna tasks  : {len(luna.tasks)}")

print(f"\n  New tasks auto-created:")
new_walk  = next(t for t in mochi.tasks if t.title == "Morning Walk" and t.status == "pending")
new_brush = next(t for t in luna.tasks  if t.title == "Brushing"     and t.status == "pending")
print(f"  [{new_walk.frequency.value}]  {new_walk.title:<22} due on {new_walk.createdAt}  status={new_walk.status}")
print(f"  [{new_brush.frequency.value}] {new_brush.title:<22} due on {new_brush.createdAt}  status={new_brush.status}")
print()

# ---------------------------------------------------------------------------
# Demo — detectConflicts()
# ---------------------------------------------------------------------------

print(f"{'=' * 52}")
print("  detectConflicts() — no conflicts expected")
print(f"{'=' * 52}")
conflicts = plan.detectConflicts(pets=pet_lookup)
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No scheduling conflicts found.")
print()

# Force a conflict: give Flea Medication the same slot as Morning Walk (07:00)
flea_task = next(t for t in plan.tasks if t.title == "Flea Medication")
flea_task.scheduledTime = "07:00"

# Force a cross-pet conflict: give Luna's Feeding the same slot (07:00)
feeding_task = next(t for t in plan.tasks if t.title == "Feeding")
feeding_task.scheduledTime = "07:00"

print(f"{'=' * 52}")
print("  detectConflicts() — with forced conflicts")
print(f"{'=' * 52}")
conflicts = plan.detectConflicts(pets=pet_lookup)
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No scheduling conflicts found.")
print()
