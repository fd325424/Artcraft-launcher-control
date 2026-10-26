# ArtCraft Launcher Commands

ArtCraft Launcher (artcraft-toolbox) manages the installation, updates, and launching of Crafting Apps.

## CLI Tool: `artcraft-toolbox-cli`

### apps_status

List every Crafting App's install and update status, plus the toolbox's own status.

```bash
artcraft-toolbox-cli apps_status
```

Returns JSON with each app's state: installed, version, available release, update available.

### command_list

List all available commands in the registry.

```bash
artcraft-toolbox-cli command_list
artcraft-toolbox-cli command_list --filter update
artcraft-toolbox-cli command_list --enabled-only
```

**Arguments:**
- `--filter` — match command id or label (case-insensitive)
- `--enabled-only` — only show enabled commands

**Returns:** `{id, label, params, background, enabled, disabledReason}` for each command.

### command_run

Execute one engine command.

```bash
artcraft-toolbox-cli command_run --id updates.check
artcraft-toolbox-cli command_run --id app.install --params '{"app":"photocraft","version":"0.7.0"}'
artcraft-toolbox-cli command_run --id app.launch --params '{"app":"photocraft","control":true}'
artcraft-toolbox-cli command_run --id apps.updateAll
```

**Arguments:**
- `--id` — command id (required)
- `--params` — JSON object of parameters (optional)
- `--wait` — wait for background command to finish (default: true; set false to return immediately)

**Background commands** (return when job ends): `updates.check`, `app.install`, `app.update`, `apps.updateAll`, `toolbox.update`, `icons.refresh`

With `--wait false`, background commands return `{job, pending: true}` immediately.

### command_batch

Execute multiple commands in order.

```bash
artcraft-toolbox-cli command_batch --steps '[{"id":"updates.check"},{"id":"apps.updateAll"}]' --stop-on-error
```

**Arguments:**
- `--steps` — JSON array of `{id, params?, wait?}`
- `--stop-on-error` — stop on first failure

**Returns:** `{completed, failed, results}`

### jobs_list

List running background jobs.

```bash
artcraft-toolbox-cli jobs_list
```

Returns: `{jobs: [{id, command, label, done, total, apps, phase?, fraction?}]}`

### jobs_cancel

Cancel a running job.

```bash
artcraft-toolbox-cli jobs_cancel --job <job-id>
# Cancel all running jobs:
artcraft-toolbox-cli jobs_cancel
```

Returns: `{cancelled: n}`

## Engine Commands Reference

### apps.status

Get status of all apps.

```json
{"command":"apps.status","params":{}}
```

### updates.check

Check for available updates (background command).

```json
{"command":"updates.check","params":{}}
```

### apps.updateAll

Update all installed apps (background command).

```json
{"command":"apps.updateAll","params":{}}
```

### app.releases

List published versions for a specific app.

```json
{"command":"app.releases","params":{"app":"photocraft"}}
```

### app.install

Install a specific version of an app.

```json
{"command":"app.install","params":{"app":"photocraft","version":"0.7.0"}}
```

### app.update

Update a specific app.

```json
{"command":"app.update","params":{"app":"photocraft"}}
```

### app.versions

List installed versions for an app.

```json
{"command":"app.versions","params":{"app":"photocraft"}}
```

### app.rollback

Rollback an app to a previous version.

```json
{"command":"app.rollback","params":{"app":"photocraft","version":"0.6.0"}}
```

### app.launch

Launch an app, optionally with control channel.

```json
{"command":"app.launch","params":{"app":"photocraft","control":true}}
```

**Parameters:**
- `app` — app id (e.g., "photocraft", "filmcraft")
- `control` — boolean, open with control channel (default: false)

**Returns:** includes `control` field with the address and token file path if control is enabled.

### toolbox.update

Check for Launcher updates.

```json
{"command":"toolbox.update","params":{}}
```

### toolbox.apply

Apply Launcher update (swaps binary while app isn't running).

```json
{"command":"toolbox.apply","params":{}}
```

### icons.refresh

Refresh tray/menu-bar icons.

```json
{"command":"icons.refresh","params":{}}
```

## MCP Tools

When configured as an MCP server, the Launcher exposes:

| Tool | Arguments | Description |
|------|-----------|-------------|
| `apps_status` | none | Every app's install/update status + toolbox status |
| `command_list` | `filter?`, `enabled_only?` | The command registry |
| `command_run` | `id`, `params?`, `wait?` | Run one engine command |
| `command_batch` | `steps`, `stop_on_error?` | Run commands in order |
| `jobs_list` | none | Running background jobs with progress |
| `jobs_cancel` | `job?` | Cancel one job or all |
| `ui_get` | none | Bridge only: window state |
| `ui_set` | `fields` | Bridge only: change window state |
| `control_call` | `method`, `params?` | Bridge only: any control method |

## Typical Sessions

### Update everything

```bash
artcraft-toolbox-cli apps_status
artcraft-toolbox-cli command_run --id updates.check
artcraft-toolbox-cli command_run --id apps.updateAll
artcraft-toolbox-cli apps_status
```

### Install a specific version

```bash
artcraft-toolbox-cli command_run --id app.releases --params '{"app":"photocraft"}'
artcraft-toolbox-cli command_run --id app.install --params '{"app":"photocraft","version":"0.5.0"}'
```

### Troubleshoot an install

```bash
artcraft-toolbox-cli command_run --id app.versions --params '{"app":"photocraft"}'
# Then rollback if needed:
artcraft-toolbox-cli command_run --id app.rollback --params '{"app":"photocraft"}'
```

### Launch an app with control channel

```bash
artcraft-toolbox-cli command_run --id app.launch --params '{"app":"photocraft","control":true}'
# The reply contains the control address and token file path.
```

### Update the Launcher itself

```bash
artcraft-toolbox-cli command_run --id toolbox.update
# New version used at next start; toolbox.apply swaps it in while app isn't running.
```

## Data Location

- **Log**: kept in the launcher's data folder (two previous runs retained)
- **Portable Windows**: data alongside the executable
- **Standard Windows**: per-user data location
- **macOS**: system Applications folder for apps
- **Linux**: ~/.var/app/ai.storyteller.artcraft-launcher/data/artcraft-launcher/apps/ (Flatpak sandbox)
