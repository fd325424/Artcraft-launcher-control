# ArtCraft Architecture

## Overview

ArtCraft 是一个开源 AI 创意工作室，由 storytold 组织在 GitHub 上发布。它包含：

1. **ArtCraft Studio** — 主应用，集成 AI 生成和创意工作流
2. **ArtCraft Launcher (artcraft-toolbox)** — 应用启动器，管理 12 款 Crafting Apps
3. **12 款 Crafting Apps** — 对标 Adobe 的 Rust 原生应用
4. **ArtCraft AI 生成服务** — 云端 AI 生成 API，通过 MCP server 暴露

## Three Layers of Control

### L1: Launcher Control Plane (artcraft-toolbox)

Launcher 是 Crafting Apps 的安装器和更新器。

**控制面：**
- `artcraft-toolbox-cli` — 命令行工具
- `artcraft-toolbox --control PORT` — 桌面应用控制服务器
- `artcraft-toolbox-cli serve` — 无头服务器
- MCP server — 包装上述两者

**核心能力：**
- 检测已安装应用
- 从官方发布页安装应用（校验 SHA-256）
- 检查和执行更新
- 启动应用
- 管理自己的更新

**命令示例：**
```bash
artcraft-toolbox-cli apps_status
artcraft-toolbox-cli command_run --id updates.check
artcraft-toolbox-cli command_run --id app.install --params '{"app":"photocraft","version":"0.7.0"}'
artcraft-toolbox-cli command_run --id app.launch --params '{"app":"photocraft","control":true}'
```

### L2: Crafting Apps Control Plane

每款 Crafting App 提供三种接口：

**1. CLI（headless，一次性执行）**
- 每个应用有独立 CLI：`photocraft-cli`、`filmcraft-cli`、`vectorcraft-cli` 等
- 执行命令后退出，适合脚本化
- 命令数从 161（PdfCraft）到 858（PhotoCraft）不等

**2. MCP 服务器（JSON-RPC over stdio）**
- 每个应用内嵌 MCP 服务器
- 提供 `<craft>_commands`、`<craft>_describe`、`<craft>_run`、`<craft>_inspect`、`<craft>_convert` 等工具
- 以及 `<craft>_mcp_tools`、`<craft>_mcp_call`、`<craft>_mcp_status` 等 MCP 直通工具
- 引擎启动约 600ms，空闲 5 分钟后自动关闭

**3. 控制通道（JSON-RPC over loopback TCP）**
- 桌面应用启动时加 `--control PORT` 开启
- 实时驱动正在运行的应用
- 可获取 UI 状态、截图等

**12 款应用：**

| 应用 | 对标 | CLI | 命令数 | MCP 工具数 |
|------|------|-----|--------|------------|
| PhotoCraft | Photoshop | photocraft-cli | 858 | 21 |
| VectorCraft | Illustrator | vectorcraft-cli | 743 | 32 |
| FilmCraft | Premiere Pro | filmcraft-cli | 693 | 17 |
| EffectCraft | After Effects | effectcraft-cli | 669 | 27 |
| SoundCraft | Audition | soundcraft-cli | 465 | 17 |
| DesignCraft | InDesign | designcraft-cli | 446 | 25 |
| LightCraft | Lightroom | lightcraft-cli | 296 | 318 |
| GridCraft | Excel | gridcraft-cli | 315 | 21 |
| WordCraft | Word | wordcraft-cli | 460 | 16 |
| DeckCraft | PowerPoint | deckcraft-cli | 226 | 25 |
| CADCraft | AutoCAD | cadcraft-cli | 305 | 11 |
| PdfCraft | Acrobat | pdfcraft-cli | 161 | 161 |

### L3: AI Generation Control Plane

ArtCraft 的云端 AI 生成服务通过 `artcraft-mcp-server` 暴露。

**两种 MCP server：**
- `artcraft-mcp-server.exe` — 核心官方版（mcp_sessions + direct API）
- `artcraft-mcp.exe` — 社区扩展版（55 个工具）

**生成能力：**
- 图像：Flux 1 Dev/Schnell、Flux Pro 1.1 Ultra、Nano Banana Pro、Seedream 4/4.5/5、Midjourney 7/8
- 视频：Kling 3.0/2.6/2.1、Veo 3/3.1、Seedance 2.0/1.5、Sora 2、Grok Imagine
- 3D：Hunyuan 3D 2.0/2.1、WorldLabs Marble Gaussian Splatting
- 语音：TTS

**Python CLI 工具：**
- `artcraft_runner.py` — 批量图像/视频生成
- `artcraft_3d_runner.py` — 3D 网格和高斯泼溅
- `artcraft_angle_matrix.py` — 四象限相机轨道
- `artcraft_audio_weaver.py` — 音频和语音合成
- `artcraft_cost_estimator.py` — 积分和成本估算

## Control Protocol (JSON-RPC)

Launcher 和 Crafting Apps 的控制通道都使用 JSON-RPC：

```json
{"id":"1","method":"engine.execute","params":{"command":"app.status","params":{}}}
{"id":"1","ok":true,"result":{...}}
```

**认证：**
- Launcher：`auth` 方法 + token（token 文件或环境变量）
- Crafting Apps：PhotoCraft 需要认证变体，PdfCraft 基于文件
- AI 生成：Bearer token 或凭证文件

**传输：**
- Loopback TCP（127.0.0.1）
- 每行一个 JSON 请求/回复
- 超时 60 秒（排队中的请求被拒绝，已开始的不被取消）

## Security

- 所有安装都经过 SHA-256 校验 + 平台签名验证
- 控制服务器只监听 loopback
- Token 文件权限：Unix 0600，Windows 用户级 ACL
- 不会提权
