# 《沧纪元》小说自动化宣发系统 - 部署指南

## 🎯 系统概述

本系统为您的科幻小说《沧纪元》在**番茄免费小说平台**设计的全自动推广解决方案。系统具有以下特点：

- **🍅 平台专精**：针对番茄免费小说平台优化
- **🤖 智能自动化**：自动发布、回复、互动、监控
- **📊 数据驱动**：实时监控推广效果，生成优化建议
- **🔧 全栈控制**：完全开源，您可完全掌控和修改
- **🔄 持续运行**：支持cron定时任务，7x24小时自动运行

## 📁 项目结构

```
novel_promotion/
├── config.yaml                    # 主配置文件
├── novel_promoter.py              # 主推广脚本
├── tomato_novel_automation.py     # 番茄小说平台自动化模块
├── requirements.txt               # Python依赖
├── run_promotion.sh               # 运行脚本
├── cron_setup.txt                 # Cron配置建议
├── data/                          # 数据存储目录
│   ├── promotion_state.json       # 推广状态
│   └── tomato/                    # 平台数据
└── SETUP_GUIDE.md                 # 本文件
```

## 🚀 快速开始

### 步骤1：环境准备

#### 1.1 安装Python 3.8+
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS
brew install python@3.9
```

#### 1.2 安装agent-browser（浏览器自动化核心）
```bash
# 方法1：使用npm安装（推荐）
npm install -g agent-browser
agent-browser install  # 下载Chromium浏览器

# 方法2：使用pnpm安装
pnpm add -g agent-browser
agent-browser install

# 验证安装
agent-browser --version
```

#### 1.3 安装Python依赖
```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 安装额外依赖（如果需要）
# pip install selenium beautifulsoup4 webdriver-manager
```

### 步骤2：配置系统

#### 2.1 编辑配置文件 `config.yaml`
```bash
# 使用文本编辑器打开
nano config.yaml
# 或
vim config.yaml
```

主要配置项：
- `novel`: 小说基本信息（标题、作者、简介、URL）
- `promotion`: 推广策略（时间表、渠道、内容策略）
- `automation`: 自动化设置（执行模式、安全限制）
- `monitoring`: 监控配置（指标、报告频率）

**重要**：确保`novel.url`是正确的番茄小说链接。

#### 2.2 测试基础功能
```bash
# 测试内容生成
python3 novel_promoter.py test

# 测试页面打开
python3 tomato_novel_automation.py --action open

# 测试完整推广周期（模拟模式）
python3 novel_promoter.py run
```

### 步骤3：设置自动化运行

#### 3.1 创建运行脚本
```bash
# 使脚本可执行
chmod +x run_promotion.sh

# 测试脚本
./run_promotion.sh
```

#### 3.2 设置定时任务（Cron）

查看建议的Cron配置：
```bash
cat cron_setup.txt
```

添加Cron任务：
```bash
# 编辑crontab
crontab -e

# 添加以下内容（根据实际情况调整路径）
*/30 * * * * cd /完整路径/novel_promotion && python3 novel_promoter.py run
0 9 * * * cd /完整路径/novel_promotion && python3 novel_promoter.py run --task morning
0 19 * * * cd /完整路径/novel_promotion && python3 novel_promoter.py run --task evening
```

#### 3.3 手动运行测试
```bash
# 单次运行
python3 novel_promoter.py run

# 持续运行模式（调试用）
python3 novel_promoter.py continuous --interval 30

# 生成报告
python3 novel_promoter.py report --period weekly
```

## 🔧 高级配置

### 1. 浏览器自动化配置

如果需要真实的浏览器自动化（非模拟模式）：

#### 1.1 配置agent-browser会话
```bash
# 保存登录状态（如果需要登录番茄账号）
agent-browser --session cangjiyuan open https://fanqienovel.com
# 手动登录后保存状态
agent-browser --session cangjiyuan state save auth.json
```

#### 1.2 修改自动化模式
编辑`config.yaml`：
```yaml
automation:
  execution:
    mode: "actual"  # 从simulation改为actual
```

### 2. 内容策略定制

#### 2.1 修改内容模板
编辑`novel_promoter.py`中的`generate_content`函数，或直接修改`config.yaml`中的`content_strategy`部分。

#### 2.2 添加自定义模板
```python
# 在templates字典中添加
"custom_type": [
    "您的模板1 {title} {author}",
    "您的模板2 {character} {hashtags}"
]
```

### 3. 推广渠道扩展

#### 3.1 添加社交媒体平台
修改`config.yaml`中的`channels`部分：
```yaml
channels:
  - name: "微博"
    actions: ["发布微博", "参与超话", "互动抽奖"]
    api_key: "您的API密钥"  # 如果需要API
```

#### 3.2 集成其他平台
创建新的自动化模块，参考`tomato_novel_automation.py`的结构。

## 📊 监控与优化

### 1. 查看推广效果

#### 1.1 实时日志
```bash
# 查看运行日志
tail -f novel_promotion.log

