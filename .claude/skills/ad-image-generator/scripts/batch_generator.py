#!/usr/bin/env python3
"""
批量广告图片生成脚本
根据专业参数批量生成15张规范的广告图片，支持使用示例图片作为参考
"""

import os
import sys
import json
import random
from pathlib import Path
from image_generator import AdImageGenerator


def get_example_images():
    """获取示例图片列表"""
    example_dir = Path(__file__).parent.parent / "assets" / "example"
    example_images = []

    if example_dir.exists():
        for file in example_dir.glob("*.jpg"):
            example_images.append(str(file))
        for file in example_dir.glob("*.png"):
            example_images.append(str(file))
        for file in example_dir.glob("*.jpeg"):
            example_images.append(str(file))

    return example_images


def build_detailed_prompt(theme, copywriting, risk_warning, mascot_desc, logo_file, style, colors, mascot_file=None):
    """构建详细的prompt，符合SKILL.md强制设计要求"""

    color_desc = ", ".join(colors[:3]) if colors else "blue, white, accent colors"

    # 根据SKILL.md构建详细的prompt
    prompt_parts = [
        # 基础描述
        f"Professional fintech advertisement image for AI Zangle (AI涨乐), {theme} theme",
        f"Horizontal format, widescreen advertising layout, 16:9 aspect ratio",

        # 强制品牌元素 - SKILL.md要求
        f"Brand logo '{logo_file}' at top-left corner, clearly visible and prominent",
        f"Compliance risk disclaimer text at bottom: '{risk_warning}' in small clear font (8-10pt), readable and legally compliant",

        # 吉祥物整合 - SKILL.md要求
        f"Mascot character: {mascot_desc}, naturally integrated into the scene, matching {theme} theme",
        f"Mascot should interact with the environment, not just pasted on top",

        # 科技感背景构建 - SKILL.md要求
        f"Modern fintech background with depth and dimension, NO solid color backgrounds",
        f"Interactive tech elements: flowing data streams, glowing network nodes, holographic digital interfaces, circuit board patterns",
        f"Futuristic tech environment with particles, light trails, and digital effects",

        # 广告文案 - SKILL.md要求
        f"Prominent main text: '{copywriting}', large and eye-catching, excellent contrast with background",
        f"Text should be integral part of design, not just overlay",
        f"Supporting text elements that enhance the message, professionally typeset",

        # 风格和配色
        f"Style: {style}, with {color_desc} color scheme",
        f"Dark tech aesthetic with neon glow effects, cyberpunk-inspired but professional",
        f"High contrast between dark backgrounds and bright accent colors",

        # 视觉层次 - SKILL.md要求
        f"Clear visual hierarchy: 1) logo top-left, 2) main text center, 3) mascot integrated, 4) risk disclaimer bottom",
        f"Professional composition with balanced negative space, not overcrowded",
        f"All elements should work together harmoniously",

        # 质量要求
        f"High quality professional advertisement image, clean modern layout",
        f"Photorealistic rendering where appropriate, detailed textures",
        f"No watermarks, no generic stock photo look",
        f"Consistent lighting and shadows throughout the scene"
    ]

    # 添加特定主题的额外描述
    if "投资" in theme or "理财" in theme:
        prompt_parts.append("Include subtle financial charts, graphs, or market data visualization in background")
    elif "安全" in theme or "防护" in theme:
        prompt_parts.append("Include security shield elements, lock icons, or protective barriers in design")
    elif "智能" in theme or "AI" in theme:
        prompt_parts.append("Include AI neural network visualization, brain patterns, or intelligent system elements")
    elif "数据" in theme or "分析" in theme:
        prompt_parts.append("Include data visualization elements, charts, graphs, or analytics dashboards")
    elif "支付" in theme or "银行" in theme:
        prompt_parts.append("Include payment card elements, currency symbols, or banking interface elements")

    return ", ".join(prompt_parts)


