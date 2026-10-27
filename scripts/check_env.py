#!/usr/bin/env python3
"""
ArtCraft Environment Detection

Detects installed components:
  - ArtCraft Launcher (artcraft-toolbox / artcraft-launcher)
  - Crafting App CLIs (photocraft-cli, filmcraft-cli, etc.)
  - ArtCraft MCP server
  - Credentials/tokens

Usage:
    python check_env.py
    python check_env.py --json
"""

import json
import os
import shutil
import sys
from pathlib import Path


# --- Launcher tools to detect ---
LAUNCHER_TOOLS = ["artcraft-toolbox", "artcraft-toolbox-cli", "artcraft-launcher"]

# --- Crafting App CLIs to detect ---
CRAFT_CLIS = [
    "photocraft-cli",
    "vectorcraft-cli",
    "filmcraft-cli",
    "effectcraft-cli",
    "soundcraft-cli",
    "designcraft-cli",
    "lightcraft-cli",
    "gridcraft-cli",
    "wordcraft-cli",
    "deckcraft-cli",
    "cadcraft-cli",
    "pdfcraft-cli",
]

# --- Common install directories for Crafting App CLIs ---
# (checked when the CLI is not on PATH)
CRAFT_INSTALL_DIRS = [
    Path("C:/Program Files"),          # scan *Craft/*raft subdirs here
    Path("C:/Program Files/ArtCraft"),
    Path.home() / "Artcraft" / "apps",
    Path("D:/Artcraft/apps"),
]

# --- MCP server executables to detect ---
MCP_SERVERS = ["artcraft-mcp-server.exe", "artcraft-mcp.exe"]

# --- Credential locations to check ---
CRED_HOME = Path.home() / "Artcraft" / "credentials"
CRED_FILES = ["artcraft_session.txt", "artcraft_avt.txt"]

# --- MCP config locations ---
MCP_CONFIGS = [
    Path.home() / ".workbuddy" / "mcp.json",
    Path.home() / ".codeium" / "windsurf" / "mcp_config.json",
]


def find_in_path(name):
    """Check if a command exists in PATH."""
    return shutil.which(name) is not None


def find_executable(name):
    """Find an executable in PATH, returning the full path or None."""
    return shutil.which(name)


def check_launcher():
    """Check for ArtCraft Launcher."""
    results = []
    for tool in LAUNCHER_TOOLS:
        path = find_executable(tool)
        results.append({
            "name": tool,
            "found": path is not None,
            "path": path,
        })
    installed = any(r["found"] for r in results)
    return {
        "component": "launcher",
        "installed": installed,
        "tools": results,
    }


def find_craft_cli(name):
    """Find a Crafting App CLI in PATH or common install dirs."""
    path = find_executable(name)
    if path:
        return path
    # Check common install directories (including one level of subdirs)
    exe_name = name + ".exe" if os.name == "nt" else name
    for d in CRAFT_INSTALL_DIRS:
        if not d.exists():
            continue
        candidates = [d]
        # Add immediate subdirectories (e.g. C:\Program Files\PdfCraft\)
        try:
            candidates.extend(p for p in d.iterdir() if p.is_dir())
        except (PermissionError, OSError):
            pass
        for c in candidates:
            try:
                for entry in c.iterdir():
                    if entry.name.lower() == exe_name.lower() and entry.is_file():
                        return str(entry)
            except (PermissionError, OSError):
                pass
    return None


def check_craft_clis():
    """Check for Crafting App CLIs."""
    results = []
    for cli in CRAFT_CLIS:
        path = find_craft_cli(cli)
        results.append({
            "name": cli,
            "found": path is not None,
            "path": path,
        })
    installed = [r["name"] for r in results if r["found"]]
    return {
        "component": "craft_clis",
        "installed_count": len(installed),
        "installed": installed,
        "missing": [r["name"] for r in results if not r["found"]],
        "tools": results,
    }


def check_mcp_server():
    """Check for ArtCraft MCP server."""
    # Check PATH for the server
    for server in MCP_SERVERS:
        path = find_executable(server)
        if path:
            return {
                "component": "mcp_server",
                "found": True,
                "path": path,
            }

    # Check common installation directories
    common_dirs = [
        Path.home() / "Artcraft" / "mcp",
        Path.home() / "artcraft-mcp" / "bin",
        Path("C:/Artcraft/mcp/bin"),
        Path("D:/Artcraft/mcp/bin"),
    ]

    for d in common_dirs:
        if d.exists():
            for server in MCP_SERVERS:
                exe = d / server
                if exe.exists():
                    return {
                        "component": "mcp_server",
                        "found": True,
                        "path": str(exe),
                    }

    return {
        "component": "mcp_server",
        "found": False,
        "path": None,
    }


