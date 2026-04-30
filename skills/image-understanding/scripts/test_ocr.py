#!/usr/bin/env python3
"""
图片理解技能测试脚本
"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from image_ocr import check_dependencies, ocr_image, process_wechat_image
except ImportError:
    print("❌ 无法导入image_ocr模块")
    sys.exit(1)

def test_dependencies():
    """测试依赖检查"""
    print("🔍 测试依赖检查...")
    errors = check_dependencies()
    
    if errors:
        print(f"❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ 所有依赖检查通过")
        return True

def test_sample_image():
    """测试样本图片"""
    print("\n🖼️ 测试样本图片...")
    
    # 创建测试图片（简单的文本图片）
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建测试图片
    img = Image.new('RGB', (800, 200), color='white')
    d = ImageDraw.Draw(img)
    
    # 尝试使用字体，如果没有则使用默认
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # 绘制测试文本
    test_text = "OpenClaw图片OCR测试\n中文测试：欢迎使用图片理解技能\nTest OCR: Hello World!"
    d.text((50, 50), test_text, fill='black', font=font)
    
    # 保存测试图片
    test_image_path = "/tmp/test_ocr_image.jpg"
    img.save(test_image_path)
    print(f"✅ 创建测试图片: {test_image_path}")
    
    return test_image_path

def run_ocr_tests(image_path):
    """运行OCR测试"""
    print("\n🧪 运行OCR功能测试...")
    
    tests = [
        ("图片信息", "info"),
        ("识别文字", "text"),
        ("分析图片", "analyze")
    ]
    
    all_passed = True
    
    for command_name, test_name in tests:
        print(f"\n📋 测试: {command_name}")
        print("-" * 40)
        
        result = ocr_image(image_path, command_name)
        
        if result.get("success"):
            print(f"✅ {command_name} 测试通过")
            
            # 显示部分结果
            if "formatted" in result:
                # 显示前3行
                lines = result["formatted"].split('\n')
                for line in lines[:3]:
                    print(f"  {line}")
                if len(lines) > 3:
                    print(f"  ... ({len(lines)-3} 更多行)")
            elif "text" in result:
                text = result["text"]
                if len(text) > 100:
                    print(f"  识别结果: {text[:100]}...")
                else:
                    print(f"  识别结果: {text}")
            else:
                print(f"  成功，但无格式化输出")
        else:
            print(f"❌ {command_name} 测试失败")
            print(f"   错误: {result.get('error', '未知错误')}")
            all_passed = False
    
    return all_passed

def test_wechat_integration():
    """测试微信图片集成"""
    print("\n📱 测试微信图片集成...")
    
    # 查找微信接收的图片
    wechat_image_dir = "/root/.openclaw/media/inbound"
    wechat_images = []
    
    if os.path.exists(wechat_image_dir):
        for root, dirs, files in os.walk(wechat_image_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    wechat_images.append(os.path.join(root, file))
    
    if wechat_images:
        # 使用最新的微信图片
        latest_image = max(wechat_images, key=os.path.getmtime)
        print(f"✅ 找到微信图片: {os.path.basename(latest_image)}")
        
        # 测试处理
        result = process_wechat_image(latest_image, "识别文字")
        
        if result.get("success"):
            print(f"✅ 微信图片处理成功")
            if "formatted" in result:
                lines = result["formatted"].split('\n')
                for line in lines[:2]:
                    print(f"  {line}")
            return True
        else:
            print(f"❌ 微信图片处理失败: {result.get('error')}")
            return False
    else:
        print("ℹ️ 未找到微信图片，跳过此测试")
        return True  # 跳过不算失败

def performance_test():
    """性能测试"""
    print("\n⚡ 性能测试...")
    
    import time
    
    # 创建小测试图片
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='white')
    perf_image = "/tmp/perf_test.jpg"
    img.save(perf_image)
    
    # 测试响应时间
    start_time = time.time()
    result = ocr_image(perf_image, "图片信息")
    end_time = time.time()
    
    if result.get("success"):
        response_time = (end_time - start_time) * 1000  # 毫秒
        print(f"✅ 响应时间: {response_time:.1f}ms")
        
        if response_time < 1000:
            print("  性能评级: 🟢 优秀")
        elif response_time < 3000:
            print("  性能评级: 🟡 良好")
        else:
            print("  性能评级: 🔴 较慢")
        
        return True
    else:
        print(f"❌ 性能测试失败: {result.get('error')}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🖼️ 图片理解技能 - 完整测试套件")
    print("=" * 60)
    
    # 记录测试结果
    test_results = {}
    
    # 1. 依赖测试
    test_results["dependencies"] = test_dependencies()
    
    # 2. 创建测试图片
    test_image = test_sample_image()
    
    # 3. OCR功能测试
    if test_image and os.path.exists(test_image):
        test_results["ocr_functions"] = run_ocr_tests(test_image)
    else:
        test_results["ocr_functions"] = False
        print("❌ 无法创建测试图片")
    
    # 4. 微信集成测试
    test_results["wechat_integration"] = test_wechat_integration()
    
    # 5. 性能测试
    test_results["performance"] = performance_test()
    
    # 清理测试文件
    if os.path.exists(test_image):
        os.unlink(test_image)
        print(f"\n🧹 清理测试图片")
    
    # 测试总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, passed in test_results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} {status}")
    
    print("-" * 60)
    print(f"总测试: {total_tests} | 通过: {passed_tests} | 失败: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！技能可以正常使用。")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())