#!/bin/bash
# 白月科技资讯仪表板 - 一键安装脚本

set -e

echo "🤖 白月科技资讯仪表板安装向导"
echo "=" * 60

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要Python 3.8+，请先安装Python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python版本: $PYTHON_VERSION"

# 创建工作目录
WORK_DIR="$HOME/tech_news_dashboard"
echo "📁 创建工作目录: $WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# 复制文件
echo "📋 复制必要文件..."
cp /root/.openclaw/workspace/apple_style_news_dashboard.html ./index.html
cp /root/.openclaw/workspace/news_crawler.py ./
cp /root/.openclaw/workspace/tech_dashboard_mobile.html ./mobile.html

# 创建配置文件
echo "⚙️ 创建配置文件..."
cat > config.json << 'EOF'
{
  "sources": {
    "tech": {
      "name": "3C数码",
      "keywords": ["苹果", "华为", "小米", "三星", "折叠屏", "5G", "芯片", "手机"],
      "rss_feeds": [
        "https://36kr.com/feed",
        "https://www.huxiu.com/rss",
        "https://www.ithome.com/rss",
        "https://www.chinaz.com/feed"
      ]
    },
    "ai": {
      "name": "AI人工智能",
      "keywords": ["AI", "人工智能", "大模型", "GPT", "芯片", "英伟达", "OpenAI"],
      "rss_feeds": [
        "https://www.jiqizhixin.com/rss",
        "https://www.leiphone.com/feed",
        "https://www.msra.cn/feed"
      ]
    }
  },
  "output": {
    "json_file": "news_data.json",
    "html_file": "dashboard_with_data.html",
    "update_frequency": 3600
  },
  "crawler": {
    "max_articles": 10,
    "cache_hours": 6,
    "user_agent": "白月科技资讯爬虫/1.0"
  }
}
EOF

# 安装Python依赖
echo "🔧 安装Python依赖..."
pip3 install --user feedparser requests || {
    echo "⚠️  使用系统包管理器安装..."
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3-pip python3-venv
        pip3 install feedparser requests
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
        pip3 install feedparser requests
    else
        echo "❌ 无法自动安装依赖，请手动运行: pip3 install feedparser requests"
    fi
}

# 测试依赖
echo "🧪 测试依赖..."
python3 -c "import feedparser, requests; print('✅ 依赖检查通过')" || {
    echo "❌ 依赖检查失败"
    exit 1
}

# 创建数据目录
mkdir -p news_data

# 创建运行脚本
echo "📝 创建运行脚本..."
cat > run_crawler.sh << 'EOF'
#!/bin/bash
# 运行资讯爬虫

cd "$(dirname "$0")"

echo "🕒 $(date '+%Y-%m-%d %H:%M:%S')"
echo "🤖 启动白月科技资讯爬虫..."

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 运行爬虫
python3 news_crawler.py --mode rss --config config.json

# 生成最终HTML
if [ -f "news_data/news_dashboard_latest.html" ]; then
    cp news_data/news_dashboard_latest.html dashboard_latest.html
    echo "✅ 仪表板已更新: dashboard_latest.html"
fi

if [ -f "news_data/news_data.json" ]; then
    echo "📊 数据统计:"
    python3 -c "
