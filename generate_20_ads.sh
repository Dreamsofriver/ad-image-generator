#!/bin/bash
cd /Users/qiangjohn/terry-photos-v2.0.2

MASCOT_DIR="./.claude/skills/ad-image-generator/assets/elements/吉祥物姿势包"
DARK_REF="./.claude/skills/ad-image-generator/assets/example/深色"
LIGHT_REF="./.claude/skills/ad-image-generator/assets/example/浅色"

DARK_PROMPT="请参考第一张图片（深色参考图）的广告设计风格和布局，生成一张金融类广告图片。必须严格限制图片尺寸为1344*768。电脑屏幕、桌面等元素要替换为其他更有创意、更多样化的元素，采用部分金融科技元素，外加一些小的金融元素（如小钻石、小宝箱等），还可选择性地添加一些背景风景元素，除了logo、标题大字、吉祥物、风险提示外，其他元素都要多加替换。吉祥物的形象必须完全符合第二张图片（吉祥物姿势包中的图片）中的吉祥物形象。广告图片中必须包含和深色参考图完全相同的中间标题大字，这个标题必须准确无误，一个字都不能错。左上角的logo必须和深色参考图的logo保持一致。右下角的'投资有风险，入市需谨慎'必须直接从深色参考图照搬，不要有任何变化。整体风格要专业、现代、吸引人，适合金融投资类广告。"

LIGHT_PROMPT="请参考第一张图片（浅色参考图）的广告设计风格和布局，生成一张金融类广告图片。必须严格限制图片尺寸为1344*768。电脑屏幕、桌面等元素要替换为其他更有创意、更多样化的元素，采用部分金融科技元素，外加一些小的金融元素（如小钻石、小宝箱等），还可选择性地添加一些背景风景元素，除了logo、标题大字、吉祥物、风险提示外，其他元素都要多加替换。吉祥物的形象必须完全符合第二张图片（吉祥物姿势包中的图片）中的吉祥物形象。广告图片中必须包含和浅色参考图完全相同的中间标题大字，这个标题必须准确无误，一个字都不能错。左上角的logo必须使用浅色背景专用logo（logo2.png）。右下角的'投资有风险，入市需谨慎'必须直接从浅色参考图照搬，不要有任何变化。整体风格要专业、现代、吸引人，适合金融投资类广告，保持浅色背景的清新感。"

echo "==== 开始生成 10 张深色广告图片 ===="
for i in {1..10}; do
    MASCOT=$(ls "$MASCOT_DIR"/*.png | gshuf -n 1 2>/dev/null || ls "$MASCOT_DIR"/*.png | sort -R | head -n 1)
    if [ -z "$MASCOT" ]; then
        MASCOT=$(ls "$MASCOT_DIR"/*.png | awk 'BEGIN{srand()} {print rand()"\t"$0}' | sort -n | cut -f2- | head -n 1)
    fi
    echo "[深色 $i/10] 使用吉祥物: $(basename "$MASCOT")"
    python3 generate_ad_from_reference.py \
      --reference "$DARK_REF" \
      --additional "$MASCOT" \
      --prompt "$DARK_PROMPT"
done

echo "==== 开始生成 10 张浅色广告图片 ===="
for i in {1..10}; do
    MASCOT=$(ls "$MASCOT_DIR"/*.png | gshuf -n 1 2>/dev/null || ls "$MASCOT_DIR"/*.png | sort -R | head -n 1)
    if [ -z "$MASCOT" ]; then
        MASCOT=$(ls "$MASCOT_DIR"/*.png | awk 'BEGIN{srand()} {print rand()"\t"$0}' | sort -n | cut -f2- | head -n 1)
    fi
    echo "[浅色 $i/10] 使用吉祥物: $(basename "$MASCOT")"
    python3 generate_ad_from_reference.py \
      --reference "$LIGHT_REF" \
      --additional "$MASCOT" \
      --prompt "$LIGHT_PROMPT"
done

echo "==== 20 张图片生成完成 ===="
