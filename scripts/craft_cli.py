#!/usr/bin/env python3
"""
ArtCraft Crafting App CLI 封装器

功能：
    将各 Crafting App CLI 的多种语法风格封装为统一命令入口，
    自动按应用选择正确的语法风格生成并执行命令。

用法：
    # 列出某应用的命令
    python craft_cli.py list --app designcraft

    # 搜索命令
    python craft_cli.py search --app designcraft --search "export"

    # 查看命令详情
    python craft_cli.py describe --app designcraft --id "file.exportPdf"

    # 执行命令（自动检测语法风格）
    python craft_cli.py run --app designcraft --cmd "file.exportPdf" --params '{"path":"out.pdf"}'

    # 执行多条命令（每个 --params 与前面的 --cmd 配对）
    python craft_cli.py run --app designcraft --cmd "file.new" --cmd "page.insert" --params '{}'

    # 执行 FilmCraft JSONL 脚本
    python craft_cli.py run --app filmcraft --script script.jsonl

    # PdfCraft 透传（子命令风格）
    python craft_cli.py run --app pdfcraft --cmd "info report.pdf --page 1"

    # 检查文件
    python craft_cli.py inspect --app photocraft --file "image.psd"

    # 格式转换
    python craft_cli.py convert --app photocraft --input "a.psd" --output "b.png"

    # 仅显示生成的 CLI 命令而不执行
    python craft_cli.py run --app designcraft --cmd "file.exportPdf" --dry-run
"""

# 引入标准库：argparse 解析参数，json 处理 JSON，shlex shell 引号处理，subprocess 执行外部命令，sys 标准输出
import argparse
import json
import shlex
import subprocess
import sys


# ---------------------------------------------------------------------------
# 各应用的 CLI 配置档案（PROFILES）
#
# style "engine"         — `commands` / `describe` / `run --cmd ID=JSON`
#                          （designcraft 已对照真实二进制验证；
#                           photocraft/vectorcraft 依据官方 photocraft-cli v0.16 指南，同族）
# style "inline-json"    — `--cmd 'id={json}'` 单次调用中可重复
# style "key-value"      — 位置参数 id + `--key=value` 键值对
# style "positional-json" — 位置参数 id + '{json}' 参数
# style "script"         — `--script file.jsonl`
# style "subcommand"     — 原始子命令透传（pdfcraft，已验证）
# ---------------------------------------------------------------------------

PROFILES = {
    # ---- 已对照真实二进制验证（2026-10-31）----
    "designcraft": {
        "style": "engine",
        "list": ["commands"],                 # commands [FILTER]
        "search": ["commands"],               # 过滤条件为位置参数
        "search_positional": True,
        "describe": ["describe"],             # describe COMMAND
        "describe_positional": True,
        "run_base": ["run"],
        "run_input_flag": "--in",             # run --in FILE | --sample
        "run_no_input": ["--sample"],
        "run_output_flag": "--export",
    },
    # ---- 官方指南（photocraft-cli v0.16），本机未验证 ----
    "photocraft": {
        "style": "engine",
        "list": ["commands"],
        "search": ["commands", "--filter"],
        "search_positional": False,
        "describe": ["commands", "--filter"],  # + id + --json 获取参数文档
        "describe_positional": True,
        "describe_json": True,
        "run_base": ["run"],
        "run_input_flag": None,               # 输入文件为位置参数
        "run_input_positional": True,
        "run_no_input": ["--new"],
        "run_output_flag": "--out",
    },
    "vectorcraft": {
        "style": "engine",
        "list": ["commands"],
        "search": ["commands", "--filter"],
        "search_positional": False,
        "describe": ["commands", "--filter"],
        "describe_positional": True,
        "describe_json": True,
        "run_base": ["run"],
        "run_input_flag": None,
        "run_input_positional": True,
        "run_no_input": ["--new"],
        "run_output_flag": "--out",
    },

    # ---- 文档化分组（语法未在本机验证）----
    "gridcraft":    {"style": "inline-json"},
    "cadcraft":     {"style": "inline-json"},
    "deckcraft":    {"style": "inline-json"},
    "wordcraft":    {"style": "inline-json"},
    "soundcraft":   {"style": "inline-json"},
    "lightcraft":   {"style": "key-value"},
    "effectcraft":  {"style": "positional-json"},
    "filmcraft":    {"style": "script"},

    # ---- 已对照真实二进制验证（2026-10-31）----
    "pdfcraft":     {"style": "subcommand"},
}

