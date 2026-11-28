# Contributing

How to change this project. Participants only need the [README](README.md). Start with the aims and the design principles below: they decide how much to build and what to leave out, and the rules after them apply to every change.

## About the project

This repository contains the workshop code for a trip-planning agent that remembers travelers across conversations. It is a teaching project, for developers who are new to Redis Agent Memory, LangGraph or AI agents. Participants start from an agent with no memory and add it exercise by exercise.

### What this project aims to demonstrate

The goal is to show, in a working and readable example, how an agent reuses knowledge at three levels, and why it is done that way:

- **Earlier in the same conversation** (working memory): what was said so far.
- **About the traveler, from past conversations** (long-term memory): what it learned and kept.
- **Answers it already gave to similar questions** (the semantic cache): what it can reuse without asking the model again.

It aims to show:

- **Working memory:** what the conversation (session) holds, when it is read and written, and how it reaches the model.
- **Long-term memory:** how it differs from working memory, what it holds, and the two ways it is filled: the model saving a fact with a tool, and the service extracting facts from sessions by itself.
- **Retrieving memory:** the model deciding when to search (a tool), against the code always searching first (a step in the graph), and what each costs and gives.
- **Agent workflows:** tool calling, and how a workflow is put together (state, nodes, routing, streaming).
- **Semantic caching:** reusing an answer to a question that was already asked, what is safe to cache and what is not (anything personal or live), and the cost and latency it saves.
- **Integration:** how a framework (LangGraph), a model provider (OpenAI), an external tool server (Google Maps over MCP) and a data store (Redis Agent Memory) are wired into one app.

It does not aim to demonstrate complete trip-planning logic, or production-ready authentication and authorisation. Those stay simple on purpose.

## Motivations

