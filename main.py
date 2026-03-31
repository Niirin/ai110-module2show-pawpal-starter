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
# Setup — Tasks for Mochi
# ---------------------------------------------------------------------------

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
))

mochi.addTask(Task(
    petId=mochi.petId,
    title="Fetch & Play",
    category="enrichment",
    frequency=Frequency.DAILY,
    duration=20,
    priority=2,
    preferredTime="afternoon",
    isReq=False,
))

# ---------------------------------------------------------------------------
# Setup — Tasks for Luna
# ---------------------------------------------------------------------------

luna.addTask(Task(
    petId=luna.petId,
    title="Feeding",
    category="feeding",
    frequency=Frequency.TWICE_DAILY,
    duration=10,
    priority=3,
    preferredTime="morning",
    isReq=True,
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
))

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
