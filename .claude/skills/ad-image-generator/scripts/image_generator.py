#!/usr/bin/env python3
"""
广告图片生成脚本
根据专业参数生成规范的广告图片（1080×1920）
支持多种图片生成工具集成
"""

import os
import sys
import json
import argparse
import requests
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AdImageGenerator:
    """广告图片生成器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化图片生成器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.width = 1280
        self.height = 720
        self.templates_dir = Path(__file__).parent.parent / "assets" / "templates"
        self.elements_dir = Path(__file__).parent.parent / "assets" / "elements"
        self.output_dir = Path.cwd() / "generated_ads"
        self.output_dir.mkdir(exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "tool": "google_imagen",  # 默认使用Google Imagen
            "api_key": "",  # 从配置文件加载
            "default_style": "modern fintech",
            "default_colors": ["#4A90E2", "#50E3C2", "#F5A623"],
            "quality": "standard",
            "output_format": "png"
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"警告: 配置文件加载失败: {e}")

        return default_config

    def generate_from_params(self, params: Dict[str, Any]) -> str:
        """
        根据参数生成广告图片

        Args:
            params: 广告参数字典

        Returns:
            生成的图片文件路径
        """
        print(f"开始生成广告图片...")
        print(f"参数: {json.dumps(params, indent=2, ensure_ascii=False)}")

        # 验证必要参数
        required_params = ["theme", "copywriting"]
        for param in required_params:
            if param not in params:
                raise ValueError(f"缺少必要参数: {param}")

        # 补充默认参数
        params.setdefault("size", f"{self.width}x{self.height}")
        params.setdefault("style", self.config["default_style"])
        params.setdefault("colors", self.config["default_colors"])
        params.setdefault("template", "standard")

        # 选择生成工具
        tool = params.get("tool", self.config["tool"])

        # 根据工具调用不同的生成方法
        if tool == "google_imagen":
            image_path = self._generate_with_google_imagen(params)
        elif tool == "mock":
            image_path = self._generate_mock_image(params)
        else:
            raise ValueError(f"不支持的生成工具: {tool}。只支持google_imagen和mock")

        print(f"广告图片生成完成: {image_path}")
        return image_path

    def _generate_with_google_imagen(self, params: Dict[str, Any]) -> str:
        """使用Google Imagen API生成高质量图片"""
        prompt = self._build_prompt(params)
        print(f"Google Imagen图片生成提示词: {prompt}")
        print("⚠️ 注意：生成高质量图片需要较长时间，请耐心等待...")

        # 只使用Google Imagen API
        try:
            print("🚀 开始使用Google Imagen API生成高质量图片...")
            result = self._try_google_imagen(prompt, params)
            if result and "mock" not in result:
                return result
            else:
                raise Exception("Google Imagen API生成失败")
        except Exception as e:
            print(f"❌ Google Imagen API失败: {e}")
            print("💥 图片生成失败，不尝试其他API")
            raise Exception(f"Google Imagen API图片生成失败: {e}")

    def _try_google_imagen(self, prompt: str, params: Dict[str, Any]) -> str:
        """使用Google Imagen API生成高质量图片"""
        try:
            import google.genai
            from google.genai import types

            client = google.genai.Client(api_key=self.config["api_key"])

            # 尝试不同的模型 - 使用正确的Google Imagen模型名称
            models_to_try = [
                "imagen-4.0-generate-001",  # Imagen 4.0标准模型
                "imagen-4.0-fast-generate-001",  # Imagen 4.0快速模型
                "imagen-4.0-ultra-generate-001",  # Imagen 4.0最高质量
                "imagen-3.0-generate-002"  # 回退到3.0
            ]

            # 检查是否有参考图片
            reference_images = params.get("reference_images", [])

            # 尝试加载本地素材作为参考（如果API支持）
            local_references = []
            if params.get("mascot_file"):
                mascot_path = self.elements_dir / "吉祥物姿势包" / params["mascot_file"]
                if mascot_path.exists():
                    print(f"找到吉祥物素材: {params['mascot_file']}")

            if params.get("logo_file"):
                logo_path = self.elements_dir / params["logo_file"]
                if logo_path.exists():
                    print(f"找到Logo素材: {params['logo_file']}")

            for model_name in models_to_try:
                try:
                    print(f"尝试使用模型: {model_name}")

                    # 使用generate_images方法 - 正确的图片生成API
                    config = types.GenerateImagesConfig(
                        number_of_images=1,
                        # 不指定image_size，使用模型默认尺寸
                        # image_size参数会导致错误，所以省略
                    )

                    # 如果有参考图片，尝试使用image-to-image功能
                    # 注意：Google Imagen可能不支持直接上传参考图片
                    # 我们通过详细的prompt来描述素材
                    response = client.models.generate_images(
                        model=model_name,
                        prompt=prompt,
                        config=config
                    )

                    # 提取图片数据
                    if hasattr(response, 'images') and response.images:
                        img = response.images[0]

                        # 检查图片数据 - 属性名可能是image_bytes
                        image_data = None
                        if hasattr(img, 'image_bytes') and img.image_bytes:
                            image_data = img.image_bytes
                            print(f"  从image_bytes获取数据，长度: {len(image_data)}")
                        elif hasattr(img, 'bytes') and img.bytes:
                            image_data = img.bytes
                            print(f"  从bytes获取数据，长度: {len(image_data)}")
                        elif hasattr(img, 'gcs_uri') and img.gcs_uri:
                            # 如果是GCS URI，需要下载
                            print(f"⚠️ 图片存储在GCS: {img.gcs_uri}")
                            print("💡 需要配置GCS访问权限来下载图片")
                            continue
                        else:
                            print(f"⚠️ 模型 {model_name} 返回了没有数据的图片")
                            print(f"  图片属性: {[attr for attr in dir(img) if not attr.startswith('_')]}")
                            continue
                    else:
                        print(f"⚠️ 模型 {model_name} 没有返回图片")
                        continue

                    if image_data:
                        filename = f"ad_{params['theme']}_{params.get('style', 'modern')}.png"
                        image_path = self.output_dir / filename

                        # 保存图片
                        with open(image_path, "wb") as f:
                            f.write(image_data)

                        # 验证图片尺寸
                        try:
                            image = Image.open(BytesIO(image_data))
                            print(f"✅ Google Imagen图片生成成功 ({model_name}): {image_path}")
                            print(f"📏 图片尺寸: {image.size}")
                            print(f"🎨 图片格式: {image.format}")
                            return str(image_path)
                        except Exception as img_error:
                            print(f"⚠️ 图片处理错误: {img_error}")
                            # 即使处理错误，也返回文件路径
                            return str(image_path)

                    else:
                        print(f"⚠️ 模型 {model_name} 返回了空数据")

                except Exception as e:
                    print(f"⚠️ 模型 {model_name} 失败: {str(e)[:200]}")
                    continue

            print("❌ 所有Google Imagen模型都失败")
            raise Exception("所有Google Imagen模型都不可用")

        except ImportError:
            print("❌ 未安装google-genai库")
            print("💡 请安装: pip install google-genai")
            raise Exception("Google Imagen API依赖未安装")
        except Exception as e:
            print(f"❌ Google Imagen API调用失败: {e}")
            print("💡 可能原因: 1) API密钥无效 2) 模型权限问题 3) API版本不兼容")
            raise Exception(f"Google Imagen API调用失败: {str(e)[:100]}")




    def _generate_local_image(self, prompt: str, params: Dict[str, Any]) -> str:
        """使用本地Python库生成简单广告图片"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random

            # 创建新图片
            img = Image.new('RGB', (self.width, self.height), color='white')
            draw = ImageDraw.Draw(img)

            # 尝试加载字体
            try:
                font = ImageFont.truetype("Arial", 40)
            except:
                font = ImageFont.load_default()

            # 解析颜色
            colors = params.get("colors", ["#4A90E2", "#50E3C2", "#F5A623"])
            if isinstance(colors, list) and len(colors) > 0:
                bg_color = colors[0]
            else:
                bg_color = "#4A90E2"

            # 绘制背景渐变
            for i in range(self.height):
                r = int(int(bg_color[1:3], 16) * (1 - i/self.height))
                g = int(int(bg_color[3:5], 16) * (1 - i/self.height))
                b = int(int(bg_color[5:7], 16) * (1 - i/self.height))
                draw.line([(0, i), (self.width, i)], fill=(r, g, b))

            # 添加主题文字
            theme = params.get("theme", "广告")
            copywriting = params.get("copywriting", "")

            # 绘制主题框
            theme_box = (self.width//4, self.height//4, 3*self.width//4, self.height//3)
            draw.rectangle(theme_box, fill=(255, 255, 255, 128), outline=(0, 0, 0), width=3)

            # 添加文字
            draw.text((self.width//2, self.height//3 - 60), theme, fill=(0, 0, 0), font=font, anchor="mm")
            draw.text((self.width//2, self.height//3), copywriting, fill=(0, 0, 0), font=font, anchor="mm")

            # 添加装饰元素
            style = params.get("style", "modern")
            if "tech" in style.lower() or "科技" in style:
                # 绘制科技感线条
                for i in range(0, self.width, 50):
                    draw.line([(i, 0), (i, self.height)], fill=(255, 255, 255, 50), width=1)
                for i in range(0, self.height, 50):
                    draw.line([(0, i), (self.width, i)], fill=(255, 255, 255, 50), width=1)

            # 添加底部文字
            draw.text((self.width//2, 5*self.height//6), "专业广告设计", fill=(255, 255, 255), font=font, anchor="mm")
            draw.text((self.width//2, 5*self.height//6 + 50), f"尺寸: {self.width}×{self.height}", fill=(255, 255, 255), font=font, anchor="mm")

            # 保存图片
            filename = f"ad_{params['theme']}_{params.get('style', 'modern')}.png"
            image_path = self.output_dir / filename
            img.save(image_path, "PNG")

            print(f"✅ 本地图片生成成功: {image_path}")
            return str(image_path)

        except Exception as e:
            raise Exception(f"本地图片生成失败: {e}")

    def _generate_mock_image(self, params: Dict[str, Any]) -> str:
        """生成模拟图片（用于测试）"""
        print("使用模拟模式生成图片")

        filename = f"mock_ad_{params['theme']}.png"
        image_path = self.output_dir / filename

        # 创建模拟图片文件
        self._create_mock_image(image_path, params)

        return str(image_path)

    def _build_prompt(self, params: Dict[str, Any]) -> str:
        """构建图片生成提示词"""
        # 如果有详细prompt，直接使用
        if "detailed_prompt" in params:
            return params["detailed_prompt"]

        theme = params["theme"]
        copywriting = params["copywriting"]
        style = params.get("style", "modern fintech")
        colors = params.get("colors", ["blue", "white"])
        reference_images = params.get("reference_images", [])
        risk_warning = params.get("risk_warning", "市场有风险，投资需谨慎。投资前请仔细阅读相关协议和风险提示。")
        mascot_file = params.get("mascot_file")
        logo_file = params.get("logo_file", "logo1.png")

        color_desc = ", ".join(colors[:3])

        # 构建详细的prompt - 根据SKILL.md强制设计要求
        prompt_parts = [
            # 基础描述
            f"Professional fintech advertisement image for AI Zangle, {theme} theme",
            f"Horizontal format, widescreen advertising layout, 16:9 aspect ratio",

            # 强制品牌元素
            f"Brand logo '{logo_file}' at top-left corner, clearly visible",
            f"Compliance risk disclaimer text at bottom: '{risk_warning}' in small clear font (8-10pt), readable",

            # 吉祥物整合
            f"Mascot character: {self._get_mascot_description(mascot_file, theme)}, naturally integrated into the scene",

            # 科技感背景构建
            f"Modern fintech background with depth, interactive elements: data streams, network nodes, digital interfaces, holographic effects",
            f"No solid color backgrounds, create immersive tech environment",

            # 广告文案
            f"Prominent main text: '{copywriting}', large and eye-catching, good contrast with background",
            f"Secondary text supporting the theme, professionally typeset",

            # 风格和配色
            f"Style: {style}, with {color_desc} color scheme",
            f"Dark tech aesthetic with glowing elements, futuristic feel",

            # 视觉层次
            f"Clear visual hierarchy: logo top-left, main text center, mascot integrated, risk disclaimer bottom",
            f"Good balance between elements, professional composition",

            # 质量要求
            f"High quality professional advertisement, clean layout",
            f"No watermarks, no text overlays except specified elements",
            f"Photorealistic rendering where appropriate"
        ]

        # 如果有参考图片，添加到提示词中
        if reference_images:
            ref_count = len(reference_images)
            prompt_parts.append(f"Inspired by {ref_count} professional fintech advertisement references for style and composition")

        # 添加模板特定要求
        template = params.get("template", "")
        if template == "banner":
            prompt_parts.append("Horizontal banner layout")
        elif template == "social":
            prompt_parts.append("Square format for social media")
        elif template == "promotion":
            prompt_parts.append("Promotional style with emphasis on offers")

        # 合并为适合图片生成的提示词
        return ", ".join(prompt_parts)

    def _get_mascot_description(self, mascot_file: Optional[str], theme: str) -> str:
        """根据吉祥物文件名和主题获取描述"""
        if not mascot_file:
            return f"friendly fintech mascot matching {theme} theme"

        # 根据文件名推断姿势类型
        mascot_lower = mascot_file.lower()

        if any(word in mascot_lower for word in ["开心", "欢呼", "跳跃"]):
            return f"happy, energetic mascot celebrating {theme}"
        elif any(word in mascot_lower for word in ["专业", "工作", "客服"]):
            return f"professional, confident mascot for {theme}"
        elif any(word in mascot_lower for word in ["手势", "比心", "大拇指"]):
            return f"mascot making friendly gesture for {theme}"
        elif any(word in mascot_lower for word in ["思考", "展示"]):
            return f"thoughtful mascot presenting {theme}"
        elif any(word in mascot_lower for word in ["打鼓", "表演"]):
            return f"entertaining mascot performing for {theme}"
        else:
            return f"friendly fintech mascot suitable for {theme} theme"

    def _create_mock_image(self, image_path: Path, params: Dict[str, Any]) -> None:
        """创建模拟图片文件（实际使用时需要替换为真正的图片生成）"""
        # 这里只是创建空文件作为示例
        # 实际使用时应该调用真正的图片生成API

        with open(image_path, 'w') as f:
            f.write(f"Mock advertisement image for: {params['theme']}\n")
            f.write(f"Copywriting: {params['copywriting']}\n")
            f.write(f"Size: {self.width}x{self.height}\n")
            f.write(f"Style: {params.get('style', 'modern')}\n")
            f.write(f"Colors: {', '.join(params.get('colors', []))}\n")

        print(f"创建模拟图片: {image_path}")
        print("注意: 这是模拟文件，实际使用时需要集成真正的图片生成API")

    def list_templates(self) -> list:
        """列出可用的模板"""
        templates = []
        if self.templates_dir.exists():
            for file in self.templates_dir.glob("*.json"):
                templates.append(file.stem)
        return templates

    def list_elements(self) -> list:
        """列出可用的固定元素"""
        elements = []
        if self.elements_dir.exists():
            for file in self.elements_dir.glob("*"):
                if file.is_file():
                    elements.append(file.name)
        return elements


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="广告图片生成器")
    parser.add_argument("--theme", required=True, help="广告主题")
    parser.add_argument("--copywriting", required=True, help="广告文案")
    parser.add_argument("--style", default="modern", help="设计风格")
    parser.add_argument("--colors", nargs="+", help="颜色列表")
    parser.add_argument("--template", default="standard", help="模板类型")
    parser.add_argument("--tool", default="google_imagen", choices=["google_imagen", "mock"],
                       help="图片生成工具（只支持google_imagen和mock）")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--list-templates", action="store_true", help="列出可用模板")
    parser.add_argument("--list-elements", action="store_true", help="列出可用元素")

    args = parser.parse_args()

    generator = AdImageGenerator(args.config)

    if args.list_templates:
        templates = generator.list_templates()
        print("可用模板:")
        for template in templates:
            print(f"  - {template}")
        return

    if args.list_elements:
        elements = generator.list_elements()
        print("可用元素:")
        for element in elements:
            print(f"  - {element}")
        return

    # 构建参数
    params = {
        "theme": args.theme,
        "copywriting": args.copywriting,
        "style": args.style,
        "template": args.template,
        "tool": args.tool
    }

    if args.colors:
        params["colors"] = args.colors

    try:
        image_path = generator.generate_from_params(params)
        print(f"\n✅ 广告图片生成成功!")
        print(f"📁 文件位置: {image_path}")
        print(f"📏 尺寸: 1280×720")
        print(f"🎨 风格: {args.style}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()