# 帮助文本中展示的语法风格说明
SYNTAX_HELP = """Syntax styles:
  engine           designcraft, photocraft, vectorcraft
                   commands / describe / run --cmd ID=JSON
  inline-json      gridcraft, cadcraft, deckcraft, wordcraft, soundcraft
                   --cmd 'id={json}' (repeatable)
  key-value        lightcraft
                   id --key=value ...
  positional-json  effectcraft
                   id '{json}'
  script           filmcraft
                   --script file.jsonl
  subcommand       pdfcraft (passthrough: --cmd "info file.pdf --page 1")
"""


def run_cli(args_list, capture_output=True):
    """执行一条 CLI 命令并返回结果字典。"""
    try:
        # 使用 subprocess.run 执行外部命令
        result = subprocess.run(
            args_list,
            capture_output=capture_output,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        # 封装执行结果（returncode / stdout / stderr / ok）
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "ok": result.returncode == 0,
        }
    # 命令不存在（CLI 未安装）
    except FileNotFoundError:
        return {"returncode": -1, "ok": False, "error": f"Command not found: {args_list[0]}"}
    # 执行超时（60 秒）
    except subprocess.TimeoutExpired:
        return {"returncode": -2, "ok": False, "error": "Command timed out (60s)"}
    # 其他异常
    except Exception as e:
        return {"returncode": -3, "ok": False, "error": str(e)}


def emit_and_run(args_list, dry_run):
    """dry-run 模式仅打印命令；否则执行命令。"""
    # dry-run：用 shlex.quote 对每个参数加引号后拼接为字符串显示
    if dry_run:
        return {"returncode": 0, "ok": True, "stdout": " ".join(shlex.quote(a) for a in args_list), "dry_run": True}
    # 正常执行
    return run_cli(args_list)


# ---------------------------------------------------------------------------
# 各语法风格的命令构建器
# ---------------------------------------------------------------------------

def build_list(cli, profile, dry_run):
    """构建"列出命令"的 CLI 调用。"""
    # engine 风格：使用 profile["list"]（如 ["commands"]）
    if profile["style"] == "engine":
        return emit_and_run([cli] + profile["list"], dry_run)
    # subcommand 风格（pdfcraft）：无命令注册表，展示 --help
    if profile["style"] == "subcommand":
        return emit_and_run([cli, "--help"], dry_run)
    # 其他文档化分组：command_list
    return emit_and_run([cli, "command_list"], dry_run)


def build_search(cli, profile, keyword, dry_run):
    """构建"搜索命令"的 CLI 调用。"""
    # engine 风格
    if profile["style"] == "engine":
        # 基础搜索命令（如 commands 或 commands --filter）
        args = [cli] + profile["search"]
        if profile.get("search_positional"):
            # 过滤条件为位置参数（如 designcraft-cli commands export）
            if keyword:
                args.append(keyword)
        elif keyword:
            # 过滤条件通过 --filter 选项传递
            args.extend(["--filter", keyword])
        return emit_and_run(args, dry_run)
    # subcommand 风格：无命令注册表，返回错误提示
    if profile["style"] == "subcommand":
        return {
            "returncode": 1, "ok": False,
            "error": "pdfcraft has no command registry; see 'pdfcraft-cli --help' for its subcommands",
        }
    # 其他分组：command_list --search
    return emit_and_run([cli, "command_list", "--search", keyword], dry_run)


