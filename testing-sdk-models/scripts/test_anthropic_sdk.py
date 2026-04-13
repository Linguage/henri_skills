#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Claude Agent SDK 对各模型 provider 的连通性
用法:
  python test_sdk.py [provider]          # 测试指定 provider (默认 glm)
  python test_sdk.py --all               # 测试所有可用 provider
  python test_sdk.py --switch <provider> # 切换 provider 并测试
  python test_sdk.py --switch --list     # 列出所有可用 provider
  python test_sdk.py claude               # 使用当前环境变量（原始 Claude）
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

KEYS_DIR = Path.home() / ".configanthropic" / "keys"
SCRIPT_DIR = Path(__file__).resolve().parent


def list_providers() -> list[str]:
    """列出所有可用 provider"""
    if not KEYS_DIR.exists():
        return []
    return sorted(p.name for p in KEYS_DIR.iterdir() if p.is_file())


def load_provider(name: str) -> str:
    """从 ~/.configanthropic/keys/<name> 读取并设置环境变量，返回模型名"""
    key_file = KEYS_DIR / name
    if not key_file.exists():
        available = ", ".join(list_providers()) or "(无)"
        print(f"❌ 配置文件不存在: {key_file}")
        print(f"   可用 provider: {available}")
        sys.exit(1)

    for line in key_file.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip('"').strip("'")

    model = os.environ.get("ANTHROPIC_MODEL", "unknown")
    print(f"🔑 已加载 {name} → 模型: {model}")
    return model


def clear_provider_env():
    """清除 provider 环境变量，恢复默认"""
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"):
        os.environ.pop(key, None)


def switch_api(provider: str) -> None:
    """调用 switch_api.sh 切换 provider，并将环境变量同步到当前进程"""
    if provider == "--list":
        # 直接列出可用 provider
        print("📋 可用 provider:")
        for p in list_providers():
            key_file = KEYS_DIR / p
            model = "unknown"
            for line in key_file.read_text(encoding="utf-8").splitlines():
                if "ANTHROPIC_MODEL" in line:
                    model = line.split("=", 1)[1].strip().strip('"').strip("'")
            print(f"   {p} → {model}")
        return

    # 通过 bash 执行 switch_api.sh 并捕获导出的环境变量
    script = f"""
        source "{SCRIPT_DIR}/switch_api.sh" "{provider}" >&2
        # 输出当前环境变量供 Python 捕获
        echo "ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY:-}}"
        echo "ANTHROPIC_BASE_URL=${{ANTHROPIC_BASE_URL:-}}"
        echo "ANTHROPIC_MODEL=${{ANTHROPIC_MODEL:-}}"
    """
    result = subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True
    )
    # 显示 switch_api.sh 的输出（在 stderr）
    if result.stderr:
        print(result.stderr.strip())

    if result.returncode != 0:
        sys.exit(1)

    # 解析并设置环境变量
    clear_provider_env()
    for line in result.stdout.strip().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            if v:  # 非空才设置
                os.environ[k] = v


async def test_provider(provider: str) -> bool:
    """测试单个 provider，返回是否成功"""
    # 每次测试前清除旧变量
    clear_provider_env()

    if provider not in ("off", "claude"):
        model = load_provider(provider)
    else:
        model = "default (Claude)"
        print(f"🔑 使用当前环境默认配置 → {model}")

    # 延迟导入，确保环境变量生效后再初始化
    from claude_agent_sdk import query, ClaudeAgentOptions

    # Claude 原生模式用 opus plan；第三方 provider 不设 model（由环境变量控制）
    is_claude = provider in ("off", "claude")
    opts = ClaudeAgentOptions(
        allowed_tools=[],
        model="claude-opus-4-6" if is_claude else None,
        permission_mode="plan" if is_claude else None,
    )

    print(f"🧪 测试中...", end=" ", flush=True)

    try:
        async for message in query(
            prompt="请用中文简单介绍一下你自己，限制在50字以内。",
            options=opts,
        ):
            if hasattr(message, "result"):
                print(f"✅ 成功")
                print(f"   结果: {message.result}")
            elif hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(f"✅ 收到回复")
                        print(f"   回复: {block.text}")
        return True

    except Exception as e:
        error_msg = str(e)
        if "hit your limit" in error_msg.lower():
            print(f"⚠️  已达用量上限")
        else:
            print(f"❌ 失败: {error_msg}")
        return False


async def main():
    # 避免嵌套 Claude Code 检测
    os.environ.pop("CLAUDECODE", None)

    args = sys.argv[1:]

    # --switch 模式：调用 switch_api.sh 切换并测试
    if "--switch" in args:
        args.remove("--switch")
        target = args[0] if args else "--list"
        switch_api(target)
        if target == "--list":
            sys.exit(0)
        # 切换后自动测试（provider 已通过 switch_api 加载，用 off 跳过重复加载）
        ok = await test_provider("off")
        sys.exit(0 if ok else 1)

    if "--all" in args:
        providers = list_providers()
        if not providers:
            print(f"❌ 未找到任何 provider，请检查 {KEYS_DIR}")
            sys.exit(1)

        print(f"📋 测试所有 provider: {', '.join(providers)}\n")
        results: dict[str, bool] = {}

        for p in providers:
            print(f"\n{'='*40}")
            results[p] = await test_provider(p)

        # 汇总
        print(f"\n{'='*40}")
        print("📊 测试汇总:")
        for p, ok in results.items():
            status = "✅ 通过" if ok else "❌ 失败"
            print(f"   {p}: {status}")

        failed = sum(1 for ok in results.values() if not ok)
        sys.exit(1 if failed else 0)

    else:
        provider = args[0] if args else "glm"
        ok = await test_provider(provider)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
