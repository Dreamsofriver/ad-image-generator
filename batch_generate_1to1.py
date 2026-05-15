#!/usr/bin/env python3
"""批量生成：1:1 正方形 10 张"""
import random
import sys
from pathlib import Path

# 引入主生成器
sys.path.insert(0, str(Path(__file__).parent))
from generate_ad_from_reference import AdImageGenerator

# --- 主题池（10 个）---
THEMES = {
    1: "自然风光",
    2: "科技",
    3: "金融",
    4: "都市风光",
    5: "名胜古迹",
    6: "小宝物",
    7: "生活类",
    8: "线索/探索类",
    9: "旅游景区",
    10: "运动类",
}

MUST_INCLUDE = {3, 6, 8}  # 金融、小宝物、线索/探索类 至少选 1 个

BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR / ".claude" / "skills" / "ad-image-generator" / "assets"
SQUARE_DIR = ASSETS / "example" / "正方形"
MASCOT_DIR = ASSETS / "elements" / "吉祥物姿势包"


def pick_random_themes():
    """随机选择 2~3 个主题，必须包含 MUST_INCLUDE 中至少 1 个"""
    must_pick = random.choice(list(MUST_INCLUDE))
    remaining = [t for t in THEMES if t != must_pick]
    extra_count = random.choice([1, 2])  # 再选 1~2 个，总共 2~3
    extras = random.sample(remaining, extra_count)
    selected = [must_pick] + extras
    random.shuffle(selected)
    return [THEMES[t] for t in selected]


def pick_random_mascot():
    """从吉祥物姿势包随机选一张"""
    images = list(MASCOT_DIR.glob("*.png"))
    return random.choice(images)


def build_prompt(themes, mascot_name):
    """构建动态 prompt"""
    theme_str = " + ".join(themes)
    return (
        f"请参考第一张图片（正方形参考图）的广告设计风格和布局，生成一张金融类广告图片。"
        f"必须严格限制图片尺寸为1024*1024。"
        f"电脑屏幕、桌面等元素要替换为其他更有创意、更多样化的元素，"
        f"采用{theme_str}，"
        f"除了logo、标题大字、吉祥物、风险提示外，其他元素都要多加替换。"
        f"吉祥物的形象必须完全符合第二张图片（吉祥物姿势包中的图片）中的吉祥物形象。"
        f"广告图片中必须包含和正方形参考图完全相同的中间标题大字，这个标题必须准确无误，一个字都不能错。"
        f"整体风格要专业、现代、吸引人，适合金融投资类广告。"
    )


def main():
    config_path = BASE_DIR / "google_ai_config_gemini.json"
    generator = AdImageGenerator(str(config_path))
    total = 10
    success = 0

    for i in range(10):
        themes = pick_random_themes()
        mascot = pick_random_mascot()
        prompt = build_prompt(themes, mascot.stem)

        print(f"\n{'='*60}")
        print(f"🟩 正方形 #{i+1}/10 | 主题: {' + '.join(themes)} | 吉祥物: {mascot.name}")
        print(f"{'='*60}")

        result = generator.generate_from_reference(
            reference_image_path=str(SQUARE_DIR),
            prompt=prompt,
            additional_images=[str(mascot)],
            aspect_ratio="1:1",
        )
        if result:
            success += 1

    print(f"\n{'='*60}")
    print(f"🎉 批量生成完成! 成功 {success}/{total} 张")
    print(f"📁 输出目录: {generator.output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