def build_describe(cli, profile, cmd_id, dry_run):
    """构建"查看命令详情"的 CLI 调用。"""
    # engine 风格
    if profile["style"] == "engine":
        # 基础 describe 命令（如 describe 或 commands --filter）
        args = [cli] + profile["describe"]
        if profile.get("describe_positional"):
            # 命令 id 为位置参数（如 designcraft-cli describe file.exportPdf）
            args.append(cmd_id)
        else:
            # 命令 id 通过 --id 选项传递
            args.extend(["--id", cmd_id])
        if profile.get("describe_json"):
            # 附加 --json 以获取 JSON 格式参数文档
            args.append("--json")
        return emit_and_run(args, dry_run)
    # subcommand 风格：无 describe，返回错误提示
    if profile["style"] == "subcommand":
        return {
            "returncode": 1, "ok": False,
            "error": "pdfcraft has no describe; run 'pdfcraft-cli <subcommand> --help' style usage via --help",
        }
    # 文档化旧分组（key-value / positional-json）：describe COMMAND
    if profile["style"] in ("key-value", "positional-json"):
        return emit_and_run([cli, "describe", cmd_id], dry_run)
    # 其他分组：describe --id COMMAND
    return emit_and_run([cli, "describe", "--id", cmd_id], dry_run)


def build_run(cli, profile, cmd, params, input_file, output_file, script, dry_run):
    """构建"执行命令"的 CLI 调用（核心逻辑，按风格分支）。"""
    style = profile["style"]

    # FilmCraft / script 风格：需要 JSONL 脚本文件
    if style == "script":
        if not script:
            return {"returncode": 1, "ok": False, "error": "filmcraft requires --script file.jsonl"}
        return emit_and_run([cli, "--script", script], dry_run)

    # PdfCraft 透传（subcommand 风格）
    if style == "subcommand":
        if not cmd:
            return {"returncode": 1, "ok": False, "error": "--cmd required (e.g. --cmd 'info file.pdf')"}
        # cmd 是 --cmd 值列表；透传行取第一个
        # 将透传字符串按 shell 规则拆分为参数列表
        try:
            parts = shlex.split(cmd[0])
        except ValueError as e:
            # 引号使用错误
            return {"returncode": 1, "ok": False, "error": f"bad --cmd quoting: {e}"}
        return emit_and_run([cli] + parts, dry_run)

    # 通用前置检查：非 script/subcommand 风格必须提供 --cmd
    if not cmd:
        return {"returncode": 1, "ok": False, "error": "--cmd required for run action"}

    # engine 风格：run [--in FILE|--sample|--new|位置文件] --cmd ID=JSON ...
    if style == "engine":
        # 基础命令（run）
        args = [cli] + profile["run_base"]
        if input_file:
            if profile.get("run_input_positional"):
                # 输入文件为位置参数
                args.append(input_file)
            else:
                # 输入文件通过 flag 传递（如 --in）
                args.extend([profile["run_input_flag"], input_file])
        else:
            # 无输入文件时使用替代参数（如 --sample / --new）
            args.extend(profile.get("run_no_input", []))
        if output_file:
            # 输出文件通过 flag 传递（如 --export / --out）
            args.extend([profile["run_output_flag"], output_file])
        # 将每个 --cmd 与其对应的 --params 配对生成 --cmd ID=JSON
        for c, p in zip(cmd, params):
            if p:
                args.extend(["--cmd", f"{c}={json.dumps(p, ensure_ascii=False)}"])
            else:
                args.extend(["--cmd", c])
        return emit_and_run(args, dry_run)

    # inline-json 风格：单次调用中重复 --cmd 'id={json}'
    if style == "inline-json":
        args = [cli]
        for c, p in zip(cmd, params):
            inline = f"{c}={json.dumps(p or {}, ensure_ascii=False)}"
            args.extend(["--cmd", inline])
        return emit_and_run(args, dry_run)

    # key-value 风格：位置 id + --key=value ...
    if style == "key-value":
        results = []
        for c, p in zip(cmd, params):
            args = [cli, c]
            for k, v in (p or {}).items():
                args.append(f"--{k}={v}")
            results.append({"command": c, "result": emit_and_run(args, dry_run)})
        return _merge(results, dry_run)

    # positional-json 风格：位置 id + '{json}'
    if style == "positional-json":
        results = []
        for c, p in zip(cmd, params):
            args = [cli, c]
            if p:
                args.append(json.dumps(p, ensure_ascii=False))
            results.append({"command": c, "result": emit_and_run(args, dry_run)})
        return _merge(results, dry_run)

    # 未知风格报错
    return {"returncode": 1, "ok": False, "error": f"unsupported style: {style}"}


