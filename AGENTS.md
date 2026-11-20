# AGENTS.md

Guidance for AI agents (and people) working on this project.

## About the project

This repository contains the workshop code for trip-planning agent that remembers travelers across conversations. It is a teaching project, for developers who are new to Redis Agent Memory, LangGraph or AI agents. Participants start from an agent with no memory and add it exercise by exercise.

### What this project aims to demonstrate

The goal is to give them a working, readable example of how to give an agent memory, and why it is done that way. It aims to show:

- **Working memory:** what the conversation (session) holds, when it is read and written, and how it reaches the model.
- **Long-term memory:** how it differs from working memory, what it holds, and the two ways it is filled: the model saving a fact with a tool, and the service extracting facts from sessions by itself.
- **Retrieving memory:** the model deciding when to search (a tool), against the code always searching first (a step in the graph), and what each costs and gives.
- **Agent workflows:** tool calling, and how a workflow is put together (state, nodes, routing, streaming).
- **Semantic caching:** reusing an answer to a question that was already asked, what is safe to cache and what is not (anything personal or live), and the cost and latency it saves.
- **Integration:** how a framework (LangGraph), a model provider (OpenAI), an external tool server (Google Maps over MCP) and a data store (Redis Agent Memory) are wired into one app.

It does not aim to demonstrate complete trip-planning logic, or production-ready authentication and authorisation. Those stay simple on purpose.

## Design principles

The more complicated the codebase gets, the harder it is to follow, and a workshop that can't be followed teaches nothing. Balance three things:

- **Simplicity:** a reader only needs to know what the exercise needs. Use the fewest tools, libraries and concepts, and do not pick one that readers would have to learn first. For example, the front end is plain HTML, CSS and JavaScript, not React, because React would assume the reader knows it.
- **Longevity:** it is easy to test, and to move to another provider or framework.
- **Solid foundations:** the way the code is structured and organised is a pattern that would hold up if it were applied in production. This is about the architecture and the patterns, not about making the app's own features production-grade. The features stay as simple as the exercise needs.

Choose a structure that would carry over to production when it is cheap and keeps the code easy to read, such as separating layers and not hard-coding settings. Leave out anything that only matters for a production version of the features themselves, or that would bury the exercise under extra code, extra layers or extra files.

When something is left out on purpose, say so in a comment or the README, so readers know it is a choice. A new abstraction, helper or file has to earn its place: if only one thing uses it, it is probably too much.

The rules for changing the project (packages, code style, the exercise files, the architecture diagram and the front end) are in [CONTRIBUTING.md](./CONTRIBUTING.md). They apply to every change.

## What to leave out during development unless asked for

Heavy production concerns are not goals of this project, and adding them would make the code harder to follow. Do not build them unless you are asked to:

- Concurrent updates and race conditions
- Data privacy, personal data handling, authentication and authorisation (the traveler's name on the login screen stands in for a real login)
- Rate limiting, abuse, hostile input and other hardening
- Scaling, retries, failover, monitoring and other operations work

If one of these is truly worth knowing, say so in one line at the end, as a note.
