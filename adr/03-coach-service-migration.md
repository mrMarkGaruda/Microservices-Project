# ADR-003: Coach Service Migration `SESSION 2`

## Context

The main app was getting slow because the WOD (Workout of the Day) feature was too heavy and took time to run. To fix this and make things easier to manage, we moved the WOD part into its own service called "coach".

## Migration Steps
1. **Moved the WOD Code**  
    - Took the WOD generator out of the main app and put it into a new service called coach.
    - The coach has two parts you can call: `/generate-wod` and `/health`.

2. **Set Up the Rules (API Contract)**  
    - Made a clear rule for how the main app talks to the coach (using OpenAPI).
    - The main app sends the user’s email and a list of exercises to skip.

3. **Used a Safe Switch (Strangler Fig)**  
    - Added a setting called `USE_COACH_MICROSERVICE`.
    - If it’s turned on, the main app sends WOD requests to the coach.
    - If the coach is down, it uses the old way so nothing breaks.

4. **Coach Doesn’t Store Info**  
    - The coach just makes workouts. It doesn’t save any user data.
    - The user’s workout history stays in the main app.

5. **Made It Easy to Run and Grow**  
    - Both the coach and main app run in containers using Docker Compose.
    - You can run more than one coach to handle more users.

6. **Tested Everything**  
    - Used a tool called k6 to make sure the WOD feature can handle lots of users.
    - Checked that both apps are healthy and give the right answers.

## Reasoning Behind Choices
- **Strangler Fig Pattern:**  
    Lets us switch to the new system slowly, without shutting anything down. If something breaks, we can go back easily.

- **Coach Doesn’t Store Data:**  
    The coach just makes workouts. It doesn’t keep any info, so it’s easy to run more than one.

- **Clear API Docs (OpenAPI):**  
    Makes it easy for developers and tools to understand how the apps talk to each other.

- **Simple HTTP Calls:**  
    The main app and coach talk using normal web requests, which is easy to set up.

- **Docker Compose:**  
    Helps us run everything together on one machine for testing and launching.

## Lessons Learned

- Moving heavy code into a separate service makes the app faster and easier to manage.
- Using clear rules (API contracts) and switches (feature flags) helps make safe changes.
- Services that don’t store data (stateless) are easier to grow and fix.