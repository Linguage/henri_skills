# 第四阶段：图片来源分类

使用 `classify_images.py` 对 `图片/` 中的散落图片进行来源分类。

## 三层分类系统

| 层级 | 方法 | 覆盖率 | 说明 |
|------|------|--------|------|
| Layer 1 | 文件名模式匹配 | ~80% | 识别 ChatGPT/Gemini/微信/Telegram/Twitter/知乎/截图/手机拍摄 等 |
| Layer 2 | EXIF 元数据 | ~10% | 有相机参数 → 手机拍摄，有设备型号匹配 → 自己的设备 |
| Layer 3 | 视觉特征 | ~5% | 亮度/对比度/边缘密度/纯色区域比例 → 截图/文档/照片/插画 |
| 兜底 | 其他图片 | ~5% | 无法匹配的归入 `其他图片/` |

## 分类类别

| 类别 | 来源判断依据 | 典型文件名模式 |
|------|-------------|---------------|
| AI生成图片/ChatGPT | 文件名 `ChatGPT Image *` | ChatGPT Image YYYY年M月D日... |
| AI生成图片/Gemini | 文件名 `Gemini_Generated_Image_*` | Gemini_Generated_Image_*.png |
| 社交平台图片/微信 | 文件名 `微信图片_*` `wechat_*` `mmexport*` | 微信图片_YYYY-MM-DD... |
| 社交平台图片/Telegram | 文件名 `photo_*_y/w.jpg` | photo_*.jpg |
| 社交平台图片/Twitter | 文件名 `G*/HBTg*/twitter-*` | G*.jpeg |
| 社交平台图片/知乎 | 文件名 `v2-*` | v2-*.webp |
| 手机拍摄 | EXIF 含相机参数或文件名 `IMG_*/DSC_*` | IMG_*.jpg |
| 截图 | 文件名 `ScreenShot_*`/`clipboard_*` 或视觉特征 | ScreenShot_*.png |
| 网络下载图片 | 文件名 `maxresdefault*/BingWallpaper*` 或视觉兜底 | maxresdefault.jpg |
| 学术与工程图片 | 文件名含学术关键词 | *.png |
| 其他图片 | 无匹配模式 | 任意 |

## 图片分类工作流

1. **扫描图片目录**：运行脚本扫描 `图片/` 根目录和 `图片/其他图片/` 根目录的散落图片
2. **生成分类报告**：展示每张图片的分类结果、置信度和判断依据
3. **用户确认**：展示分类汇总，用户确认或调整后执行移动
4. **执行分类移动**：加 `--move` 参数执行文件移动

```bash
# 步骤 1-3：生成分类报告
conda run -n henri_env python .claude/skills/organize-downloads/classify_images.py

# 也可导出 JSON 结果
conda run -n henri_env python .claude/skills/organize-downloads/classify_images.py --json 图片/classification_report.json

# 步骤 4：确认后执行移动
conda run -n henri_env python .claude/skills/organize-downloads/classify_images.py --move

# 仅扫描根目录（不扫描其他图片/）
conda run -n henri_env python .claude/skills/organize-downloads/classify_images.py --scan-root

# 自定义设备白名单（EXIF 匹配用）
conda run -n henri_env python .claude/skills/organize-downloads/classify_images.py --own-devices iPhone iPad "Xiaomi 14"
```

## 添加新规则

当发现新的文件名模式时，编辑 `classification_rules.json`（外部规则配置）：
```json
{
  "filename_patterns": [
    {"regex": "^新模式", "category": "类别", "subcategory": "子类别", "confidence": 0.85}
  ]
}
```
