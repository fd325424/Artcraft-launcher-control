# ArtCraft Control Protocol

The control protocol is how agents, scripts, and tests drive ArtCraft applications from outside. It uses one JSON request per line, one JSON reply per line, over loopback TCP or a pipe.

## Two Server Types

### Desktop App (artcraft-toolbox --control)
The running Launcher window. Supports everything the engine does, plus window state (ui.get, ui.set) and quitting.

### Headless Server (artcraft-toolbox-cli serve)
One engine session without a window, on stdio or a loopback port. Same engine methods, plus batch.

### MCP Server
Wraps either one of the above. See mcp-configuration.md.

## Starting the Control Server

```bash
artcraft-toolbox --control 7877 --control-token-file /path/to/artcraft-toolbox.token
```

- Server listens on 127.0.0.1 only (loopback)
- If the token file doesn't exist, the app creates it with a fresh 256-bit token
  - Unix: mode 0600
  - Windows: protected with user-only ACL
- An existing token file is reused
- `--control-token` passes the token directly (visible in process list — prefer the file)
- Without token arguments, the app generates one for this launch and prints it to stderr (never to the log)

### Environment Variables

```
ARTCRAFT_TOOLBOX_CONTROL_PORT
ARTCRAFT_TOOLBOX_CONTROL_TOKEN
ARTCRAFT_TOOLBOX_CONTROL_TOKEN_FILE
```

Arguments win over environment variables.

## Authentication

The first request on every connection must authenticate. Nothing else is dispatched before it:

```json
{"id":"auth","method":"auth","params":{"token":"..."}}
{"id":"auth","ok":true,"result":{"authenticated":true}}
```

A wrong token gets one error reply and the connection is closed.

## Request/Reply Format

After authentication, each request is one line, each reply one line with the same id:

```json
{"id":1,"method":"ui.get","params":{}}
{"id":1,"ok":true,"result":{"ui":{"tab":"apps","search":""},"notice":null}}

{"id":2,"method":"engine.execute","params":{"command":"app.status","params":{"app":"photocraft"}}}
{"id":2,"ok":false,"error":"unknown app `nope`"}
```

**Rules:**
- `params` must be a JSON object (omit it or pass `null` for none)
- Requests are handled on the UI thread between frames
- The server waits up to 60 seconds for a reply
  - A request still queued at that deadline is refused with `{"error":"timeout"}`
  - Work that has started is never cancelled by a timeout

## Methods

### engine.execute

Run an engine command.

**Params:** `{command, params?, wait?}`

**Reply:** the command's JSON result

**Background commands** (updates.check, app.install, app.update, apps.updateAll, toolbox.update, icons.refresh):
- Reply when the job ends
- With `wait: false`, reply `{job, pending: true}` immediately

### engine.commands

List all commands.

**Params:** `{filter?}`

**Reply:** `{id, label, params, background, enabled, disabledReason}` for each command
- `filter` matches id or label (case-insensitive)

### jobs.list

List running background jobs.

**Params:** `{}`

**Reply:** `{jobs: [{id, command, label, done, total, apps, phase?, fraction?}]}`

### jobs.cancel

Cancel running jobs.

**Params:** `{job?}`

**Reply:** `{cancelled: n}`
- Without `job`, cancels every running job
- An unknown job id is an error

### ui.get

Get the window state.

**Params:** `{}`

**Reply:** `{ui, notice, restartWanted, quitting, window, services, language, jobs}`

**ui fields:**
- `tab` — "apps" or "settings"
- `search` — app list filter text (max 200 chars, no control characters)
- `searchOpen` — show search field instead of tabs
- `availableFolded` — fold the "Available apps" panel
- `selected` — open an app's page by catalog id (null returns to list)
- `confirmUninstall` — open uninstall question for an app id (null closes it)

### ui.set

Change window state.

**Params:** any subset of ui fields

**Reply:** same as ui.get, after the change

### app.quit

Quit the application.

**Params:** `{}`

**Reply:** `{quitting: true}`
- The window closes (to tray when there is one, like the close button)

### methods

List all available methods.

**Params:** `{}`

**Reply:** this list

## Crafting App Control Channels

Each Crafting App has its own control channel when launched with `--control`.

### PhotoCraft
Authenticated variant of the control protocol.

```bash
photocraft --control 7979
```

### FilmCraft
```bash
filmcraft --control 9876
# or set FILMCRAFT_CONTROL_PORT
```

Time accepts seconds, frame, or timecode. FilmCraft counts ticks at 254,016,000,000/s.

Example commands:
```json
{"method":"engine.execute","params":{"command":"timeline.place","params":{"item":1,"track":"V1","seconds":0,"duration":1270080000000}}}
{"method":"engine.execute","params":{"command":"effects.setParam","params":{"clip":87,"effect":"lumetri","param":"curve_luma","value":[[0,0],[0.25,0.21],[0.75,0.82],[1,1]]}}}
{"method":"ui.screenshot","params":{"path":"frame.png"}}
```

### EffectCraft
```bash
effectcraft --control 9877
```

### VectorCraft
```bash
vectorcraft --control 7979
```

### LightCraft
```bash
lightcraft --control 7980
```

### PdfCraft
File-based control: `pdfcraft --control FILE`

### Other Apps
Dynamic ports: start with `app --port PORT`, then pass port to control.

## MCP Resource Endpoints

When running as an MCP server, the following resources are available:

- `artcraft-toolbox://apps` — live JSON of apps_status
- `artcraft-toolbox://commands` — live JSON of command_list

Resource reads are uncached. The tool and resource catalogs are private and cached for 10 minutes.

## Error Handling

| Error | Meaning |
|-------|---------|
| `unknown app` | App not installed or wrong id |
| `unknown command` | Command id doesn't exist |
| `timeout` | Request queued > 60 seconds |
| `authentication failed` | Wrong token |
| JSON-RPC -32602 | Unknown tool argument (names the key) |
| JSON-RPC -32700 | Malformed JSON line |

## Transport Details

- Loopback TCP only (127.0.0.1)
- One JSON object per line
- Requests handled on UI thread between frames
- Reply reflects the state the next frame draws
- 60-second timeout for queued requests
- Started work is never cancelled by timeout
