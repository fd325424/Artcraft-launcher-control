#!/usr/bin/env python3
"""
ArtCraft 控制协议客户端

功能：
    向正在运行的 ArtCraft Launcher 或 Crafting App 发送 JSON-RPC 请求
    （通过 loopback TCP 连接），并自动处理认证。

协议要点：
    按控制协议规定，每条连接的首个请求必须是 `auth`；
    因此本客户端在【同一条连接】上先认证、再发送真实请求。

用法：
    python control_call.py --host 127.0.0.1 --port 7877 \
        --method engine.execute --params '{"command":"apps.status"}'

    python control_call.py --host 127.0.0.1 --port 7877 \
        --method ui.get

    python control_call.py --host 127.0.0.1 --port 7877 \
        --method engine.execute --params '{"command":"app.launch","params":{"app":"photocraft","control":true}}'

    # 使用 token 文件
    python control_call.py --port 7877 --token-file /path/to/token \
        --method engine.execute --params '{"command":"apps.status"}'
"""

# 引入标准库：argparse 解析命令行参数，json 处理 JSON，socket 建立 TCP 连接，sys 标准错误输出，Path 路径操作
import argparse
import json
import socket
import sys
from pathlib import Path


def read_token(token_file=None):
    """从文件读取控制 token，失败返回 None。"""
    # 仅当指定了 token 文件路径时才读取
    if token_file:
        try:
            # 读取文件内容并去除首尾空白（strip）
            return Path(token_file).read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            # 文件不存在返回 None
            return None
    # 未指定文件返回 None
    return None


def _send_line(sock, request):
    """发送一行 JSON 请求，并返回解析后的响应行。"""
    # 将请求字典序列化为 JSON 字符串并追加换行符
    req_line = json.dumps(request) + "\n"
    # 将字符串编码为 UTF-8 字节并发送到 socket
    sock.sendall(req_line.encode("utf-8"))

    # 累积接收响应字节
    response = b""
    # 循环接收，直到读到以换行符结尾的一行
    while True:
        # 每次最多接收 4096 字节
        chunk = sock.recv(4096)
        # 对端关闭连接则退出循环
        if not chunk:
            break
        # 拼接本次接收的数据
        response += chunk
        # 以换行符结尾则说明一行响应接收完毕
        if response.endswith(b"\n"):
            break

    # 未收到任何响应
    if not response:
        return {"ok": False, "error": "No response from server"}
    # 解码字节为字符串、去除首尾空白、解析为 JSON 字典
    return json.loads(response.decode("utf-8").strip())


def send_authenticated(host, port, method, params=None, token=None, request_id="1"):
    """
    建立【单条】TCP 连接，先发送认证请求（协议要求每连接首个请求必须为 auth），
    然后在【同一条连接】上发送真实请求。

    返回真实请求的响应，或错误字典。
    认证失败会在错误字典中标记 "stage": "auth"，便于调用方区分。
    """
    # params 未指定时初始化为空字典
    if params is None:
        params = {}

    # 创建 TCP socket 对象
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置 10 秒超时
    sock.settimeout(10)
    try:
        # 连接到目标主机端口
        sock.connect((host, port))

        # 1) 在这条连接上先发送认证请求
        # 认证请求格式：{"id":"auth","method":"auth","params":{"token":"..."}}
        auth_reply = _send_line(sock, {
            "id": "auth",
            "method": "auth",
            "params": {"token": token or ""},
        })
        # 若认证失败
        if not auth_reply.get("ok"):
            # 确保错误消息存在
            auth_reply.setdefault("error", "authentication failed")
            # 标记为认证阶段失败
            auth_reply["stage"] = "auth"
            return auth_reply

        # 2) 在【同一条连接】上发送真实请求
        # 请求格式：{"id":<request_id>,"method":<method>,"params":<params>}
        return _send_line(sock, {"id": request_id, "method": method, "params": params})
    # 连接超时异常
    except socket.timeout:
        return {"ok": False, "error": "Connection timed out"}
    # 连接被拒绝（服务未启动）
    except ConnectionRefusedError:
        return {"ok": False, "error": "Connection refused — is the app running?"}
    # 响应 JSON 解析失败
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON response: {e}"}
    # 其他未预期异常
    except Exception as e:
        return {"ok": False, "error": str(e)}
    # finally 确保 socket 关闭
    finally:
        sock.close()


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="Send JSON-RPC requests to ArtCraft control protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # 帮助文本底部示例（RawDescriptionHelpFormatter 保留原始格式）
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
    # 主机参数，默认 127.0.0.1
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    # 端口参数，默认 7877
    parser.add_argument("--port", type=int, default=7877, help="Port (default: 7877)")
    # token 文件路径
    parser.add_argument("--token-file", help="Path to control token file")
    # token 直接指定（注意：会出现在进程列表中，推荐使用文件方式）
    parser.add_argument("--token", help="Control token (visible in process list — prefer file)")
    # 方法名（必填）
    parser.add_argument("--method", required=True, help="Method name (e.g., engine.execute, ui.get)")
    # JSON 参数，默认空对象
    parser.add_argument("--params", default="{}", help="JSON parameters")
    # 原始 JSON 输出开关
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # 解析命令行参数
    args = parser.parse_args()

    # 解析 --params JSON 字符串
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        # 解析失败输出到 stderr 并退出
        print(f"Error: invalid --params JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # 获取 token：优先命令行 --token，其次从文件读取
    token = args.token or read_token(args.token_file)

    # 在单条连接上完成认证 + 真实请求
    reply = send_authenticated(args.host, args.port, args.method, params, token=token)

    # JSON 输出模式：直接打印原始响应
    if args.json:
        print(json.dumps(reply, indent=2, ensure_ascii=False))
    else:
        # 人读输出模式
        # 若为认证阶段失败
        if reply.get("stage") == "auth":
            print(f"Authentication failed: {reply.get('error', 'unknown error')}")
            print("Check your token file or --token argument.")
            sys.exit(1)
        # 若请求成功
        if reply.get("ok"):
            result = reply.get("result", {})
            # 结果为字典或列表时美化输出
            if isinstance(result, (dict, list)):
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                # 其他类型直接打印
                print(result)
        else:
            # 请求失败输出错误并退出
            print(f"Error: {reply.get('error', 'unknown error')}")
            sys.exit(1)


# 脚本入口：直接运行本文件时调用 main()
if __name__ == "__main__":
    main()
