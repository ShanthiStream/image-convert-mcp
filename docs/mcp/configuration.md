# MCP Configuration

Configure the image-convert-mcp server for your MCP client.

## Basic Configuration

Add to your MCP client's settings:

```json
{
  "mcpServers": {
    "image-convert": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/image-convert-mcp"
    }
  }
}
```

## Transport Modes

### stdio (Default)

Standard input/output transport. Best for local integrated usage.

```json
{
  "mcpServers": {
    "image-convert": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/image-convert-mcp"
    }
  }
}
```

### SSE (HTTP)

Server-Sent Events transport for remote or HTTP-based access.

```bash
# Start SSE server
python mcp_server.py --transport sse --port 8000
```

Configure client:

```json
{
  "mcpServers": {
    "image-convert": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Docker Configuration

```json
{
  "mcpServers": {
    "image-convert": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "/images:/images", "image-convert-mcp"]
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_CONVERT_LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |

## Client-Specific Setup

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "image-convert": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/image-convert-mcp"
    }
  }
}
```

### Cline / Continue

Add to your extension settings or `settings.json`:

```json
{
  "mcp.servers": {
    "image-convert": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/image-convert-mcp"
    }
  }
}
```

## Verification

After configuration, verify the server is accessible by asking your AI agent:

> "What image conversion tools do you have available?"

The agent should respond with information about `convert_image_single` and `convert_image_batch` tools.
