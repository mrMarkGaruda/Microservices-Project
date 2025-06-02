# ADR-002: Coach Service Migration

## Context

The workout of the day api is kind of slow it takes 3 to 5 seconds to respond. This means we can only support about 120 users at the same time. So to fix this, we kind of need to move the WOD feature into its own service, but we want to do it without any downtime.



## Decision

We’ll build a new so called "coach" microservice for our api WOD generation. We’ll use the strangler fig pattern so the switch happens slowly and safely, with no break in the service.



## Migration Steps



### Phase 1: Create the microservice

- Move the WOD (Workout of the Day) code into a new Flask app

- Run it on port 5001

- Start with just 6 simple workout templates

- Add a health check so we know it’s running okay



### Phase 2: Strangler Fig Implementation

- Add a setting called `USE_COACH_MICROSERVICE` to switch between the old and new code

- If the setting is going to be on, send wod requests to the new coach service

- If something goes wrong, it's going to fall back to the old way of generating WODs

- Make sure there’s going to be a timeout as well as error handling so users don’t get stuck waiting for it



### Phase 3: Data Separation

- The coach service only creates workouts it doesn’t store anything 

- User history is going to stay in the main app’s database

- To avoid repeating the excercises, the main app will send a list of exercises to skip in the request



### Phase 4: Gradual Migration

- So we will start by sending 0% of traffic to the coach service

- Then watch how it performs and check for any errors

- Gradually increase the traffic as everything looks good

- Once it’s fully working and stable, it will remove the old code



## Rationale

### Strangler Fig Pattern

- It would let us move features carefully with no downtime

- Going to make it very easy to go back if something goes wrong

- Much more safer than switching everything all at once

- Helps us try out both old and new versions



### Service Boundaries

- Coach service: it will only make WODs, pretty fast and doesn’t keep data 

- Main app: going to handle user info, workout history, as well as login

- keeps these parts separate which would avoid confusion and errors



### Technology Choices

- Use flask to match our current system

- Use docker to package and run the apps easily

- Use environment variables to set configs safely

- Use http rest api so the services can talk to each other



## Benefits

- It can grow the WOD service separately from the main app

- Quicker responses: 1-2 seconds instead of 3-5 seconds

- Issues in the coach service will not crash the whole app

- Would be way easier to test and update just the coach service

- Ready for adding new coach features later



## Risks

- Possible delays when services will talk over the network

- Working with more services can be more complex

- Need to handle how services depend on each other

- Way more chances for failure since it is split into parts



## Monitoring

- Both services will have health check endpoints to show that they are working fine

- It's going to track how fast each service responds

- Keep an eye on how often errors happen

- Watch how often the system changes back to the old service