def _merge(results, dry_run):
    """合并 key-value / positional-json 风格的多条命令结果。"""
    # 只有一条命令时直接返回该结果
    if len(results) == 1:
        return results[0]["result"]
    # dry-run 模式：拼接各命令的 stdout
    if dry_run:
        return {"returncode": 0, "ok": True, "dry_run": True,
                "stdout": "\n".join(r["result"].get("stdout", "") for r in results)}
    # 正常模式：返回结构化结果（ok 为所有命令均成功）
    return {"results": results, "ok": all(r["result"].get("ok") for r in results),
            "returncode": 0 if all(r["result"].get("ok") for r in results) else 1}


def build_inspect(cli, profile, file_path, dry_run):
    """构建"检查文件"的 CLI 调用。"""
    # 前置检查：必须提供文件路径
    if not file_path:
        return {"returncode": 1, "ok": False, "error": "--file required for inspect"}
    # subcommand 风格（pdfcraft）：使用 info 子命令
    if profile["style"] == "subcommand":
        return emit_and_run([cli, "info", file_path], dry_run)
    # engine 风格：使用 info
    if profile["style"] == "engine":
        return emit_and_run([cli, "info", file_path], dry_run)
    # 其他风格：inspect --file
    return emit_and_run([cli, "inspect", "--file", file_path], dry_run)


def build_convert(cli, profile, input_file, output_file, dry_run):
    """构建"格式转换"的 CLI 调用。"""
    # 前置检查：输入与输出文件都必须提供
    if not input_file or not output_file:
        return {"returncode": 1, "ok": False, "error": "--input and --output required for convert"}
    # subcommand 风格（pdfcraft）：无 convert，提示改用 run 透传
    if profile["style"] == "subcommand":
        return {"returncode": 1, "ok": False,
                "error": "pdfcraft has no convert; use 'run --cmd \"combine a.pdf b.pdf --out m.pdf\"' etc."}
    # engine 风格：convert INPUT OUTPUT
    if profile["style"] == "engine":
        return emit_and_run([cli, "convert", input_file, output_file], dry_run)
    # 其他风格：convert --input ... --output ...
    return emit_and_run([cli, "convert", "--input", input_file, "--output", output_file], dry_run)


