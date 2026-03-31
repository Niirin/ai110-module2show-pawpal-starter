# PawPal+ Project Reflection

## 1. System Design

Core actions a user should be able to perform:
- Add/register a pet and their information
- Add (daily) tasks related to that pet
- Prioritize the tasks and make it into a pet care plan 

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- My UML contains the following object classes and methods: 
- pet: attributes: petId, name, species, breed, age, weight, sex, medicalNotes, activityLevel, feeding, specialNeeds, tasks(list of task for that pet); methods: addTask, updateInfo, removeTask, getTasks, getTaskForDate, getImportantInfo
- owner: userId or ownerId, name, email, preferences, pets; methods: addPet, removePet, updatePet, getPet, getAvailableTime
- task: taskId, petId, title, category, duration, priority, frequency, preferredTime, isReq, notes, status; methods: markCompleted, markSkipped, updatePriority, updateTask, isDueOn, getTaskSummary
- dailyPlan: planId, date, ownerId, tasks, totalEstTime, explanation; methods: generatePlan(owner, pet(s), task(s)), sortByPriority, getPlanSummary, getReason

- A summary of the relationships modeled:
    - Owner → Pet: one owner can have many pets (1 to 0..*)
    - Pet → Task: one pet can have many tasks (1 to 0..*)
    - Owner → DailyPlan: one owner generates many daily plans (1 to 0..*)
    - DailyPlan → Task: each plan schedules one or more tasks (1 to 1..*)

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- `Task.frequency` was changed from a plain `String` to a `Frequency` enum (`DAILY`, `TWICE_DAILY`, `WEEKLY`, `BIWEEKLY`, `AS_NEEDED`). The original freeform string had no validation, meaning `isDueOn()` could silently break on a typo. An enum makes the allowed values explicit and prevents that class of bug entirely.
- Three date fields were added to `Task`: `createdAt`, `scheduledTime`, and `lastCompleted`. Without these, `isDueOn()` had no anchor to calculate recurrence from, and `markCompleted()` had nowhere to record when a task was finished. These fields are what connect a task's definition to its actual history and assigned time slot.
- `DailyPlan.generatePlan()` was split into two private helper methods: `_filterDueTasks()` and `_fitToTimeWindow()`. The original single method was responsible for filtering, prioritizing, and time-fitting all at once, making it hard to test or debug one step in isolation. Separating the steps means each piece of scheduling logic can be verified independently.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
- One tradeoff of this scheduler is: ease of implementation but not too realistic. It works by including required tasks first, then fill remaining time with optional tasks by priority. However, it does not deeply consider preferred times, task order dependencies, medication timing rules, or whether two tasks should happen far apart.
- This tradeoff is reasonable for this scenario because this is the 1st iteration of the system. The current implementation is practical and easy to understand as well as use. The more complex inner logic can be added in later versions.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