import json
with open('news_data/news_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
tech = len(data.get('data', {}).get('tech', []))
ai = len(data.get('data', {}).get('ai', []))
print(f'   3C数码: {tech} 篇')
print(f'   AI人工智能: {ai} 篇')
"
fi

echo "🎉 完成！用浏览器打开 dashboard_latest.html 查看"
EOF

chmod +x run_crawler.sh

# 创建定时任务脚本
echo "⏰ 创建定时任务脚本..."
cat > setup_cron.sh << 'EOF'
#!/bin/bash
# 设置定时任务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CRON_JOB="0 */2 * * * cd '$SCRIPT_DIR' && ./run_crawler.sh >> cron.log 2>&1"

echo "当前用户的定时任务:"
crontab -l 2>/dev/null || echo "暂无定时任务"

echo ""
echo "要添加每2小时自动更新的定时任务吗？ (y/N)"
read -r answer

if [[ "$answer" =~ ^[Yy]$ ]]; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ 定时任务已添加：每2小时自动更新"
    echo "   运行: crontab -l 查看"
    echo "   运行: crontab -e 编辑"
else
    echo "ℹ️ 手动运行: ./run_crawler.sh"
fi
EOF

chmod +x setup_cron.sh

# 创建使用说明
echo "📖 创建使用说明..."
cat > README.md << 'EOF'
# 📱 白月科技资讯仪表板

苹果风格的科技资讯仪表板，支持自动抓取3C数码和AI行业资讯。

## 🚀 快速开始

### 1. 首次运行
```bash
# 运行爬虫获取数据
./run_crawler.sh

# 用浏览器打开生成的仪表板
open dashboard_latest.html  # macOS
xdg-open dashboard_latest.html  # Linux
start dashboard_latest.html  # Windows
```

### 2. 设置自动更新（可选）
```bash
# 设置每2小时自动更新
./setup_cron.sh

# 或手动添加定时任务
crontab -e
# 添加: 0 */2 * * * /完整路径/run_crawler.sh >> cron.log 2>&1
```

### 3. 手动更新数据
```bash
# 随时运行爬虫更新数据
./run_crawler.sh
```

## 📁 文件说明

- `index.html` - 苹果风格仪表板（静态版本）
- `dashboard_latest.html` - 包含最新数据的仪表板
- `news_crawler.py` - Python爬虫核心
- `config.json` - 配置文件（可修改数据源）
- `news_data/` - 数据存储目录
- `run_crawler.sh` - 运行脚本
- `setup_cron.sh` - 定时任务设置

## ⚙️ 配置自定义

### 1. 修改数据源
编辑 `config.json`：
```json
{
  "sources": {
    "tech": {
      "name": "3C数码",
      "keywords": ["你的关键词"],
      "rss_feeds": ["你的RSS源"]
    }
  }
}
```

### 2. 添加RSS源
- 36氪: https://36kr.com/feed
- 虎嗅: https://www.huxiu.com/rss  
- IT之家: https://www.ithome.com/rss
- 机器之心: https://www.jiqizhixin.com/rss

### 3. 使用API搜索（可选）
```bash
# 设置Tavily API Key
export TAVILY_API_KEY="your_api_key"

# 使用API模式运行
python3 news_crawler.py --mode api
```

## 🔧 高级功能

### 数据库支持
爬虫自动创建SQLite数据库 (`news_data/news.db`)，可查询历史数据。

### 多模式运行
```bash
# RSS模式（默认）
python3 news_crawler.py --mode rss

# API模式（需要TAVILY_API_KEY）
python3 news_crawler.py --mode api

# 混合模式
python3 news_crawler.py --mode all

# 不使用缓存
python3 news_crawler.py --no-cache
```

### 数据分析
```bash
# 查看数据统计
python3 -c "
import json
with open('news_data/news_data.json', 'r') as f:
    data = json.load(f)
print(f'文章总数: {len(data[\"data\"][\"tech\"]) + len(data[\"data\"][\"ai\"])}')
"

# 导出为CSV
python3 -c "
import json, csv
with open('news_data/news_data.json', 'r') as f:
    data = json.load(f)

with open('news_data/export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['分类', '标题', '来源', '时间', 'URL'])
    for cat in ['tech', 'ai']:
        for article in data['data'][cat]:
            writer.writerow([cat, article['title'][:50], article['source'], article['time'], article['url']])
print('✅ 导出到: news_data/export.csv')
"
```

## 🌐 网络要求

- RSS模式：需要能访问RSS源（可能需要网络代理）
- API模式：需要TAVILY_API_KEY和网络连接
- 本地运行：爬虫运行后，HTML文件可完全离线使用

## 🔒 隐私与安全

- 所有数据在本地处理
- 不收集用户信息
- 可完全离线使用
- 开源透明，可审计代码

## 🆘 常见问题

### Q: 爬虫运行失败
A: 检查网络连接，或修改config.json中的RSS源

### Q: 数据不更新
A: 删除 `news_data/cache.json` 强制刷新

### Q: 如何添加新分类？
A: 在config.json的sources中添加新分类配置

### Q: 支持中文搜索吗？
A: 是的，关键词和RSS源都支持中文

## 📞 技术支持

问题反馈或功能建议：
- 通过白月AI助理
- 检查 `cron.log` 错误日志
- 运行 `python3 news_crawler.py --setup` 重新初始化

---

**版本**: 2.0 (2026-04-01)
**维护**: 白月AI助理
**许可**: 开源，自由使用和修改
```

echo "✅ 安装完成！"
echo ""
echo "🎯 下一步操作："
echo "1. 运行爬虫获取数据: ./run_crawler.sh"
echo "2. 打开仪表板: open dashboard_latest.html"
echo "3. (可选)设置自动更新: ./setup_cron.sh"
echo ""
echo "📁 工作目录: $WORK_DIR"
echo "📖 详细说明: cat README.md"
echo ""
echo "🚀 享受您的专属科技资讯仪表板！"