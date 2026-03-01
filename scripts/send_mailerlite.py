import sys
print("=== 脚本开始执行 ===", flush=True)

import os
import subprocess
import requests

print(f"当前工作目录: {os.getcwd()}", flush=True)
api_key = os.getenv('MAILERLITE_API_KEY')
print(f"环境变量 MAILERLITE_API_KEY 是否存在: {'是' if api_key else '否'}", flush=True)
if not api_key:
    print("错误: MAILERLITE_API_KEY 未设置", flush=True)
    sys.exit(1)

REPO = os.getenv('REPO')
print(f"环境变量 REPO: {REPO}", flush=True)

API_BASE = 'https://api.mailerlite.com/api/v2'

# 使用 git diff 获取新增文件列表
try:
    # 获取上一次提交与当前提交之间新增的文件（包括重命名等，但这里只取新增）
    result = subprocess.run(
        ['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD~1', 'HEAD'],
        capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        # HEAD~1 可能不存在（首次提交），此时回退到列出所有 tracked 文件？但首次推送我们暂时不处理
        print(f"git diff 返回错误，可能没有上一次提交。错误: {result.stderr}", flush=True)
        # 尝试使用 git ls-files 获取所有文件？但会包括历史文件。为简单，直接退出
        print("可能是首次提交，无新增文件可检测", flush=True)
        sys.exit(0)

    new_files = result.stdout.strip().split('\n')
    if new_files == ['']:
        new_files = []
    print(f"git diff 检测到的新增文件: {new_files}", flush=True)

    # 筛选 post 文件夹下的文件
    new_posts = [f for f in new_files if f.startswith('post/')]
    print(f"新增的文章: {new_posts}", flush=True)

except Exception as e:
    print(f"执行 git diff 失败: {e}", flush=True)
    sys.exit(1)

if not new_posts:
    print("没有新增文章，脚本正常退出", flush=True)
    sys.exit(0)

# 处理第一篇新增文章
post_path = new_posts[0]
print(f"处理文章: {post_path}", flush=True)

try:
    with open(post_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print("成功读取文章内容", flush=True)
except Exception as e:
    print(f"读取文章失败: {e}", flush=True)
    sys.exit(1)

# 提取标题和摘要（可根据你的文章格式调整）
title = os.path.basename(post_path).replace('.md', '').replace('-', ' ').title()
summary = content[:200].replace('\n', ' ') + '...'
print(f"标题: {title}", flush=True)

# 构建文章 URL（请根据你的实际博客地址修改）
base_url = "https://zhr-0731.github.io"  # 你的 GitHub Pages 地址
article_url = f"{base_url}/post/{os.path.basename(post_path).replace('.md', '.html')}"
print(f"文章 URL: {article_url}", flush=True)

html_content = f"""
<h1>{title}</h1>
<p>{summary}</p>
<p><a href="{article_url}">阅读全文</a></p>
"""

# 调用 MailerLite API
headers = {
    'Content-Type': 'application/json',
    'X-MailerLite-ApiKey': api_key
}

campaign_data = {
    "name": f"博客更新：{title}",
    "subject": f"博客更新：{title}",
    "type": "regular",
    "groups": ["all"],  # 建议先改为测试组 ID 进行测试
    "content": {"html": html_content, "plain": summary}
}

print("正在创建 campaign...", flush=True)
try:
    resp = requests.post(f"{API_BASE}/campaigns", json=campaign_data, headers=headers)
    resp.raise_for_status()
    result = resp.json()
    print(f"API 响应: {result}", flush=True)
    campaign_id = result.get('data', {}).get('id') or result.get('id')
    print(f"Campaign 创建成功，ID: {campaign_id}", flush=True)
except Exception as e:
    print(f"创建 campaign 失败: {e}", flush=True)
    if 'resp' in locals():
        print(f"响应内容: {resp.text}", flush=True)
    sys.exit(1)

print("正在发送 campaign...", flush=True)
try:
    send_resp = requests.post(f"{API_BASE}/campaigns/{campaign_id}/send", headers=headers)
    send_resp.raise_for_status()
    print("邮件已发送至所有订阅者！", flush=True)
except Exception as e:
    print(f"发送 campaign 失败: {e}", flush=True)
    if 'send_resp' in locals():
        print(f"响应内容: {send_resp.text}", flush=True)
    sys.exit(1)

print("=== 脚本执行完毕 ===", flush=True)
