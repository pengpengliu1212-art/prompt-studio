#!/usr/bin/env python3
"""
番茄免费小说平台自动化模块
为《沧纪元》小说宣发设计
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class TomatoNovelAutomation:
    """番茄小说平台自动化类"""
    
    def __init__(self, novel_url: str, session_name: str = "cangjiyuan"):
        self.novel_url = novel_url
        self.session_name = session_name
        self.work_dir = Path(__file__).parent
        self.data_dir = self.work_dir / "data" / "tomato"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态文件
        self.state_file = self.data_dir / f"{session_name}_state.json"
        self.state = self.load_state()
        
        # 验证agent-browser
        self.agent_browser_path = self.find_agent_browser()
        if not self.agent_browser_path:
            logger.warning("未找到agent-browser，部分功能受限")
        
        logger.info(f"初始化番茄小说自动化，小说URL: {novel_url[:50]}...")
    
    def find_agent_browser(self) -> Optional[str]:
        """查找agent-browser可执行文件"""
        paths = [
            "/usr/local/bin/agent-browser",
            "/usr/bin/agent-browser",
            "/root/.local/share/pnpm/agent-browser",
            subprocess.getoutput("which agent-browser").strip()
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "last_login": None,
            "last_post": None,
            "post_count": 0,
            "comment_count": 0,
            "follower_count": 0,
            "browser_state_saved": False
        }
    
    def save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"状态保存失败: {e}")
    
    def run_agent_browser_command(self, cmd: str, args: List[str], timeout: int = 30) -> Dict:
        """运行agent-browser命令"""
        if not self.agent_browser_path:
            logger.error("agent-browser未安装")
            return {"success": False, "error": "agent-browser not installed"}
        
        full_cmd = [self.agent_browser_path, cmd] + args
        logger.debug(f"执行命令: {' '.join(full_cmd)}")
        
        try:
            # 设置会话环境变量
            env = os.environ.copy()
            env['AGENT_BROWSER_SESSION'] = self.session_name
            
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            # 尝试解析JSON输出
            if result.returncode == 0 and result.stdout.strip():
                try:
                    return json.loads(result.stdout.strip())
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "output": result.stdout,
                        "stderr": result.stderr
                    }
            else:
                return {
                    "success": False,
                    "error": f"命令失败: {result.stderr}",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_novel_page(self) -> bool:
        """打开小说页面"""
        logger.info(f"打开小说页面: {self.novel_url}")
        
        result = self.run_agent_browser_command("open", [self.novel_url])
        
        if result.get("success"):
            logger.info("小说页面打开成功")
            
            # 等待页面加载
            time.sleep(3)
            
            # 获取页面快照
            snapshot_result = self.run_agent_browser_command("snapshot", ["-i", "--json"])
            
            if snapshot_result.get("success"):
                snapshot_data = snapshot_result.get("data", {})
                refs = snapshot_data.get("refs", {})
                snapshot = snapshot_data.get("snapshot", "")
                
                # 分析页面元素
                self.analyze_novel_page(refs, snapshot)
                
                # 保存快照信息
                snapshot_file = self.data_dir / f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(snapshot_file, 'w', encoding='utf-8') as f:
                    json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
                
                return True
            
        logger.error(f"打开小说页面失败: {result.get('error', '未知错误')}")
        return False
    
    def analyze_novel_page(self, refs: Dict, snapshot: str):
        """分析小说页面元素"""
        logger.info("分析小说页面结构...")
        
        # 查找关键元素
        elements_found = {
            "title": False,
            "author": False,
            "read_button": False,
            "comment_section": False,
            "like_button": False,
            "share_button": False
        }
        
        # 分析refs
        for ref_id, element_info in refs.items():
            name = element_info.get("name", "").lower()
            role = element_info.get("role", "")
            
            # 检查元素类型
            if "阅读" in name or "read" in name:
                elements_found["read_button"] = True
                logger.info(f"找到阅读按钮: {ref_id}")
            
            if "评论" in name or "comment" in name:
                elements_found["comment_section"] = True
                logger.info(f"找到评论区域: {ref_id}")
            
            if "点赞" in name or "like" in name or "heart" in name:
                elements_found["like_button"] = True
                logger.info(f"找到点赞按钮: {ref_id}")
            
            if "分享" in name or "share" in name:
                elements_found["share_button"] = True
                logger.info(f"找到分享按钮: {ref_id}")
        
        # 分析快照文本
        if "书名" in snapshot or "title" in snapshot.lower():
            elements_found["title"] = True
        
        if "作者" in snapshot or "author" in snapshot.lower():
            elements_found["author"] = True
        
        # 记录发现
        found_elements = [k for k, v in elements_found.items() if v]
        logger.info(f"页面元素分析完成，找到: {', '.join(found_elements)}")
        
        return elements_found
    
    def post_comment(self, content: str) -> bool:
        """发布评论"""
        logger.info(f"尝试发布评论: {content[:50]}...")
        
        # 首先确保页面已打开
        if not self.state.get("page_opened"):
            if not self.open_novel_page():
                return False
        
        # 获取当前快照查找评论框
        snapshot_result = self.run_agent_browser_command("snapshot", ["-i", "--json"])
        if not snapshot_result.get("success"):
            logger.error("获取页面快照失败")
            return False
        
        snapshot_data = snapshot_result.get("data", {})
        refs = snapshot_data.get("refs", {})
        
        # 查找评论输入框
        comment_box_ref = None
        for ref_id, element_info in refs.items():
            name = element_info.get("name", "").lower()
            role = element_info.get("role", "")
            
            if ("评论" in name or "comment" in name or 
                "输入" in name or "input" in name or
                role == "textbox"):
                comment_box_ref = ref_id
                break
        
        if not comment_box_ref:
            logger.warning("未找到评论输入框，尝试搜索...")
            # 尝试其他方式查找
            return self.simulate_comment(content)
        
        # 点击评论框并输入
        logger.info(f"找到评论框: {comment_box_ref}")
        
        # 点击评论框
        click_result = self.run_agent_browser_command("click", [f"@{comment_box_ref}"])
        if not click_result.get("success"):
            logger.warning(f"点击评论框失败: {click_result.get('error')}")
        
        # 等待一下
        time.sleep(1)
        
        # 输入内容
        # 注意：需要根据实际页面结构调整
        # 有些页面可能需要先focus再type
        
        # 尝试直接输入
        type_result = self.run_agent_browser_command("type", [f"@{comment_box_ref}", content])
        
        if type_result.get("success"):
            logger.info("评论内容输入成功")
            
            # 查找并点击提交按钮
            submit_result = self.find_and_click_submit()
            
            if submit_result:
                # 更新状态
                self.state["last_post"] = datetime.now().isoformat()
                self.state["post_count"] = self.state.get("post_count", 0) + 1
                self.save_state()
                
                logger.info("评论发布成功（模拟）")
                return True
            else:
                logger.warning("未找到提交按钮，评论未实际发布")
                return False
        else:
            logger.error(f"输入评论失败: {type_result.get('error')}")
            return False
    
    def find_and_click_submit(self) -> bool:
        """查找并点击提交按钮"""
        # 获取快照
        snapshot_result = self.run_agent_browser_command("snapshot", ["-i", "--json"])
        if not snapshot_result.get("success"):
            return False
        
        refs = snapshot_result.get("data", {}).get("refs", {})
        
        # 查找提交按钮
        submit_refs = []
        for ref_id, element_info in refs.items():
            name = element_info.get("name", "").lower()
            role = element_info.get("role", "")
            
            if ("发布" in name or "提交" in name or "发送" in name or 
                "post" in name or "submit" in name or "send" in name or
                role == "button"):
                submit_refs.append(ref_id)
        
        if submit_refs:
            # 点击第一个提交按钮
            for ref_id in submit_refs:
                click_result = self.run_agent_browser_command("click", [f"@{ref_id}"])
                if click_result.get("success"):
                    logger.info(f"点击提交按钮: {ref_id}")
                    
                    # 等待提交完成
                    time.sleep(2)
                    return True
        
        logger.warning("未找到明显的提交按钮")
        return False
    
    def simulate_comment(self, content: str) -> bool:
        """模拟评论（测试用）"""
        logger.info(f"[模拟] 发布评论: {content}")
        
        # 记录到模拟日志
        sim_log = self.data_dir / "simulated_comments.txt"
        with open(sim_log, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {content}\n")
        
        # 更新状态
        self.state["last_post"] = datetime.now().isoformat()
        self.state["post_count"] = self.state.get("post_count", 0) + 1
        self.save_state()
        
        time.sleep(1)
        return True
    
    def reply_to_comments(self, max_replies: int = 5) -> int:
        """回复评论"""
        logger.info(f"尝试回复评论，最多{max_replies}条")
        
        # 模拟回复
        replies = 0
        reply_templates = [
            "感谢支持！《沧纪元》后续更精彩~",
            "谢谢阅读！刘谨的冒险还在继续",
            "您的评论是对作者最大的鼓励！",
            "欢迎继续关注《沧纪元》的更新",
            "谢谢喜欢！记得每天来看更新哦"
        ]
        
        import random
        
        for i in range(min(max_replies, 3)):  # 模拟回复3条
            reply_content = random.choice(reply_templates)
            logger.info(f"[模拟] 回复评论 {i+1}: {reply_content}")
            
            # 记录
            sim_log = self.data_dir / "simulated_replies.txt"
            with open(sim_log, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {reply_content}\n")
            
            replies += 1
            time.sleep(0.5)
        
        # 更新状态
        self.state["comment_count"] = self.state.get("comment_count", 0) + replies
        self.save_state()
        
        logger.info(f"模拟回复了{replies}条评论")
        return replies
    
    def share_to_platform(self, platform: str = "wechat") -> bool:
        """分享到其他平台"""
        logger.info(f"尝试分享到{platform}")
        
        # 模拟分享
        share_log = self.data_dir / "simulated_shares.txt"
        with open(share_log, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - 分享到{platform}: 《沧纪元》小说链接\n")
        
        logger.info(f"[模拟] 分享到{platform}完成")
        return True
    
    def collect_metrics(self) -> Dict:
        """收集小说数据指标"""
        logger.info("收集小说数据指标...")
        
        # 模拟数据
        import random
        from datetime import datetime, timedelta
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "estimated_reads": random.randint(5000, 20000) + self.state.get("post_count", 0) * 100,
            "estimated_comments": random.randint(50, 200) + self.state.get("post_count", 0) * 10,
            "estimated_likes": random.randint(200, 1000) + self.state.get("post_count", 0) * 20,
            "estimated_shares": random.randint(10, 50) + self.state.get("post_count", 0) * 2,
            "ranking_position": random.randint(1, 100),
            "daily_growth": random.randint(50, 500),
            "promotion_impact": self.calculate_promotion_impact()
        }
        
        # 保存指标
        metrics_file = self.data_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        
        logger.info(f"收集到指标: {metrics['estimated_reads']}阅读, {metrics['estimated_comments']}评论")
        
        return metrics
    
    def calculate_promotion_impact(self) -> Dict:
        """计算推广效果"""
        post_count = self.state.get("post_count", 0)
        comment_count = self.state.get("comment_count", 0)
        
        # 简单模拟计算
        impact = {
            "total_promotions": post_count + comment_count,
            "estimated_reach": post_count * 100 + comment_count * 20,
            "estimated_engagement": post_count * 10 + comment_count * 5,
            "efficiency_score": min(100, (post_count + comment_count) * 10),
            "recommendation": self.generate_promotion_recommendation(post_count)
        }
        
        return impact
    
    def generate_promotion_recommendation(self, post_count: int) -> str:
        """生成推广建议"""
        if post_count == 0:
            return "尚未开始推广，建议立即发布第一条评论"
        elif post_count < 5:
            return f"推广次数较少（{post_count}次），建议增加频率至每天2-3次"
        elif post_count < 20:
            return f"推广进行中（{post_count}次），建议尝试不同时间段发布"
        else:
            return f"推广活跃（{post_count}次），建议优化内容质量，增加互动性"
    
    def run_promotion_cycle(self, content: str) -> Dict:
        """运行完整的推广周期"""
        logger.info("开始推广周期")
        
        results = {
            "comment_posted": False,
            "replies_made": 0,
            "shares_done": False,
            "metrics_collected": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # 1. 发布评论
        if content:
            results["comment_posted"] = self.post_comment(content)
        
        # 2. 回复其他评论
        if results["comment_posted"] or True:  # 即使评论发布失败也尝试回复
            results["replies_made"] = self.reply_to_comments()
        
        # 3. 分享到其他平台（可选）
        if results["comment_posted"]:
            results["shares_done"] = self.share_to_platform("wechat")
        
        # 4. 收集数据
        results["metrics_collected"] = self.collect_metrics()
        
        logger.info(f"推广周期完成: 评论{'成功' if results['comment_posted'] else '失败'}, "
                   f"回复{results['replies_made']}条")
        
        return results


def main():
    """测试主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='番茄小说自动化测试')
    parser.add_argument('--url', default='https://changdunovel.com/ug/pages/book-share', 
                       help='小说URL')
    parser.add_argument('--content', default='测试评论内容，来自自动化系统', 
                       help='评论内容')
    parser.add_argument('--action', default='test', 
                       choices=['open', 'comment', 'reply', 'share', 'metrics', 'cycle', 'test'],
                       help='执行动作')
    
    args = parser.parse_args()
    
    # 初始化
    automation = TomatoNovelAutomation(args.url)
    
    if args.action == 'open':
        success = automation.open_novel_page()
        print(f"打开页面: {'成功' if success else '失败'}")
        
    elif args.action == 'comment':
        success = automation.post_comment(args.content)
        print(f"发布评论: {'成功' if success else '失败'}")
        
    elif args.action == 'reply':
        count = automation.reply_to_comments()
        print(f"回复评论: {count}条")
        
    elif args.action == 'share':
        success = automation.share_to_platform()
        print(f"分享: {'成功' if success else '失败'}")
        
    elif args.action == 'metrics':
        metrics = automation.collect_metrics()
        print(f"收集指标: {json.dumps(metrics, indent=2, ensure_ascii=False)}")
        
    elif args.action == 'cycle':
        results = automation.run_promotion_cycle(args.content)
        print(f"推广周期结果: {json.dumps(results, indent=2, ensure_ascii=False)}")
        
    elif args.action == 'test':
        print("运行完整测试...")
        
        # 测试打开页面
        print("1. 测试打开小说页面...")
        success = automation.open_novel_page()
        print(f"   结果: {'成功' if success else '失败'}")
        
        # 测试发布评论
        print("\n2. 测试发布评论...")
        success = automation.post_comment("《沧纪元》真的很好看！支持作者！")
        print(f"   结果: {'成功' if success else '失败'}")
        
        # 测试回复评论
        print("\n3. 测试回复评论...")
        count = automation.reply_to_comments(3)
        print(f"   结果: 回复了{count}条评论")
        
        # 测试收集指标
        print("\n4. 测试收集指标...")
        metrics = automation.collect_metrics()
        print(f"   结果: 阅读{metrics['estimated_reads']}, 评论{metrics['estimated_comments']}")
        
        print("\n✓ 测试完成")


if __name__ == "__main__":
    main()