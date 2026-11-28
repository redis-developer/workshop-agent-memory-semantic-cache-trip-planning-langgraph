# AGENTS.md

Guidance for AI agents working on this project.

This is a teaching project: a trip-planning agent that remembers travelers, which participants build exercise by exercise. Before you change anything, read [CONTRIBUTING.md](./CONTRIBUTING.md). Its aims and design principles decide how much to build and what to leave out, and its rules (packages, code style, the exercise files, the architecture diagram and the front end) apply to every change.

## What to leave out during development unless asked for

Heavy production concerns are not goals of this project, and adding them would make the code harder to follow. Do not build them unless you are asked to:

- Concurrent updates and race conditions
- Data privacy, personal data handling, authentication and authorisation (the traveler's name on the login screen stands in for a real login)
- Rate limiting, abuse, hostile input and other hardening
- Scaling, retries, failover, monitoring and other operations work

If one of these is truly worth knowing, say so in one line at the end, as a note.
