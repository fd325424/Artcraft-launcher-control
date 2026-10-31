# ArtCraft AI Generation MCP

The ArtCraft MCP server (from third-party community project [theCosmicCrafter/artcraft-mcp](https://github.com/theCosmicCrafter/artcraft-mcp), not storytold official) enables AI-driven generation of images, video, 3D models, Gaussian splats, and speech. This reference covers the model matrix, parameters, and Python CLI tools.

## MCP Server

### Executables

- `bin/artcraft-mcp.exe` — full tool suite (60+ tools; older docs called the core one `artcraft-mcp-server.exe`)

### Authentication

Resolved in order:

1. `ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN` — dedicated MCP session Bearer token (`mcp_session_private_...`)
2. `ARTCRAFT_API_KEY` — exchanged with `POST /v1/mcp/session/create` for an active session
3. `ARTCRAFT_SESSION` + `ARTCRAFT_AVT` — session cookie env vars
4. Credential files in `~/Artcraft/credentials/`:
   - `artcraft_session.txt`
   - `artcraft_avt.txt`
5. ArtCraft Desktop App Store — `%LOCALAPPDATA%\ai.artcraft.app\.cookies`

### MCP Tools

The full suite includes tools across 15 modules:

| Module | Example Tools |
|--------|--------------|
| Image | `artcraft_generate_image` |
| Video | `artcraft_generate_video` |
| 3D | `artcraft_generate_3d_object` |
| Voice | TTS / voice synthesis |
| Media | media asset management |
| Account | credit balance, cost estimation |
| Jobs | job polling, cancellation |

## Image Models

| Model | Notes |
|-------|-------|
| Flux 1 Dev | High quality, slower |
| Flux 1 Schnell | Fast, lower quality |
| Flux Pro 1.1 Ultra | Highest quality flux |
| Nano Banana Pro | Good for editing |
| Seedream 4 | Latest Seedream |
| Seedream 4.5 | Refined |
| Seedream 5 | Latest |
| Midjourney 7 | MJ v7 |
| Midjourney 8 | MJ v8 |

## Video Models

| Model | Notes |
|-------|-------|
| Kling 3.0 | Latest Kling |
| Kling 2.6 | |
| Kling 2.1 | |
| Veo 3 | Google Veo 3 |
| Veo 3.1 | |
| Seedance 2.0 | |
| Seedance 1.5 | |
| Sora 2 | OpenAI Sora 2 |
| Grok Imagine Video | xAI Grok video |

## 3D & Splat Models

| Model | Notes |
|-------|-------|
| Hunyuan 3D 2.0 | Mesh generation |
| Hunyuan 3D 2.1 | Mesh generation |
| WorldLabs Marble | Gaussian Splat |

## Python CLI Tools

> 以下脚本位于 artcraft-mcp 仓库的 `tools/` 目录，需先 clone 该仓库。All scripts communicate directly with `bin/artcraft-mcp.exe` over stdio JSON-RPC without external servers.

### artcraft_runner.py — Batch Image & Video Generation

```bash
python tools/artcraft_runner.py \
  --prompt "Cinematic cyberpunk alleyway at dusk, anamorphic lens, neon reflections" \
  --model flux_1_dev \
  --copies 2 \
  --out-dir "./outputs"
```

**Parameters:**
- `--prompt` — text description (required)
- `--model` — model id (default: flux_1_dev)
- `--copies` — number of generations (default: 1)
- `--out-dir` — output directory (required)
- `--negative-prompt` — negative prompt (optional)
- `--aspect-ratio` — e.g. "1:1", "16:9", "9:16" (optional)
- `--resolution` — e.g. "1024x1024" (optional)

### artcraft_cost_estimator.py — Credit Balance & Cost

```bash
python tools/artcraft_cost_estimator.py --check-balance
python tools/artcraft_cost_estimator.py --check-balance --video-model seedance_2p0 --duration 5
```

**Parameters:**
- `--check-balance` — show current credit balance
- `--video-model` — estimate cost for a specific video model
- `--duration` — video duration in seconds
- `--image-model` — estimate cost for a specific image model

### artcraft_3d_runner.py — 3D Mesh & Gaussian Splat

```bash
python tools/artcraft_3d_runner.py \
  --image "path/to/character.png" \
  --mode both \
  --out-dir "./outputs/3d"
```

**Parameters:**
- `--image` — source image (required)
- `--mode` — `mesh`, `splat`, or `both` (default: both)
- `--model` — 3D model id (default: hunyuan_3d_2_1)
- `--out-dir` — output directory (required)

### artcraft_angle_matrix.py — 4-Quadrant Camera Orbit

```bash
python tools/artcraft_angle_matrix.py \
  --image "path/to/subject.png" \
  --prompt "Maintain facial details during camera orbit" \
  --out-dir "./outputs/orbit"
```

**Parameters:**
- `--image` — source image (required)
- `--prompt` — orbit prompt (required)
- `--out-dir` — output directory (required)

### artcraft_audio_weaver.py — Audio & Voice Synthesis

```bash
python tools/artcraft_audio_weaver.py \
  --text "Hello world" \
  --voice "default" \
  --out-dir "./outputs/audio"
```

**Parameters:**
- `--text` — text to synthesize (required)
- `--voice` — voice preset (optional)
- `--out-dir` — output directory (required)

## Companion API Bridge

For applications integrating the MCP server as a managed subprocess, `companion/mcp_routes.py` provides FastAPI endpoints:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/mcp/health` | Check process state and PID |
| `POST /api/mcp/start` | Spawn the binary with stdio pipes |
| `POST /api/mcp/stop` | Gracefully terminate or kill |
| `POST /api/mcp/token` | Exchange API keys/cookies for an MCP session token |

## JSON-RPC Schemas

Complete tool definitions in the artcraft-mcp repo's `schemas/` directory (60+ JSON files):

- `artcraft_generate_image.json`
- `artcraft_generate_video.json`
- `artcraft_generate_3d_object.json`
- ... (52 more)

## Typical Workflows

### Generate an image

```bash
python tools/artcraft_runner.py \
  --prompt "A serene mountain lake at sunrise" \
  --model nano_banana_pro \
  --out-dir "./outputs"
```

### Generate a video from an image

```bash
python tools/artcraft_runner.py \
  --prompt "Slow pan across the landscape" \
  --model kling_3_0 \
  --input "./mountain.png" \
  --out-dir "./outputs/video"
```

### Check credits before generating

```bash
python tools/artcraft_cost_estimator.py --check-balance --video-model seedance_2p0 --duration 5
```

### Generate a 3D model from a product photo

```bash
python tools/artcraft_3d_runner.py \
  --image "product.png" \
  --mode mesh \
  --out-dir "./outputs/3d"
```
