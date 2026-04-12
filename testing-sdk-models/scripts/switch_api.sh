#!/bin/bash
# switch-api wrapper：切换 provider 并 source 环境变量到当前 shell
# 用法: source scripts/switch_api.sh <glm|minimax|claude>
#
# 在非交互场景（如 Amp Bash 调用）中，直接 source key 文件设置环境变量

KEYS_DIR="$HOME/.configanthropic/keys"
PROVIDER="${1:-glm}"

case "$PROVIDER" in
    claude|off)
        unset ANTHROPIC_API_KEY ANTHROPIC_BASE_URL ANTHROPIC_MODEL
        echo "→ 已切换到官方 Claude（清除 provider 变量）"
        ;;
    --list)
        echo "📋 可用 provider:"
        for f in "$KEYS_DIR"/*; do
            [ -f "$f" ] || continue
            name=$(basename "$f")
            model=$(grep ANTHROPIC_MODEL "$f" | head -1 | sed 's/.*=//;s/"//g;s/'"'"'//g')
            echo "   $name → $model"
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
        echo "→ 已切换到 $PROVIDER (模型: ${ANTHROPIC_MODEL:-unknown})"
        ;;
esac
