---
name: artcraft-launcher-control
description: 通过 AI 操作 ArtCraft 开源创意工作室。覆盖三层控制面：Launcher 应用管理（安装/更新/启动 Crafting Apps）、Crafting Apps 创作（PhotoCraft/VectorCraft/FilmCraft 等 12 款应用的 CLI/MCP/控制通道）、AI 生成能力（图像/视频/3D/语音）。当用户要求操作 ArtCraft、管理 Crafting Apps、用 ArtCraft 做创作、或询问 ArtCraft 安装配置时使用此技能。
---

# ArtCraft Launcher Control

## Overview

ArtCraft 是一个开源 AI 创意工作室，包含对标 Adobe 的 12 款 Rust 应用（Crafting Apps）。每款应用都提供 CLI、MCP 服务器和控制通道三种接口，Launcher 本身也有独立的 CLI 和控制协议。本技能让 AI 能够通过自然语言驱动 ArtCraft 完成从应用管理到实际创作的全部工作。

ArtCraft 的三层控制面：

| 层级 | 控制面 | 适用场景 | 连接方式 |
|------|--------|----------|----------|
| L1 | Launcher (artcraft-toolbox) | 检测/安装/更新/启动 Crafting Apps | CLI / 控制协议 / MCP |
| L2 | Crafting Apps (12 款) | PhotoCraft 修图、FilmCraft 剪辑、VectorCraft 画矢量等 | 各自 CLI / MCP / 控制通道 |
| L3 | AI 生成 (artcraft-mcp-server) | 图像/视频/3D/语音生成、积分管理 | MCP / Python CLI |

## Workflow Decision Tree

收到用户请求后，按以下顺序判断操作层级：

```
1. 用户想安装/更新/管理 Crafting Apps？
   → L1 Launcher 控制面
   → 读 references/launcher-commands.md

2. 用户想用某款 Crafting App 做创作？
   → L2 Crafting Apps 控制面
   → 读 references/craft-cli-syntax.md 和 references/craft-apps-catalog.md

3. 用户想用 AI 生成图像/视频/3D/语音？
   → L3 AI 生成控制面
   → 读 references/ai-generation-mcp.md

4. 用户还没装 ArtCraft？
   → 先读 references/installation.md 引导安装

5. 不确定用户意图？
   → 先问清楚，再路由到对应层级
```

## Environment Detection

操作 ArtCraft 前，先检测环境是否就绪：

```bash
python scripts/check_env.py
```

脚本检测：
- Launcher 是否安装（artcraft-toolbox / artcraft-launcher）
- 各 Crafting App CLI 是否可用（photocraft-cli、filmcraft-cli 等）
- MCP server 是否配置
- 凭证/Token 是否存在

如果检测到缺失组件，根据 references/installation.md 引导用户完成安装。

## L1: Launcher 应用管理

Launcher 负责 Crafting Apps 的检测、安装、更新和启动。

### CLI 方式

```bash
# 检测所有应用状态
artcraft-toolbox-cli apps_status

# 检查更新
artcraft-toolbox-cli command_run --id updates.check

# 安装/更新特定应用
artcraft-toolbox-cli command_run --id app.install --params '{"app":"photocraft","version":"0.7.0"}'
artcraft-toolbox-cli command_run --id apps.updateAll

# 启动应用（带控制通道）
artcraft-toolbox-cli command_run --id app.launch --params '{"app":"photocraft","control":true}'
```

### 控制协议方式（JSON-RPC over loopback TCP）

启动 Launcher 控制服务器：

```bash
artcraft-toolbox --control 7877 --control-token-file /path/to/token
```

然后通过 JSON-RPC 调用：

```json
{"id":"1","method":"engine.execute","params":{"command":"app.status","params":{}}}
{"id":"2","method":"engine.execute","params":{"command":"apps.updateAll","params":{}}}
```

完整命令列表和参数详见 references/launcher-commands.md。

### MCP 方式

