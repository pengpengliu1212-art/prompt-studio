# 🖼️ 图片理解技能 - 使用指南

基于龙虾AI图片理解脚本的OpenClaw技能，提供完整的图片文字识别、内容分析和图片信息提取功能。

## 📋 技能状态

✅ **已就绪** - 所有组件已配置完成

## 🗂️ 技能结构

```
image-understanding/
├── SKILL.md                    # 技能定义文档
├── README.md                   # 本使用指南
├── scripts/
│   ├── image_ocr.py           # OpenClaw包装脚本
│   └── test_ocr.py            # 测试脚本
└── references/
    └── user_config.json       # 用户提供的技能配置
```

## 🔧 核心组件

### 1. 龙虾AI图片理解脚本
- **位置**: `/home/ubuntu/lobster_image_skill_simple.py`
- **依赖**: Tesseract OCR, Pillow, pytesseract
- **虚拟环境**: `/home/ubuntu/lobster_venv/bin/python3`

### 2. OpenClaw包装脚本
- **位置**: `scripts/image_ocr.py`
- **功能**: 提供统一的API接口和错误处理
- **支持**: 文字识别、图片分析、图片信息

## 🚀 快速开始

### 基本使用
```bash
# 1. 文字识别
python3 scripts/image_ocr.py text /path/to/image.jpg

# 2. 图片分析
python3 scripts/image_ocr.py analyze /path/to/image.jpg

# 3. 图片信息
python3 scripts/image_ocr.py info /path/to/image.jpg
```

### 微信图片识别
```bash
# 识别最新接收的微信图片
python3 scripts/image_ocr.py text $(ls -t /root/.openclaw/media/inbound/*/*.jpg | head -1)
```

### Python API
```python
from scripts.image_ocr import ocr_image, process_wechat_image

# 识别本地图片
result = ocr_image("screenshot.jpg", "识别文字")
if result["success"]:
    print(result.get("formatted", result.get("text")))

# 处理微信图片
wechat_result = process_wechat_image("/path/to/wechat_image.jpg", "分析图片")
```

## 💬 在OpenClaw中使用

### 手动调用
当用户发送图片请求识别时，白月可以：

1. **保存图片**到临时路径
2. **调用包装脚本**进行识别
3. **返回格式化结果**

### 示例响应
```
用户：[发送图片] "识别一下这个图片的文字"
白月：正在识别图片文字...
📄 识别到文字 (156 字符):
这里是识别出的文字内容...
```

### 自动化集成
根据用户提供的配置，可以设置自动触发：

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

## 🧪 功能验证

### 测试OCR功能
```bash
cd /root/.openclaw/workspace/skills/image-understanding
python3 scripts/test_ocr.py
```

### 验证依赖
```bash
# 检查虚拟环境
/home/ubuntu/lobster_venv/bin/python3 --version

# 检查OCR核心功能
/home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 图片信息 /tmp/test.jpg
```

## ⚙️ 配置说明

### 1. 用户配置
已保存的配置：`references/user_config.json`
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

### 2. 技能配置
在OpenClaw中启用技能的步骤：

1. **将配置添加到OpenClaw技能系统**
2. **确保命令路径正确**
3. **设置触发模式**

### 3. 环境变量
```bash
# 可选：设置默认语言
export OCR_DEFAULT_LANGUAGE="chi_sim+eng"

# 可选：设置临时目录
export OCR_TEMP_DIR="/tmp/ocr_cache"
```

## 🔍 故障排除

### 常见问题

1. **依赖缺失**
   ```bash
   # 安装系统依赖
   sudo apt install -y tesseract-ocr tesseract-ocr-chi-sim
   
   # 安装Python依赖
   /home/ubuntu/lobster_venv/bin/python3 -m pip install pytesseract Pillow
   ```

2. **图片路径错误**
   - 确保图片文件存在
   - 检查文件权限
   - 验证图片格式（支持JPG、PNG、GIF、BMP）