def check_credentials():
    """Check for ArtCraft credentials."""
    results = []
    for fname in CRED_FILES:
        fpath = CRED_HOME / fname
        exists = fpath.exists()
        results.append({
            "name": fname,
            "exists": exists,
            "path": str(fpath),
        })

    # Check env vars
    env_vars = {
        "ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN": os.environ.get("ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN"),
        "ARTCRAFT_API_KEY": os.environ.get("ARTCRAFT_API_KEY"),
        "ARTCRAFT_SESSION": os.environ.get("ARTCRAFT_SESSION"),
        "ARTCRAFT_AVT": os.environ.get("ARTCRAFT_AVT"),
    }
    env_found = {k: v is not None for k, v in env_vars.items()}

    # Check desktop app cookies
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    cookies_dir = Path(local_appdata) / "ai.artcraft.app" / ".cookies" if local_appdata else None
    cookies_found = cookies_dir.exists() if cookies_dir else False

    return {
        "component": "credentials",
        "files": results,
        "env_vars": env_found,
        "desktop_cookies": {
            "found": cookies_found,
            "path": str(cookies_dir) if cookies_dir else None,
        },
        "any_valid": any(r["exists"] for r in results) or any(env_found.values()) or cookies_found,
    }


def check_mcp_config():
    """Check for MCP configuration in client configs."""
    results = []
    for config_path in MCP_CONFIGS:
        if config_path.exists():
            try:
                content = config_path.read_text(encoding="utf-8")
                # Simple check for "artcraft" in the config
                has_artcraft = "artcraft" in content.lower()
                results.append({
                    "path": str(config_path),
                    "exists": True,
                    "has_artcraft": has_artcraft,
                })
            except Exception as e:
                results.append({
                    "path": str(config_path),
                    "exists": True,
                    "has_artcraft": False,
                    "error": str(e),
                })
        else:
            results.append({
                "path": str(config_path),
                "exists": False,
                "has_artcraft": False,
            })
    return {
        "component": "mcp_config",
        "configs": results,
        "any_configured": any(r.get("has_artcraft") for r in results),
    }


def main():
    use_json = "--json" in sys.argv

    report = {
        "artcraft_env_check": {
            "launcher": check_launcher(),
            "craft_clis": check_craft_clis(),
            "mcp_server": check_mcp_server(),
            "credentials": check_credentials(),
            "mcp_config": check_mcp_config(),
        }
    }

    if use_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    # Human-readable output
    lc = report["artcraft_env_check"]

    print("=" * 60)
    print("  ArtCraft Environment Check")
    print("=" * 60)

    # Launcher
    print("\n  [L1] Launcher")
    if lc["launcher"]["installed"]:
        for tool in lc["launcher"]["tools"]:
            status = "OK" if tool["found"] else "--"
            print(f"    {status}  {tool['name']:<25} {tool['path'] or ''}")
    else:
        print("    [MISSING] ArtCraft Launcher not found in PATH")
        print("    -> Download from getartcraft.com or GitHub releases (storytold)")

    # Craft CLIs
    print("\n  [L2] Crafting App CLIs")
    if lc["craft_clis"]["installed_count"] > 0:
        print(f"    Installed: {lc['craft_clis']['installed_count']}/12")
        for name in lc["craft_clis"]["installed"]:
            print(f"    OK  {name}")
        if lc["craft_clis"]["missing"]:
            print(f"    Missing: {', '.join(lc['craft_clis']['missing'])}")
    else:
        print("    [MISSING] No Crafting App CLIs found")
        print("    -> Install via ArtCraft Launcher")

    # MCP Server
    print("\n  [L3] MCP Server")
    if lc["mcp_server"]["found"]:
        print(f"    OK  {lc['mcp_server']['path']}")
    else:
        print("    [MISSING] artcraft-mcp-server not found")
        print("    -> git clone https://github.com/theCosmicCrafter/artcraft-mcp")

    # Credentials
    print("\n  [Auth] Credentials")
    cred = lc["credentials"]
    if cred["any_valid"]:
        print("    OK  At least one credential source found")
        for f in cred["files"]:
            status = "OK" if f["exists"] else "--"
            print(f"    {status}  {f['name']}")
        for var, found in cred["env_vars"].items():
            status = "OK" if found else "--"
            print(f"    {status}  {var}")
    else:
        print("    [MISSING] No credentials found")
        print("    -> Log into ArtCraft desktop app or set env vars")

    # MCP Config
    print("\n  [MCP] Client Config")
    for config in lc["mcp_config"]["configs"]:
        if config["exists"]:
            status = "OK" if config["has_artcraft"] else "--"
            print(f"    {status}  {config['path']}")
        else:
            print(f"    --   {config['path']} (not found)")

    # Summary
    print("\n" + "=" * 60)
    ready = (
        lc["launcher"]["installed"]
        and lc["craft_clis"]["installed_count"] > 0
    )
    if ready:
        print("  Status: Ready for Launcher + Crafting App operations")
    else:
        print("  Status: NOT ready — install ArtCraft first")
        print("  See: references/installation.md in this skill")
    print("=" * 60)


if __name__ == "__main__":
    main()
