# Contributing

How to change this project. Participants only need the [README](README.md). Read the aims and the design principles in [AGENTS.md](./AGENTS.md) first, since they decide how much to build and what to leave out.

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

Each feature is a folder in `backend/modules/` with up to three layers. `api/` holds the routes, `domain/` holds the logic, and `data/` holds the calls to Redis Agent Memory. The agent has its own module, `ai/agent_workflow/`: `graph.py` connects the steps, `nodes.py` holds what each step does, and `tools/` holds what the model can call. Routes and tools stay thin and hand the real work to the domain and data layers.

### Code style

- Use whole words for names, with no abbreviations and no single letters (except an iterator such as `i`). Name a variable for what it holds.
- Do not add a helper, a layer or a file that only one thing uses. A reader should not have to follow code that the lesson does not need.
- Do not add logs that are not needed.
- Fix a problem at its source, not where it shows up.

### The exercise files

The exercise files are notebook-style scripts (Jupytext percent format): the `# %%` lines split a file into cells, with the explanation as markdown cells. A part that a participant writes is marked in the text, and a part that is already written says "(solved)". When you change one, keep its explanation, the README exercise and the diagram saying the same thing.

### Seeding

`scripts/seed_agent_memory.py` creates memories for the demo travelers. `--reset` first deletes every memory of those travelers, including the ones the service extracted, then creates them again.

## The architecture diagram

`frontend/architecture.html` is a single page: an inline SVG, its styles, and a script at the bottom. It shows how the pieces fit and lights up what each exercise adds. It is linked from the README and from the app, so it has to match the code.

Update it whenever you add, remove, rename or reroute a piece of the app, or change an exercise.

- **Which exercise adds a piece:** give the piece (and the arrows to and from it) a `data-ex="N"`. It is greyed out until the diagram reaches exercise N.
- **Numbers on the steps:** the steps of the graph (`data-step`) are numbered in order, and a step that is not built yet has no number. A new step goes into the list in `render()`.
- **Text that changes with the exercise:** `data-show-from` and `data-hide-from` show or hide a label from a given exercise on.
- **The text above the diagram:** the title and the description of each exercise are in the `STAGES` table at the top of the script. Change `LAST_STAGE` if you add an exercise.
- **Tooltips:** give every piece a `data-info`, written for a reader who is new to it.
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
