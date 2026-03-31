# UML Diagram — PawPal+

```mermaid
classDiagram
    class Frequency {
        <<enumeration>>
        DAILY
        TWICE_DAILY
        WEEKLY
        BIWEEKLY
        AS_NEEDED
    }

    class Owner {
        +String ownerId
        +String name
        +String email
        +Dict preferences
        +int availableMinutes
        +List~Pet~ pets
        +addPet(pet: Pet)
        +removePet(petId: String)
        +updatePet(petId: String, info: Dict)
        +getPet(petId: String) Pet
        +getAvailableTime() int
    }

    class Pet {
        +String petId
        +String name
        +String species
        +String breed
        +int age
        +float weight
        +String sex
        +String medicalNotes
        +String activityLevel
        +Dict feeding
        +String specialNeeds
        +List~Task~ tasks
        +addTask(task: Task)
        +removeTask(taskId: String)
        +updateInfo(info: Dict)
        +getTasks() List~Task~
        +getTasksForDate(date: Date) List~Task~
        +getImportantInfo() Dict
    }

    class Task {
        +String taskId
        +String petId
        +String title
        +String category
        +Frequency frequency
        +int duration
        +int priority
        +String preferredTime
        +bool isReq
        +String notes
        +String status
        +Date createdAt
        +Date scheduledTime
        +Date lastCompleted
        +markCompleted()
        +markSkipped()
        +updatePriority(priority: int)
        +updateTask(info: Dict)
        +isDueOn(date: Date) bool
        +getTaskSummary() Dict
    }

    class DailyPlan {
        +String planId
        +Date date
        +String ownerId
        +List~String~ petIds
        +List~Task~ tasks
        +int totalEstTime
        +String explanation
        +generatePlan(owner: Owner, pets: List~Pet~, tasks: List~Task~)
        +_filterDueTasks(tasks: List~Task~, date: Date) List~Task~
        +_fitToTimeWindow(tasks: List~Task~, availableMinutes: int) List~Task~
        +sortByPriority()
        +getPlanSummary() Dict
        +getReason() String
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Owner "1" --> "0..*" DailyPlan : generates
    DailyPlan "1" --> "1..*" Task : contains
    DailyPlan "0..*" --> "1..*" Pet : plans for
    Task "0..*" --> "1" Frequency : uses
```

## Changes from original

| What changed | Where | Why |
|---|---|---|
| `Frequency` enum added | new class | Replaces freeform `frequency: str` — `isDueOn` needs a finite set of values |
| `Task.frequency` → `Frequency` type | `Task` | Uses enum instead of raw string |
| `Task.createdAt` added | `Task` | Anchor date for recurrence — `isDueOn` needs a start reference |
| `Task.scheduledTime` added | `Task` | Stores assigned time slot after `generatePlan` places the task |
| `Task.lastCompleted` added | `Task` | Lets `isDueOn` skip already-done tasks and compute gaps for weekly/biweekly |
| All `*Id` fields use UUID default | all classes | Objects can be created without manually passing IDs |
| `Owner.availableMinutes` added | `Owner` | Explicit field (e.g. `90`) used by scheduler — not buried in `preferences` dict |
| `DailyPlan.petIds` added | `DailyPlan` | Plan tracks which pets it covers without holding full `Pet` objects |
| `DailyPlan._filterDueTasks()` added | `DailyPlan` | Breaks `generatePlan` into a testable step — filters by due date |
| `DailyPlan._fitToTimeWindow()` added | `DailyPlan` | Breaks `generatePlan` into a testable step — trims tasks to available time |
