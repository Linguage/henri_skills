#!/bin/bash
# switch-api wrapper：切换 provider 并 source 环境变量到当前 shell
# 用法: source scripts/switch_api.sh <glm|minimax|claude>
#
# 在非交互场景（如 Amp Bash 调用）中，直接 source key 文件设置环境变量
# 同时设置 OPENAI_BASE_URL 供 OpenAI Agents SDK 使用

KEYS_DIR="$HOME/.configanthropic/keys"
PROVIDER="${1:-glm}"

# OpenAI 兼容端点映射（Anthropic 端点从 key 文件读取）
_get_openai_base_url() {
    case "$1" in
        glm)     echo "https://open.bigmodel.cn/api/paas/v4" ;;
        minimax) echo "https://api.minimax.io/v1" ;;
        *)       echo "" ;;
    esac
}

case "$PROVIDER" in
    claude|off)
        unset ANTHROPIC_API_KEY ANTHROPIC_BASE_URL ANTHROPIC_MODEL OPENAI_BASE_URL
        echo "→ 已切换到官方 Claude（清除 provider 变量）"
        ;;
    --list)
        echo "📋 可用 provider:"
        for f in "$KEYS_DIR"/*; do
            [ -f "$f" ] || continue
            name=$(basename "$f")
            model=$(grep ANTHROPIC_MODEL "$f" | head -1 | sed 's/.*=//;s/"//g;s/'"'"'//g')
            openai_url=$(_get_openai_base_url "$name")
            echo "   $name → $model"
            echo "         anthropic: $(grep ANTHROPIC_BASE_URL "$f" | head -1 | sed 's/.*=//;s/"//g;s/'"'"'//g')"
            [ -n "$openai_url" ] && echo "         openai:    $openai_url"
        done
        ;;
    *)
        KEY_FILE="$KEYS_DIR/$PROVIDER"
        if [ ! -f "$KEY_FILE" ]; then
            echo "❌ 配置文件不存在: $KEY_FILE"
            echo "   可用 provider:"
            ls "$KEYS_DIR" 2>/dev/null | sed 's/^/     /'
            return 1 2>/dev/null || exit 1
        fi
        source "$KEY_FILE"
        OPENAI_URL=$(_get_openai_base_url "$PROVIDER")
        if [ -n "$OPENAI_URL" ]; then
            export OPENAI_BASE_URL="$OPENAI_URL"
        else
            unset OPENAI_BASE_URL
        fi
        echo "→ 已切换到 $PROVIDER (模型: ${ANTHROPIC_MODEL:-unknown})"
        echo "  anthropic: ${ANTHROPIC_BASE_URL:-N/A}"
        echo "  openai:    ${OPENAI_BASE_URL:-N/A}"
        ;;
esac
