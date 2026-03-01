import sys
print("=== 脚本开始执行 ===", flush=True)

import os
import requests
from git import Repo

print(f"当前工作目录: {os.getcwd()}", flush=True)
api_key = os.getenv('MAILERLITE_API_KEY')
print(f"环境变量 MAILERLITE_API_KEY 是否存在: {'是' if api_key else '否'}", flush=True)
if not api_key:
    print("错误: MAILERLITE_API_KEY 未设置", flush=True)
    sys.exit(1)

REPO = os.getenv('REPO')
print(f"环境变量 REPO: {REPO}", flush=True)

API_BASE = 'https://api.mailerlite.com/api/v2'

# 获取本次新增的文章
try:
    repo = Repo('.')
    print("成功打开 Git 仓库", flush=True)
except Exception as e:
    print(f"打开 Git 仓库失败: {e}", flush=True)
    sys.exit(1)

commits = list(repo.iter_commits('HEAD~1..HEAD'))
print(f"获取到 commits 数量: {len(commits)}", flush=True)

if not commits:
    print("没有找到 commits (可能只有一次提交)，退出", flush=True)
    sys.exit(0)

# 获取与上一次提交的差异
try:
    parent = commits[0].parents[0] if commits[0].parents else None
    diff = commits[0].diff(parent)
    print(f"差异文件列表: {[d.a_path for d in diff]}", flush=True)
except Exception as e:
    print(f"获取 diff 失败: {e}", flush=True)
    sys.exit(1)

new_posts = [d.a_path for d in diff if d.a_path.startswith('post/') and d.change_type == 'A']
print(f"新增的文章: {new_posts}", flush=True)

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
