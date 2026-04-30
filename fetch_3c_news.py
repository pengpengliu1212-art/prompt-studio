#!/usr/bin/env python3
"""
3C数码资讯获取脚本
用于从各大科技网站获取最新资讯
"""

import json
import random
import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time

class TechNewsFetcher:
    """3C数码资讯获取器"""
    
    def __init__(self):
        self.sources = {
            'techcrunch': 'https://techcrunch.com/category/gadgets/',
            'theverge': 'https://www.theverge.com/tech',
            'cnet': 'https://www.cnet.com/tech/',
            'engadget': 'https://www.engadget.com/',
            'gsmarena': 'https://www.gsmarena.com/news.php3',
            'tomshardware': 'https://www.tomshardware.com/news',
            'anandtech': 'https://www.anandtech.com/',
            'arstechnica': 'https://arstechnica.com/gadgets/'
        }
        
        self.categories = {
            'mobile': ['手机', '平板', '智能手机', '折叠屏', '5G'],
            'computer': ['电脑', '笔记本', '台式机', 'CPU', 'GPU', '内存', '硬盘'],
            'ai': ['人工智能', 'AI', '机器学习', '深度学习', 'GPT'],
            'iot': ['智能家居', '物联网', '智能设备', '智能音箱'],
            'gaming': ['游戏', '电竞', '游戏机', '显卡', '游戏本']
        }
        
    def fetch_news_from_source(self, source_name: str, url: str) -> List[Dict]:
        """从指定来源获取新闻"""
        news_list = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 模拟解析不同网站的新闻
            # 在实际应用中，需要为每个网站编写特定的解析逻辑
            for i in range(3):  # 模拟获取3条新闻
                news = {
                    'id': f"{source_name}_{int(time.time())}_{i}",
                    'title': self._generate_mock_title(source_name),
                    'excerpt': self._generate_mock_excerpt(),
                    'category': random.choice(list(self.categories.keys())),
                    'source': source_name.capitalize(),
                    'time': self._get_relative_time(i),
                    'image': self._get_mock_image(),
                    'url': f"https://{source_name}.com/article/{int(time.time())}_{i}"
                }
                news_list.append(news)
                
        except Exception as e:
            print(f"从 {source_name} 获取新闻失败: {e}")
            
        return news_list
    
    def _generate_mock_title(self, source: str) -> str:
        """生成模拟新闻标题"""
        prefixes = ['最新', '重磅', '独家', '突发', '深度']
        subjects = ['苹果', '三星', '华为', '小米', '英伟达', 'AMD', '英特尔', '微软', '谷歌']
        actions = ['发布', '推出', '泄露', '曝光', '宣布', '确认']
        products = ['iPhone', 'Galaxy', 'Mate', 'Mi', 'RTX', 'Ryzen', 'Core', 'Surface', 'Pixel']
        features = ['AI功能', '折叠屏', '5G网络', '长续航', '高性能', '轻薄设计']
        
        title = f"{random.choice(prefixes)}：{random.choice(subjects)}{random.choice(actions)}{random.choice(products)}"
        
        if random.random() > 0.5:
            title += f"，{random.choice(features)}全面升级"
        
        return title
    
    def _generate_mock_excerpt(self) -> str:
        """生成模拟新闻摘要"""
        sentences = [
            "据最新消息，该产品将在下个月正式发布。",
            "性能相比上一代提升超过30%，功耗进一步降低。",
            "采用了全新的设计语言，更加符合现代审美。",
            "支持最新的技术标准，为用户带来更好的体验。",
            "价格方面预计会有小幅上涨，但性价比依然突出。",
            "首批上市地区包括中国、美国和欧洲主要国家。",
            "预购活动将于本周五正式开启，限量发售。"
        ]
        
        return ''.join(random.sample(sentences, random.randint(2, 4)))
    
    def _get_relative_time(self, index: int) -> str:
        """获取相对时间"""
        hours_ago = index * 2 + 1
        return f"{hours_ago}小时前"
    
    def _get_mock_image(self) -> str:
        """获取模拟图片URL"""
        image_ids = [
            '1511707171634-5f897ff02aa9',
            '1620712943543-bcc4688e7485',
            '1496181133206-80ce9b88a853',
            '1558618666-fcd25c85cd64',
            '1606144042614-b2417e99c4e3',
            '1512941937669-90a1b58e7e9c',
            '1587202372634-32705e3bf49c',
            '1677442136019-21780ecad995'
        ]
        
        image_id = random.choice(image_ids)
        return f"https://images.unsplash.com/photo-{image_id}?w=400&h=200&fit=crop"
    
    def get_all_news(self, limit: int = 20) -> List[Dict]:
        """获取所有新闻"""
        all_news = []
        
        print("开始获取3C数码资讯...")
        
        for source_name, url in self.sources.items():
            print(f"正在从 {source_name} 获取资讯...")
            news = self.fetch_news_from_source(source_name, url)
            all_news.extend(news)
            
            # 避免请求过于频繁
            time.sleep(0.5)
        
        # 按时间排序（模拟）
        all_news.sort(key=lambda x: int(x['id'].split('_')[1]), reverse=True)
        
        # 限制数量
        return all_news[:limit]
    
    def get_news_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """按分类获取新闻"""
        all_news = self.get_all_news(limit * 3)
        
        # 过滤分类
        filtered_news = [news for news in all_news if news['category'] == category]
        
        return filtered_news[:limit]
    
    def save_to_json(self, news_list: List[Dict], filename: str = '3c_news.json'):
        """保存新闻到JSON文件"""
        data = {
            'last_updated': datetime.datetime.now().isoformat(),
            'total_news': len(news_list),
            'news': news_list
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(news_list)} 条新闻到 {filename}")
        
    def generate_api_response(self) -> Dict:
        """生成API响应格式"""
        news = self.get_all_news(15)
        
        return {
            'status': 'success',
            'timestamp': datetime.datetime.now().isoformat(),
            'data': {
                'news': news,
                'categories': list(self.categories.keys()),
                'sources': list(self.sources.keys())
            }
        }


def main():
    """主函数"""
    fetcher = TechNewsFetcher()
    
    # 获取所有新闻
    print("\n=== 获取最新3C数码资讯 ===")
    all_news = fetcher.get_all_news(12)
    
    # 显示新闻
    print(f"\n共获取 {len(all_news)} 条新闻：")
    for i, news in enumerate(all_news, 1):
        print(f"{i}. [{news['category']}] {news['title']} - {news['source']} ({news['time']})")
    
    # 保存到文件
    fetcher.save_to_json(all_news)
    
    # 生成API响应
    api_response = fetcher.generate_api_response()
    print(f"\nAPI响应示例：")
    print(json.dumps(api_response, ensure_ascii=False, indent=2)[:500] + "...")
    
    # 按分类获取
    print("\n=== 按分类获取 ===")
    for category in fetcher.categories.keys():
        category_news = fetcher.get_news_by_category(category, 3)
        print(f"{category}: {len(category_news)} 条")


if __name__ == "__main__":
    main()