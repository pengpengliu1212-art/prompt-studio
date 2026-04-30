#!/usr/bin/env python3
import json
import subprocess
import sys

# 读取Markdown文件内容
with open('/root/.openclaw/workspace/钢化膜商业计划书.md', 'r', encoding='utf-8') as f:
    markdown_content = f.read()

# 构建参数
params = {
    "title": "钢化膜公司商业计划书（300万预算版）",
    "mdx": markdown_content,
    "content_format": "markdown"
}

# 转换为JSON字符串
args_json = json.dumps(params, ensure_ascii=False)

# 调用mcporter
cmd = ["mcporter", "call", "tencent-docs.create_smartcanvas_by_mdx", "--args", args_json]
print(f"执行命令: {' '.join(cmd[:3])} ...")
print(f"参数长度: {len(args_json)} 字符")

result = subprocess.run(cmd, capture_output=True, text=True, cwd="/root/.openclaw/workspace/skills/tencent-docs")
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("返回码:", result.returncode)

# 解析结果
if result.returncode == 0:
    try:
        output = json.loads(result.stdout)
        if "file_id" in output and "url" in output:
            print(f"\n✅ 文档创建成功！")
            print(f"文件ID: {output['file_id']}")
            print(f"文档URL: {output['url']}")
            # 将URL保存到文件
            with open('/root/.openclaw/workspace/tdoc_url.txt', 'w') as f:
                f.write(output['url'])
        else:
            print(f"响应缺少必要字段: {output}")
    except json.JSONDecodeError:
        print(f"无法解析JSON响应: {result.stdout}")
else:
    print(f"命令执行失败")