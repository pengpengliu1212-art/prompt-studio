---
name: image-understanding
description: "使用Tesseract OCR识别图片中的文字并分析内容。基于龙虾AI图片理解技能，支持中文识别、内容分析和图片信息提取。"
homepage: ""
metadata:
  openclaw:
    emoji: "🖼️"
    requires: 
      bins: ["python3"]
      files: ["/home/ubuntu/lobster_venv/bin/python3", "/home/ubuntu/lobster_image_skill_simple.py"]
    install:
      - id: "setup-lobster-script"
        kind: "manual"
        label: "配置龙虾AI图片理解脚本"
        steps:
          - "确保 /home/ubuntu/lobster_venv/bin/python3 存在"
          - "确保 /home/ubuntu/lobster_image_skill_simple.py 存在"
          - "确保已安装依赖: pytesseract, Pillow"
---

# 图片理解技能

基于Tesseract OCR的图片文字识别与内容分析技能，使用龙虾AI图片理解脚本实现。

## 功能

### 1. 文字识别
- 提取图片中的文字（支持中文、英文）
- 统计字符数和行数
- 支持中英文混合识别

### 2. 图片分析
- 获取图片基本信息（尺寸、格式、大小）
- 自动检测内容类型（发票、合同、证件、文档等）
- 提取文字并分析

### 3. 图片信息
- 详细的图片元数据
- 文件大小和格式信息
- 色彩模式和尺寸

## 依赖要求

### 系统依赖
```bash
# Tesseract OCR
sudo apt install -y tesseract-ocr tesseract-ocr-chi-sim

# Python依赖（已在虚拟环境中）
/home/ubuntu/lobster_venv/bin/python3 -m pip install pytesseract Pillow
```

### 文件依赖
- `/home/ubuntu/lobster_venv/bin/python3` - Python虚拟环境
- `/home/ubuntu/lobster_image_skill_simple.py` - 主技能脚本
- `/home/ubuntu/simple_image_reader.py` - OCR核心模块

## 使用方法

### 基础命令
```bash
# 1. 文字识别
/home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 识别文字 /path/to/image.jpg

# 2. 图片分析
/home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 分析图片 /path/to/image.jpg

# 3. 图片信息
/home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 图片信息 /path/to/image.jpg
```

### OpenClaw集成使用
当用户发送图片并请求识别时，白月可以：
1. 保存接收到的图片到临时路径
2. 调用龙虾AI脚本进行识别
3. 返回格式化的识别结果

### 示例对话
```
用户：[发送图片] "识别一下这个图片的文字"
白月：使用图片理解技能识别图片内容...
📄 识别到文字 (256 字符):
这里是识别出的文字内容...
```

## 技能配置

### 配置示例
```json
{
  "skills": {
    "image_understanding": {
      "enabled": true,
      "name": "图片理解",
      "description": "识别图片中的文字并分析内容",
      "command": "python /home/ubuntu/lobster_image_skill_simple.py",
      "patterns": [
        "识别图片",
        "图片文字",
        "分析图片",
        "图片内容"
      ]
    }
  }
}
```

### 环境检查
```bash
# 检查虚拟环境
/home/ubuntu/lobster_venv/bin/python3 --version

# 检查OCR依赖
/home/ubuntu/lobster_venv/bin/python3 -c "import pytesseract; from PIL import Image; print('依赖检查通过')"

# 测试技能脚本
/home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 图片信息 /tmp/test.jpg
```

## 性能优化

### 提高识别准确率
1. **图片预处理**
   ```bash
   # 转换为灰度图
   convert input.jpg -colorspace Gray gray.jpg
   
   # 提高对比度
   convert input.jpg -contrast -contrast enhanced.jpg
   
   # 调整尺寸
   convert input.jpg -resize 200% large.jpg
   ```

2. **语言配置**
   ```bash
   # 仅中文识别
   -l chi_sim
   
   # 中英文混合（默认）
   -l chi_sim+eng
   
   # 仅英文
   -l eng
   ```

### 处理特定场景
- **发票/收据**: 自动检测财务关键词
- **证件识别**: 检测身份证、驾驶证等格式
- **合同文档**: 识别合同条款和签署方

## 故障排除

### 常见问题
1. **找不到Tesseract**
   ```bash
   sudo apt install -y tesseract-ocr tesseract-ocr-chi-sim
   ```

2. **Python模块缺失**
   ```bash
   /home/ubuntu/lobster_venv/bin/python3 -m pip install pytesseract Pillow
   ```

3. **识别准确率低**
   - 确保图片清晰度足够
   - 尝试图片预处理
   - 调整语言参数

4. **中文识别失败**
   ```bash
   # 检查中文语言包
   ls /usr/share/tesseract-ocr/4.00/tessdata/chi_sim.traineddata
   
   # 重新安装语言包
   sudo apt install --reinstall tesseract-ocr-chi-sim
   ```

### 调试模式
```bash
# 开启详细输出
DEBUG=1 /home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 识别文字 image.jpg

# 检查图片信息
file image.jpg
identify image.jpg
```

## 扩展功能

### 添加新语言
```bash
# 安装其他语言包
sudo apt install -y tesseract-ocr-jpn    # 日文
sudo apt install -y tesseract-ocr-kor    # 韩文
sudo apt install -y tesseract-ocr-fra    # 法文
```

### 自定义内容分析
编辑 `/home/ubuntu/simple_image_reader.py` 中的 `analyze_image` 函数，添加自定义的内容类型检测逻辑。

### 批量处理
```bash
#!/bin/bash
# batch_ocr.sh
for img in *.jpg *.png; do
    echo "处理: $img"
    /home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 识别文字 "$img" > "${img%.*}.txt"
done
```

## 安全与隐私

### 数据保护
- 所有图片处理都在本地进行
- 不发送图片到外部服务器
- 临时文件在使用后清理

### 使用限制
- 仅支持常见图片格式（JPG、PNG、GIF、BMP）
- 最大图片尺寸建议不超过10MB
- 文字识别准确率受图片质量影响

## 更新日志

### v1.0 (2026-04-01)
- 基于龙虾AI图片理解脚本
- 支持中文OCR识别
- 集成到OpenClaw技能系统
- 提供完整的配置和文档

---

**注意**: 本技能依赖于外部脚本 `/home/ubuntu/lobster_image_skill_simple.py`，请确保该脚本及其依赖正确安装。