# ---------------------------------------------------------------------------

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="ArtCraft Crafting App CLI Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # 底部展示语法风格说明
        epilog=SYNTAX_HELP,
    )
    # 动作参数（必选）：list / search / describe / run / inspect / convert
    parser.add_argument("action", choices=["list", "search", "describe", "run", "inspect", "convert"],
                        help="Action to perform")
    # 应用名（必填），如 designcraft
    parser.add_argument("--app", required=True, help="App name (e.g., designcraft)")
    # 命令 id（可重复；每个 --params 与前面的 --cmd 配对）
    parser.add_argument("--cmd", action="append",
                        help="Command id (repeatable; each --params pairs with the --cmd before it)")
    # JSON 参数（可重复，与前面的 --cmd 配对）
    parser.add_argument("--params", action="append",
                        help="JSON parameters for the preceding --cmd (repeatable)")
    # FilmCraft JSONL 脚本文件路径
    parser.add_argument("--script", help="JSONL script file path (FilmCraft)")
    # 搜索关键词
    parser.add_argument("--search", help="Search keyword for list/search")
    # describe 动作的命令 id
    parser.add_argument("--id", help="Command id for describe")
    # inspect 动作的文件路径
    parser.add_argument("--file", help="File path for inspect")
    # convert / run 动作的输入文件
    parser.add_argument("--input", help="Input file for convert / run")
    # convert / run 动作的输出文件
    parser.add_argument("--output", help="Output file for convert / run")
    # 原始 JSON 输出开关
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    # dry-run 开关：仅打印命令不执行
    parser.add_argument("--dry-run", action="store_true", help="Print the CLI command without executing it")

    # 解析命令行参数
    args = parser.parse_args()

    # 根据应用名生成 CLI 可执行名（如 designcraft -> designcraft-cli）
    cli_name = f"{args.app}-cli"
    # 从 PROFILES 中查找应用配置
    profile = PROFILES.get(args.app)
    # 应用不存在时报错并列出已知应用
    if profile is None:
        print(f"Error: unknown app '{args.app}'. Known apps: {', '.join(sorted(PROFILES))}", file=sys.stderr)
        sys.exit(1)

    # 将每个 --params 与它前面的 --cmd 配对
    cmds = args.cmd or []
    # 解析每个 --params JSON（可能为空）
    params_list = [json.loads(p) if p else {} for p in (args.params or [])]
    if len(params_list) > len(cmds):
        # params 数量多于 cmd 数量时报参数配对错误
        print("Error: --params given without a matching --cmd", file=sys.stderr)
        sys.exit(1)
    # 生成 (cmd, params) 配对列表；缺失 params 的 cmd 使用空字典
    paired = [(cmds[i], params_list[i] if i < len(params_list) else {}) for i in range(len(cmds))]

    try:
        # 根据动作类型分发到对应的构建器
        if args.action == "list":
            result = build_list(cli_name, profile, args.dry_run)
        elif args.action == "search":
            # search 动作必须提供 --search
            if not args.search:
                print("Error: --search required for search action", file=sys.stderr)
                sys.exit(1)
            result = build_search(cli_name, profile, args.search, args.dry_run)
        elif args.action == "describe":
            # describe 动作必须提供 --id
            if not args.id:
                print("Error: --id required for describe action", file=sys.stderr)
                sys.exit(1)
            result = build_describe(cli_name, profile, args.id, args.dry_run)
        elif args.action == "run":
            # 拆分配对后的 cmd 与 params 列表
            cmd_ids = [c for c, _ in paired]
            cmd_params = [p for _, p in paired]
            result = build_run(cli_name, profile, cmd_ids, cmd_params,
                               args.input, args.output, args.script, args.dry_run)
        elif args.action == "inspect":
            result = build_inspect(cli_name, profile, args.file, args.dry_run)
        elif args.action == "convert":
            result = build_convert(cli_name, profile, args.input, args.output, args.dry_run)
        else:
            # 未知动作（理论上不会触发，因 choices 已限定）
            result = {"returncode": 1, "ok": False, "error": f"unknown action {args.action}"}
    except json.JSONDecodeError as e:
        # JSON 参数解析失败：输出错误并退出
        print(f"Error: invalid --params JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    if args.json:
        # JSON 模式：美化输出
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 人读模式
        if result.get("ok"):
            output = result.get("stdout", "")
            # 有 stdout 则直接输出，否则输出完整结果 JSON
            print(output if output else json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 失败：优先使用 error，其次 stderr，最后通用错误消息
            msg = result.get("error") or result.get("stderr") or \
                f"Command failed with return code {result.get('returncode')}"
            print(msg, file=sys.stderr)
            sys.exit(1)


# 脚本入口：直接运行本文件时调用 main()
if __name__ == "__main__":
    main()
