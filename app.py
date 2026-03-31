import streamlit as st
from pawpal_system import Owner, Pet, Task, DailyPlan, Frequency


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

# --- Initialize vault keys once ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Set up owner & pet"):
    if st.session_state.owner is None:
        pet = Pet(name=pet_name, species=species, breed="mixed", age=3, weight=10.0, sex="F")
        owner = Owner(name=owner_name, email="", availableMinutes=60)
        owner.addPet(pet)
        st.session_state.owner = owner
        st.session_state.pet = pet
        st.success(f"Created owner '{owner_name}' with pet '{pet_name}'!")
    else:
        st.info(f"Owner '{st.session_state.owner.name}' already exists. Reset below to start over.")

if st.button("Reset owner & pet"):
    st.session_state.owner = None
    st.session_state.pet = None
    st.success("Session cleared. You can set up a new owner and pet.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if st.session_state.pet is None:
        st.error("Set up an owner & pet first before adding tasks.")
    else:
        priority_map = {"low": 1, "medium": 2, "high": 3}
        task = Task(
            petId=st.session_state.pet.petId,
            title=task_title,
            category="general",
            frequency=Frequency.DAILY,
            duration=int(duration),
            priority=priority_map[priority],
            preferredTime="morning",
            isReq=False,
        )
        st.session_state.pet.addTask(task)
        st.success(f"Added task: {task_title}")

if st.session_state.pet and st.session_state.pet.tasks:
    st.write("Current tasks:")
    st.table([t.getTaskSummary() for t in st.session_state.pet.tasks])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a daily plan for all due tasks fitted to the owner's available time.")

if st.button("Generate schedule"):
    if st.session_state.owner is None or st.session_state.pet is None:
        st.error("Set up an owner & pet first.")
    elif not st.session_state.pet.tasks:
        st.error("Add at least one task before generating a schedule.")
    else:
        from datetime import date
        owner = st.session_state.owner
        plan = DailyPlan(plan_date=date.today(), ownerId=owner.ownerId)
        plan.generatePlan(owner, owner.pets, owner.getAllTasks())
        summary = plan.getPlanSummary()

        st.success(f"Scheduled {summary['taskCount']} task(s) — {summary['totalEstTime']} min total")
        st.markdown(f"**Plan explanation:** {summary['explanation']}")

        if summary["tasks"]:
            st.markdown("### Scheduled Tasks")
            st.table(summary["tasks"])
