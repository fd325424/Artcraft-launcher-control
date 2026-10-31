# ArtCraft Launcher Control

[![GitHub stars](https://img.shields.io/github/stars/fd325424/Artcraft-launcher-control)](https://github.com/fd325424/Artcraft-launcher-control/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An AI skill for controlling the [ArtCraft](https://github.com/storytold) open-source creative studio — manage apps, drive Crafting Apps, and generate AI media through natural language.

ArtCraft 是开源 AI 创意工作室，包含 13 款对标 Adobe/Figma 的 Rust 应用（PhotoCraft、FilmCraft、VectorCraft 等）。本技能让 AI 能够通过自然语言驱动 ArtCraft 完成从应用管理到实际创作的全部工作。

## Features

- **三层控制面** — 覆盖 Launcher 管理、Crafting Apps 创作、AI 生成能力
- **三种连接方式** — CLI、MCP 服务器、JSON-RPC 控制通道
- **13 款 Crafting Apps** — PhotoCraft、VectorCraft、FilmCraft、EffectCraft、SoundCraft、DesignCraft、LightCraft、GridCraft、WordCraft、DeckCraft、CADCraft、PdfCraft、FigCraft
- **完整文档** — 9 份参考文档 + 3 个可执行脚本
- **即装即用** — 兼容 WorkBuddy、Claude Code、OpenClaw 等支持 SKILL.md 格式的平台

## Architecture

ArtCraft exposes three layers of control:

| Layer | Control Plane | Use Case | Connection |
|-------|--------------|----------|------------|
| **L1** | Launcher (artcraft-toolbox) | Install / update / launch Crafting Apps | CLI / Control Protocol / MCP |
| **L2** | Crafting Apps (13 apps) | PhotoCraft editing, FilmCraft editing, VectorCraft drawing, etc. | Per-app CLI / MCP / Control Channel |
| **L3** | AI Generation (artcraft-mcp) | Image / video / 3D / voice generation | MCP / Python CLI |

## Installation

### 1. Install ArtCraft

Download the ArtCraft Launcher from [getartcraft.com](https://getartcraft.com) or GitHub releases (storytold organization), then install the Crafting Apps you need.

### 2. Install the Skill

**For WorkBuddy / Claude Code:**

Clone this repository and place the skill in your skills directory:

```bash
git clone https://github.com/fd325424/Artcraft-launcher-control.git
cp -r artcraft-launcher-control ~/.workbuddy/skills/
# or for Claude Code:
cp -r artcraft-launcher-control ~/.claude/skills/
```

**For OpenClaw:**

Copy to the workspace skills directory:

```bash
cp -r artcraft-launcher-control ~/.openclaw/workspace/skills/
```

### 3. Verify Installation

```bash
python scripts/check_env.py
```

This checks for the Launcher, Crafting App CLIs, MCP server, and credentials.

## Usage

Once the skill is installed, use natural language:

| Say this | The AI will |
|----------|-------------|
| "Check ArtCraft environment" | Run check_env.py and report what's missing |
| "Install ArtCraft Launcher" | Guide you through download and installation |
| "Update all Crafting Apps" | Run updates.check + apps.updateAll via Launcher |
| "Use PhotoCraft to add a layer to this image" | Call photocraft-cli to execute creation commands |
| "Generate a cyberpunk-style image with AI" | Use artcraft-mcp image generation |
| "Edit a video with FilmCraft" | Generate JSONL script and run filmcraft-cli |

## Skill Structure

```
artcraft-launcher-control/
├── SKILL.md                    # Main instruction file (trigger conditions + routing + workflows)
├── references/                 # 9 reference documents
│   ├── architecture.md         # ArtCraft overall architecture
│   ├── installation.md         # Complete installation guide
│   ├── launcher-commands.md    # Launcher full command reference
│   ├── control-protocol.md     # JSON-RPC control protocol spec
│   ├── craft-cli-syntax.md     # 5 CLI syntax groups (A-E)
│   ├── craft-apps-catalog.md   # 12 Crafting Apps capability catalog
│   ├── mcp-configuration.md    # MCP configuration for various clients
│   ├── ai-generation-mcp.md    # AI generation model matrix + Python CLI
│   └── troubleshooting.md      # Common errors and troubleshooting
└── scripts/                    # 3 executable scripts
    ├── check_env.py            # Environment detection
    ├── control_call.py         # JSON-RPC control protocol client
    └── craft_cli.py            # Unified Crafting App CLI wrapper
```

## Scripts

### check_env.py

Detects installed components: Launcher, Crafting App CLIs, MCP server, credentials.

```bash
python scripts/check_env.py          # Human-readable output
python scripts/check_env.py --json   # JSON output
```

### control_call.py

Send JSON-RPC requests to a running ArtCraft Launcher or Crafting App over loopback TCP.

```bash
python scripts/control_call.py --port 7877 --token-file token.txt \
    --method engine.execute --params '{"command":"apps.status"}'
```

### craft_cli.py

Wraps the various Crafting App CLI syntaxes into a single command.

```bash
# List commands
python scripts/craft_cli.py list --app photocraft

# Search commands
python scripts/craft_cli.py search --app photocraft --search "layer"

# Run a command
python scripts/craft_cli.py run --app photocraft --cmd "layer.add" --params '{"x":100,"y":100}'
```

## Crafting Apps

13 native Rust applications, each with its own CLI, MCP server, and control channel:

| App | Equivalent | CLI |
|-----|-----------|-----|
| PhotoCraft | Photoshop | photocraft-cli |
| VectorCraft | Illustrator | vectorcraft-cli |
| FilmCraft | Premiere Pro | filmcraft-cli |
| EffectCraft | After Effects | effectcraft-cli |
| SoundCraft | Audition | soundcraft-cli |
| DesignCraft | InDesign | designcraft-cli |
| LightCraft | Lightroom | lightcraft-cli |
| GridCraft | Excel | gridcraft-cli |
| WordCraft | Word | wordcraft-cli |
| DeckCraft | PowerPoint | deckcraft-cli |
| CADCraft | AutoCAD | cadcraft-cli |
| PdfCraft | Acrobat | pdfcraft-cli |
| FigCraft | Figma | figcraft-cli |

命令数随版本快速变化，以各 CLI 的 `commands` 子命令实时查询为准。

## MCP Configuration

### AI Generation MCP

> 以下 MCP server 来自第三方社区项目 [theCosmicCrafter/artcraft-mcp](https://github.com/theCosmicCrafter/artcraft-mcp)（非 storytold 官方），需先 clone 该仓库。

Add to your MCP client config (e.g., `~/.workbuddy/mcp.json` or `~/.claude.json`):

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

Authentication (in priority order):
1. `ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN` env var
2. `ARTCRAFT_API_KEY` env var
3. Credential files in `~/Artcraft/credentials/`
4. Desktop app cookies in `%LOCALAPPDATA%\ai.artcraft.app\.cookies`

### Launcher MCP

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

## Requirements

- **Windows** 10/11 (64-bit), **macOS** 11+, or **Linux** (glibc)
- **Python** 3.x (for scripts)
- ArtCraft Launcher and Crafting Apps installed (see installation.md)

## License

MIT — see [LICENSE](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit and push
5. Open a pull request

## Links

- [ArtCraft Official Site](https://getartcraft.com)
- [ArtCraft GitHub Organization](https://github.com/storytold)（官方）
- [artcraft-toolbox](https://github.com/smyrgeorge/artcraft-toolbox)（社区套件管理器，非官方）
- [ArtCraft MCP Server](https://github.com/theCosmicCrafter/artcraft-mcp)（第三方社区项目，非官方）
- [DSH ArtCraft Plugins](https://github.com/lznnnnn1998/dsh-artcraft)（第三方社区项目，非官方）
