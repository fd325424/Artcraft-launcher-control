# ArtCraft Troubleshooting

## Environment Detection

Run `python scripts/check_env.py` first to identify missing components.

## Common Errors

### "unknown app" or "unknown command"

**Cause:** App not installed, or wrong id.

**Solution:**
```bash
artcraft-toolbox-cli status
artcraft-toolbox-cli list
```
Install missing apps via Launcher.

### "command not found" (CLI not in PATH)

**Cause:** Crafting App CLI not installed or not in PATH.

**Solution:**
1. Check if the binary exists:
   ```bash
   which photocraft-cli
   ```
2. Install via Launcher:
   ```bash
   artcraft-toolbox-cli install photocraft
   ```
3. Add to PATH if installed but not recognized.

### "authentication failed"

**Cause:** Missing or expired credentials.

**Solution:**
1. Check credential files:
   ```bash
   ls ~/Artcraft/credentials/
   ```
2. Check environment variables:
   ```bash
   echo $ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN
   echo $ARTCRAFT_API_KEY
   ```
3. Re-login in the ArtCraft desktop app to refresh cookies.
4. Verify the desktop app stores cookies:
   ```bash
   ls %LOCALAPPDATA%\ai.artcraft.app\.cookies
   ```

### "timeout" (control protocol)

**Cause:** Request queued > 60 seconds.

**Solution:**
1. Check if the app is running.
2. Use CLI instead of control protocol for long operations.
3. Check `jobs_list` for stuck background jobs.
4. Verify the app isn't doing heavy processing.

### "permission denied" (control protocol)

**Cause:** Wrong token or token file not readable.

**Solution:**
1. Verify the token file exists and is readable.
2. Check the token matches:
   ```bash
   cat /path/to/token
   ```
3. Restart the app to regenerate the token.

### MCP server won't start

**Cause:** Path incorrect, missing dependencies, or not trusted.

**Solution:**
1. Verify the executable path:
   ```bash
   C:\path\to\artcraft-mcp\bin\artcraft-mcp.exe --version
   ```
2. Check `~/.workbuddy/mcp.json` has correct path.
3. Open connector management and click "Trust".
4. Check for missing runtime dependencies.

### Crafting App crashes on launch

**Cause:** Early alpha software, missing dependencies, or incompatible version.

**Solution:**
1. Check the launcher log (in data folder, two previous runs retained).
2. Update to the latest version:
   ```bash
   artcraft-toolbox-cli update --all
   ```
3. Rollback if a recent update caused issues (via MCP `command_run` or control protocol `engine.execute`):
   ```json
   {"method":"engine.execute","params":{"command":"app.rollback","params":{"app":"photocraft"}}}
   ```
4. Report the issue with: OS, app, and the log.

### FilmCraft CLI script errors

**Cause:** Malformed JSONL or invalid command parameters.

**Solution:**
1. Validate the JSONL file:
   ```bash
   cat script.jsonl | python -c "import sys,json; [json.loads(l) for l in sys.stdin]"
   ```
2. Check each command exists:
   ```bash
   filmcraft-cli commands
   ```
3. Verify timecode format (ticks at 254,016,000,000/s).

### PSD file corruption in PhotoCraft

**Cause:** Complex layer styles or advanced smart objects (early alpha limitation).

**Solution:**
1. Flatten layers before importing.
2. Simplify smart objects.
3. The author reports 99%+ of test samples work — report failures with the PSD.

### Disk space issues

**Cause:** Insufficient space for installation or generation.

**Solution:**
1. Check available space.
2. Clean up previous outputs.
3. Use `--out-dir` to target specific locations.

### MCP bridge mode can't connect

**Cause:** Launcher not running, wrong port, or token mismatch.

**Solution:**
1. Verify Launcher is running with control enabled:
   ```bash
   artcraft-toolbox --control 7877 --control-token-file /path/to/token
   ```
2. Check the port matches in the MCP config.
3. Verify the token file matches.
4. Ensure only loopback addresses are used.

### Craft MCP not warming up

**Cause:** Plugin not installed correctly, or binary not found.

**Solution:**
1. Reinstall the plugin (third-party DSH method, see mcp-configuration.md):
   ```bash
   dsh plugin --profile web add dsh-artcraft-plugin-photocraft
   ```
2. Verify the binary:
   ```bash
   photocraft-cli --version
   ```
3. Check `scripts/verify.mjs` output.

## Log Locations

| Component | Location |
|-----------|----------|
| Launcher log | data folder (two previous runs retained) |
| Portable Windows | alongside executable |
| Crafting App data | per-app user data folder |
| MCP credentials | `~/Artcraft/credentials/` |
| Desktop app cookies | `%LOCALAPPDATA%\ai.artcraft.app\.cookies` |

## Reporting Issues

Include these details when reporting bugs:

1. **Operating system** — exact version
2. **App being used** — Launcher, which Crafting App, or MCP server
3. **Launcher log** — from the data folder
4. **Command/method** — what was attempted
5. **Error message** — exact text

## Backup Recommendation

- Keep backups of files opened in Crafting Apps (early alpha).
- Important PSD/AI files: maintain original copies.
- Generated outputs: verify before overwriting.