# 查看数据目录
ls -la data/
```

#### 1.2 生成报告
```bash
# 日报
python3 novel_promoter.py report --period daily

# 周报  
python3 novel_promoter.py report --period weekly

# 月报
python3 novel_promoter.py report --period monthly
```

报告包含：
- 推广次数统计
- 预计触达人数
- 内容类型分析
- 优化建议

### 2. 数据监控

系统自动监控：
- 📈 阅读量增长趋势
- 💬 评论互动情况
- ⭐ 收藏和推荐数据
- 👥 新读者增长

数据存储在`data/`目录下的JSON文件中。

## 🚨 故障排除

### 常见问题1：agent-browser安装失败
```bash
# 检查Node.js版本
node --version  # 需要Node.js 16+

# 尝试使用系统包管理器
# Ubuntu/Debian
sudo apt install -y chromium-browser
# 然后使用Selenium替代方案
```

### 常见问题2：Python依赖安装失败
```bash
# 使用清华源加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 常见问题3：Cron任务不执行
```bash
# 检查Cron服务状态
systemctl status cron  # Ubuntu/Debian
systemctl status crond # CentOS/RHEL

# 查看Cron日志
grep CRON /var/log/syslog  # Ubuntu/Debian
tail -f /var/log/cron      # CentOS/RHEL

# 测试Cron环境
# 在crontab中添加测试任务
* * * * * echo "test" >> /tmp/cron_test.log
```

### 常见问题4：页面无法访问
```bash
# 检查网络连接
ping changdunovel.com

# 检查代理设置
# 如果需要代理，配置环境变量
export HTTP_PROXY="http://your-proxy:port"
export HTTPS_PROXY="http://your-proxy:port"
```

## 🔒 安全与隐私

### 1. 账号安全
- 🔐 **不要**在配置文件中硬编码密码
- 🔑 使用环境变量存储敏感信息
- 📝 定期更新访问令牌

### 2. 数据保护
- 💾 所有数据存储在本地
- 🚫 不发送数据到外部服务器
- 🔄 定期备份数据目录

### 3. 合规使用
- ⚖️ 遵守番茄小说平台规则
- ⏱️ 设置合理的请求频率
- 📋 人工审核重要内容

## 🛠️ 开发与扩展

### 1. 代码结构
```
novel_promoter.py              # 主控制器
├── NovelPromoter类            # 核心逻辑
├── 内容生成模块
├── 任务调度模块
└── 报告生成模块

tomato_novel_automation.py    # 平台适配器
├── TomatoNovelAutomation类   # 平台专用逻辑
├── 浏览器自动化
├── 页面解析
└── 数据收集
```

### 2. 添加新功能

#### 2.1 新的推广渠道
1. 创建新的自动化类
2. 实现标准接口（post_comment, collect_metrics等）
3. 在主控制器中集成

#### 2.2 新的内容类型
1. 在`generate_content`函数中添加模板
2. 更新配置文件的`content_strategy`
3. 测试内容生成

#### 2.3 数据分析增强
1. 扩展`monitor_performance`方法
2. 添加新的数据源
3. 改进报告生成

### 3. 性能优化
```bash
# 启用缓存
# 减少不必要的页面加载
# 批量处理任务
# 异步执行IO操作
```

## 📞 支持与维护

### 1. 获取帮助
- 📖 查看本文档
- 🔍 检查错误日志 `novel_promotion.log`
- 🐛 查看GitHub Issues（如果有）

### 2. 更新系统
```bash
# 备份当前配置
cp config.yaml config.yaml.backup
cp -r data data.backup

# 获取更新
git pull origin main  # 如果使用Git

# 重新安装依赖
pip install -r requirements.txt --upgrade
```

### 3. 备份策略
```bash
# 每日备份脚本示例
#!/bin/bash
BACKUP_DIR="/backup/novel_promotion_$(date +%Y%m%d)"
cp -r /path/to/novel_promotion "$BACKUP_DIR"
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"
```

## 🎉 开始推广！

完成所有配置后，您的《沧纪元》小说将享受：

1. **⏰ 定时推广**：每天多个时间点自动发布内容
2. **🤝 智能互动**：自动回复读者评论
3. **📈 效果监控**：实时跟踪推广数据
4. **💡 优化建议**：基于数据的智能优化

**启动系统：**
```bash
# 首次完整运行
python3 novel_promoter.py run

# 设置自动化
python3 novel_promoter.py setup

# 开始持续推广
# （系统将通过Cron自动运行）
```

祝您的《沧纪元》在番茄小说平台大获成功！🚀

---

**版本**: 1.0  
**更新日期**: 2026-04-01  
**维护者**: 白月AI助理  
**技术支持**: 通过OpenClaw平台联系