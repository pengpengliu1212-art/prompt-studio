#!/usr/bin/env python3
"""
3C数码资讯API服务器
提供RESTful API接口获取最新资讯
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import datetime
import random
from typing import Dict, List
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模拟数据库
class NewsDatabase:
    """模拟新闻数据库"""
    
    def __init__(self):
        self.news_data = self._load_initial_data()
        self.categories = ['mobile', 'computer', 'ai', 'iot', 'gaming']
        self.sources = ['TechCrunch', 'The Verge', 'CNET', 'Engadget', 'GSMArena', "Tom's Hardware"]
    
    def _load_initial_data(self) -> List[Dict]:
        """加载初始数据"""
        return [
            {
                "id": "1",
                "title": "苹果发布iPhone 16系列：AI功能全面升级",
                "excerpt": "苹果最新发布的iPhone 16系列搭载了全新的A18芯片，AI处理能力提升40%，并引入了多项AI摄影功能...",
                "category": "mobile",
                "source": "TechCrunch",
                "time": "2小时前",
                "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=200&fit=crop",
                "url": "https://techcrunch.com/iphone-16-ai-features"
            },
            {
                "id": "2",
                "title": "英伟达发布新一代AI芯片，性能提升3倍",
                "excerpt": "英伟达在GTC大会上发布了新一代Blackwell架构AI芯片，专为大规模AI训练和推理设计...",
                "category": "ai",
                "source": "The Verge",
                "time": "4小时前",
                "image": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=400&h=200&fit=crop",
                "url": "https://www.theverge.com/nvidia-blackwell-ai-chips"
            },
            {
                "id": "3",
                "title": "微软Surface Pro 10发布：搭载骁龙X Elite",
                "excerpt": "微软最新Surface Pro 10搭载高通骁龙X Elite处理器，续航时间长达22小时，支持5G网络...",
                "category": "computer",
                "source": "CNET",
                "time": "6小时前",
                "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=200&fit=crop",
                "url": "https://www.cnet.com/surface-pro-10-review"
            },
            {
                "id": "4",
                "title": "小米智能家居生态再添新品：全屋智能控制中心",
                "excerpt": "小米发布全新智能家居控制中心，支持超过1000种智能设备，实现真正的全屋智能联动...",
                "category": "iot",
                "source": "Engadget",
                "time": "8小时前",
                "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=200&fit=crop",
                "url": "https://www.engadget.com/xiaomi-smart-home-hub"
            },
            {
                "id": "5",
                "title": "索尼PS5 Pro规格泄露：性能大幅提升",
                "excerpt": "据内部消息，索尼正在开发PS5 Pro，GPU性能预计提升45%，支持8K游戏和增强的光线追踪...",
                "category": "gaming",
                "source": "IGN",
                "time": "10小时前",
                "image": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400&h=200&fit=crop",
                "url": "https://www.ign.com/ps5-pro-leaks"
            },
            {
                "id": "6",
                "title": "华为鸿蒙Next正式版发布：完全脱离安卓",
                "excerpt": "华为正式发布鸿蒙Next操作系统，不再兼容安卓应用，标志着华为生态的完全独立...",
                "category": "mobile",
                "source": "华为官方",
                "time": "12小时前",
                "image": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=200&fit=crop",
                "url": "https://consumer.huawei.com/harmonyos-next"
            },
            {
                "id": "7",
                "title": "AMD锐龙9000系列处理器性能曝光",
                "excerpt": "AMD下一代锐龙9000系列处理器采用Zen 5架构，单核性能提升超过20%，功耗进一步优化...",
                "category": "computer",
                "source": "Tom's Hardware",
                "time": "14小时前",
                "image": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=400&h=200&fit=crop",
                "url": "https://www.tomshardware.com/amd-ryzen-9000-leak"
            },
            {
                "id": "8",
                "title": "OpenAI发布GPT-5：多模态能力全面升级",
                "excerpt": "OpenAI正式发布GPT-5，在推理能力、多模态理解和代码生成方面都有显著提升...",
                "category": "ai",
                "source": "OpenAI Blog",
                "time": "16小时前",
                "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=200&fit=crop",
                "url": "https://openai.com/blog/gpt-5"
            }
        ]
    
    def get_all_news(self, limit: int = 20) -> List[Dict]:
        """获取所有新闻"""
        return self.news_data[:limit]
    
    def get_news_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """按分类获取新闻"""
        filtered = [news for news in self.news_data if news['category'] == category]
        return filtered[:limit]
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return self.categories
    
    def get_sources(self) -> List[str]:
        """获取所有来源"""
        return self.sources
    
    def add_news(self, news: Dict) -> Dict:
        """添加新闻"""
        news['id'] = str(len(self.news_data) + 1)
        news['time'] = "刚刚"
        self.news_data.insert(0, news)
        return news
    
    def generate_mock_news(self) -> Dict:
        """生成模拟新闻"""
        categories = ['mobile', 'computer', 'ai', 'iot', 'gaming']
        titles = [
            "三星Galaxy Z Fold 6设计图泄露，更轻薄设计",
            "英特尔第15代酷睿处理器性能提升25%",
            "特斯拉推出全新智能家居产品线",
            "任天堂Switch 2确认支持4K游戏",
            "谷歌Pixel 9系列将搭载自研Tensor G4芯片",
            "Meta发布新一代VR头显，分辨率提升至8K",
            "戴尔发布全球最薄游戏本，厚度仅14mm",
            "联想ThinkPad X1 Carbon 2025款发布"
        ]
        
        return {
            "title": random.choice(titles),
            "excerpt": "据最新消息，该产品将在近期正式发布，性能相比上一代有显著提升...",
            "category": random.choice(categories),
            "source": random.choice(self.sources),
            "image": f"https://images.unsplash.com/photo-{random.randint(1510000000000, 1700000000000)}?w=400&h=200&fit=crop",
            "url": f"https://example.com/article/{random.randint(1000, 9999)}"
        }

# 初始化数据库
db = NewsDatabase()

@app.route('/')
def index():
    """首页"""
    return jsonify({
        "message": "3C数码资讯API服务器",
        "version": "1.0.0",
        "endpoints": {
            "/api/news": "获取所有新闻",
            "/api/news/<category>": "按分类获取新闻",
            "/api/categories": "获取所有分类",
            "/api/sources": "获取所有来源",
            "/api/refresh": "刷新新闻（模拟）",
            "/": "API文档"
        }
    })

@app.route('/api/news')
def get_news():
    """获取所有新闻"""
    limit = request.args.get('limit', default=20, type=int)
    news = db.get_all_news(limit)
    
    return jsonify({
        "status": "success",
        "timestamp": datetime.datetime.now().isoformat(),
        "data": {
            "news": news,
            "total": len(news)
        }
    })

@app.route('/api/news/<category>')
def get_news_by_category(category):
    """按分类获取新闻"""
    if category not in db.categories:
        return jsonify({
            "status": "error",
            "message": f"分类 '{category}' 不存在"
        }), 404
    
    limit = request.args.get('limit', default=10, type=int)
    news = db.get_news_by_category(category, limit)
    
    return jsonify({
        "status": "success",
        "timestamp": datetime.datetime.now().isoformat(),
        "data": {
            "category": category,
            "news": news,
            "total": len(news)
        }
    })

@app.route('/api/categories')
def get_categories():
    """获取所有分类"""
    categories = db.get_categories()
    
    # 获取每个分类的新闻数量
    category_stats = []
    for category in categories:
        news_count = len([n for n in db.news_data if n['category'] == category])
        category_stats.append({
            "id": category,
            "name": {
                "mobile": "手机平板",
                "computer": "电脑硬件",
                "ai": "人工智能",
                "iot": "智能家居",
                "gaming": "游戏电竞"
            }.get(category, category),
            "count": news_count
        })
    
    return jsonify({
        "status": "success",
        "data": {
            "categories": category_stats
        }
    })

@app.route('/api/sources')
def get_sources():
    """获取所有来源"""
    sources = db.get_sources()
    
    # 获取每个来源的新闻数量
    source_stats = []
    for source in sources:
        news_count = len([n for n in db.news_data if n['source'] == source])
        source_stats.append({
            "name": source,
            "count": news_count
        })
    
    return jsonify({
        "status": "success",
        "data": {
            "sources": source_stats
        }
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_news():
    """刷新新闻（模拟）"""
    # 生成一些新的模拟新闻
    new_news_count = random.randint(1, 3)
    new_news = []
    
    for _ in range(new_news_count):
        mock_news = db.generate_mock_news()
        added_news = db.add_news(mock_news)
        new_news.append(added_news)
    
    return jsonify({
        "status": "success",
        "message": f"成功添加 {len(new_news)} 条新资讯",
        "data": {
            "new_news": new_news,
            "total_news": len(db.news_data)
        }
    })

@app.route('/api/stats')
def get_stats():
    """获取统计信息"""
    total_news = len(db.news_data)
    
    # 按分类统计
    category_stats = {}
    for category in db.categories:
        count = len([n for n in db.news_data if n['category'] == category])
        category_stats[category] = count
    
    # 按来源统计
    source_stats = {}
    for source in db.sources:
        count = len([n for n in db.news_data if n['source'] == source])
        if count > 0:
            source_stats[source] = count
    
    return jsonify({
        "status": "success",
        "data": {
            "total_news": total_news,
            "categories": category_stats,
            "sources": source_stats,
            "last_updated": datetime.datetime.now().isoformat()
        }
    })

@app.route('/3c-news')
def serve_news_page():
    """提供3C资讯页面"""
    return send_from_directory('.', '3c-news.html')

if __name__ == '__main__':
    print("=== 3C数码资讯API服务器 ===")
    print("服务器启动中...")
    print(f"访问 http://localhost:5000/ 查看API文档")
    print(f"访问 http://localhost:5000/3c-news 查看3C资讯页面")
    print(f"访问 http://localhost:5000/api/news 获取新闻数据")
    print("\n按 Ctrl+C 停止服务器")
    
    app.run(host='0.0.0.0', port=5000, debug=True)