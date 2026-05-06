#!/usr/bin/env python3
"""
批量生成广告图片脚本
生成15张16:9横图广告图片
"""

import os
import sys
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_generator import AdImageGenerator


def main():
    """批量生成15张广告图片"""

    # 15个不同的广告主题和文案
    ad_configs = [
        {
            "theme": "智能理财",
            "copywriting": "智能资产配置，财富稳健增长",
            "style": "modern fintech"
        },
        {
            "theme": "数字银行",
            "copywriting": "全线上银行服务，随时随地办理",
            "style": "modern fintech"
        },
        {
            "theme": "区块链金融",
            "copywriting": "安全透明的区块链金融服务",
            "style": "tech"
        },
        {
            "theme": "智能风控",
            "copywriting": "AI智能风控，保障资金安全",
            "style": "modern fintech"
        },
        {
            "theme": "量化交易",
            "copywriting": "算法交易，精准把握市场机会",
            "style": "tech"
        },
        {
            "theme": "移动支付",
            "copywriting": "扫码支付，便捷生活",
            "style": "modern"
        },
        {
            "theme": "金融云服务",
            "copywriting": "企业级金融云解决方案",
            "style": "modern fintech"
        },
        {
            "theme": "智能信贷",
            "copywriting": "快速审批，智能信贷评估",
            "style": "modern fintech"
        },
        {
            "theme": "数字货币",
            "copywriting": "安全便捷的数字货币交易",
            "style": "tech"
        },
        {
            "theme": "保险科技",
            "copywriting": "智能保险，个性化保障方案",
            "style": "modern fintech"
        },
        {
            "theme": "跨境支付",
            "copywriting": "全球支付，无国界金融",
            "style": "modern"
        },
        {
            "theme": "金融数据分析",
            "copywriting": "大数据分析，洞察金融趋势",
            "style": "tech"
        },
        {
            "theme": "智能投顾",
            "copywriting": "个性化投资建议，专业资产配置",
            "style": "modern fintech"
        },
        {
            "theme": "供应链金融",
            "copywriting": "优化供应链，提升资金效率",
            "style": "modern"
        },
        {
            "theme": "绿色金融",
            "copywriting": "可持续发展，绿色金融创新",
            "style": "modern"
        }
    ]

    print("🚀 开始批量生成15张广告图片...")
    print(f"📁 输出目录: {Path.cwd() / 'generated_ads'}")
    print(f"📏 尺寸要求: 16:9横图格式")
    print(f"🎨 生成工具: Google Imagen API")
    print("=" * 60)

    # 初始化生成器
    generator = AdImageGenerator()

    success_count = 0
    failed_count = 0
    failed_items = []

    # 批量生成
    for i, config in enumerate(ad_configs, 1):
        print(f"\n📸 正在生成第 {i}/15 张图片...")
        print(f"  主题: {config['theme']}")
        print(f"  文案: {config['copywriting']}")
        print(f"  风格: {config['style']}")

        try:
            # 构建参数
            params = {
                "theme": config["theme"],
                "copywriting": config["copywriting"],
                "style": config["style"],
                "template": "standard",
                "tool": "google_imagen",
                "colors": ["#4A90E2", "#50E3C2", "#F5A623"]  # 默认配色
            }

            # 生成图片
            start_time = time.time()
            image_path = generator.generate_from_params(params)
            elapsed_time = time.time() - start_time

            print(f"  ✅ 生成成功!")
            print(f"    文件: {os.path.basename(image_path)}")
            print(f"    耗时: {elapsed_time:.1f}秒")

            success_count += 1

            # 添加延迟，避免API速率限制
            if i < len(ad_configs):
                wait_time = 5  # 5秒间隔
                print(f"    ⏳ 等待{wait_time}秒后继续...")
                time.sleep(wait_time)

        except Exception as e:
            print(f"  ❌ 生成失败: {e}")
            failed_count += 1
            failed_items.append({
                "index": i,
                "theme": config["theme"],
                "error": str(e)
            })

            # 失败后等待更长时间
            wait_time = 10
            print(f"    ⏳ 失败后等待{wait_time}秒...")
            time.sleep(wait_time)

    # 生成报告
    print("\n" + "=" * 60)
    print("📊 批量生成完成!")
    print(f"✅ 成功: {success_count} 张")
    print(f"❌ 失败: {failed_count} 张")

    if success_count > 0:
        print(f"\n📁 生成的图片保存在: {Path.cwd() / 'generated_ads'}")

        # 列出成功生成的图片
        print("\n📋 成功生成的图片列表:")
        ads_dir = Path.cwd() / "generated_ads"
        if ads_dir.exists():
            # 按修改时间排序，获取最新的15个文件
            png_files = list(ads_dir.glob("ad_*.png"))
            png_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for i, file_path in enumerate(png_files[:success_count], 1):
                file_size = file_path.stat().st_size
                size_mb = file_size / 1024 / 1024
                print(f"  {i:2d}. {file_path.name} ({size_mb:.1f} MB)")

    if failed_count > 0:
        print(f"\n⚠️ 失败的生成项目:")
        for item in failed_items:
            print(f"  第{item['index']}张: {item['theme']} - {item['error'][:100]}...")

    print("\n🎉 批量生成任务完成!")


if __name__ == "__main__":
    main()