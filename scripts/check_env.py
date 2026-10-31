#!/usr/bin/env python3
"""
ArtCraft 环境检测脚本

功能：
    检测本机已安装的 ArtCraft 组件：
      - ArtCraft Launcher（artcraft-toolbox / artcraft-launcher）
      - Crafting App CLI（photocraft-cli、filmcraft-cli 等 12 款）
      - ArtCraft MCP server
      - 凭证 / 令牌

用法：
    python check_env.py              # 人读输出
    python check_env.py --json        # JSON 输出（供程序消费）
"""

# 引入标准库：json 用于 JSON 输出，os 用于环境变量与平台判断，shutil 用于 PATH 查找，sys 用于参数，Path 用于路径操作
import json
import os
import shutil
import sys
from pathlib import Path


# --- Launcher 待检测工具名 ---
# Launcher 是应用启动器，支持多个可能的可执行名
LAUNCHER_TOOLS = ["artcraft-toolbox", "artcraft-toolbox-cli", "artcraft-launcher"]

# --- Crafting App CLI 待检测列表 ---
# 12 款 Crafting Apps 的 CLI 可执行名（注意：官网实际为 13 款，含 FigCraft，但本列表沿用项目既有口径）
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

# --- Crafting App CLI 常见安装目录 ---
# （当 CLI 不在 PATH 时，回退扫描这些目录及其一层子目录）
CRAFT_INSTALL_DIRS = [
    Path("C:/Program Files"),          # 扫描此处 *Craft/*raft 子目录
    Path("C:/Program Files/ArtCraft"),
    Path.home() / "Artcraft" / "apps",
    Path("D:/Artcraft/apps"),
]

# --- MCP server 可执行文件名 ---
# 官方 core 版与社区扩展版的可执行名都检测
MCP_SERVERS = ["artcraft-mcp.exe", "artcraft-mcp-server.exe"]

# --- 凭证文件位置 ---
# ArtCraft 桌面应用凭据默认存放于用户目录下
CRED_HOME = Path.home() / "Artcraft" / "credentials"
# 会话与 AVT 令牌文件名
CRED_FILES = ["artcraft_session.txt", "artcraft_avt.txt"]

# --- MCP 客户端配置文件位置 ---
# 覆盖 WorkBuddy 与 Windsurf 两类主流客户端
MCP_CONFIGS = [
    Path.home() / ".workbuddy" / "mcp.json",
    Path.home() / ".codeium" / "windsurf" / "mcp_config.json",
]


def find_in_path(name):
    """检查命令是否存在于 PATH 中（返回 bool）。"""
    # shutil.which 在 PATH 中查找可执行文件，找到则返回路径，否则 None
    return shutil.which(name) is not None


def find_executable(name):
    """在 PATH 中查找可执行文件，返回完整路径或 None。"""
    # 返回路径字符串本身（而非 bool），便于后续直接使用
    return shutil.which(name)


def check_launcher():
    """检测 ArtCraft Launcher 是否安装。"""
    results = []
    # 遍历三个可能的 Launcher 可执行名
    for tool in LAUNCHER_TOOLS:
        # 在 PATH 中查找
        path = find_executable(tool)
        # 记录每个工具的查找结果
        results.append({
            "name": tool,
            "found": path is not None,
            "path": path,
        })
    # 只要有一个工具存在即视为 Launcher 已安装
    installed = any(r["found"] for r in results)
    return {
        "component": "launcher",
        "installed": installed,
        "tools": results,
    }


