#!/usr/bin/env python3
"""
广告图片生成器 - 从参考图片生成
使用Google Gemini Vision API生成相似的广告图片
"""

import json
import base64
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO
import google.genai
from google.genai import types

class AdImageGenerator:
    """广告图片生成器 - 使用Gemini Vision API"""

    def __init__(self, config_path=None):
        """初始化生成器"""
        self.config = self._load_config(config_path)
        self.assets_dir = Path(__file__).parent / ".claude" / "skills" / "ad-image-generator" / "assets"
        self.example_dir = self.assets_dir / "example"

        # 输出目录
        self.output_dir = Path("generated_ads")
        self.output_dir.mkdir(exist_ok=True)

        # 可用的Gemini Vision模型
        self.vision_models = [
            "models/gemini-2.5-flash-image",
            "models/gemini-3-pro-image-preview",
            "models/gemini-3.1-flash-image-preview"
        ]

    def _load_config(self, config_path):
        """加载配置文件"""
        default_config = {
            "api_key": "",
            "output_format": "png",
            "default_model": "models/gemini-2.5-flash-image"
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"警告: 配置文件加载失败: {e}")

        return default_config

    def _image_to_base64(self, image_path):
        """将图片转换为base64字符串"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            print(f"图片转base64失败: {e}")
            return None

    def generate_from_reference(self, reference_image_path, prompt=None, model_name=None, additional_images=None, aspect_ratio="9:16"):
        """从参考图片生成广告图片"""
        print("=" * 60)
        print("广告图片生成器 - 从参考图片生成")
        print("=" * 60)

        # 检查参考图片或目录
        ref_path = Path(reference_image_path)
        if not ref_path.exists():
            print(f"❌ 参考图片或目录不存在: {reference_image_path}")
            return None

        # 记录分类名称（用于命名）
        category_name = ref_path.stem

        if ref_path.is_dir():
            import random
            valid_exts = {".png", ".jpg", ".jpeg"}
            images = [p for p in ref_path.iterdir() if p.suffix.lower() in valid_exts and p.is_file()]
            if not images:
                print(f"❌ 目录中没有找到图片文件: {reference_image_path}")
                return None
            ref_path_rand = random.choice(images)
            print(f"📁 从目录随机选择参考图片: {ref_path_rand}")
            reference_image_path = str(ref_path_rand)

        self.current_category = category_name # 保存当前分类名称（深色/浅色等）

        print(f"最终参考图片: {reference_image_path}")

        # 读取参考图片
        try:
            with open(reference_image_path, "rb") as f:
                image_data = f.read()
            print("✅ 参考图片加载成功")
        except Exception as e:
            print(f"❌ 参考图片加载失败: {e}")
            return None

        # 读取额外图片
        additional_parts = []
        if additional_images:
            for i, img_path in enumerate(additional_images):
                if Path(img_path).exists():
                    try:
                        with open(img_path, "rb") as f:
                            img_data = f.read()
                        additional_parts.append(types.Part.from_bytes(
                            data=img_data,
                            mime_type="image/png"
                        ))
                        print(f"✅ 额外图片 {i+1} 加载成功: {img_path}")
                    except Exception as e:
                        print(f"❌ 额外图片 {i+1} 加载失败: {e}")
                else:
                    print(f"❌ 额外图片 {i+1} 不存在: {img_path}")

        # 使用默认或指定的prompt
        if not prompt:
            prompt = "请参考这张图片，生成一张相似的广告图片。必须严格限制图片尺寸为768*1376。"

        print(f"提示词: {prompt}")

        # 准备上传parts
        parts = [
            types.Part.from_bytes(
                data=image_data,
                mime_type="image/png"
            ),
            types.Part.from_text(text=prompt)
        ]

        # 添加额外图片parts
        parts.extend(additional_parts)

        # 调用Gemini Vision API
        print("\n调用Gemini Vision API...")

        # 使用指定的模型或尝试所有可用模型
        models_to_try = [model_name] if model_name else self.vision_models

        for model in models_to_try:
            try:
                print(f"  尝试模型: {model}")

                client = google.genai.Client(api_key=self.config["api_key"])

                response = client.models.generate_content(
                    model=model,
                    contents=parts,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio
                        )
                    )
                )

                print(f"  ✅ 模型 {model} 响应成功")

                # 处理响应
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.inline_data is not None:
                                # 保存生成的图片
                                image_data = part.inline_data.data

                                # 生成文件名
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"ad_from_{self.current_category}_{timestamp}.png"
                                output_path = self.output_dir / filename

                                # 保存图片
                                with open(output_path, "wb") as f:
                                    f.write(image_data)

                                # 验证图片
                                img_pil = Image.open(BytesIO(image_data))
                                print(f"\n✅ 广告图片生成成功!")
                                print(f"  文件名: {filename}")
                                print(f"  尺寸: {img_pil.size}")
                                print(f"  保存位置: {output_path}")

                                # 保存生成信息
                                self._save_generation_info(output_path, reference_image_path, model, prompt, additional_images)

                                return str(output_path)

                print(f"  ⚠️ 模型 {model} 响应中没有图片数据")

            except Exception as e:
                print(f"  ❌ 模型 {model} 失败: {e}")
                continue

        print("❌ 所有模型都失败")
        return None

    def _save_generation_info(self, image_path, reference_image_path, model_name, prompt, additional_images=None):
        """保存生成信息"""
        info = {
            "generated_at": datetime.now().isoformat(),
            "reference_image": str(reference_image_path),
            "model_used": model_name,
            "prompt": prompt,
            "image_path": str(image_path),
            "additional_images": additional_images if additional_images else []
        }

        info_file = self.output_dir / "generation_info.json"
        all_info = []

        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    all_info = json.load(f)
            except:
                all_info = []

        all_info.append(info)

        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(all_info, f, ensure_ascii=False, indent=2)

        print(f"  生成信息已保存: {info_file}")

    def batch_generate(self, reference_images, prompts=None, aspect_ratio="9:16"):
        """批量生成广告图片"""
        results = []

        if not prompts:
            prompts = [None] * len(reference_images)

        for i, (ref_img, prompt) in enumerate(zip(reference_images, prompts)):
            print(f"\n{'='*60}")
            print(f"生成第 {i+1}/{len(reference_images)} 张广告图片...")

            result = self.generate_from_reference(ref_img, prompt, aspect_ratio=aspect_ratio)
            if result:
                results.append(result)

        print(f"\n{'='*60}")
        print("批量生成完成!")
        print(f"成功生成 {len(results)}/{len(reference_images)} 张广告图片")

        return results

def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="广告图片生成器 - 从参考图片生成")
    parser.add_argument("--reference", default="./.claude/skills/ad-image-generator/assets/example/浅色",
                       help="参考图片或文件夹路径（默认：浅色文件夹）")
    parser.add_argument("--prompt", help="生成提示词（默认：请参考这张图片，生成一张相似的广告图片。必须严格限制图片尺寸为768*1376。）")
    parser.add_argument("--model", help="指定使用的模型")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--batch", nargs="+", help="批量生成，提供多个参考图片路径")
    parser.add_argument("--additional", nargs="+", help="额外参考图片路径")
    parser.add_argument("--aspect-ratio", default="9:16", help="生成图片宽高比（默认：9:16）= 768*1376竖版")

    args = parser.parse_args()

    # 初始化生成器
    generator = AdImageGenerator(args.config)

    try:
        if args.batch:
            # 批量生成
            print("开始批量生成广告图片...")
            results = generator.batch_generate(args.batch, [args.prompt] * len(args.batch) if args.prompt else None)

            if results:
                print(f"\n🎉 批量生成完成!")
                print(f"📁 输出目录: {generator.output_dir}")
                print(f"📊 成功数量: {len(results)}/{len(args.batch)}")
        else:
            # 单张生成
            print("开始生成广告图片...")
            final_path = generator.generate_from_reference(
                reference_image_path=args.reference,
                prompt=args.prompt,
                model_name=args.model,
                additional_images=args.additional,
                aspect_ratio=args.aspect_ratio
            )

            if final_path:
                print(f"\n🎉 广告图片生成成功!")
                print(f"📁 文件位置: {final_path}")
                print(f"\n📋 生成详情:")
                print(f"  参考图片: {args.reference}")
                print(f"  提示词: {args.prompt if args.prompt else '请参考这张图片，生成一张相似的广告图片。必须严格限制图片尺寸为768*1376。'}")
                print(f"  宽高比: {args.aspect_ratio}")
                print(f"  输出目录: {generator.output_dir}")
            else:
                print("❌ 广告图片生成失败")

    except KeyboardInterrupt:
        print("\n❌ 用户中断生成过程")
    except Exception as e:
        print(f"❌ 生成失败: {e}")

if __name__ == "__main__":
    main()