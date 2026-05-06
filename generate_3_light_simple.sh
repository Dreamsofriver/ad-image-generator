#!/bin/bash

echo "开始生成3张浅色广告图片..."

# 浅色图片使用的吉祥物图片列表
LIGHT_MASCOTS=("开心.png" "欢呼.png" "比心.png")

# 浅色图片标准化提示词（参考图片由脚本从浅色文件夹随机选取）
LIGHT_PROMPT="请参考第一张图片（浅色参考图）的广告设计风格和布局，生成一张金融类广告图片。必须严格限制图片尺寸为768*1376。电脑屏幕、桌面等元素要替换为其他更有创意、更多样化的元素，以金融元素为主体（如股票K线图、交易数据大屏、投资组合仪表盘、理财产品展示、支付场景、金融图表、银行建筑、保险精算报表、货币符号、理财计算器等），辅以少量科技元素点缀（如数据流光线、科技感网格、数字孪生可视化、全息投影效果等），除了logo、标题大字、吉祥物、右下角风险提示外，其他元素都要多加替换。吉祥物的形象必须完全符合第二张图片（吉祥物姿势包中的图片）中的吉祥物形象。广告图片中必须包含和浅色参考图完全相同的中间标题大字，这个标题必须准确无误，一个字都不能错。左上角的logo必须使用浅色背景专用logo（logo2.png）。右下角的'投资有风险，入市需谨慎'必须直接从浅色参考图照搬，不要有任何变化。整体风格要专业、现代、吸引人，适合金融投资类广告，保持浅色背景的清新感。"

# 参考图片目录（脚本会随机选取其中一张）
REFERENCE_LIGHT="./.claude/skills/ad-image-generator/assets/example/浅色"

# 计数器
COUNT=0

for mascot in "${LIGHT_MASCOTS[@]}"; do
    COUNT=$((COUNT + 1))
    echo "正在生成第${COUNT}张浅色广告图片（使用吉祥物: ${mascot}）..."
    
    ADDITIONAL_IMG="./.claude/skills/ad-image-generator/assets/elements/吉祥物姿势包/${mascot}"
    
    python3 generate_ad_from_reference.py \
        --reference "${REFERENCE_LIGHT}" \
        --additional "${ADDITIONAL_IMG}" \
        --prompt "${LIGHT_PROMPT}" \
        --config "google_ai_config_gemini.json" &
    
    # 等待当前进程完成
    wait $!
    
    if [ $? -eq 0 ]; then
        echo "✅ 第${COUNT}张浅色广告图片生成成功！"
    else
        echo "❌ 第${COUNT}张浅色广告图片生成失败！"
    fi
    
    echo ""
    
    # 等待2秒避免API限制
    sleep 2
done

echo "浅色广告图片批量生成完成！共生成 ${COUNT} 张图片。"
