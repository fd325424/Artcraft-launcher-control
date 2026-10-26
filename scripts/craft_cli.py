#!/usr/bin/env python3
"""
ArtCraft Crafting App CLI Wrapper

Wraps the various Crafting App CLI syntaxes into a single command.

Usage:
    # List commands for an app
    python craft_cli.py list --app photocraft

    # Search commands
    python craft_cli.py search --app photocraft --search "layer"

    # Describe a command
    python craft_cli.py describe --app photocraft --id "layer.add"

    # Run a command (auto-detects syntax group)
    python craft_cli.py run --app photocraft --cmd "layer.add" --params '{"x":100,"y":100}'

    # Run multiple commands
    python craft_cli.py run --app photocraft --cmd "layer.add" --params '{...}' --cmd "layer.opacity" --params '{...}'

    # Run a FilmCraft JSONL script
    python craft_cli.py run --app filmcraft --script script.jsonl

    # Inspect a file
    python craft_cli.py inspect --app photocraft --file "image.psd"

    # Convert between formats
    python craft_cli.py convert --app photocraft --input "a.psd" --output "b.png"
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


# Syntax groups (from craft-cli-syntax.md)
SYNTAX_GROUPS = {
    "A": {
        "apps": ["gridcraft", "cadcraft", "deckcraft", "wordcraft", "soundcraft", "designcraft"],
        "pattern": "--cmd 'id={...}'",
    },
    "B": {
        "apps": ["photocraft", "vectorcraft"],
        "pattern": "--cmd id --params '{...}'",
    },
    "C": {
        "apps": ["lightcraft", "pdfcraft"],
        "pattern": "positional id key=value",
    },
    "D": {
        "apps": ["effectcraft"],
        "pattern": "positional id {json}",
    },
    "E": {
        "apps": ["filmcraft"],
        "pattern": "JSONL script file",
    },
}


def get_syntax_group(app_name):
    """Get the syntax group for an app."""
    for group_id, group in SYNTAX_GROUPS.items():
        if app_name in group["apps"]:
            return group_id
    return None


def build_command(app_name, cli_name, cmd, params, group):
    """Build the actual CLI command based on syntax group."""
    if group == "A":
        # --cmd 'id={...}'
        inline = {cmd: params} if params else {cmd: {}}
        cmd_str = json.dumps(inline, ensure_ascii=False)
        return [cli_name, "--cmd", cmd_str]
    elif group == "B":
        # --cmd id --params '{...}'
        args = [cli_name, "--cmd", cmd]
        if params:
            args.extend(["--params", json.dumps(params, ensure_ascii=False)])
        return args
    elif group == "C":
        # positional id key=value
        args = [cli_name, cmd]
        for k, v in (params or {}).items():
            args.append(f"{k}={v}")
        return args
    elif group == "D":
        # positional id {json}
        args = [cli_name, cmd]
        if params:
            args.append(json.dumps(params, ensure_ascii=False))
        return args
    elif group == "E":
        # FilmCraft: need script file
        return None  # Handled separately
    return None


def run_cli(args_list, capture_output=True):
    """Execute a CLI command and return the result."""
    try:
        result = subprocess.run(
            args_list,
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "ok": result.returncode == 0,
        }
    except FileNotFoundError:
        return {"returncode": -1, "ok": False, "error": f"Command not found: {args_list[0]}"}
    except subprocess.TimeoutExpired:
        return {"returncode": -2, "ok": False, "error": "Command timed out (60s)"}
    except Exception as e:
        return {"returncode": -3, "ok": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="ArtCraft Crafting App CLI Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Syntax groups:
  A: gridcraft, cadcraft, deckcraft, wordcraft, soundcraft, designcraft
     --cmd 'id={...}'
  B: photocraft, vectorcraft
     --cmd id --params '{...}'
  C: lightcraft, pdfcraft
     positional id key=value
  D: effectcraft
     positional id {json}
  E: filmcraft
     JSONL script file
        """,
    )
    parser.add_argument("action", choices=["list", "search", "describe", "run", "inspect", "convert"],
                        help="Action to perform")
    parser.add_argument("--app", required=True, help="App name (e.g., photocraft)")
    parser.add_argument("--cmd", action="append", help="Command id (can repeat)")
    parser.add_argument("--params", help="JSON parameters for the command")
    parser.add_argument("--script", help="JSONL script file path (FilmCraft)")
    parser.add_argument("--search", help="Search keyword for command_list")
    parser.add_argument("--id", help="Command id for describe/inspect/convert")
    parser.add_argument("--file", help="File path for inspect")
    parser.add_argument("--input", help="Input file for convert")
    parser.add_argument("--output", help="Output file for convert")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Resolve CLI name
    cli_name = f"{args.app}-cli"
    group = get_syntax_group(args.app)

    if group is None:
        print(f"Error: unknown app '{args.app}'", file=sys.stderr)
        sys.exit(1)

    # --- list ---
    if args.action == "list":
        args_list = [cli_name, "command_list"]
        result = run_cli(args_list)

    # --- search ---
    elif args.action == "search":
        args_list = [cli_name, "command_list", "--search", args.search]
        result = run_cli(args_list)

    # --- describe ---
    elif args.action == "describe":
        if group in ("A", "B", "E"):
            args_list = [cli_name, "describe", "--id", args.id]
        else:
            args_list = [cli_name, "describe", args.id]
        result = run_cli(args_list)

    # --- run ---
    elif args.action == "run":
        if args.script:
            # FilmCraft script mode
            args_list = [cli_name, "--script", args.script]
            result = run_cli(args_list, capture_output=False)
        else:
            if not args.cmd:
                print("Error: --cmd required for run action", file=sys.stderr)
                sys.exit(1)

            params = json.loads(args.params) if args.params else {}

            # Build and run each command
            all_outputs = []
            for i, cmd in enumerate(args.cmd):
                cmd_params = params if i == 0 else {}
                args_list = build_command(args.app, cli_name, cmd, cmd_params, group)
                if args_list is None:
                    print(f"Error: cannot build command for '{args.app}'", file=sys.stderr)
                    sys.exit(1)
                result = run_cli(args_list)
                all_outputs.append({"command": cmd, "result": result})
                if not result["ok"] and result.get("error"):
                    print(f"Error running '{cmd}': {result['error']}", file=sys.stderr)

            if args.json:
                result = {"results": all_outputs}
            else:
                result = all_outputs[0] if len(all_outputs) == 1 else {"results": all_outputs}

    # --- inspect ---
    elif args.action == "inspect":
        args_list = [cli_name, "inspect", "--file", args.file]
        result = run_cli(args_list)

    # --- convert ---
    elif args.action == "convert":
        args_list = [cli_name, "convert", "--input", args.input, "--output", args.output]
        result = run_cli(args_list)

    # Output
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("ok", result.get("returncode", 0) == 0):
            output = result.get("stdout", "")
            print(output if output else json.dumps(result, indent=2, ensure_ascii=False))
        else:
            stderr = result.get("stderr", "")
            error = result.get("error", "")
            msg = error or stderr or f"Command failed with return code {result.get('returncode')}"
            print(msg, file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