def generate_batch_ads(num_images=15):
    """批量生成广告图片"""
    print(f"开始批量生成 {num_images} 张广告图片...")
    print(f"使用修改后的技能，支持示例图片参考")

    # 获取示例图片
    example_images = get_example_images()
    print(f"找到 {len(example_images)} 张示例图片作为参考")

    if example_images:
        print("示例图片列表:")
        for i, img in enumerate(example_images[:5], 1):
            print(f"  {i}. {Path(img).name}")
        if len(example_images) > 5:
            print(f"  ... 还有 {len(example_images)-5} 张")

    # 获取吉祥物文件列表
    mascot_dir = Path(__file__).parent.parent / "assets" / "elements" / "吉祥物姿势包"
    mascot_files = []
    if mascot_dir.exists():
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            mascot_files.extend([f.name for f in mascot_dir.glob(ext)])
    print(f"找到 {len(mascot_files)} 个吉祥物姿势文件")

    # 吉祥物姿势描述映射（根据文件名提供描述）
    mascot_descriptions = {
        "1.png": "专业自信站姿的吉祥物",
        "2.png": "手持文档的吉祥物",
        "3.png": "思考姿势的吉祥物",
        "4.png": "展示手势的吉祥物",
        "5-1.png": "开心跳跃的吉祥物",
        "8.png": "比心手势的吉祥物",
        "9.png": "欢呼庆祝的吉祥物",
        "12.png": "客服姿势的吉祥物",
        "14.png": "打鼓表演的吉祥物",
        "16.png": "手持铃铛的吉祥物",
        "1234 1.png": "数字手势的吉祥物",
        "1236.png": "胜利手势的吉祥物",
        "Component 44.png": "专业工作姿势的吉祥物",
        "Frame 2134595626.png": "框架展示的吉祥物",
        "Group 2134595756.png": "团队合作的吉祥物",
        "Mask group.png": "神秘面具的吉祥物",
        "开心.png": "开心表情的吉祥物",
        "开心跳跃1 1.png": "开心跳跃姿势1",
        "开心跳跃1 2.png": "开心跳跃姿势2",
        "大拇指.png": "点赞手势的吉祥物",
        "比心.png": "比心手势的吉祥物",
        "欢呼.png": "欢呼庆祝的吉祥物",
        "萌宠打鼓 1.png": "打鼓表演的萌宠",
        "萌宠-客服 1.png": "客服姿势的萌宠",
        "手-0度调整 1.png": "伸手姿势的吉祥物",
        "手-45度调整 1.png": "45度伸手的吉祥物",
        "图层 1.png": "图层1姿势的吉祥物",
        "图层 2.png": "图层2姿势的吉祥物",
        "图层 3.png": "图层3姿势的吉祥物",
        "图层 4.png": "图层4姿势的吉祥物",
        "铃铛-修改 1.png": "手持铃铛的吉祥物",
        "组 7 3.png": "组合姿势的吉祥物",
        "无持仓_自选.png": "无持仓姿势的吉祥物",
        "ip 1.png": "IP展示的吉祥物",
        "image 26104.png": "形象展示1的吉祥物",
        "image 26105.png": "形象展示2的吉祥物",
        "image 26115.png": "形象展示3的吉祥物"
    }

    # 广告主题和文案示例 - AI涨乐金融科技主题
    ad_themes = [
        "AI智能投资助手",
        "金融科技理财平台",
        "数字银行服务",
        "智能投顾系统",
        "区块链金融应用",
        "移动支付解决方案",
        "金融数据分析平台",
        "智能风控系统",
        "数字货币钱包",
        "跨境支付服务",
        "智能信贷评估",
        "金融云服务平台",
        "智能保险顾问",
        "量化交易系统",
        "金融安全防护"
    ]

    ad_copywritings = [
        "AI涨乐，您的投资好帮手",
        "投资就找AI涨乐",
        "AI涨乐，智能投资新选择",
        "让AI涨乐为您财富增值",
        "AI涨乐，投资更简单",
        "智慧投资，从AI涨乐开始",
        "AI涨乐，您的私人投资顾问",
        "投资未来，选择AI涨乐",
        "AI涨乐，让投资更智能",
        "专业投资，AI涨乐相伴",
        "AI涨乐，投资路上的好伙伴",
        "智能投顾，就选AI涨乐",
        "AI涨乐，助您财富增长",
        "投资理财，AI涨乐更懂您",
        "AI涨乐，开启智能投资时代"
    ]

    # 风险提示文本
    risk_warnings = [
        "市场有风险，投资需谨慎。投资前请仔细阅读相关协议和风险提示。",
        "理财有风险，投资需谨慎。过往业绩不代表未来表现。",
        "投资有风险，入市需谨慎。请根据自身风险承受能力选择合适产品。",
        "金融产品存在风险，可能损失本金。请理性投资，谨慎决策。",
        "投资理财存在市场风险，请充分了解产品特性后再做决策。",
        "数字资产价格波动较大，投资前请评估自身风险承受能力。",
        "智能投顾仅供参考，不构成投资建议。投资决策需独立判断。",
        "金融科技服务需谨慎使用，注意个人信息和资金安全。",
        "跨境支付涉及汇率风险，请关注相关费用和汇率波动。",
        "云计算服务存在数据安全风险，请选择可靠服务商。",
        "保险产品条款复杂，购买前请仔细阅读保险合同。",
        "量化交易策略存在失效风险，历史回测不代表未来收益。",
        "金融安全防护需持续更新，注意防范网络诈骗和黑客攻击。",
        "数字货币投资风险较高，可能面临监管政策变化风险。",
        "信贷产品需按时还款，逾期可能影响个人信用记录。"
    ]

    styles = ["modern fintech", "tech", "minimal fintech", "elegant fintech", "creative fintech"]
    color_schemes = [
        ["#0A192F", "#00D4FF", "#FFFFFF"],  # 深蓝科技风
        ["#1A1A2E", "#00FFAB", "#FFFFFF"],  # 深紫绿科技
        ["#121212", "#FFD700", "#FFFFFF"],  # 黑金科技
        ["#000814", "#4CC9F0", "#FFFFFF"],  # 深空蓝科技
        ["#1A1A2E", "#9D4EDD", "#FFFFFF"],  # 深紫渐变
        ["#0D1B2A", "#00BBF9", "#FFFFFF"],  # 深蓝粒子
        ["#14213D", "#FCA311", "#FFFFFF"],  # 深蓝橙都市
        ["#001219", "#94D2BD", "#FFFFFF"],  # 深绿二进制
        ["#1B263B", "#9A4C95", "#FFFFFF"],  # 深紫波纹
        ["#212529", "#52B788", "#FFFFFF"]   # 深绿网格
    ]

    # 初始化生成器 - 使用项目根目录的配置文件
    config_path = Path("/Users/qiangjohn/terry-photos/google_ai_config.json")
    print(f"使用配置文件: {config_path}")
    generator = AdImageGenerator(str(config_path))

    # 生成15张图片
    generated_images = []

    for i in range(1, num_images + 1):
        print(f"\n{'='*60}")
        print(f"生成第 {i}/{num_images} 张广告图片...")

        # 选择参数（按顺序使用，确保每个主题都有）
        theme_idx = (i - 1) % len(ad_themes)
        theme = ad_themes[theme_idx]
        copywriting = ad_copywritings[theme_idx]
        risk_warning = risk_warnings[theme_idx]
        style = styles[theme_idx % len(styles)]
        colors = color_schemes[theme_idx % len(color_schemes)]

        # 选择吉祥物（按顺序使用）
        if mascot_files:
            mascot_idx = (i - 1) % len(mascot_files)
            mascot_file = mascot_files[mascot_idx]
            mascot_desc = mascot_descriptions.get(mascot_file, f"吉祥物姿势{mascot_idx+1}")
        else:
            mascot_file = None
            mascot_desc = "金融科技吉祥物"

        # 选择Logo（奇数用logo1，偶数用logo2）
        logo_file = "logo1.png" if i % 2 == 1 else "logo2.png"

        # 构建详细的prompt参数
        detailed_prompt = build_detailed_prompt(
            theme=theme,
            copywriting=copywriting,
            risk_warning=risk_warning,
            mascot_desc=mascot_desc,
            logo_file=logo_file,
            style=style,
            colors=colors,
            mascot_file=mascot_file
        )

        # 构建参数 - 使用Google Imagen生成高质量图片
        params = {
            "theme": theme,
            "copywriting": copywriting,
            "style": style,
            "colors": colors,
            "template": "standard",
            "tool": "google_imagen",  # 使用Google Imagen生成
            "detailed_prompt": detailed_prompt,  # 添加详细prompt
            "risk_warning": risk_warning,
            "mascot_file": mascot_file,
            "logo_file": logo_file
        }

        # 如果有示例图片，随机选择1-3张作为参考
        if example_images:
            num_refs = random.randint(1, min(3, len(example_images)))
            ref_images = random.sample(example_images, num_refs)
            params["reference_images"] = ref_images
            print(f"参考图片: {', '.join([Path(img).name for img in ref_images])}")

        print(f"主题: {theme}")
        print(f"文案: {copywriting}")
        print(f"风险提示: {risk_warning[:30]}...")
        print(f"吉祥物: {mascot_desc}")
        print(f"Logo: {logo_file}")
        print(f"风格: {style}")
        print(f"配色: {colors}")
        print(f"详细prompt长度: {len(detailed_prompt)}字符")

        try:
            # 生成图片
            image_path = generator.generate_from_params(params)
            generated_images.append(image_path)
            print(f"✅ 第 {i} 张图片生成成功: {Path(image_path).name}")

        except Exception as e:
            print(f"❌ 第 {i} 张图片生成失败: {e}")
            # 尝试使用模拟模式
            try:
                print("尝试使用模拟模式...")
                params["tool"] = "mock"
                image_path = generator.generate_from_params(params)
                generated_images.append(image_path)
                print(f"✅ 第 {i} 张图片（模拟模式）生成成功: {Path(image_path).name}")
            except Exception as e2:
                print(f"❌ 模拟模式也失败: {e2}")

    print(f"\n{'='*60}")
    print(f"批量生成完成!")
    print(f"成功生成 {len(generated_images)}/{num_images} 张广告图片")

    if generated_images:
        print("\n生成的图片列表:")
        for i, img_path in enumerate(generated_images, 1):
            print(f"  {i}. {Path(img_path).name}")

    # 生成汇总报告
    report_path = generator.output_dir / "batch_generation_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"批量广告图片生成报告\n")
        f.write(f"{'='*40}\n")
        f.write(f"生成时间: {generated_images[0] if generated_images else 'N/A'}\n")
        f.write(f"总数量: {num_images}\n")
        f.write(f"成功数量: {len(generated_images)}\n")
        f.write(f"失败数量: {num_images - len(generated_images)}\n")
        f.write(f"\n生成的图片:\n")
        for img_path in generated_images:
            f.write(f"  - {Path(img_path).name}\n")
        f.write(f"\n示例图片参考: {len(example_images)} 张\n")
        if example_images:
            f.write("示例图片列表:\n")
            for img in example_images[:10]:
                f.write(f"  - {Path(img).name}\n")
            if len(example_images) > 10:
                f.write(f"  ... 还有 {len(example_images)-10} 张\n")

    print(f"\n📋 生成报告已保存: {report_path}")
    print(f"📁 所有图片保存在: {generator.output_dir}")

    return generated_images


def main():
    """命令行入口点"""
    import argparse

    parser = argparse.ArgumentParser(description="批量广告图片生成器")
    parser.add_argument("--num", type=int, default=15, help="生成图片数量（默认15）")
    parser.add_argument("--config", help="配置文件路径")

    args = parser.parse_args()

    try:
        generate_batch_ads(args.num)
    except KeyboardInterrupt:
        print("\n❌ 用户中断生成过程")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 批量生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()