# ArtCraft MCP Configuration

## Overview

ArtCraft exposes three MCP surfaces:

1. **artcraft-mcp-server** — AI generation (image/video/3D/voice)
2. **Launcher MCP** — app management (apps_status, command_run, etc.)
3. **Crafting App MCP** — per-app creation tools

## 1. AI Generation MCP (artcraft-mcp-server)

### Download

```bash
git clone https://github.com/theCosmicCrafter/artcraft-mcp
cd artcraft-mcp
```

Binaries in `bin/`:
- `artcraft-mcp-server.exe` — core official (mcp_sessions + direct API)
- `artcraft-mcp.exe` — community 55-tool edition

### WorkBuddy Configuration

Edit `~/.workbuddy/mcp.json`:

```json
{
  "mcpServers": {
    "artcraft": {
      "command": "C:\\path\\to\\artcraft-mcp\\bin\\artcraft-mcp-server.exe",
      "args": []
    }
  }
}
```

### Authentication

The server resolves credentials in order:

1. **Environment variable** `ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN`
2. **Environment variable** `ARTCRAFT_API_KEY`
3. **Environment variables** `ARTCRAFT_SESSION` + `ARTCRAFT_AVT`
4. **Credential files** in `~/Artcraft/credentials/`:
   - `artcraft_session.txt`
   - `artcraft_avt.txt`
5. **Desktop app** — `%LOCALAPPDATA%\ai.artcraft.app\.cookies`

### How to Get Credentials

1. Log into ArtCraft at getartcraft.com
2. Open the ArtCraft desktop app and sign in
3. The app stores cookies in the locations above
4. Or export the session token from the app settings

### One-Click Setup

```bash
python setup_mcp.py
```

Auto-detects and registers in Claude Desktop, Windsurf, or Cursor.

### Available MCP Tools

The 55-tool community edition includes:

| Category | Example Tools |
|----------|--------------|
| Image | `artcraft_generate_image` |
| Video | `artcraft_generate_video` |
| 3D | `artcraft_generate_3d_object` |
| Voice | TTS / voice synthesis |
| Media | media asset management |
| Account | credit balance, cost estimation |
| Jobs | job polling, cancellation |

See ai-generation-mcp.md for the full model matrix.

## 2. Launcher MCP

### Headless Mode

```json
{
  "mcpServers": {
    "artcraft-toolbox": {
      "command": "artcraft-toolbox-cli",
      "args": ["mcp"]
    }
  }
}
```

Runs an in-process engine session without a window.

### Bridge Mode

Connect to a running Launcher window:

```json
{
  "mcpServers": {
    "artcraft-toolbox": {
      "command": "artcraft-toolbox-cli",
      "args": ["mcp", "--bridge", "127.0.0.1:7877", "--control-token-file", "/path/to/token"]
    }
  }
}
```

Or set environment variable `ARTCRAFT_TOOLBOX_CONTROL_TOKEN_FILE`.

Bridge mode allows the agent to see and drive the live window (ui.get, ui.set, control_call).

### Tools

| Tool | Arguments | Description |
|------|-----------|-------------|
| `apps_status` | none | Every app's install/update status + toolbox status |
| `command_list` | `filter?`, `enabled_only?` | Command registry |
| `command_run` | `id`, `params?`, `wait?` | Run one engine command |
| `command_batch` | `steps`, `stop_on_error?` | Run commands in order |
| `jobs_list` | none | Running background jobs |
| `jobs_cancel` | `job?` | Cancel one or all jobs |
| `ui_get` | none | Bridge only: window state |
| `ui_set` | `fields` | Bridge only: change window state |
| `control_call` | `method`, `params?` | Bridge only: any control method |

### Resources

- `artcraft-toolbox://apps` — live JSON of apps_status
- `artcraft-toolbox://commands` — live JSON of command_list

## 3. Crafting App MCP

Each Crafting App ships its own MCP server. When configured as an MCP client, the app is spawned per-plugin and kept warm (~600ms startup).

### Per-App Tools

Every craft exposes:

| Tool | Purpose |
|------|---------|
| `<craft>_commands` | Search/list commands |
| `<craft>_describe` | Get command details |
| `<craft>_run` | Execute commands |
| `<craft>_inspect` | Inspect a file |
| `<craft>_convert` | Convert between formats |
| `<craft>_mcp_tools` | List MCP tools |
| `<craft>_mcp_call` | Call MCP tool directly |
| `<craft>_mcp_status` | Check MCP server status |

### DSH Plugin Method

Install craft plugins via DSH:

```bash
# Install all 12 craft plugins
node scripts/install-into-profile.mjs --profile web

# Or install a single craft
dsh plugin --profile web add dsh-artcraft-plugin-photocraft
```

Each craft is its own package: `dsh-artcraft-plugin-<craft>`.

### MCP Behavior

- Spawned once per plugin and kept warm
- Startup cost: ~600ms per craft
- Shuts down after 5 idle minutes or when plugin unloads
- MCP tools have real JSON Schemas served over JSON-RPC

## WorkBuddy-Specific Notes

### After Editing mcp.json

The new MCP server will NOT activate automatically. The user must:

1. Open the connector management page (top-right)
2. Find the new server entry
3. Click "Trust" to enable it

### Verification

After configuration:

```bash
# Check the MCP server is reachable
python scripts/check_env.py
```

### Troubleshooting MCP

| Problem | Solution |
|---------|----------|
| Server won't start | Check path is correct, executable exists |
| Auth fails | Check credentials in ~/Artcraft/credentials/ or env vars |
| Tools not appearing | Click "Trust" in connector management |
| Bridge mode can't connect | Ensure Launcher is running with --control |
| Craft MCP not warming | Check plugin installed correctly |