def find_craft_cli(name):
    """查找 Crafting App CLI：先查 PATH，再回退常见安装目录。"""
    # 第一步：直接查 PATH
    path = find_executable(name)
    if path:
        return path
    # 第二步：回退到常见安装目录（含一层子目录，如 C:\Program Files\PdfCraft\）
    # 根据操作系统决定可执行文件后缀（Windows 为 .exe）
    exe_name = name + ".exe" if os.name == "nt" else name
    for d in CRAFT_INSTALL_DIRS:
        # 目录不存在则跳过
        if not d.exists():
            continue
        # 候选目录列表：当前目录本身
        candidates = [d]
        # 加入当前目录的一级子目录（如 C:\Program Files\PdfCraft）
        try:
            candidates.extend(p for p in d.iterdir() if p.is_dir())
        except (PermissionError, OSError):
            # 目录不可读时静默跳过，继续下一个候选
            pass
        for c in candidates:
            try:
                # 在候选目录内查找文件名匹配的可执行文件
                for entry in c.iterdir():
                    if entry.name.lower() == exe_name.lower() and entry.is_file():
                        return str(entry)
            except (PermissionError, OSError):
                # 目录不可读时静默跳过
                pass
    # 未找到返回 None
    return None


def check_craft_clis():
    """检测所有 Crafting App CLI 的安装情况。"""
    results = []
    # 逐个检测 12 款 CLI
    for cli in CRAFT_CLIS:
        path = find_craft_cli(cli)
        results.append({
            "name": cli,
            "found": path is not None,
            "path": path,
        })
    # 已安装的 CLI 名称列表
    installed = [r["name"] for r in results if r["found"]]
    return {
        "component": "craft_clis",
        "installed_count": len(installed),
        "installed": installed,
        "missing": [r["name"] for r in results if not r["found"]],
        "tools": results,
    }


def check_mcp_server():
    """检测 ArtCraft MCP server 是否安装。"""
    # 第一步：在 PATH 中查找两个 MCP 可执行文件
    for server in MCP_SERVERS:
        path = find_executable(server)
        if path:
            return {
                "component": "mcp_server",
                "found": True,
                "path": path,
            }

    # 第二步：回退到常见安装目录
    common_dirs = [
        Path.home() / "Artcraft" / "mcp",
        Path.home() / "artcraft-mcp" / "bin",
        Path("C:/Artcraft/mcp/bin"),
        Path("D:/Artcraft/mcp/bin"),
    ]

    # 在每个候选目录中查找 MCP 可执行文件
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

    # 未找到返回未安装
    return {
        "component": "mcp_server",
        "found": False,
        "path": None,
    }


def check_credentials():
    """检测 ArtCraft 凭证：文件、环境变量、桌面应用 Cookie。"""
    results = []
    # 逐个检查凭证文件是否存在
    for fname in CRED_FILES:
        fpath = CRED_HOME / fname
        exists = fpath.exists()
        results.append({
            "name": fname,
            "exists": exists,
            "path": str(fpath),
        })

    # 检查相关环境变量（API key / 会话令牌等）
    env_vars = {
        "ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN": os.environ.get("ARTCRAFT_MCP_PRIVATE_SESSION_TOKEN"),
        "ARTCRAFT_API_KEY": os.environ.get("ARTCRAFT_API_KEY"),
        "ARTCRAFT_SESSION": os.environ.get("ARTCRAFT_SESSION"),
        "ARTCRAFT_AVT": os.environ.get("ARTCRAFT_AVT"),
    }
    # 转换为 {变量名: 是否存在} 的布尔映射
    env_found = {k: v is not None for k, v in env_vars.items()}

    # 检查桌面应用 Cookie 目录（用于桌面登录态）
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
        # 只要任一凭证来源存在即视为有效
        "any_valid": any(r["exists"] for r in results) or any(env_found.values()) or cookies_found,
    }


def check_mcp_config():
    """检测 MCP 客户端配置中是否包含 ArtCraft。"""
    results = []
    # 逐个检查配置文件
    for config_path in MCP_CONFIGS:
        if config_path.exists():
            try:
                # 读取配置文件内容
                content = config_path.read_text(encoding="utf-8")
                # 简单检查配置中是否出现 "artcraft" 字样（大小写不敏感）
                has_artcraft = "artcraft" in content.lower()
                results.append({
                    "path": str(config_path),
                    "exists": True,
                    "has_artcraft": has_artcraft,
                })
            except Exception as e:
                # 读取失败时记录错误但不中断
                results.append({
                    "path": str(config_path),
                    "exists": True,
                    "has_artcraft": False,
                    "error": str(e),
                })
        else:
            # 配置文件不存在
            results.append({
                "path": str(config_path),
                "exists": False,
                "has_artcraft": False,
            })
    return {
        "component": "mcp_config",
        "configs": results,
        # 任一配置中包含 ArtCraft 即视为已配置
        "any_configured": any(r.get("has_artcraft") for r in results),
    }


