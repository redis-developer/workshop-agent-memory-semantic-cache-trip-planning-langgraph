FROM mcr.microsoft.com/devcontainers/python:3.15

# Install uv in the image so Codespaces setup does not depend on pip or a user-local PATH.
COPY --from=ghcr.io/astral-sh/uv:0.13.10 /uv /uvx /usr/local/bin/
