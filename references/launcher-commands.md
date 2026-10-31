# ArtCraft Launcher Commands

ArtCraft Launcher (artcraft-toolbox) manages the installation, updates, and launching of Crafting Apps.

> 说明：`artcraft-toolbox` 是社区维护的套件管理器（smyrgeorge/artcraft-toolbox，非 storytold 官方仓库，但遵循官方发布契约）。`apps_status`、`command_list`、`command_run` 等是 **MCP 工具名**；CLI 子命令为 `status` / `list` / `check` / `install` / `update` / `open` / `mcp` / `serve`。引擎命令 ID（`updates.check`、`app.install` 等）通过 MCP 工具 `command_run` 或控制协议 `engine.execute` 调用。

## CLI Tool: `artcraft-toolbox-cli`

### status

Show every Crafting App's install and update status, plus the toolbox's own status.

```bash
artcraft-toolbox-cli status
```

### list

List the app catalog (headless).

```bash
artcraft-toolbox-cli list
```

### check

Check GitHub for new releases.

```bash
artcraft-toolbox-cli check
```

### install

Download, verify and install an app.

```bash
artcraft-toolbox-cli install photocraft
```

### update

Update apps (keeps old versions).

```bash
artcraft-toolbox-cli update --all
# Update a single app:
artcraft-toolbox-cli update photocraft
```

### open

Open a Crafting App, optionally with its control channel for agents.

```bash
artcraft-toolbox-cli open photocraft --control
artcraft-toolbox-cli open photocraft --no-control
```

### mcp

Start the MCP server over the whole command registry.

```bash
artcraft-toolbox-cli mcp
# Bridge to a running Launcher window:
artcraft-toolbox-cli mcp --bridge 127.0.0.1:7877 --control-token-file /path/to/token
```

### serve

Headless engine session over stdio or a loopback port (control protocol).

```bash
artcraft-toolbox-cli serve --port 7877
```

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
artcraft-toolbox-cli status
artcraft-toolbox-cli check
artcraft-toolbox-cli update --all
artcraft-toolbox-cli status
```

### Install a specific version

安装特定版本需通过 MCP `command_run`（引擎命令 `app.releases` / `app.install`）或控制协议：

```json
{"method":"engine.execute","params":{"command":"app.releases","params":{"app":"photocraft"}}}
{"method":"engine.execute","params":{"command":"app.install","params":{"app":"photocraft","version":"0.5.0"}}}
```

### Troubleshoot an install

```json
{"method":"engine.execute","params":{"command":"app.versions","params":{"app":"photocraft"}}}
{"method":"engine.execute","params":{"command":"app.rollback","params":{"app":"photocraft"}}}
```

### Launch an app with control channel

```bash
artcraft-toolbox-cli open photocraft --control
# Or via engine command; the reply contains the control address and token file path:
# {"method":"engine.execute","params":{"command":"app.launch","params":{"app":"photocraft","control":true}}}
```

### Update the Launcher itself

```json
{"method":"engine.execute","params":{"command":"toolbox.update"}}
```

New version used at next start; `toolbox.apply` swaps it in while app isn't running.

## Data Location

- **Log**: kept in the launcher's data folder (two previous runs retained)
- **Portable Windows**: data alongside the executable
- **Standard Windows**: per-user data location
- **macOS**: system Applications folder for apps
- **Linux**: ~/.var/app/ai.storyteller.artcraft-launcher/data/artcraft-launcher/apps/ (Flatpak sandbox)