将 Launcher MCP 配置到 WorkBuddy 后，可直接调用 `apps_status`、`command_list`、`command_run` 等工具。配置方法见 references/mcp-configuration.md。

## L2: Crafting Apps 创作

12 款 Crafting Apps 各有独立的 CLI 和 MCP 服务器。核心应用：

| 应用 | 对标 | CLI | 命令数 |
|------|------|-----|--------|
| PhotoCraft | Photoshop | photocraft-cli | 858 |
| VectorCraft | Illustrator | vectorcraft-cli | 743 |
| FilmCraft | Premiere Pro | filmcraft-cli | 693 |
| EffectCraft | After Effects | effectcraft-cli | 669 |
| SoundCraft | Audition | soundcraft-cli | 465 |
| DesignCraft | InDesign | designcraft-cli | 446 |
| LightCraft | Lightroom | lightcraft-cli | 296 |
| GridCraft | Excel | gridcraft-cli | 315 |
| WordCraft | Word | wordcraft-cli | 460 |
| DeckCraft | PowerPoint | deckcraft-cli | 226 |
| CADCraft | AutoCAD | cadcraft-cli | 305 |
| PdfCraft | Acrobat | pdfcraft-cli | 161 |

### CLI 调用语法

不同应用的 CLI 语法有差异，详见 references/craft-cli-syntax.md。常见模式：

```bash
# GridCraft/CADCraft/DeckCraft/WordCraft/SoundCraft/DesignCraft 风格
gridcraft-cli --cmd 'id={...}'

# PhotoCraft/VectorCraft 风格
photocraft-cli --cmd id --params '{...}'

# LightCraft 风格
lightcraft-cli id key=value

# EffectCraft 风格
effectcraft-cli id '{...}'

# FilmCraft 风格（需要生成 JSONL 脚本文件）
filmcraft-cli --script script.jsonl

# PdfCraft 风格（子命令，独立语法）
pdfcraft-cli info <file.pdf>
pdfcraft-cli text <file.pdf> --page 1
pdfcraft-cli render <file.pdf> --page 1 --out page.png
pdfcraft-cli combine a.pdf b.pdf --out merged.pdf
pdfcraft-cli split <in.pdf> --every 5 --out-dir pages/
```

### MCP 方式

每个 Crafting App 都有自己的 MCP 服务器。配置后可调用：

```
photocraft_commands  {"search":"layer"}
photocraft_describe  {"id":"layer.add"}
photocraft_run       {"commands":[...],"save":"..."}
photocraft_inspect   {"file":"..."}
photocraft_convert   {"input":"...","output":"..."}
```

### 控制通道方式

桌面应用启动时加 `--control` 参数即可开启控制通道，然后通过 JSON-RPC 驱动：

```bash
photocraft --control 7979
```

```json
{"method":"engine.execute","params":{"command":"layer.add","params":{...}}}
```

## L3: AI 生成能力

ArtCraft 的 AI 生成通过 artcraft-mcp-server 提供，支持图像、视频、3D 网格、高斯泼溅、语音合成。

### MCP 配置

在 `~/.workbuddy/mcp.json` 中添加：

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

认证方式（按优先级）：
1. 环境变量 `ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN`
2. 环境变量 `ARTCRAFT_API_KEY`
3. 凭证文件 `~/Artcraft/credentials/artcraft_session.txt` 和 `artcraft_avt.txt`
4. 桌面应用存储 `%LOCALAPPDATA%\ai.artcraft.app\.cookies`

### Python CLI 工具

```bash
# 批量图像/视频生成
python tools/artcraft_runner.py --prompt "描述" --model flux_1_dev --copies 2 --out-dir ./outputs

# 检查积分
python tools/artcraft_cost_estimator.py --check-balance --video-model seedance_2p0 --duration 5

# 3D 生成
python tools/artcraft_3d_runner.py --image "path.png" --mode both --out-dir ./outputs/3d
```

支持的模型矩阵详见 references/ai-generation-mcp.md。

## Common Workflows

### 工作流 1：全新环境从零安装

