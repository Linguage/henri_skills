#!/usr/bin/env python3
"""基于 OpenAI Agents SDK 测试第三方 provider (GLM / MiniMax)"""

import asyncio
import sys
from pathlib import Path

KEYS_DIR = Path.home() / ".configanthropic" / "keys"

PROVIDERS = {
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
    },
    "minimax": {
        "base_url": "https://api.minimax.io/v1",
    },
}


def list_providers() -> list[str]:
    if not KEYS_DIR.exists():
        return []
    return sorted(p.name for p in KEYS_DIR.iterdir() if p.is_file())


def load_key(name: str) -> tuple[str, str]:
    key_file = KEYS_DIR / name
    if not key_file.exists():
        print(f"❌ 配置文件不存在: {key_file}")
        sys.exit(1)
    api_key = ""
    model = ""
    for line in key_file.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if "=" in line:
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if "API_KEY" in k or "AUTH_TOKEN" in k:
                api_key = v
            if k == "ANTHROPIC_MODEL":
                model = v
    return api_key, model


async def test_provider(name: str) -> bool:
    from agents import (
        Agent,
        AsyncOpenAI,
        OpenAIChatCompletionsModel,
        Runner,
        set_tracing_disabled,
    )

    set_tracing_disabled(True)

    if name not in PROVIDERS:
        print(f"❌ 未知 provider: {name}")
        return False

    api_key, model = load_key(name)
    base_url = PROVIDERS[name]["base_url"]

    print(f"🔑 {name} → 模型: {model}, 端点: {base_url}")
    print(f"🧪 测试中...", end=" ", flush=True)

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    glm_model = OpenAIChatCompletionsModel(model=model, openai_client=client)

    agent = Agent(
        name=f"{name} Agent",
        instructions="你是一个简洁的助手，用中文回答，限制在50字以内。",
        model=glm_model,
    )

    try:
        result = await Runner.run(
            agent,
            "请用中文简单介绍一下你自己。",
        )
        print(f"✅ 成功")
        print(f"   回复: {result.final_output}")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


async def main():
    args = sys.argv[1:]

    if "--all" in args:
        providers = list_providers()
        if not providers:
            print(f"❌ 未找到 provider，请检查 {KEYS_DIR}")
            sys.exit(1)
        print(f"📋 测试所有 provider: {', '.join(providers)}\n")
        results = {}
        for p in providers:
            if p not in PROVIDERS:
                print(f"⚠️  跳过 {p}（未配置端点）")
                continue
            print(f"\n{'=' * 40}")
            results[p] = await test_provider(p)
        print(f"\n{'=' * 40}")
        print("📊 汇总:")
        for p, ok in results.items():
            print(f"   {p}: {'✅ 通过' if ok else '❌ 失败'}")
        sys.exit(1 if any(not v for v in results.values()) else 0)
    else:
        provider = args[0] if args else "glm"
        ok = await test_provider(provider)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