def main():
    # 判断是否使用 JSON 输出模式
    use_json = "--json" in sys.argv

    # 构建完整检测报告（包含五大组件）
    report = {
        "artcraft_env_check": {
            "launcher": check_launcher(),
            "craft_clis": check_craft_clis(),
            "mcp_server": check_mcp_server(),
            "credentials": check_credentials(),
            "mcp_config": check_mcp_config(),
        }
    }

    # JSON 模式：直接输出
    if use_json:
        # indent=2 美化缩进；ensure_ascii=False 保留中文
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    # 人读输出模式
    lc = report["artcraft_env_check"]

    # 打印标题
    print("=" * 60)
    print("  ArtCraft Environment Check")
    print("=" * 60)

    # --- L1 Launcher 检测结果 ---
    print("\n  [L1] Launcher")
    if lc["launcher"]["installed"]:
        # 已安装：列出各工具状态
        for tool in lc["launcher"]["tools"]:
            status = "OK" if tool["found"] else "--"
            print(f"    {status}  {tool['name']:<25} {tool['path'] or ''}")
    else:
        # 未安装：给出提示
        print("    [MISSING] ArtCraft Launcher not found in PATH")
        print("    -> Download from getartcraft.com or GitHub releases (storytold)")

    # --- L2 Crafting App CLIs 检测结果 ---
    print("\n  [L2] Crafting App CLIs")
    if lc["craft_clis"]["installed_count"] > 0:
        # 已安装部分 CLI
        print(f"    Installed: {lc['craft_clis']['installed_count']}/12")
        for name in lc["craft_clis"]["installed"]:
            print(f"    OK  {name}")
        # 列出缺失的 CLI
        if lc["craft_clis"]["missing"]:
            print(f"    Missing: {', '.join(lc['craft_clis']['missing'])}")
    else:
        # 未安装任何 CLI
        print("    [MISSING] No Crafting App CLIs found")
        print("    -> Install via ArtCraft Launcher")

    # --- L3 MCP Server 检测结果 ---
    print("\n  [L3] MCP Server")
    if lc["mcp_server"]["found"]:
        print(f"    OK  {lc['mcp_server']['path']}")
    else:
        print("    [MISSING] artcraft-mcp server not found")
        print("    -> git clone https://github.com/theCosmicCrafter/artcraft-mcp (third-party)")

    # --- 凭证检测结果 ---
    print("\n  [Auth] Credentials")
    cred = lc["credentials"]
    if cred["any_valid"]:
        # 至少有一个凭证源
        print("    OK  At least one credential source found")
        for f in cred["files"]:
            status = "OK" if f["exists"] else "--"
            print(f"    {status}  {f['name']}")
        for var, found in cred["env_vars"].items():
            status = "OK" if found else "--"
            print(f"    {status}  {var}")
    else:
        # 无任何凭证
        print("    [MISSING] No credentials found")
        print("    -> Log into ArtCraft desktop app or set env vars")

    # --- MCP 客户端配置检测结果 ---
    print("\n  [MCP] Client Config")
    for config in lc["mcp_config"]["configs"]:
        if config["exists"]:
            # 配置文件存在：显示是否有 ArtCraft
            status = "OK" if config["has_artcraft"] else "--"
            print(f"    {status}  {config['path']}")
        else:
            # 配置文件不存在
            print(f"    --   {config['path']} (not found)")

    # --- 总结 ---
    print("\n" + "=" * 60)
    # 判断是否就绪：Launcher 已装 且 至少一个 CLI 已装
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


# 脚本入口：直接运行本文件时调用 main()
if __name__ == "__main__":
    main()
