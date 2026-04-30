# 3C数码行业实时资讯系统

一个实时收录和展示3C数码行业资讯的网页应用，包含前端展示页面和后端API服务器。

## 功能特性

- 📱 **实时资讯展示**：展示最新的3C数码行业新闻
- 🏷️ **智能分类**：按手机平板、电脑硬件、人工智能、智能家居、游戏电竞分类
- 🔄 **自动刷新**：支持手动刷新和定时更新
- 📊 **数据统计**：显示资讯来源和分类统计
- 🌐 **响应式设计**：适配各种屏幕尺寸
- 🚀 **RESTful API**：提供完整的API接口

## 文件结构

```
.
├── 3c-news.html          # 前端展示页面
├── api_server.py         # Flask API服务器
├── fetch_3c_news.py      # 资讯获取脚本
└── README.md            # 说明文档
```

## 快速开始

### 1. 启动API服务器

```bash
python3 api_server.py
```

服务器启动后访问：
- http://localhost:5000/ - API文档
- http://localhost:5000/3c-news - 3C资讯页面
- http://localhost:5000/api/news - 新闻数据API

### 2. 使用资讯获取脚本

```bash
python3 fetch_3c_news.py
```

## API接口

### 获取所有新闻
```
GET /api/news
参数：limit (可选，默认20)
```

### 按分类获取新闻
```
GET /api/news/<category>
参数：limit (可选，默认10)
分类：mobile, computer, ai, iot, gaming
```

### 获取所有分类
```
GET /api/categories
```

### 获取所有来源
```
GET /api/sources
```

### 刷新新闻（模拟）
```
POST /api/refresh
```

### 获取统计信息
```
GET /api/stats
```

## 前端功能

### 主要特性
- **分类筛选**：点击分类按钮筛选不同类别的资讯
- **实时更新**：显示最后更新时间，支持手动刷新
- **响应式布局**：自适应手机、平板和桌面设备
- **平滑动画**：卡片悬停效果和刷新动画
- **通知系统**：操作成功提示

### 使用说明
1. 打开 `3c-news.html` 或访问 `http://localhost:5000/3c-news`
2. 使用顶部分类按钮筛选资讯
3. 点击右下角刷新按钮获取最新资讯
4. 点击资讯卡片查看详情（模拟）

## 数据源

系统支持从以下科技网站获取资讯（模拟）：
- TechCrunch
- The Verge
- CNET
- Engadget
- GSMArena
- Tom's Hardware
- AnandTech
- Ars Technica

## 技术栈

### 前端
- HTML5 / CSS3
- JavaScript (原生)
- 响应式设计
- CSS Grid / Flexbox

### 后端
- Python 3
- Flask (Web框架)
- RESTful API设计
- CORS支持

### 数据
- 模拟数据生成
- JSON格式存储
- 实时时间戳

## 扩展开发

### 添加真实数据源
1. 修改 `fetch_3c_news.py` 中的 `sources` 字典
2. 实现对应网站的解析逻辑
3. 配置定时任务自动获取

### 添加新分类
1. 在 `api_server.py` 的 `categories` 列表中添加
2. 在前端 `3c-news.html` 中添加对应按钮
3. 更新分类映射关系

### 部署到生产环境
1. 使用 Gunicorn 或 uWSGI 部署Flask应用
2. 配置Nginx反向代理
3. 设置SSL证书
4. 配置数据库（如MySQL、PostgreSQL）

## 配置说明

### 修改端口
编辑 `api_server.py`：
```python
app.run(host='0.0.0.0', port=8080, debug=False)  # 修改端口号
```

### 修改数据源
编辑 `fetch_3c_news.py`：
```python
self.sources = {
    'new_source': 'https://new-source.com/tech-news',
    # 添加更多数据源
}
```

### 自定义样式
编辑 `3c-news.html` 中的CSS部分，修改：
- 颜色主题
- 字体设置
- 布局样式
- 动画效果

## 注意事项

1. 当前版本使用模拟数据，实际部署时需要配置真实数据源
2. 生产环境请关闭调试模式：`debug=False`
3. 建议添加用户认证和API限流
4. 定期备份数据
5. 遵守各数据源的使用条款

## 许可证

本项目仅供学习和演示使用，请遵守相关法律法规。

## 联系方式

如有问题或建议，请通过OpenClaw联系开发者。

---

**最后更新：2025年3月**