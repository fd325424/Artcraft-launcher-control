#!/usr/bin/env python3
"""
ArtCraft Control Protocol Client

Send JSON-RPC requests to a running ArtCraft Launcher or Crafting App
over loopback TCP. Handles authentication automatically.

Usage:
    python control_call.py --host 127.0.0.1 --port 7877 \
        --method engine.execute --params '{"command":"apps.status"}'

    python control_call.py --host 127.0.0.1 --port 7877 \
        --method ui.get

    python control_call.py --host 127.0.0.1 --port 7877 \
        --method engine.execute --params '{"command":"app.launch","params":{"app":"photocraft","control":true}}'

    # With token file
    python control_call.py --port 7877 --token-file /path/to/token \
        --method apps.status
"""

import argparse
import json
import socket
import sys
from pathlib import Path


def read_token(token_file=None):
    """Read the control token from file or return None."""
    if token_file:
        try:
            return Path(token_file).read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return None
    return None


def send_request(host, port, method, params=None, token=None, request_id="1"):
    """Send a single JSON-RPC request and return the reply."""
    if params is None:
        params = {}

    # Build request
    if method == "auth":
        request = {"id": request_id, "method": "auth", "params": {"token": token or ""}}
    else:
        request = {"id": request_id, "method": method, "params": params}

    req_line = json.dumps(request) + "\n"

    # Connect and send
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        sock.connect((host, port))
        sock.sendall(req_line.encode("utf-8"))

        # Receive reply
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if response.endswith(b"\n"):
                break

        if not response:
            return {"ok": False, "error": "No response from server"}

        reply = json.loads(response.decode("utf-8").strip())
        return reply
    except socket.timeout:
        return {"ok": False, "error": "Connection timed out"}
    except ConnectionRefusedError:
        return {"ok": False, "error": "Connection refused — is the app running?"}
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(
        description="Send JSON-RPC requests to ArtCraft control protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get app status
  python control_call.py --port 7877 --token-file token.txt --method engine.execute --params '{"command":"apps.status"}'

  # Get window state
  python control_call.py --port 7877 --token-file token.txt --method ui.get

  # List commands
  python control_call.py --port 7877 --token-file token.txt --method engine.commands --params '{}'

  # Launch an app with control
  python control_call.py --port 7877 --token-file token.txt --method engine.execute --params '{"command":"app.launch","params":{"app":"photocraft","control":true}}'
        """,
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7877, help="Port (default: 7877)")
    parser.add_argument("--token-file", help="Path to control token file")
    parser.add_argument("--token", help="Control token (visible in process list — prefer file)")
    parser.add_argument("--method", required=True, help="Method name (e.g., engine.execute, ui.get)")
    parser.add_argument("--params", default="{}", help="JSON parameters")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Parse params
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Error: invalid --params JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Get token
    token = args.token or read_token(args.token_file)

    # First: authenticate
    auth_reply = send_request(args.host, args.port, "auth", {"token": token or ""}, request_id="auth")

    if not auth_reply.get("ok"):
        if args.json:
            print(json.dumps(auth_reply, indent=2))
        else:
            print(f"Authentication failed: {auth_reply.get('error', 'unknown error')}")
            print("Check your token file or --token argument.")
        sys.exit(1)

    # Then: send the actual request
    reply = send_request(args.host, args.port, args.method, params, request_id="1")

    if args.json:
        print(json.dumps(reply, indent=2, ensure_ascii=False))
    else:
        if reply.get("ok"):
            result = reply.get("result", {})
            if isinstance(result, (dict, list)):
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(result)
        else:
            print(f"Error: {reply.get('error', 'unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
