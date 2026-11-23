# Troubleshooting

Find your problem below. If it is not here, run `uv run python scripts/check.py` first. It tests the memory service, OpenAI and Google Maps, and says which one fails.

## Setting up

**`uv sync` fails, or uv picks an old Python**

Upgrade uv (`brew upgrade uv` on a Mac, or see the [uv install docs](https://docs.astral.sh/uv/)). Each uv release knows only the Python versions that existed when it was made, so an older uv cannot fetch the Python this project needs.

**`Failed to spawn: uvicorn`, or `No module named 'backend'`**

The virtual environment is stale, or it was built for another folder. Leave any active environment, then rebuild it from the project folder:

```bash
deactivate 2>/dev/null; unset VIRTUAL_ENV
rm -rf .venv && uv sync
```

The server is started with `uv run uvicorn backend.main:app`. An older version of this project used `app.main:app`, so a command from your shell history may be out of date.

**Port 3000 is already in use**

Start the server on another port, for example `--port 3001`, and open that port instead.

**A setting is missing**

Copy `.env.example` to `.env` and fill it in, or set the values as Codespaces secrets. `scripts/check.py` names what is missing.

## The app

**The page loads, but the chat does nothing**

Look at the terminal the server runs in. It prints one line for each step the agent takes, and an error there says which service failed. `scripts/check.py` tests all three services.

**A new memory does not show in the Memory tab**

The service reads each conversation and extracts memories on its own, after the turn, on the extraction cadence you set. Give it about 5 minutes and refresh. `save_memory` writes straight away, so a fact saved with it appears at once.

**The agent mentions things you never said**

It is using old memories, from an earlier run or extracted from an earlier conversation. For the seeded travelers, `uv run python scripts/seed_agent_memory.py --reset` deletes their memories and creates them again. To remove everything in the store, flush it from the console of your Redis Agent Memory service.

**What did the agent use for this answer?**

The **Memory** tab, under **This turn**, shows the memories the agent was given and each tool it called. The server's terminal shows the same calls, one line per layer.

## Notebooks

**A cell says a module is missing**

You probably are on the wrong kernel. Choose **Reuse Knowledge for Agentic AI**, the one registered with this project's packages. If it is not in the list, register it again with the command in the README.

**The graph cell does not draw the graph**

It uses the mermaid.ink website, so it needs an internet connection. Restart the kernel after changing the graph.
