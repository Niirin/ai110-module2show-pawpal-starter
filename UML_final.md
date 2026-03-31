# UML Diagram — PawPal+ (Final)

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
        +getAllTasks() List~Task~
        +getAllTasksForDate(date: Date) List~Task~
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
        +markTaskCompleted(taskId: String)
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
        +Optional~String~ scheduledTime
        +Optional~Date~ lastCompleted
        +int dailyCompletionCount
        +markCompleted()
        +markSkipped()
        +updatePriority(priority: int)
        +updateTask(info: Dict)
        +isDueOn(date: Date) bool
        +getNextOccurrence() Optional~Task~
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
        +sortByTime()
        +filterBy(status: String, pet_name: String, pets: Dict) List~Task~
        +detectConflicts(pets: Dict) List~String~
        +getTasksByPet() Dict
        +getPlanSummary() Dict
        +getReason() String
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Owner "1" --> "0..*" DailyPlan : generates
    DailyPlan "1" --> "0..*" Task : schedules
    DailyPlan "0..*" --> "1..*" Pet : plans for
    Task "0..*" --> "1" Frequency : uses
    Task ..> Task : getNextOccurrence()
```
