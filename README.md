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
- The answers it reuses are kept in a [RedisVL](https://redis.io/docs/latest/develop/ai/redisvl/) semantic cache.

## Set up

Get the code first.

**In GitHub Codespaces** (nothing to install): open the repository in a Codespace.

**On your machine** ([uv](https://docs.astral.sh/uv/) installed; it fetches Python 3.15 for you). To install uv, use one of these (see the [installation guide](https://docs.astral.sh/uv/getting-started/installation/)):

- macOS with Homebrew: `brew install uv`
- macOS and Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Set environment variables

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

**A database to attach it to.** The service needs an active Redis Cloud database, with a public endpoint, Redis Search and the default user enabled. If you don't have one, [create a database](https://redis.io/docs/latest/operate/rc/databases/create-database/). Once it exists, copy its public endpoint and the password of the default user from the [Redis Cloud console](https://cloud.redis.io/), and put them together as `redis://default:<password>@<endpoint>`. This is your `REDIS_URL`, which the semantic cache uses later.

**Create the service.** In the [Redis Cloud console](https://cloud.redis.io/), choose **Agent Memory** under **Iris**, then **Create Agent Memory service** and **Customize settings**. Enter a name, pick the database and its `default` user, and under **Memory configuration** enter:

| Setting | Value |
|---|---|
| Short-term TTL | 1 day |
| Long-term TTL | 365 days |
| Extraction cadence | 5 minutes |

Choose **Create**.

**Create an API key.** On the service's **Configuration** tab, choose **Create API key** and copy the key. The console shows it only once. This is your `IRIS_AGENT_MEMORY_API_KEY`.

**Copy the connection details.** On the same tab, copy the **Store ID** and the URL from the **URL List**. Use the endpoint's base address, including `https://`, and leave off the `/iris/data/v1/agent-memory/...` path. The URL is your `IRIS_AGENT_MEMORY_URL` and the Store ID is your `IRIS_AGENT_MEMORY_STORE_ID`.

**Add a memory type for traveler preferences.** In the console, open **Memory types & extraction** and choose **Add type**. Create `traveler_preference`, extracted from the conversation:

| Setting | Value |
|---|---|
| Description | Lasting travel preferences and standing instructions for a traveler |
| Extraction prompt | Extract a traveler preference only when the user explicitly states something stable about themselves: a lasting travel preference, a constraint such as a dietary requirement, or a standing instruction. Preserve explicit dietary requirements and food preferences. Ignore transient task details, which belong to the current session only and must not become long-term memories: a destination they are interested in or about to visit ("I want to go to Goa", "I'm going to San Francisco next month"), trip dates, questions about places or the weather ("what is the weather like in Bengaluru?"), and requests for a plan or recommendation. Do not infer a preference from what the user only asked about. Put anything that does not fit another field under standing_instructions. |

| Field | Type | Description |
|---|---|---|
| `interests` | `list[str]` | Interests from this list: food, landmarks, offbeat, slow, outdoors, nightlife, culture |
| `budget` | `str` | One of low, mid or high |
| `group_size` | `str` | One of solo, pair, family or group |
| `food_and_dietary` | `list[str]` | Dietary requirements and food preferences, such as vegetarian, nut allergy or loves street food |
| `standing_instructions` | `list[str]` | Rules to apply every time, such as "always include a rest day" or "avoid long walks" |

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

### See the finished app (optional)

```bash
./solve run --port 5010
```

Open http://localhost:5010 (in a Codespace, open port 5010).

### Seed some travelers (optional)

```bash
uv run python scripts/seed_agent_memory.py
```

This gives three travelers (ashwin, bhavana and kyle) some memories already, so there is something to find in exercises 4 and 5. Log in with one of those names to use them. Add `--reset` to delete their memories and start them over.

### Seed the semantic cache (for exercise 6)

```bash
uv run python scripts/seed_semantic_cache.py
```

This fills the cache with answers to 15 questions about popular places (Goa, Bali, Paris, New York and more), each with its place cards, so there is something to find in exercise 6. It uses the database from your `REDIS_URL`. It is safe to run again: it empties the cache first, including any answer the cache kept by itself in exercise 7, then adds these answers.

## Workshop instructions

You spend your time on the memory code. The rest of the app is already written. The app you start with has no memory at all, and each exercise adds one piece.

To see how the pieces fit together, and which ones each exercise adds, open the [architecture diagram](frontend/architecture.html). With the app running, it is at http://localhost:3000/architecture.html.

### How to work on the files (your choice)

**In your own editor.** Open the files from the table, edit them and save. The running app only sees what you save, and `--reload` restarts it when you do.

**Or run them as notebooks in JupyterLab (optional).** The exercise files can be run cell by cell, so you can try a step on its own before the app uses it. Register the kernel once (a Codespace already has it), then start JupyterLab:

```bash
uv run python -m ipykernel install --sys-prefix --name workshop-agent-memory-semantic-cache-trip-planning-langgraph --display-name "Reuse Knowledge for Agentic AI" --env PYTHONPATH "$(pwd)"
uv run jupyter lab
```

Right-click an exercise file and choose **Open With → Notebook**. When it asks for a kernel, choose **Reuse Knowledge for Agentic AI**: it is the one with this project's packages, so a cell that says a module is missing is on another kernel.

### Overview

#### Part 1: Agent memory

| Exercise | What to do | Relevant files |
|---|---|---|
| 1. See what no memory looks like | Run the app and watch it forget | none |
| 2. Working memory | Remember the conversation so far | [`session_memory.py`](backend/modules/ai/agent_memory/session_memory.py), [`index.py`](backend/modules/ai/agent_workflow/index.py) |
| 3. Storing long-term memory | Let the model save a lasting fact | [`long_term_memory.py`](backend/modules/ai/agent_memory/long_term_memory.py), [`memory_tools.py`](backend/modules/ai/agent_workflow/tools/memory_tools.py) |
| 4. Retrieving long-term memory (the model decides) | Let the model search what it saved | [`long_term_memory.py`](backend/modules/ai/agent_memory/long_term_memory.py), [`memory_tools.py`](backend/modules/ai/agent_workflow/tools/memory_tools.py) |
| 5. Retrieving long-term memory (the code decides) | Look up memories before the agent runs | [`nodes.py`](backend/modules/ai/agent_workflow/nodes.py) |

#### Part 2: Semantic cache

| Exercise | What to do | Relevant files |
|---|---|---|
| 6. Semantic caching: check the cache | Find a stored answer for a question with a similar meaning, and skip the agent on a match | [`public_cache.py`](backend/modules/ai/semantic_cache/public_cache.py), [`nodes.py`](backend/modules/ai/agent_workflow/nodes.py) |
| 7. Semantic caching: store in the cache | Keep answers that are worth reusing, so similar questions find them | [`public_cache.py`](backend/modules/ai/semantic_cache/public_cache.py), [`nodes.py`](backend/modules/ai/agent_workflow/nodes.py) |

### Exercises

Where to write: look for `# TODO` in the files.

Stuck? You have two ways to get the solution:

- **Copy it from the file.** Under each step there is a collapsed **Show solution** block with the finished code. Open it and copy what you need. It shows when you open the file as a notebook in JupyterLab, or in VS Code's notebook view.
- **Run `./solve`.** Each step gives a `./solve` command. It saves your version of the files in `.solve-backup/`, then copies the finished code over them. A solution includes what the earlier steps in the same file did, so run them in order if you skip one. `./solve all` runs every step. On Windows, run it as `python solve 2a`.

#### Exercise 1: see what no memory looks like

Nothing to write. Run the app and ask for a 3-day food trip in Tokyo, then say your budget is mid-range and ask for a plan. Then press **New session** and ask "can you adjust it for a family of four?". The assistant has no idea what you mean. Without memory, every conversation starts from nothing.

---

#### Exercise 2: working memory

Make the agent remember the conversation so far.

1. **Step A.** Add each message to the session in Redis Agent Memory, and read the session back.

   Skip ahead with the solution: `./solve 2a`
2. **Step B.** Before each model call, put the conversation so far into the prompt. Ask "which city did I just ask about?" to try it. Then change how much of it the model gets, and watch what it forgets.

   Skip ahead with the solution: `./solve 2b`

Full solution: `./solve 2`

---

#### Exercise 3: storing long-term memory (the model decides)

Make a lasting fact outlive the conversation.

1. **Step A.** Create a long-term memory with its text, its owner (the traveler), a type (semantic for a preference, episodic for something that happened) and topics.

   Skip ahead with the solution: `./solve 3a`
2. **Step B.** Write the `save_memory` tool and give it to the agent, by adding it to the `memory_tools` list at the bottom of its file. Say "I'm vegetarian", then open the **Memory** tab.

   Skip ahead with the solution: `./solve 3b`

Full solution: `./solve 3`

The service also reads each conversation and extracts memories on its own, about 5 minutes after the turn. `save_memory` writes straight away, and the model chooses what to keep.

---

#### Exercise 4: retrieving long-term memory (the model decides)

Let the model look up what it saved.

1. **Step A.** Search a traveler's long-term memories by meaning, only their own, with an optional memory type.

   Skip ahead with the solution: `./solve 4a`
2. **Step B.** Write the `search_memories` tool and add it to the `memory_tools` list. Start a new session and ask for something in different words, such as "any food restrictions I should remember?". The search is by meaning, not by keyword.

   Skip ahead with the solution: `./solve 4b`

Full solution: `./solve 4`

---

#### Exercise 5: retrieving long-term memory (the code decides)

Instead of waiting for the model to ask, look up memories before the agent runs, so it has them from the first word.

- Write `retrieve_memories` in `nodes.py`, which searches for what the traveler just said.
- Log in as `ashwin`, say "hey", and see what the agent already knows. Then try logging in as your own user.

Full solution: `./solve 5`

---

#### Exercise 6: semantic caching, check the cache

A question that was already answered does not need the agent again. Check the cache first, and if a similar question is in it, return that answer straight away. The cache is RedisVL's [semantic cache](https://redis.io/docs/latest/develop/ai/redisvl/user_guide/how_to_guides/llmcache/), in the database from your `REDIS_URL`. It compares the meaning of questions, not their words.

1. **Seed the cache.** Fill the cache with answers to 15 questions about popular places (Goa, Bali, Paris, New York and more), the way the traveler memories were seeded. Each answer comes with its place cards:

   ```bash
   uv run python scripts/seed_semantic_cache.py
   ```
2. **Step A.** Look a question up in the cache, so that a question with a similar meaning finds the stored answer and its cards.

   Skip ahead with the solution: `./solve 6a`
3. **Step B.** Write `check_cache` in `nodes.py`. On a hit the graph ends there, and on a miss it goes on to the agent. Start a new session and ask "What should I see in Paris?".
   Skip ahead with the solution: `./solve 6b`

Full solution: `./solve 6`

---

#### Exercise 7: semantic caching, store in the cache

Let the cache fill itself. After the agent answers, keep the question and its answer to be reused for others.

1. **Step A.** Store a question together with its answer in the cache.

   Skip ahead with the solution: `./solve 7a`
2. **Step B.** Write `store_in_cache` in `nodes.py`. Ask something you haven't asked before, then ask it again: the second answer comes from the cache.

   An answer with the weather, one written with a traveler's memories, one without places, or follow-up questions such as "and the second one?" are left out.

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
