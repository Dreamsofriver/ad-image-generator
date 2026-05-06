#!/bin/bash
set -e

PYTHON=".claude/skills/ad-image-generator/scripts/venv/bin/python3"
REF_DARK="./.claude/skills/ad-image-generator/assets/example/深色"
REF_LIGHT="./.claude/skills/ad-image-generator/assets/example/浅色"
MAS_BASE="./.claude/skills/ad-image-generator/assets/elements/吉祥物姿势包"
CONFIG="google_ai_config_gemini.json"

MASCOTS=(
    "1.png"
    "2.png"
    "3.png"
    "4.png"
    "12.png"
    "14.png"
    "大拇指.png"
    "比心.png"
    "欢呼.png"
    "开心.png"
)

DARK_PROMPT="请参考第一张图片（深色参考图）的广告设计风格和布局，生成一张金融类广告图片。必须严格限制图片尺寸为768*1376。电脑屏幕、桌面等元素要替换为其他更有创意、更多样化的元素，以金融元素为主体（如股票K线图、交易数据大屏、投资组合仪表盘、理财产品展示、支付场景、金融图表、银行建筑、保险精算报表、货币符号、理财计算器等），辅以少量科技元素点缀（如数据流光线、科技感网格、数字孪生可视化、全息投影效果等），除了logo、标题大字、吉祥物、右下角风险提示外，其他元素都要多加替换。吉祥物的形象必须完全符合第二张图片（吉祥物姿势包中的图片）中的吉祥物形象。广告图片中必须包含和深色参考图完全相同的中间标题大字，这个标题必须准确无误，一个字都不能错。左上角的logo必须和深色参考图的logo保持一致。右下角的'投资有风险，入市需谨慎'必须直接从深色参考图照搬，不要有任何变化。整体风格要专业、现代、吸引人，适合金融投资类广告。"

LIGHT_PROMPT="请参考第一张图片（浅色参考图）的广告设计风格和布局，生成一张金融类广告图片。必须严格限制图片尺寸为768*1376。电脑屏幕、桌面等元素要替换为其他更有创意、更多样化的元素，以金融元素为主体（如股票K线图、交易数据大屏、投资组合仪表盘、理财产品展示、支付场景、金融图表、银行建筑、保险精算报表、货币符号、理财计算器等），辅以少量科技元素点缀（如数据流光线、科技感网格、数字孪生可视化、全息投影效果等），除了logo、标题大字、吉祥物、右下角风险提示外，其他元素都要多加替换。吉祥物的形象必须完全符合第二张图片（吉祥物姿势包中的图片）中的吉祥物形象。广告图片中必须包含和浅色参考图完全相同的中间标题大字，这个标题必须准确无误，一个字都不能错。左上角的logo必须使用浅色背景专用logo（logo2.png）。右下角的'投资有风险，入市需谨慎'必须直接从浅色参考图照搬，不要有任何变化。整体风格要专业、现代、吸引人，适合金融投资类广告，保持浅色背景的清新感。"

echo "============================================================"
echo "  批量生成标准化广告图片: 10张深色 + 10张浅色"
echo "============================================================"
echo ""

gen_one() {
    local theme="$1"
    local ref="$2"
    local mascot="$3"
    local prompt="$4"
    local idx="$5"

    echo "----------------------------------------"
    echo "  [${theme}] 第 ${idx}/10 张, 吉祥物: ${mascot}"
    echo "----------------------------------------"

    $PYTHON generate_ad_from_reference.py \
        --reference "$ref" \
        --additional "${MAS_BASE}/${mascot}" \
        --prompt "$prompt" \
        --config "$CONFIG"

    echo "  ✅ [${theme}] 第 ${idx}/10 张完成"
    echo ""
}

echo "=== 开始生成10张深色图片 ==="
for i in $(seq 0 9); do
    gen_one "深色" "$REF_DARK" "${MASCOTS[$i]}" "$DARK_PROMPT" "$((i+1))"
done

echo "=== 开始生成10张浅色图片 ==="
for i in $(seq 0 9); do
    gen_one "浅色" "$REF_LIGHT" "${MASCOTS[$i]}" "$LIGHT_PROMPT" "$((i+1))"
done

echo "============================================================"
echo "  批量生成完成!"
echo "  深色图片: 10 张"
echo "  浅色图片: 10 张"
echo "  总计: 20 张"
echo "  输出目录: generated_ads/"
echo "============================================================"
