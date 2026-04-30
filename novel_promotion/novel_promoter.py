#!/usr/bin/env python3
"""
《沧纪元》小说自动化宣发系统
为番茄免费小说平台设计
作者：白月AI助理
"""

import os
import sys
import json
import yaml
import time
import random
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('novel_promotion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NovelPromoter:
    """小说推广自动化核心类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self.load_config(config_path)
        self.novel_info = self.config['novel']
        self.promotion_config = self.config['promotion']
        self.automation_config = self.config['automation']
        
        # 工作目录
        self.work_dir = Path(__file__).parent
        self.data_dir = self.work_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # 状态文件
        self.state_file = self.data_dir / "promotion_state.json"
        self.state = self.load_state()
        
        # 内容模板库
        self.templates = self.promotion_config['content_strategy']['templates']
        
        logger.info(f"初始化《{self.novel_info['title']}》推广系统")
        logger.info(f"作者：{self.novel_info['author']}")
    
    def load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def load_state(self) -> Dict:
        """加载状态文件"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "last_promotion": None,
            "promotion_count": 0,
            "engagement_stats": {},
            "scheduled_tasks": [],
            "content_history": []
        }
    
    def save_state(self):
        """保存状态文件"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"状态保存失败: {e}")
    
    def generate_content(self, content_type: str, **kwargs) -> str:
        """生成推广内容"""
        
        # 基础模板
        templates = {
            "daily_morning": [
                "🌅 早安，书友们！新的一天开始，《{title}》最新章已更新，{character}的{journey}进行中... {hashtags}",
                "☀️ 清晨第一缕阳光，最适合阅读《{title}》。今日更新：{chapter_preview} {hashtags}",
                "📚 早安阅读时间到！《{title}》等待你的探索。{author}带你进入{world}... {hashtags}"
            ],
            "chapter_update": [
                "📖 最新章更新！《{title}》第{chapter}章：{chapter_title}... {hashtags}",
                "✨ 新鲜出炉！《{title}》{chapter}章已更新，{plot_teaser} {hashtags}",
                "🔥 剧情加速！《{title}》{chapter}章带来{development}... {hashtags}"
            ],
            "character_analysis": [
                "🎭 角色深度解析：{character}的{aspect}。在《{title}》中，他/她面临着{challenge}... {hashtags}",
                "🤔 人物剖析：{character}为什么{action}？背后隐藏着{secret}... {hashtags}",
                "🌟 角色亮点：{character}的{quality}让人印象深刻。在{event}中他/她展现了{behavior}... {hashtags}"
            ],
            "world_building": [
                "🌌 世界观揭秘：《{title}》中的{world_element}。{description} {hashtags}",
                "🗺️ 故事舞台：探索《{title}》的{location}，这里发生着{events}... {hashtags}",
                "⚡ 设定解析：《{title}》独特的{system}系统，如何影响{character}的命运？ {hashtags}"
            ],
            "reader_interaction": [
                "💭 读者提问：如果你是{character}，会如何{decision}？评论区聊聊~ {hashtags}",
                "🤝 互动时间：你对《{title}》的{aspect}有什么看法？分享你的观点！ {hashtags}",
                "🎯 剧情预测：下一章会发生{what}？猜中有奖！ {hashtags}"
            ],
            "author_behind": [
                "✍️ 创作幕后：{author}分享创作{title}的{insight}... {hashtags}",
                "📝 作者笔记：关于{character}的设计灵感来自{inspiration}... {hashtags}",
                "🎨 创作心路：{author}谈{title}的{creative_process}... {hashtags}"
            ]
        }
        
        # 默认参数
        params = {
            "title": self.novel_info['title'],
            "author": self.novel_info['author'],
            "character": "刘谨",
            "journey": "逆转未来之旅",
            "world": "时间循环的科幻世界",
            "hashtags": " ".join([f"#{tag}" for tag in self.promotion_config['content_strategy']['hashtags'][:3]]),
            # 模板通用参数
            "chapter_preview": "火星战役真相逐渐浮出水面",
            "chapter": "最新",
            "chapter_title": "时间裂缝的抉择",
            "plot_teaser": "刘谨面临关键选择",
            "development": "剧情重大转折",
            "aspect": "性格特点",
            "challenge": "逆转未来的艰难任务",
            "action": "做出关键决定",
            "secret": "未揭晓的真相",
            "quality": "坚韧不拔",
            "event": "火星战役",
            "behavior": "英勇无畏",
            "world_element": "时间循环系统",
            "description": "一个可以改变过去未来的神秘机制",
            "location": "火星前线基地",
            "events": "时间悖论事件",
            "system": "昊天神帝天赋",
            "decision": "应对时间危机",
            "what": "意想不到的转折",
            "insight": "创作灵感",
            "inspiration": "科幻经典与东方哲学",
            "creative_process": "世界观构建",
            **kwargs
        }
        
        # 选择模板
        if content_type in templates:
            template = random.choice(templates[content_type])
        else:
            template = random.choice(templates["reader_interaction"])
        
        # 填充模板
        content = template.format(**params)
        
        # 记录生成的内容
        self.state["content_history"].append({
            "type": content_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"生成{content_type}内容: {content[:50]}...")
        return content
    
    def schedule_promotion(self):
        """安排推广任务"""
        
        schedule = self.promotion_config['schedule']
        now = datetime.now()
        
        tasks = []
        
        # 每日任务
        if 'daily' in schedule:
            for task in schedule['daily']:
                task_time = datetime.strptime(task['time'], "%H:%M")
                task_dt = datetime.combine(now.date(), task_time.time())
                
                # 如果今天的时间已过，安排到明天
                if task_dt < now:
                    task_dt += timedelta(days=1)
                
                tasks.append({
                    "action": task['action'],
                    "scheduled_time": task_dt.isoformat(),
                    "content_type": self.map_action_to_content_type(task['action'])
                })
        
        # 每周任务
        if 'weekly' in schedule:
            for task in schedule['weekly']:
                # 简化处理：安排到下个周一/周五
                tasks.append({
                    "action": task['action'],
                    "scheduled_time": f"每周{task['day']}",
                    "content_type": self.map_action_to_content_type(task['action'])
                })
        
        self.state["scheduled_tasks"] = tasks
        self.save_state()
        
        logger.info(f"安排了{len(tasks)}个推广任务")
        return tasks
    
    def map_action_to_content_type(self, action: str) -> str:
        """将动作映射到内容类型"""
        mapping = {
            "发布早安推文": "daily_morning",
            "发布午间阅读推荐": "chapter_update",
            "发布晚间更新提醒": "chapter_update",
            "发布睡前故事片段": "character_analysis",
            "发布周更总结": "world_building",
            "发布周末阅读预告": "reader_interaction"
        }
        return mapping.get(action, "reader_interaction")
    
    def check_and_execute_tasks(self):
        """检查并执行计划任务"""
        now = datetime.now()
        executed = []
        
        for task in self.state.get("scheduled_tasks", []):
            if isinstance(task['scheduled_time'], str) and ':' in task['scheduled_time']:
                try:
                    task_time = datetime.fromisoformat(task['scheduled_time'])
                    # 检查是否到了执行时间（允许±30分钟）
                    if abs((task_time - now).total_seconds()) <= 1800:
                        logger.info(f"执行任务: {task['action']}")
                        self.execute_promotion_task(task)
                        executed.append(task)
                except:
                    pass
        
        # 移除已执行的任务
        self.state["scheduled_tasks"] = [
            t for t in self.state["scheduled_tasks"] 
            if t not in executed
        ]
        
        if executed:
            self.save_state()
        
        return executed
    
    def execute_promotion_task(self, task: Dict):
        """执行推广任务"""
        content_type = task.get('content_type', 'reader_interaction')
        content = self.generate_content(content_type)
        
        # 更新状态
        self.state["last_promotion"] = datetime.now().isoformat()
        self.state["promotion_count"] = self.state.get("promotion_count", 0) + 1
        
        logger.info(f"执行推广: {task['action']}")
        logger.info(f"内容: {content}")
        
        # 根据配置选择执行方式
        if self.automation_config['execution']['mode'] == 'simulation':
            self.simulate_post(content)
        else:
            # 实际发布逻辑（需要具体实现）
            self.actual_post(content)
        
        return True
    
    def simulate_post(self, content: str):
        """模拟发布（测试用）"""
        logger.info(f"[模拟发布] {content}")
        
        # 记录到模拟日志
        sim_log = self.data_dir / "simulation_log.txt"
        with open(sim_log, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {content}\n")
        
        # 随机模拟互动
        time.sleep(1)
        
        return True
    
    def actual_post(self, content: str):
        """实际发布到平台（需要具体实现）"""
        # 这里需要实现具体的发布逻辑
        # 可能使用agent-browser自动化浏览器
        # 或调用平台API（如果有）
        
        logger.warning("实际发布功能尚未实现，当前为模拟模式")
        return self.simulate_post(content)
    
    def monitor_performance(self):
        """监控推广效果"""
        # 这里可以添加实际的数据监控逻辑
        # 例如：爬取小说页面数据
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "promotion_count": self.state.get("promotion_count", 0),
            "last_promotion": self.state.get("last_promotion"),
            "estimated_reach": random.randint(100, 1000) * self.state.get("promotion_count", 1),
            "estimated_engagement": random.randint(10, 100) * self.state.get("promotion_count", 1)
        }
        
        self.state["engagement_stats"][datetime.now().isoformat()] = stats
        
        logger.info(f"监控数据: 推广{stats['promotion_count']}次，预计触达{stats['estimated_reach']}人")
        
        return stats
    
    def generate_report(self, period: str = "daily") -> Dict:
        """生成推广报告"""
        
        if period == "daily":
            start_time = datetime.now() - timedelta(days=1)
        elif period == "weekly":
            start_time = datetime.now() - timedelta(days=7)
        elif period == "monthly":
            start_time = datetime.now() - timedelta(days=30)
        else:
            start_time = datetime.now() - timedelta(days=1)
        
        # 筛选时间段内的数据
        recent_stats = {}
        for ts, stats in self.state.get("engagement_stats", {}).items():
            try:
                stat_time = datetime.fromisoformat(ts)
                if stat_time >= start_time:
                    recent_stats[ts] = stats
            except:
                pass
        
        # 计算汇总
        total_promotions = sum(s.get("promotion_count", 0) for s in recent_stats.values())
        total_reach = sum(s.get("estimated_reach", 0) for s in recent_stats.values())
        total_engagement = sum(s.get("estimated_engagement", 0) for s in recent_stats.values())
        
        report = {
            "period": period,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_promotions": total_promotions,
            "total_estimated_reach": total_reach,
            "total_estimated_engagement": total_engagement,
            "average_reach_per_promotion": total_reach / max(total_promotions, 1),
            "content_types_used": list(set(
                c.get("type", "unknown") 
                for c in self.state.get("content_history", [])
                if datetime.fromisoformat(c.get("timestamp", "2000-01-01")) >= start_time
            )),
            "recommendations": self.generate_recommendations(recent_stats)
        }
        
        # 保存报告
        report_file = self.data_dir / f"report_{period}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"生成{period}报告: {total_promotions}次推广，触达{total_reach}人")
        
        return report
    
    def generate_recommendations(self, stats: Dict) -> List[str]:
        """根据数据生成优化建议"""
        recommendations = []
        
        if len(stats) < 3:
            recommendations.append("数据积累不足，建议持续推广至少3天后再进行优化分析")
        
        if self.state.get("promotion_count", 0) < 5:
            recommendations.append("推广次数较少，建议增加推广频率，尝试不同时间段发布")
        
        # 内容多样性建议
        content_types = set(
            c.get("type", "unknown") 
            for c in self.state.get("content_history", [])
        )
        if len(content_types) < 3:
            recommendations.append(f"内容类型较少（当前{len(content_types)}种），建议尝试更多类型：角色解析、世界观介绍、读者互动等")
        
        # 时间优化建议
        recommendations.append("建议记录每次推广的具体互动数据，以便优化发布时间")
        recommendations.append("可以尝试在读者活跃时段（晚间20-22点）增加互动内容")
        
        return recommendations
    
    def run_once(self):
        """单次运行：检查并执行任务"""
        logger.info("开始单次推广检查")
        
        # 检查并执行计划任务
        executed = self.check_and_execute_tasks()
        
        # 监控效果
        stats = self.monitor_performance()
        
        # 如果有执行任务，生成简要报告
        if executed:
            logger.info(f"本次执行了{len(executed)}个任务")
        
        return executed, stats
    
    def run_continuous(self, interval_minutes: int = 30):
        """持续运行模式"""
        logger.info(f"启动持续运行模式，检查间隔: {interval_minutes}分钟")
        
        try:
            while True:
                self.run_once()
                logger.info(f"等待{interval_minutes}分钟...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("收到停止信号，退出持续运行模式")
    
    def setup_automation(self):
        """设置自动化任务（如cron）"""
        logger.info("设置自动化任务...")
        
        # 创建运行脚本
        script_content = f'''#!/bin/bash
cd "{self.work_dir}"
python3 novel_promoter.py run
'''
        
        script_path = self.work_dir / "run_promotion.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        script_path.chmod(0o755)
        
        # 生成cron配置建议
        cron_suggestions = f'''
建议的cron配置（每30分钟检查一次）：
*/30 * * * * cd "{self.work_dir}" && python3 novel_promoter.py run

每日固定时间任务示例：
0 9 * * *   cd "{self.work_dir}" && python3 novel_promoter.py run --task morning
0 12 * * *  cd "{self.work_dir}" && python3 novel_promoter.py run --task noon
0 19 * * *  cd "{self.work_dir}" && python3 novel_promoter.py run --task evening
0 21 * * *  cd "{self.work_dir}" && python3 novel_promoter.py run --task night
'''
        
        logger.info(cron_suggestions)
        
        # 保存cron配置到文件
        cron_file = self.work_dir / "cron_setup.txt"
        with open(cron_file, 'w', encoding='utf-8') as f:
            f.write(cron_suggestions)
        
        return script_path, cron_suggestions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='《沧纪元》小说自动化宣发系统')
    parser.add_argument('action', nargs='?', default='run', 
                       choices=['run', 'schedule', 'report', 'setup', 'continuous', 'test'],
                       help='执行动作: run(单次运行), schedule(安排任务), report(生成报告), setup(设置自动化), continuous(持续运行), test(测试)')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--period', default='daily', choices=['daily', 'weekly', 'monthly'], 
                       help='报告周期（用于report动作）')
    parser.add_argument('--interval', type=int, default=30, 
                       help='持续运行检查间隔（分钟，用于continuous动作）')
    parser.add_argument('--task', help='指定任务类型执行')
    
    args = parser.parse_args()
    
    # 初始化推广器
    try:
        promoter = NovelPromoter(args.config)
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        return 1
    
    # 执行对应动作
    if args.action == 'run':
        executed, stats = promoter.run_once()
        print(f"✓ 执行完成: {len(executed)}个任务")
        
    elif args.action == 'schedule':
        tasks = promoter.schedule_promotion()
        print(f"✓ 已安排{len(tasks)}个推广任务")
        for task in tasks:
            print(f"  - {task['action']} @ {task['scheduled_time']}")
        
    elif args.action == 'report':
        report = promoter.generate_report(args.period)
        print(f"✓ {args.period}报告生成完成")
        print(f"  推广次数: {report['total_promotions']}")
        print(f"  预计触达: {report['total_estimated_reach']}人")
        print(f"  预计互动: {report['total_estimated_engagement']}次")
        print("\n优化建议:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
    elif args.action == 'setup':
        script_path, cron_suggestions = promoter.setup_automation()
        print(f"✓ 自动化设置完成")
        print(f"  运行脚本: {script_path}")
        print(cron_suggestions)
        
    elif args.action == 'continuous':
        promoter.run_continuous(args.interval)
        
    elif args.action == 'test':
        # 测试内容生成
        print("测试内容生成:")
        for content_type in ['daily_morning', 'chapter_update', 'character_analysis']:
            content = promoter.generate_content(content_type)
            print(f"\n{content_type}:")
            print(f"  {content}")
        
        print(f"\n✓ 测试完成")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())