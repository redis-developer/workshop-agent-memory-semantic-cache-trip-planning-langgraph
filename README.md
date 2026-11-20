# Workshop: Reuse Knowledge for Agentic AI

Learn how to provide your agent with working and long-term memory, and cut cost and latency by reusing what it already knows.

## Table of contents

- [Introduction](#introduction)
- [Set up](#set-up)
- [Run the application](#run-the-application)
- [Workshop instructions](#workshop-instructions)
- [If something looks wrong](#if-something-looks-wrong)
- [Resources](#resources)
- [Maintainers](#maintainers)

## Introduction

You will give a trip-planning agent two kinds of memory: what was said in this conversation, and what it should remember about the traveler next time. You will also add a semantic cache, so the agent can skip redundant LLM calls by reusing answers it already has.

- The agent runs on [LangGraph](https://langchain-ai.github.io/langgraph/), [FastAPI](https://fastapi.tiangolo.com/) and OpenAI.
- It finds places and the weather with [Google Maps](https://developers.google.com/maps/ai/maps-experience-agent-tools/reference/mcp).
- Everything it remembers is kept in [Redis Agent Memory](https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/).

## Set up

Get the code first.

**In GitHub Codespaces** (nothing to install): open the repository in a Codespace.

**On your machine** ([uv](https://docs.astral.sh/uv/) installed; it fetches Python 3.15 for you):

```bash
uv sync
cp .env.example .env
```

Each step below gives you an environment variable. Put it in `.env`, or in a Codespace add it as a secret (when it asks, or in your Codespaces settings).

### 1. OpenAI API key

Create a key on the [OpenAI API keys page](https://platform.openai.com/api-keys). This is your `OPENAI_API_KEY`.

### 2. Google Maps API key

The agent finds places and the weather through Google's own [Google Maps MCP server](https://developers.google.com/maps/ai/maps-experience-agent-tools/reference/mcp). It needs a key to connect. In the [Google Cloud console](https://console.cloud.google.com/), use a project with billing enabled, enable the **Maps Experience agent tools** API, and create an API key. This is your `GOOGLE_MAPS_API_KEY`.

### 3. Redis Agent Memory

These steps follow the [quickstart](https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/quickstart/).

**A database to attach it to.** The service needs an active Redis Cloud database on a Pro or Essentials plan, with a public endpoint, Redis Search and the default user enabled. See the [prerequisites and limitations](https://redis.io/docs/latest/operate/iris/agent-memory/create-service#prerequisites-and-limitations).

**Create the service.** In the [Redis Cloud console](https://cloud.redis.io/), choose **Agent Memory** under **Iris**, then **Create Agent Memory service** and **Customize settings**. Enter a name, pick the database and its `default` user, and under **Memory configuration** enter:

| Setting | Value |
|---|---|
| Short-term TTL | 1 day |
| Long-term TTL | 365 days |
| Extraction cadence | 1 minute |

Choose **Create**.

**Create an API key.** On the service's **Configuration** tab, choose **Create API key** and copy the key. The console shows it only once. This is your `IRIS_AGENT_MEMORY_API_KEY`.

**Copy the connection details.** On the same tab, copy the **Store ID** and the URL from the **URL List**. Use the endpoint's base address, including `https://`, and leave off the `/iris/data/v1/agent-memory/...` path. The URL is your `IRIS_AGENT_MEMORY_URL` and the Store ID is your `IRIS_AGENT_MEMORY_STORE_ID`.

**Add a memory type for traveler preferences.** In the console, open **Memory types & extraction** and choose **Add type**. Create `traveler_preference`, extracted from the conversation:

| Setting | Value |
|---|---|
| Description | Lasting travel preferences and standing instructions for a traveler |
| Extraction prompt | Extract a traveler preference only when the user states a lasting travel preference, a constraint or a standing instruction. Preserve explicit dietary requirements and food preferences. Ignore one-off trip details such as this trip's destination, dates or places. Put anything that does not fit another field under standing_instructions. |

| Field | Type | Description |
|---|---|---|
| `interests` | `list[str]` | Interests from this list: food, landmarks, offbeat, slow, outdoors, nightlife, culture |
| `budget` | `str` | One of low, mid or high |
| `group_size` | `str` | One of solo, pair, family or group |
| `dietary_requirements` | `list[str]` | Dietary requirements that affect recommendations, such as vegetarian or nut allergy |
| `food_preferences` | `list[str]` | Cuisines, flavors or dining preferences the traveler likes or dislikes |
| `standing_instructions` | `list[str]` | Rules to apply every time, such as "always include a rest day" or "avoid long walks" |

**Two more settings.** You will see their effect in exercise 2 and exercise 3. The exclusion prompt matters most: without it the service also saves what the agent said, and places you only asked about, as if they were facts about you.

| Setting | Suggested value |
|---|---|
| Automatic summarization | After about 12 messages, keeping the most recent 6 |
| Sensitive-data exclusions | Turn on **Semantic exclusions**, with the exclusion prompt below |

```text
Do not keep passwords, access tokens, recovery codes, passport or ID numbers, payment card information, or booking confirmation codes in long-term memory. Do not keep what the assistant said or suggested, weather or other facts about a place, questions the traveler only asked, or places they only asked about. Keep only what the traveler states about themselves: lasting preferences, and trips they say they took.
```

This is advisory: it steers what the service extracts, and does not guarantee it.

### 4. Check it

```bash
uv run python scripts/check.py
```

It tests your memory service, OpenAI and Google Maps, and says what is missing or wrong.

## Run the application

### Start the app

```bash
uv run uvicorn backend.main:app --port 3000 --reload      # restarts when you save a file
```

Open http://localhost:3000 (in a Codespace, open port 3000) and type a name to log in. The name is the traveler's ID, so what the agent learns about you is kept under it.

### Seed some travelers (optional)

```bash
uv run python scripts/seed_agent_memory.py
```

This gives three travelers (ashwin, bhavana and kyle) some memories already, so there is something to find in exercises 4 and 5. Log in with one of those names to use them. Add `--reset` to delete their memories and start them over.

## Workshop instructions

You spend your time on the memory code. The rest of the app is already written. The app you start with has no memory at all, and each exercise adds one piece.

To see how the pieces fit together, and which ones each exercise adds, open the [architecture diagram](frontend/architecture.html). With the app running, it is at http://localhost:3000/architecture.html.

### How to work on the files (your choice)

**In your own editor.** Open the files from the table, edit them and save. The running app only sees what you save, and `--reload` restarts it when you do.

**Or run them as notebooks in JupyterLab (optional).** The exercise files can be run cell by cell, so you can try a step on its own before the app uses it. Register the kernel once (a Codespace already has it), then start JupyterLab:

```bash
uv run python -m ipykernel install --sys-prefix --name workshop-agent-memory-playbook-trip-planning-python --display-name "Reuse Knowledge for Agentic AI" --env PYTHONPATH "$(pwd)"
uv run jupyter lab
```

Right-click an exercise file and choose **Open With → Notebook**. When it asks for a kernel, choose **Reuse Knowledge for Agentic AI**: it is the one with this project's packages, so a cell that says a module is missing is on another kernel.

### Overview

#### Part 1: Agent memory

| Exercise | What to do | Relevant files |
|---|---|---|
| 1. See what no memory looks like | Run the app and watch it forget | none |
| 2. Working memory | Remember the conversation so far | [`conversation_repository.py`](backend/modules/chat/data/conversation_repository.py), [`chat_service.py`](backend/modules/chat/domain/chat_service.py) |
| 3. Storing long-term memory | Let the model save a lasting fact | [`profile_repository.py`](backend/modules/user/data/profile_repository.py), [`memory_tools.py`](backend/modules/ai/agent_workflow/tools/memory_tools.py) |
| 4. Retrieving long-term memory (the model decides) | Let the model search what it saved | [`profile_repository.py`](backend/modules/user/data/profile_repository.py), [`memory_tools.py`](backend/modules/ai/agent_workflow/tools/memory_tools.py) |
| 5. Retrieving long-term memory (the code decides) | Look up memories before the agent runs | [`nodes.py`](backend/modules/ai/agent_workflow/nodes.py), [`graph.py`](backend/modules/ai/agent_workflow/graph.py) |

#### Part 2: Semantic cache

| Exercise | What to do | Relevant files |
|---|---|---|
| 6. Semantic caching: check the cache | Find a stored answer for a question with a similar meaning, and skip the agent on a match | [`nodes.py`](backend/modules/ai/agent_workflow/nodes.py), [`graph.py`](backend/modules/ai/agent_workflow/graph.py) |
| 7. Semantic caching: store in the cache | Keep answers that are worth reusing, so similar questions find them | [`nodes.py`](backend/modules/ai/agent_workflow/nodes.py), [`graph.py`](backend/modules/ai/agent_workflow/graph.py) |

### Exercises

Most exercises have two steps:

- **Step A: the memory service.** Write the calls to Redis Agent Memory. You can try them on their own, and the result shows in the **Memory** tab.
- **Step B: the agent.** Connect it to the agent, as a tool or as a step in the graph.

Stuck? Each exercise gives a `./solve` command. It saves your version of the files, then copies the finished code over them. A solution includes what the earlier ones in the same file did, so run them in order if you skip one.

#### Exercise 1: see what no memory looks like

Nothing to write. Run the app and ask for a 3-day food trip in Tokyo, then say your budget is mid-range and ask for a plan. Then press **New session** and ask "can you adjust it for a family of four?". The assistant has no idea what you mean. Without memory, every conversation starts from nothing.

#### Exercise 2: working memory

Make the agent remember the conversation so far.

1. **Step A.** Add each message to the session in Redis Agent Memory, and read the session back.

   Skip ahead with the solution: `./solve 2a`
2. **Step B.** Before each model call, rebuild the prompt from the session, so the model sees the conversation. Ask "which city did I just ask about?" to try it. Then change how much of it the model gets, and watch what it forgets.

   Skip ahead with the solution: `./solve 2b`

Full solution: `./solve 2`

#### Exercise 3: storing long-term memory (the model decides)

Make a lasting fact outlive the conversation.

1. **Step A.** Create a long-term memory with its text, its owner (the traveler), a type (semantic for a preference, episodic for something that happened) and topics.

   Skip ahead with the solution: `./solve 3a`
2. **Step B.** Write the `save_memory` tool and give it to the agent. Its description tells the model when to use it. Say "I'm vegetarian", then open the **Memory** tab.

   Skip ahead with the solution: `./solve 3b`

Full solution: `./solve 3`

The service also reads each conversation and extracts memories on its own, about a minute after the turn. `save_memory` writes straight away, and the model chooses what to keep.

#### Exercise 4: retrieving long-term memory (the model decides)

Let the model look up what it saved.

1. **Step A.** Search a traveler's long-term memories by meaning, only their own, with an optional memory type.

   Skip ahead with the solution: `./solve 4a`
2. **Step B.** Write the `search_memories` tool. Start a new session and ask for something in different words, such as "any food restrictions I should remember?". The search is by meaning, not by keyword.

   Skip ahead with the solution: `./solve 4b`

Full solution: `./solve 4`

#### Exercise 5: retrieving long-term memory (the code decides)

Instead of waiting for the model to ask, look up memories before the agent runs, so it has them from the first word.

- Write `retrieve_memories`, which searches for what the traveler just said, and add it to the graph before `agent`. Run the last cell of the graph file to draw it and see the new step.
- Log in as `ashwin`, say "hey", and see what the agent already knows.

Full solution: `./solve 5`

#### Exercise 6: semantic caching, check the cache

A question that was already answered does not need the agent again. Check the cache first, and if a similar question is in it, return that answer straight away.

1. **Seed the cache.** Fill the cache with questions and answers, the way the traveler memories were seeded:

   ```bash
   uv run python scripts/seed_cache.py
   ```
2. **Step A.** Look a question up in the cache, so that a question with a similar meaning finds the stored answer.

   Skip ahead with the solution: `./solve 6a`
3. **Step B.** Write `check_cache` and put it first in the graph. On a hit the graph ends there, and on a miss it goes on to the agent. Ask a seeded question in different words, and see the agent skipped.

   Skip ahead with the solution: `./solve 6b`

Full solution: `./solve 6`

#### Exercise 7: semantic caching, store in the cache

Let the cache fill itself. After the agent answers, keep the question and its answer for the next traveler.

1. **Step A.** Store a question together with its answer in the cache.

   Skip ahead with the solution: `./solve 7a`
2. **Step B.** Write `store_in_cache` and add it after `agent`. Ask a new question twice, in different words. The second time comes from the cache.

   Skip ahead with the solution: `./solve 7b`

Full solution: `./solve 7`

## If something looks wrong

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Resources

- [Try Redis free](https://redis.io/try-free/)
- [Redis Agent Memory](https://redis.io/docs/latest/develop/ai/context-engine/agent-memory/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Google Maps MCP server](https://developers.google.com/maps/ai/maps-experience-agent-tools/reference/mcp)

## Maintainers

- **Ashwin Hariharan** - [LinkedIn](https://www.linkedin.com/in/iyerashwinhariharan/)
- **Bhavana Giri** - [LinkedIn](https://www.linkedin.com/in/bhavana-anant-giri-0a43109b/)