This workshop is written for a room of developers from outside Redis, such as [WeAreDevelopers](https://www.wearedevelopers.com/) or [Agent Con](https://globalai.community/e/2yasbdfb), general developer conferences that Redis does not run. Not everyone there uses a Redis enterprise service, and what they learn should still be useful to them afterwards. So the workshop uses both:

- **Redis Agent Memory,** the enterprise service, holds what the agent remembers.
- **Open source RedisVL** is used for other parts, so a reader can use the same idea with Redis they run themselves.

Using both shows what each one gives, and it keeps the workshop from being only a product demo or only a library tutorial.

What decides the balance is who is in the room. At a Redis event, if the audience is mostly general developers, keep the balance as it is. If it is mostly Redis customers, you can lean more on the enterprise features - create a fork or a branch of this repostory and make changes there. Keep the audience in mind before you swap one for the other.

## Design principles

The more complicated the codebase gets, the harder it is to follow, and a workshop that can't be followed teaches nothing. Balance three things:

- **Simplicity:** a reader only needs to know what the exercise needs. Use the fewest tools, libraries and concepts, and do not pick one that readers would have to learn first. For example, the front end is plain HTML, CSS and JavaScript, not React, because React would assume the reader knows it.
- **Longevity:** it is easy to test, and to move to another provider or framework.
- **Solid foundations:** the way the code is structured and organised is a pattern that would hold up if it were applied in production. This is about the architecture and the patterns, not about making the app's own features production-grade. The features stay as simple as the exercise needs.

Choose a structure that would carry over to production when it is cheap and keeps the code easy to read, such as separating layers and not hard-coding settings. Leave out anything that only matters for a production version of the features themselves, or that would bury the exercise under extra code, extra layers or extra files.

When something is left out on purpose, say so in a comment or the README, so readers know it is a choice. A new abstraction, helper or file has to earn its place: if only one thing uses it, it is probably too much.

## Before you start developing

### Update the packages

Update the packages first, every time.

1. Run `uv lock --upgrade` to move every package to its latest version, including major versions. Raise the minimum versions in `pyproject.toml` to match.
2. Run `uv sync`.
3. Run `uv run python scripts/check.py`, then start the app and use it for a few messages to check that it still works. The `libraries/` copy of marked in `frontend/` is updated the same way: copy the new file from npm, with its license.
4. If a package cannot move to its latest version, leave it and say why in the commit message.

### Use the official agent skills

When what you are building is covered by an official skill, load it and follow it instead of working from memory. These libraries change often, and the skills carry the current APIs and patterns.

- **LangChain and LangGraph:** [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills). Use `langgraph-fundamentals` for the workflow (state, nodes, edges, streaming), `langchain-fundamentals` for tools, and `langchain-dependencies` for package versions.
- **Redis:** [redis/agent-skills](https://github.com/redis/agent-skills). Use `iris-development` for Agent Memory, `redis-semantic-cache` for the semantic cache, and `redis-core` for data structures and key naming.
- **Trying the page in a browser:** `playwright-cli`, for checking the pages you changed.

## Changing the code

### Structure

Everything about the agent is in `backend/modules/ai/`:

- `agent_workflow/`:
  - `graph.py` connects the steps.
  - `nodes.py` holds what each step does.
  - `tools/` holds what the model can call.
  - `index.py` runs one turn.
- `agent_memory/` is Redis Agent Memory.
- `semantic_cache/` is the RedisVL cache.
- `providers/` is the model.
- `types.py` has the types that more than one file uses.

Code outside `ai/` imports from `backend.modules.ai`, whose `__init__.py` lists what it may use. Files inside `ai/` import each other by their full path. `chat/` and `user/` hold the routes. Routes stay thin and hand the real work to `ai/`.

### Code style

- Use whole words for names, with no abbreviations and no single letters (except an iterator such as `i`). Name a variable for what it holds.
- A blank line after a function's docstring makes the function easier to read.
- Do not add a helper, a layer or a file that only one thing uses. A reader should not have to follow code that the lesson does not need.
- Do not add logs that are not needed.
- Fix a problem at its source, not where it shows up.

### The exercise files

The exercise files are notebook-style scripts (Jupytext percent format): the `# %%` lines split a file into cells, with the explanation as markdown cells. The files in the repository are the **starter**: each step a participant writes is a stub with a `# TODO` and a hint, written so the app still runs without memory.

- A TODO of several lines is a block: `# TODO start (Exercise 2B): ...` at the top, the hint, the placeholder `return` or `raise`, and `# TODO end (Exercise 2B)` at the bottom.
- A TODO of one line is a single comment with no `start` and `end` markers, for example `# TODO (Exercise 5): search the traveler's memories.`
- A stub reads more easily with some air around it: we usually leave a blank line before a `# TODO`, between its hint and the placeholder code, before `# TODO end`, and after it.
- Under each step is a collapsed "Show solution" block (`<details>`) with the finished code. Keep every existing comment when you turn code into a stub.

The finished files are in `docs/solutions/<step>/`, at the same path as in the repository, and `./solve` copies them over. Each one has its step solved and every earlier step in the same file, and its headings say "(solved)". When you change exercise code, update the stub, the "Show solution" block and the file in `docs/solutions/` together, and keep the README exercise and the diagram saying the same thing.

### The finished app

`./solve run` builds a copy of the project with every solution in `build/solved/` and starts it from there with `uv run uvicorn backend.main:app --app-dir build/solved`. Your own files are not changed. `--port` picks the port, and 5010 is the default.

`./solve all --out <folder>` only builds the copy, for example to deploy it. The copy leaves out `.env` (set the keys as environment variables where you host it), `.git`, `.venv`, `docs/`, `build/` and caches, and it has an `app.py` at the top for hosts that look for the app there. It only builds over a folder that `./solve` made (it has a `.solve-build` file), and it refuses the project folder and the folders around it.

`./solve all` without `--out` applies every solution to your own files. A later step has everything an earlier step did in the same file, so each file is written once, from the last step, and your own versions are saved in `.solve-backup/` first.

A new step in `docs/solutions/` is picked up by all three.

## The architecture diagram

`frontend/architecture.html` is a single page: an inline SVG, its styles, and a script at the bottom. It shows how the pieces fit and lights up what each exercise adds. It is linked from the README and from the app, so it has to match the code.

Update it whenever you add, remove, rename or reroute a piece of the app, or change an exercise.

- **Which exercise adds a piece:** give the piece (and the arrows to and from it) a `data-ex="N"`. It is greyed out until the diagram reaches exercise N.
- **Numbers on the steps:** the steps of the graph (`data-step`) are numbered in order, and a step that is not built yet has no number. A new step goes into the list in `render()`.
- **Text that changes with the exercise:** `data-show-from` and `data-hide-from` show or hide a label from a given exercise on.
- **The text above the diagram:** the title and the description of each exercise are in the `STAGES` table at the top of the script. Change `LAST_STAGE` if you add an exercise.
- **Tooltips:** give every piece a `data-info`, written for a reader who is new to it.
- **Reads and writes in the step tooltips:** a step of the graph also has `data-reads` and `data-writes`, the state fields it reads and the fields it writes, as a comma-separated list (`data-writes=""` for a step that writes nothing). They build the "Reads:" and "Writes:" lines of its tooltip, so they must match what the step in `nodes.py` does with `AgentState`. `data-writes-when` adds a condition to the writes, such as "on a hit".
- **Logos:** they live in `frontend/icons/`. Use a logo as its owner provides it (their light or dark version, not recoloured) and follow their brand guidelines.
- **Checking it:** open the page, step through every exercise with the arrow keys, and look for text that overflows its box, arrows that run through boxes, and anything that stays lit too early.

Keep the diagram free of anything the code does not do.

## Front end

The page is plain HTML, CSS and JavaScript with no build step. Keep three things apart: HTML holds the content and structure (which elements exist, their order and text), CSS holds the look, and JavaScript holds the behaviour. The look means how things are presented: colours, fonts, sizes, spacing, borders, shadows, layout and animation.

**HTML**
- Use semantic elements, with page landmarks (`header`, `main`, `nav`, `aside`, `footer`), a sensible heading order, lists for lists, and `button` and `a` for what each is meant for. Use a `div` or `span` only when no semantic element fits.
- Give every form input a `label`.
- Build repeated markup from a `<template>` in `index.html`, not with `createElement` calls.

**Accessibility**
- Use native elements before ARIA, and keep keyboard use and visible focus working.
- Give images alt text, keep contrast readable, and respect reduced motion.

**CSS and themes**
- A theme is a folder in `frontend/styles/themes/<theme-name>/` with a shared `theme.css` and one stylesheet for each part of the page. A new look is a new theme, written in CSS only.
- Put colours, shadows, borders and spacing in CSS variables in `theme.css`, so a theme can change them in one place.
- Use `rem` for text and spacing, and `px` for borders, radii and shadows.
- Name classes for what a thing is, not how it looks. No inline styles and no `!important`. The layout has to work on a phone.

**JavaScript**
- JavaScript decides what to show, never how it looks. Do not set `element.style` or inline `style` attributes. Switch a class or an attribute (`classList`, `hidden`, `data-*`) and let the CSS do the rest.
- One component owns one piece of the page. Network calls live in `services/`, and components do not call `fetch`.
- State lives in data, not in the page. No globals.
- Text from the user is escaped before it goes into `innerHTML`. The agent's replies go through `utils/message-formatter.js`.
