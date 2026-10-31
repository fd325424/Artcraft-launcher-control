# ArtCraft Installation Guide

## Prerequisites

- **Windows**: Windows 10/11 (64-bit)
- **macOS**: macOS 11 Big Sur or later
- **Linux**: glibc requirements vary; AppImage/.deb/.rpm recommended
- **Node.js** ^22.19.0 || >=24.0.0 (only needed for DSH plugin install method)
- **Python** 3.x (only needed for AI generation Python CLI tools)

## Method 1: Install via Launcher (Recommended)

This is the official way to install and manage Crafting Apps.

### Step 1: Download ArtCraft Launcher

Download from official sources only:
- **getartcraft.com** — official website
- **GitHub Releases** — storytold organization

### Step 2: Install Launcher

**Windows:**
- Run the `.msi` installer (per-user)
- Or download `portable.zip` for a portable copy (data alongside executable)

**macOS:**
- Download `.dmg`, copy to Applications

**Linux:**
- `.deb` or `.rpm` (recommended)
- `.AppImage`
- `.flatpak` (requires Flatpak; uses flatpak-spawn to install apps)

### Step 3: Install Crafting Apps

1. Launch ArtCraft Launcher
2. Browse the catalog of available apps
3. Click Install on the apps you need
4. The launcher downloads the official package, verifies SHA-256 checksum, and installs

### Step 4: Verify

```bash
artcraft-toolbox-cli status
```

This shows every Crafting App's install and update status.

## Method 2: Install Crafting App CLIs Directly

Each Crafting App has a standalone CLI. You can install them individually.

### Download from GitHub Releases

All Crafting Apps are published under the `storytold` GitHub organization:

```
https://github.com/storytold/<craft-name>/releases
```

Download the appropriate binary for your OS and architecture.

### Via DSH Plugin Installer (cross-platform)

> [lznnnnn1998/dsh-artcraft](https://github.com/lznnnnn1998/dsh-artcraft) 为第三方社区项目（非 storytold 官方），使用前请自行评估。

```bash
git clone https://github.com/lznnnnn1998/dsh-artcraft
cd dsh-artcraft
node scripts/install-craft.mjs
```

This downloads signed release binaries for all 12 crafts. No Rust toolchain needed.

To compile from source instead:
```bash
node scripts/install-craft.mjs --from-source
```

### Verify CLI Installation

```bash
photocraft-cli commands
filmcraft-cli commands
vectorcraft-cli commands
```

> 若提示未知子命令，先用 `<app>-cli --help` 查看该版本实际语法。

## Method 3: Install ArtCraft MCP Server (for AI Generation)

> [theCosmicCrafter/artcraft-mcp](https://github.com/theCosmicCrafter/artcraft-mcp) 为第三方社区项目（非 storytold 官方），提供图像/视频/3D/语音生成的 MCP 服务。

### Download

```bash
git clone https://github.com/theCosmicCrafter/artcraft-mcp
cd artcraft-mcp
```

The `bin/` directory contains ready-to-run 64-bit Windows binaries:
- `artcraft-mcp.exe` — full tool suite (60+ tools)

### Authentication

The server resolves credentials in this order:

1. **Environment variable** `ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN` — dedicated MCP session Bearer token
2. **Environment variable** `ARTCRAFT_API_KEY` — automatically exchanged for a session
3. **Environment variables** `ARTCRAFT_SESSION` and `ARTCRAFT_AVT` — session cookie
4. **Credential files** in `~/Artcraft/credentials/`:
   - `artcraft_session.txt` — session cookie
   - `artcraft_avt.txt` — visitor cookie
5. **Desktop app store** — `%LOCALAPPDATA%\ai.artcraft.app\.cookies`

To get credentials:
- Log into ArtCraft at getartcraft.com
- Open the ArtCraft desktop app and sign in
- The app stores cookies automatically

### One-Click Setup

```bash
python setup_mcp.py
```

（脚本位于 artcraft-mcp 仓库根目录）This auto-detects and registers the MCP server in Claude Desktop, Windsurf, or Cursor.

## Method 4: Configure MCP in WorkBuddy

Edit `~/.workbuddy/mcp.json`:

```json
{
  "mcpServers": {
    "artcraft": {
      "command": "C:\\path\\to\\artcraft-mcp\\bin\\artcraft-mcp.exe",
      "args": []
    }
  }
}
```

For Crafting App MCP servers, each app's MCP is spawned per-plugin. See `mcp-configuration.md` for details.

## Verification Checklist

After installation, run:

```bash
python scripts/check_env.py
```

This checks:
- [ ] Launcher installed
- [ ] Crafting App CLIs available
- [ ] MCP server configured
- [ ] Credentials present

## Platform-Specific Notes

### Windows
- Launcher MSI is per-user
- App installations use Windows Installer (Program Files, Start menu)
- Portable.zip keeps data alongside executable
- Tray icon needs AppIndicator on GNOME (Linux only)

### macOS
- Apps copied from DMG to Applications folder
- Launcher is universal binary (Apple Silicon + Intel)

### Linux
- Flatpak build installs host Flatpaks when available
- Otherwise unpacks apps in its own sandbox
- GNOME needs AppIndicator extension for tray
- Launcher log in data folder (two previous runs retained)

## Important

- Only download from official sources: getartcraft.com and GitHub releases under storytold
- The Crafting Apps are early alpha — keep backups of important files
- The launcher never elevates privileges
- All installations verify SHA-256 before installing
