#!/usr/bin/env python3
"""
继续生成剩余的广告图片
"""

import os
import sys
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_generator import AdImageGenerator


def main():
    """继续生成剩余的广告图片"""

    # 剩余的广告主题和文案（跳过已生成的）
    remaining_configs = [
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

    print("🚀 继续生成剩余的8张广告图片...")
    print(f"📁 输出目录: {Path.cwd() / 'generated_ads'}")
    print("=" * 60)

    # 初始化生成器
    generator = AdImageGenerator()

    success_count = 0
    failed_count = 0

    # 检查已存在的文件
    ads_dir = Path.cwd() / "generated_ads"
    existing_files = set()
    if ads_dir.exists():
        for file in ads_dir.glob("ad_*.png"):
            existing_files.add(file.name.lower())

    # 生成剩余的图片
    for i, config in enumerate(remaining_configs, 1):
        # 检查是否已存在
        expected_filename = f"ad_{config['theme']}_{config['style']}.png".lower()
        if expected_filename in existing_files:
            print(f"\n⏭️  跳过第 {i} 张图片（已存在）:")
            print(f"  主题: {config['theme']}")
            print(f"  文件: {expected_filename}")
            continue

        print(f"\n📸 正在生成第 {i}/8 张图片...")
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
                "colors": ["#4A90E2", "#50E3C2", "#F5A623"]
            }

            # 生成图片
            start_time = time.time()
            image_path = generator.generate_from_params(params)
            elapsed_time = time.time() - start_time

            print(f"  ✅ 生成成功!")
            print(f"    文件: {os.path.basename(image_path)}")
            print(f"    耗时: {elapsed_time:.1f}秒")

            success_count += 1

            # 添加延迟
            if i < len(remaining_configs):
                wait_time = 5
                print(f"    ⏳ 等待{wait_time}秒后继续...")
                time.sleep(wait_time)

        except Exception as e:
            print(f"  ❌ 生成失败: {e}")
            failed_count += 1

            # 失败后等待更长时间
            wait_time = 10
            print(f"    ⏳ 失败后等待{wait_time}秒...")
            time.sleep(wait_time)

    # 生成报告
    print("\n" + "=" * 60)
    print("📊 继续生成完成!")
    print(f"✅ 本次成功: {success_count} 张")
    print(f"❌ 本次失败: {failed_count} 张")

    # 统计总数
    total_files = 0
    if ads_dir.exists():
        png_files = list(ads_dir.glob("ad_*.png"))
        total_files = len(png_files)

    print(f"\n📁 当前总共生成: {total_files} 张广告图片")

    if total_files > 0:
        print("\n📋 所有生成的图片列表:")
        png_files = list(ads_dir.glob("ad_*.png"))
        png_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for i, file_path in enumerate(png_files[:total_files], 1):
            file_size = file_path.stat().st_size
            size_mb = file_size / 1024 / 1024
            print(f"  {i:2d}. {file_path.name} ({size_mb:.1f} MB)")

    print("\n🎉 生成任务完成!")


if __name__ == "__main__":
    main()