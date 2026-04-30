#!/usr/bin/env python3
"""
OpenClaw 图片OCR技能包装脚本
调用龙虾AI图片理解技能
"""

import os
import sys
import subprocess
import json
import tempfile
from pathlib import Path

# 技能配置
LOBSTER_SCRIPT = "/home/ubuntu/lobster_image_skill_simple.py"
PYTHON_BIN = "/home/ubuntu/lobster_venv/bin/python3"

def check_dependencies():
    """检查依赖是否可用"""
    errors = []
    
    if not os.path.exists(PYTHON_BIN):
        errors.append(f"Python虚拟环境不存在: {PYTHON_BIN}")
    
    if not os.path.exists(LOBSTER_SCRIPT):
        errors.append(f"龙虾AI脚本不存在: {LOBSTER_SCRIPT}")
    
    # 检查Python模块
    try:
        check_cmd = [PYTHON_BIN, "-c", "import pytesseract; from PIL import Image; print('依赖检查通过')"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(f"Python依赖检查失败: {result.stderr}")
    except Exception as e:
        errors.append(f"依赖检查异常: {e}")
    
    return errors

def ocr_image(image_path, command="识别文字"):
    """
    识别图片文字
    
    Args:
        image_path: 图片文件路径
        command: 命令类型，可选：识别文字、分析图片、图片信息
    
    Returns:
        dict: 识别结果
    """
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"图片文件不存在: {image_path}",
            "tip": "请提供有效的图片文件路径"
        }
    
    # 验证命令
    valid_commands = ["识别文字", "分析图片", "图片信息"]
    if command not in valid_commands:
        return {
            "success": False,
            "error": f"无效的命令: {command}",
            "valid_commands": valid_commands
        }
    
    try:
        # 调用龙虾AI脚本
        cmd = [PYTHON_BIN, LOBSTER_SCRIPT, command, image_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"脚本执行失败: {result.stderr}",
                "returncode": result.returncode
            }
        
        # 解析输出
        output = result.stdout.strip()
        
        # 如果输出包含格式化文本，直接返回
        if output.startswith("📄") or output.startswith("🖼️") or output.startswith("📊"):
            return {
                "success": True,
                "formatted": output,
                "raw_output": output
            }
        else:
            # 尝试解析JSON输出
            try:
                json_output = json.loads(output)
                return {
                    "success": True,
                    "data": json_output,
                    "raw_output": output
                }
            except json.JSONDecodeError:
                # 不是JSON，返回原始文本
                return {
                    "success": True,
                    "text": output,
                    "raw_output": output
                }
                
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "识别超时（30秒）",
            "tip": "图片可能太大或太复杂，尝试压缩图片"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"识别过程异常: {str(e)}",
            "exception_type": type(e).__name__
        }

def process_wechat_image(image_file, command="识别文字"):
    """
    处理微信接收的图片文件
    
    Args:
        image_file: 图片文件路径或文件对象
        command: 识别命令
    
    Returns:
        dict: 识别结果
    """
    # 如果传入的是文件对象，保存到临时文件
    if hasattr(image_file, 'read'):
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(image_file.read())
            image_path = tmp.name
            is_temp = True
    else:
        image_path = str(image_file)
        is_temp = False
    
    try:
        # 执行OCR
        result = ocr_image(image_path, command)
        
        # 添加文件信息
        if os.path.exists(image_path):
            file_info = {
                "filename": os.path.basename(image_path),
                "size": os.path.getsize(image_path),
                "path": image_path
            }
            if "data" in result:
                result["data"]["file_info"] = file_info
            else:
                result["file_info"] = file_info
        
        return result
    finally:
        # 清理临时文件
        if is_temp and os.path.exists(image_path):
            os.unlink(image_path)

def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("🖼️ OpenClaw 图片OCR技能")
        print("=" * 50)
        print("用法:")
        print("  python image_ocr.py <命令> <图片路径>")
        print("")
        print("命令:")
        print("  text       识别文字")
        print("  analyze    分析图片")
        print("  info       图片信息")
        print("")
        print("示例:")
        print("  python image_ocr.py text /path/to/image.jpg")
        print("  python image_ocr.py analyze screenshot.png")
        print("")
        
        # 检查依赖
        print("依赖检查:")
        errors = check_dependencies()
        if errors:
            print("❌ 发现错误:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ 所有依赖检查通过")
        
        return
    
    # 映射命令
    command_map = {
        "text": "识别文字",
        "analyze": "分析图片", 
        "info": "图片信息"
    }
    
    cli_command = sys.argv[1]
    image_path = sys.argv[2]
    
    if cli_command not in command_map:
        print(f"❌ 未知命令: {cli_command}")
        print(f"可用命令: {', '.join(command_map.keys())}")
        sys.exit(1)
    
    # 执行OCR
    command = command_map[cli_command]
    result = ocr_image(image_path, command)
    
    # 输出结果
    if result.get("success"):
        if "formatted" in result:
            print(result["formatted"])
        elif "text" in result:
            print(result["text"])
        elif "data" in result:
            print(json.dumps(result["data"], ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"❌ OCR失败: {result.get('error', '未知错误')}")
        if "tip" in result:
            print(f"💡 {result['tip']}")
        sys.exit(1)

if __name__ == "__main__":
    main()