# ADR 03: Queue-based WOD Generation

## Context

To make the app faster and handle more users, we added a queue system with RabbitMQ. Now, the main app sends WOD jobs to the queue, and the coach service will pick them up, do the work, and save the results all in the background.


## Choices Made

- **RabbitMQ:** Used to send workout jobs because it's reliable and works well with Docker.
- **DLQ (Dead Letter Queue):** If a job fails 3 times, it’s moved to a special queue to check later.
- **Message Info:** Each message has the user’s email to know who the workout is for.
- **Queue Limits:** Messages disappear after 1 minute, and the queue can hold up to 100 messages.
- **Retry System:** If a job fails, the system tries it again up to 3 times.
- **Failure Test:** The coach service is set to fail 20% of jobs on purpose to test the retry system.
- **Saving Workouts:** The coach service saves the workouts it creates.
- **Cron Job:** A script (`cron_job.py`) runs daily to tell the app to make workouts for all users.

## Improvements & Future Work

- **Monitoring:** Watch the queue size and DLQ, set up alerts if something goes wrong.
- **Schema Validation:** Make sure every message is in the correct format before it's used.
- **Metrics:** Track how long jobs take, how many fail, and how often they retry.
- **DLQ Processing:** Add a script to retry failed messages or send alerts.
- **Security:** Use strong passwords and limit access to RabbitMQ.
- **Scalability:** Add more consumers to handle more jobs at the same time.
- **Audit Trail:** Save a record of each workout created, with time and date.

## References

- [docs/02-students_assignment.md](../docs/02-students_assignment.md)