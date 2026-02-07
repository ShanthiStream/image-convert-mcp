#!/bin/sh
# Entrypoint script to handle environment variables and run MCP server

exec python mcp_server.py --transport sse --host 0.0.0.0 --port "${PORT:-8000}"