3. **识别准确率低**
   ```bash
   # 预处理图片
   convert input.jpg -colorspace Gray -contrast enhanced.jpg
   python3 scripts/image_ocr.py text enhanced.jpg
   ```

4. **中文识别失败**
   ```bash
   # 检查中文语言包
   ls /usr/share/tesseract-ocr/4.00/tessdata/chi_sim.traineddata
   
   # 重新安装
   sudo apt install --reinstall tesseract-ocr-chi-sim
   ```

### 调试模式
```bash
# 开启详细日志
DEBUG=1 python3 scripts/image_ocr.py text image.jpg

# 直接测试龙虾脚本
/home/ubuntu/lobster_venv/bin/python3 /home/ubuntu/lobster_image_skill_simple.py 识别文字 image.jpg
```

## 📈 性能优化

### 提高识别速度
1. **缩小图片尺寸**
   ```bash
   convert large.jpg -resize 50% small.jpg
   ```

2. **使用灰度图**
   ```bash
   convert color.jpg -colorspace Gray gray.jpg
   ```

3. **批量处理优化**
   - 使用多进程处理多张图片
   - 缓存语言模型

### 提高准确率
1. **图片预处理**
   ```bash
   # 组合优化
   convert input.jpg \
     -resize 150% \
     -colorspace Gray \
     -contrast -contrast \
     -sharpen 0.5 \
     optimized.jpg
   ```

2. **语言配置**
   ```bash
   # 仅中文
   -l chi_sim
   
   # 中英文混合（默认）
   -l chi_sim+eng
   
   # 纯英文
   -l eng
   ```

## 🔒 安全与隐私

### 数据保护
- ✅ 所有处理在本地进行
- ✅ 不发送图片到外部服务器
- ✅ 临时文件自动清理
- ✅ 支持加密存储

### 使用限制
- ⚠️ 最大图片尺寸：10MB（建议）
- ⚠️ 支持格式：JPG, PNG, GIF, BMP
- ⚠️ 识别准确率依赖图片质量

## 📚 高级功能

### 自定义内容分析
编辑 `/home/ubuntu/simple_image_reader.py`，扩展 `analyze_image` 函数：

```python
def analyze_image(image_path):
    # ... 现有代码 ...
    
    # 添加自定义检测
    if "自定义关键词" in text:
        content_types.append("自定义类型")
    
    return result
```

### 批量处理
```bash
#!/bin/bash
# batch_process.sh
for img in images/*.jpg; do
    echo "处理: $(basename $img)"
    python3 scripts/image_ocr.py text "$img" > "results/$(basename $img).txt"
done
```

### API服务
```python
# api_server.py
from flask import Flask, request, jsonify
from scripts.image_ocr import ocr_image

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    image_file = request.files['image']
    result = ocr_image(image_file, "识别文字")
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🔄 更新与维护

### 版本信息
- **技能版本**: 1.0
- **龙虾脚本版本**: 1.0
- **Tesseract版本**: 4.1.1
- **更新日期**: 2026年4月1日

### 更新日志
- **v1.0**: 初始版本，基于龙虾AI图片理解脚本

### 维护任务
```bash
# 定期检查依赖
python3 scripts/test_ocr.py

# 清理临时文件
rm -rf /tmp/ocr_*.jpg

# 更新语言包
sudo apt update && sudo apt upgrade tesseract-ocr-*
```

## 🤝 技术支持

### 获取帮助
1. **查看日志**: `tail -f /var/log/ocr_service.log`
2. **测试功能**: `python3 scripts/test_ocr.py`
3. **验证依赖**: `scripts/image_ocr.py` (无参数)

### 报告问题
提供以下信息：
1. 错误信息和堆栈跟踪
2. 图片样本（如可分享）
3. 系统环境信息
4. 复现步骤

---

**状态**: ✅ 技能已就绪，可立即使用
**维护**: 白月AI助理
**最后更新**: 2026年4月1日