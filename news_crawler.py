#!/usr/bin/env python3
"""
白月科技资讯爬虫 - 全栈控制版本
支持多种数据源，完全本地运行，用户自主控制
"""

import json
import os
import sys
import time
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# 尝试导入可选依赖
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  未安装requests，部分功能受限")

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False
    print("⚠️  未安装feedparser，RSS功能不可用")

class NewsCrawler:
    """科技资讯爬虫核心类"""
    
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.data_dir = Path(self.config.get("data_dir", "./news_data"))
        self.data_dir.mkdir(exist_ok=True)
        
        # 数据缓存
        self.cache = {}
        self.cache_file = self.data_dir / "cache.json"
        
        # 数据库连接（可选）
        self.db_path = self.data_dir / "news.db"
        self.init_database()
    
    def load_config(self, config_path: str = None) -> Dict:
        """加载配置文件"""
        default_config = {
            "data_dir": "./news_data",
            "sources": {
                "tech": {
                    "name": "3C数码",
                    "keywords": ["智能手机", "电脑硬件", "消费电子", "数码配件", "苹果", "华为", "小米", "三星"],
                    "rss_feeds": [
                        "https://36kr.com/feed",
                        "https://www.huxiu.com/rss",
                        "https://www.ithome.com/rss"
                    ]
                },
                "ai": {
                    "name": "AI人工智能",
                    "keywords": ["人工智能", "AI", "机器学习", "大语言模型", "GPT", "OpenAI", "英伟达", "芯片"],
                    "rss_feeds": [
                        "https://www.jiqizhixin.com/rss",
                        "https://www.leiphone.com/feed"
                    ]
                }
            },
            "crawler": {
                "max_articles": 10,
                "cache_hours": 24,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            "output": {
                "json_file": "news_data.json",
                "html_file": "news_dashboard.html",
                "update_frequency": 3600  # 1小时
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并配置
                default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
        
        return default_config
    
    def init_database(self):
        """初始化SQLite数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建新闻表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    summary TEXT,
                    category TEXT NOT NULL,
                    publish_date TEXT,
                    crawl_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    content_hash TEXT
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON news_articles(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON news_articles(publish_date)')
            
            conn.commit()
            conn.close()
            print(f"✅ 数据库初始化完成: {self.db_path}")
            
        except Exception as e:
            print(f"⚠️  数据库初始化失败: {e}")
    
    def crawl_rss_feeds(self) -> Dict[str, List[Dict]]:
        """爬取RSS源"""
        if not HAS_FEEDPARSER:
            print("❌ 未安装feedparser，请运行: pip install feedparser")
            return {}
        
        results = {"tech": [], "ai": []}
        
        for category, cat_config in self.config["sources"].items():
            print(f"\n📡 爬取 {cat_config['name']} RSS源...")
            
            for rss_url in cat_config.get("rss_feeds", []):
                try:
                    print(f"  处理: {rss_url}")
                    feed = feedparser.parse(rss_url)
                    
                    for entry in feed.entries[:5]:  # 每个源取5条
                        article = {
                            "title": entry.get("title", ""),
                            "source": self.get_source_from_url(rss_url),
                            "url": entry.get("link", ""),
                            "summary": entry.get("summary", entry.get("description", ""))[:200],
                            "time": self.format_time(entry.get("published", "")),
                            "category": category
                        }
                        
                        # 检查是否包含关键词
                        if self.contains_keywords(article, cat_config["keywords"]):
                            results[category].append(article)
                            
                except Exception as e:
                    print(f"  ❌ RSS解析失败 {rss_url}: {e}")
        
        return results
    
    def crawl_web_search(self, use_api: bool = False) -> Dict[str, List[Dict]]:
        """通过web搜索获取资讯（需要API或手动配置）"""
        results = {"tech": [], "ai": []}
        
        if use_api and HAS_REQUESTS:
            # 使用Tavily API（需要配置API Key）
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                print("⚠️  未设置TAVILY_API_KEY环境变量")
                return results
            
            for category, cat_config in self.config["sources"].items():
                print(f"\n🔍 API搜索 {cat_config['name']}...")
                
                for keyword in cat_config["keywords"][:3]:  # 每个分类取前3个关键词
                    try:
                        response = requests.post(
                            "https://api.tavily.com/search",
                            json={
                                "api_key": api_key,
                                "query": f"{keyword} 最新消息 2026",
                                "search_depth": "basic",
                                "max_results": 5
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            for result in data.get("results", []):
                                article = {
                                    "title": result.get("title", ""),
                                    "source": "Tavily搜索",
                                    "url": result.get("url", ""),
                                    "summary": result.get("content", "")[:200],
                                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "category": category
                                }
                                results[category].append(article)
                        
                    except Exception as e:
                        print(f"  ❌ API搜索失败 {keyword}: {e}")
        
        else:
            print("\nℹ️  Web搜索模式需要：")
            print("   1. 设置TAVILY_API_KEY环境变量")
            print("   2. 运行: pip install requests")
            print("   或使用浏览器手动搜索并保存结果")
        
        return results
    
    def get_source_from_url(self, url: str) -> str:
        """从URL提取来源名称"""
        domain_map = {
            "36kr.com": "36氪",
            "huxiu.com": "虎嗅",
            "ithome.com": "IT之家",
            "jiqizhixin.com": "机器之心",
            "leiphone.com": "雷峰网",
            "qq.com": "腾讯新闻",
            "sina.com": "新浪科技",
            "sohu.com": "搜狐科技"
        }
        
        for domain, name in domain_map.items():
            if domain in url:
                return name
        
        return "网络来源"
    
    def format_time(self, time_str: str) -> str:
        """格式化时间字符串"""
        if not time_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
        
        try:
            # 尝试解析各种时间格式
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"]:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    return dt.strftime("%Y-%m-%d %H:%M")
                except:
                    continue
            
            # 如果都无法解析，返回原始字符串前部分
            return time_str[:16]
            
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def contains_keywords(self, article: Dict, keywords: List[str]) -> bool:
        """检查文章是否包含关键词"""
        text = f"{article['title']} {article['summary']}".lower()
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        return False
    
    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """去重文章"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    def save_to_database(self, articles: List[Dict]):
        """保存到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for article in articles:
                cursor.execute('''
                    INSERT OR IGNORE INTO news_articles 
                    (title, source, url, summary, category, publish_date, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article["title"],
                    article["source"],
                    article["url"],
                    article["summary"],
                    article["category"],
                    article["time"],
                    hash(f"{article['title']}{article['url']}")  # 简单哈希
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ 保存 {len(articles)} 篇文章到数据库")
            
        except Exception as e:
            print(f"⚠️  数据库保存失败: {e}")
    
    def load_from_database(self, category: str = None, limit: int = 10) -> List[Dict]:
        """从数据库加载文章"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT title, source, url, summary, publish_date FROM news_articles"
            params = []
            
            if category:
                query += " WHERE category = ?"
                params.append(category)
            
            query += " ORDER BY publish_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            articles = []
            for row in rows:
                articles.append({
                    "title": row[0],
                    "source": row[1],
                    "url": row[2],
                    "summary": row[3],
                    "time": row[4] or datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "category": category or "general"
                })
            
            return articles
            
        except Exception as e:
            print(f"⚠️  数据库加载失败: {e}")
            return []
    
    def generate_html_dashboard(self, news_data: Dict[str, List[Dict]]):
        """生成HTML仪表板"""
        template_path = Path(__file__).parent / "apple_style_news_dashboard.html"
        output_path = self.data_dir / "news_dashboard_latest.html"
        
        if not template_path.exists():
            print(f"❌ 模板文件不存在: {template_path}")
            return
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 转换为JSON字符串供JavaScript使用
            news_json = json.dumps(news_data, ensure_ascii=False, indent=2)
            
            # 在HTML中注入数据
            script_injection = f"""
            <script>
            // 注入的爬虫数据
            const CRAWLER_DATA = {news_json};
            
            // 覆盖默认的刷新函数
            window.overrideRefreshData = function() {{
                if (CRAWLER_DATA && Object.keys(CRAWLER_DATA).length > 0) {{
                    renderNewsList('tech-news-list', CRAWLER_DATA.tech || []);
                    renderNewsList('ai-news-list', CRAWLER_DATA.ai || []);
                    
                    // 保存到本地存储
                    localStorage.setItem('news_dashboard_data', JSON.stringify(CRAWLER_DATA));
                    localStorage.setItem('news_dashboard_time', Date.now().toString());
                    
                    showNotification('已加载爬虫数据 (' + new Date().toLocaleString() + ')', 'success');
                    updateStatus('爬虫数据');
                }}
            }};
            
            // 页面加载时自动加载爬虫数据
            document.addEventListener('DOMContentLoaded', function() {{
                setTimeout(window.overrideRefreshData, 500);
            }});
            </script>
            """
            
            # 在</body>前插入脚本
            html_content = html_content.replace('</body>', script_injection + '\n</body>')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML仪表板已生成: {output_path}")
            print(f"   用浏览器打开此文件查看最新资讯")
            
        except Exception as e:
            print(f"❌ HTML生成失败: {e}")
    
    def save_json_data(self, news_data: Dict[str, List[Dict]]):
        """保存为JSON文件"""
        output_file = self.data_dir / self.config["output"]["json_file"]
        
        try:
            # 添加元数据
            data_with_meta = {
                "meta": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "source": "白月科技资讯爬虫"
                },
                "data": news_data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data_with_meta, f, ensure_ascii=False, indent=2)
            
            print(f"✅ JSON数据已保存: {output_file}")
            
        except Exception as e:
            print(f"❌ JSON保存失败: {e}")
    
    def run(self, mode: str = "rss", use_cache: bool = True):
        """运行爬虫"""
        print("=" * 60)
        print("🤖 白月科技资讯爬虫 v1.0")
        print("=" * 60)
        
        # 检查缓存
        if use_cache and self.cache_file.exists():
            cache_age = time.time() - os.path.getmtime(self.cache_file)
            cache_hours = self.config["crawler"]["cache_hours"]
            
            if cache_age < cache_hours * 3600:
                print(f"📁 使用缓存数据 ({int(cache_age/3600)}小时前)")
                try:
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        self.cache = json.load(f)
                    return self.cache
                except:
                    print("⚠️  缓存读取失败，重新爬取")
        
        # 执行爬取
        news_data = {"tech": [], "ai": []}
        
        if mode == "rss" and HAS_FEEDPARSER:
            rss_results = self.crawl_rss_feeds()
            news_data["tech"].extend(rss_results.get("tech", []))
            news_data["ai"].extend(rss_results.get("ai", []))
        
        if mode == "api" or mode == "all":
            api_results = self.crawl_web_search(use_api=True)
            news_data["tech"].extend(api_results.get("tech", []))
            news_data["ai"].extend(api_results.get("ai", []))
        
        # 去重和限制数量
        max_articles = self.config["crawler"]["max_articles"]
        for category in ["tech", "ai"]:
            news_data[category] = self.deduplicate_articles(news_data[category])
            news_data[category] = news_data[category][:max_articles]
        
        # 保存结果
        self.cache = news_data
        self.save_json_data(news_data)
        self.save_to_database(news_data["tech"] + news_data["ai"])
        self.generate_html_dashboard(news_data)
        
        # 保存缓存
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        print(f"\n📊 爬取完成:")
        print(f"   3C数码: {len(news_data['tech'])} 篇")
        print(f"   AI人工智能: {len(news_data['ai'])} 篇")
        print(f"   数据目录: {self.data_dir.absolute()}")
        
        return news_data

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='白月科技资讯爬虫')
    parser.add_argument('--mode', choices=['rss', 'api', 'all'], default='rss',
                       help='爬取模式: rss(RSS源), api(API搜索), all(全部)')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--no-cache', action='store_true', help='不使用缓存')
    parser.add_argument('--install-deps', action='store_true', help='安装依赖')
    parser.add_argument('--setup', action='store_true', help='初始设置')
    
    args = parser.parse_args()
    
    # 安装依赖
    if args.install_deps:
        print("🔧 安装依赖...")
        os.system("pip install requests feedparser")
        print("✅ 依赖安装完成")
        return
    
    # 初始设置
    if args.setup:
        print("🔧 初始设置向导")
        
        # 创建配置文件示例
        config_example = {
            "sources": {
                "tech": {
                    "name": "3C数码",
                    "keywords": ["苹果", "华为", "小米", "三星", "折叠屏", "5G"],
                    "rss_feeds": [
                        "https://36kr.com/feed",
                        "https://www.huxiu.com/rss",
                        "https://www.ithome.com/rss"
                    ]
                },
                "ai": {
                    "name": "AI人工智能", 
                    "keywords": ["AI", "人工智能", "大模型", "GPT", "芯片"],
                    "rss_feeds": [
                        "https://www.jiqizhixin.com/rss",
                        "https://www.leiphone.com/feed"
                    ]
                }
            },
            "output": {
                "json_file": "news_data.json",
                "html_file": "news_dashboard.html"
            }
        }
        
        config_path = Path.home() / ".news_crawler_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_example, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 配置文件已创建: {config_path}")
        print("📋 编辑此文件自定义数据源")
        return
    
    # 运行爬虫
    crawler = NewsCrawler(args.config)
    news_data = crawler.run(mode=args.mode, use_cache=not args.no_cache)
    
    # 显示摘要
    print("\n📰 最新资讯摘要:")
    for category, articles in news_data.items():
        if articles:
            print(f"\n{crawler.config['sources'][category]['name']}:")
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. {article['title'][:50]}... ({article['source']})")

if __name__ == "__main__":
    main()