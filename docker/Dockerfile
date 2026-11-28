# The image of the Docker setup (Python, uv and the packages). It is built by compose.yaml.
# For the Codespace image, see .devcontainer/Dockerfile instead.
FROM python:3.15

COPY --from=ghcr.io/astral-sh/uv:0.13.10 /uv /uvx /usr/local/bin/

# The packages live in /opt/venv, outside the folder that is mounted at /workspace, so the mount does not hide them.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_NO_SYNC=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/workspace \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
RUN uv sync --locked \
    && python -m ipykernel install --sys-prefix --name workshop-agent-memory-semantic-cache-trip-planning-langgraph --display-name "Reuse Knowledge for Agentic AI" --env PYTHONPATH /workspace