1. 运行 `python scripts/check_env.py` 检测环境
2. 根据检测结果，读 references/installation.md 引导用户下载并安装 ArtCraft Launcher
3. 通过 Launcher 安装需要的 Crafting Apps
4. 配置 MCP（如需 AI 生成或应用级 MCP）
5. 验证：运行 `python scripts/check_env.py` 确认全部就绪

### 工作流 2：更新所有 Crafting Apps

1. `apps_status` 查看当前状态
2. `command_run --id updates.check` 检查更新
3. `command_run --id apps.updateAll` 执行更新
4. `apps_status` 确认更新完成

### 工作流 3：用 PhotoCraft 修图

1. 确认 photocraft-cli 可用（check_env.py 已检测）
2. 查可用命令：`photocraft-cli command_list`
3. 查命令参数：`photocraft-cli describe --id <command>`
4. 执行：`photocraft-cli --cmd <id> --params '{...}'`
5. 验证输出文件

### 工作流 4：用 FilmCraft 剪辑

1. 确认 filmcraft-cli 可用
2. 查看命令列表：`filmcraft-cli command_list`
3. FilmCraft 需要 JSONL 脚本文件，格式见 references/craft-cli-syntax.md
4. 执行：`filmcraft-cli --script script.jsonl`

### 工作流 4b：用 PdfCraft 处理 PDF

1. 确认 pdfcraft-cli 可用（check_env.py 已检测）
2. 查看文档信息：`pdfcraft-cli info <file.pdf>`
3. 提取文本：`pdfcraft-cli text <file.pdf> --page N`
4. 渲染页面为图片：`pdfcraft-cli render <file.pdf> --page N --out page.png`
5. 合并 PDF：`pdfcraft-cli combine a.pdf b.pdf --out merged.pdf`
6. 拆分 PDF：`pdfcraft-cli split <in.pdf> --every 5 --out-dir pages/`
7. 提取指定页：`pdfcraft-cli extract <in.pdf> --pages 1,3,5-8 --out out.pdf`
8. 批量处理：`pdfcraft-cli batch <dir> --steps convert,ocr,optimize --out-dir out/`
9. 验证输出文件

### 工作流 5：AI 生成图像

1. 确认 artcraft-mcp-server 已配置且凭证有效
2. 调用 MCP 工具生成图像（或用 Python CLI）
3. 检查输出文件

## Error Handling

常见错误及处理：

| 错误 | 原因 | 处理 |
|------|------|------|
| `unknown app` | 应用未安装 | 用 Launcher 安装对应应用 |
| `command not found` | CLI 未安装或不在 PATH | 安装对应 Crafting App 或添加 PATH |
| `authentication failed` | 凭证缺失/过期 | 重新登录或更新凭证文件 |
| `timeout` | 控制通道请求超时（60秒） | 检查应用是否在运行，或改用 CLI |
| `permission denied` | 控制协议认证失败 | 检查 token 是否正确 |
| 磁盘空间不足 | 安装或生成时空间不够 | 清理空间后重试 |

详细故障排查见 references/troubleshooting.md。

## Resources

### scripts/
- `check_env.py` — 环境检测脚本，检查 Launcher、Crafting Apps CLI、MCP 配置、凭证

### references/
- `architecture.md` — ArtCraft 整体架构和三层控制面说明
- `installation.md` — 完整安装步骤（Launcher + Crafting Apps + MCP）
- `launcher-commands.md` — Launcher 全部命令和参数
- `control-protocol.md` — 控制协议（JSON-RPC）详细规范
- `craft-cli-syntax.md` — 各 Crafting App CLI 语法差异
- `craft-apps-catalog.md` — 12 款 Crafting Apps 能力目录
- `mcp-configuration.md` — MCP 配置方法（WorkBuddy/Claude Desktop 等）
- `ai-generation-mcp.md` — AI 生成模型矩阵、参数、Python CLI 工具
- `troubleshooting.md` — 常见错误和故障排查
