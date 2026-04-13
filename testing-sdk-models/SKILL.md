---
name: testing-sdk-models
description: "Test Claude Agent SDK and OpenAI Agents SDK connectivity with third-party model providers (GLM, MiniMax, etc.). Use when asked to test SDK, test model, check API connection, or verify provider setup."
author: Henri
created: "2026-03-15"
---

# Testing SDK Models

测试两套 SDK 与第三方 model provider 的连通性。

- **test_anthropic_sdk.py** — 通过 Claude Agent SDK（Anthropic 兼容端点）测试
- **test_openai_sdk.py** — 通过 OpenAI Agents SDK（OpenAI 兼容端点）测试

## Prerequisites

- conda environment `henri_env` with `claude_agent_sdk` and `openai-agents` installed
- Provider key files in `~/.configanthropic/keys/` (e.g., `glm`, `minimax`)
- Each key file contains `export ANTHROPIC_API_KEY=...`, `ANTHROPIC_BASE_URL=...`, `ANTHROPIC_MODEL=...`

## Usage

### Anthropic SDK 测试

```bash
# Test default provider (glm)
source ~/miniconda3/etc/profile.d/conda.sh && conda activate henri_env && python scripts/test_anthropic_sdk.py

# Test specific provider
python scripts/test_anthropic_sdk.py minimax

# Test all available providers
python scripts/test_anthropic_sdk.py --all

# Use original Claude (no provider override)
python scripts/test_anthropic_sdk.py claude
```

### OpenAI SDK 测试

```bash
# Test default provider (glm)
source ~/miniconda3/etc/profile.d/conda.sh && conda activate henri_env && python scripts/test_openai_sdk.py

# Test specific provider
python scripts/test_openai_sdk.py minimax

# Test all available providers
python scripts/test_openai_sdk.py --all
```

### switch-api 集成

通过 `--switch` 调用终端的 `switch_api.sh`，自动 source 配置并测试：

```bash
# 切换到 glm 并测试
python scripts/test_anthropic_sdk.py --switch glm

# 切换到 minimax 并测试
python scripts/test_anthropic_sdk.py --switch minimax

# 切回官方 Claude 并测试
python scripts/test_anthropic_sdk.py --switch claude

# 列出所有可用 provider
python scripts/test_anthropic_sdk.py --switch --list
```

也可以在 Amp 中直接 source `switch_api.sh` 来切换（不测试）：

```bash
source scripts/switch_api.sh glm
source scripts/switch_api.sh --list
```

## Workflow

1. When the user asks to test SDK or model providers, choose the appropriate script:
   - "test anthropic SDK" / "test claude SDK" → `test_anthropic_sdk.py`
   - "test openai SDK" → `test_openai_sdk.py`
   - "test SDK" (unspecified) → run both
2. If a specific provider is mentioned (e.g., "test glm"), pass it as argument
3. If the user says "test all", use `--all` flag
4. If the user says "switch to X" or "切换到 X", use `--switch <provider>`
5. Report the results: model name, response content, success/failure
6. If a provider fails, check whether `~/.configanthropic/keys/<provider>` exists and has valid format

## Available Providers

List providers by checking `~/.configanthropic/keys/`:

```bash
ls ~/.configanthropic/keys/
```

## Troubleshooting

- **"nested session" error**: The script auto-clears `CLAUDECODE` env var; if running manually, `unset CLAUDECODE` first
- **Rate limit hit**: Response will contain "hit your limit"; wait for reset
- **Key file not found**: Create it with the three required `export` lines
