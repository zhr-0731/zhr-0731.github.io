import os
import requests
from git import Repo

# 环境变量
API_KEY = os.getenv('MAILERLITE_API_KEY')  # 你存在 Secret 中的密钥（不以 ml_ 开头）
REPO = os.getenv('REPO')
# 经典版 API 基础地址
API_BASE = 'https://api.mailerlite.com/api/v2'

# 获取本次新增的文章
repo = Repo('.')
commits = list(repo.iter_commits('HEAD~1..HEAD'))
if not commits:
    exit(0)

diff = commits[0].diff(commits[0].parents[0] if commits[0].parents else None)
new_posts = [d.a_path for d in diff if d.a_path.startswith('post/') and d.change_type == 'A']

if not new_posts:
    print("没有新增文章，退出")
    exit(0)

# 处理第一篇新增文章（可改为多篇汇总）
post_path = new_posts[0]
with open(post_path, 'r', encoding='utf-8') as f:
    content = f.read()
    # 提取标题（假设文件名就是标题，或从内容解析）
    title = os.path.basename(post_path).replace('.md', '').replace('-', ' ').title()
    # 提取前200字作为摘要
    summary = content[:200].replace('\n', ' ') + '...'

# 构建文章 URL
base_url = f"https://{REPO.replace('.github.io', '')}"
article_url = f"{base_url}/post/{os.path.basename(post_path).replace('.md', '.html')}"

# 构造邮件 HTML 内容
html_content = f"""
<h1>{title}</h1>
<p>{summary}</p>
<p><a href="{article_url}">阅读全文</a></p>
"""

def send_mailerlite_campaign():
    headers = {
        'Content-Type': 'application/json',
        'X-MailerLite-ApiKey': API_KEY   # 经典版使用相同的头
    }

    # 1. 创建 Campaign
    campaign_data = {
        "name": f"博客更新：{title}",
        "subject": f"博客更新：{title}",
        "type": "regular",                # 经典版也支持 regular
        "groups": ["all"],                 # 发送给所有订阅者，或指定组ID
        "content": {
            "html": html_content,
            "plain": summary               # 纯文本版本
        }
    }

    # 经典版创建 campaign 的端点
    resp = requests.post(f"{API_BASE}/campaigns", json=campaign_data, headers=headers)
    resp.raise_for_status()
    campaign_id = resp.json()['data']['id']   # 经典版返回结构可能略有不同，需调试
    print(f"Campaign 创建成功，ID: {campaign_id}")

    # 2. 发送 Campaign（立即发送）
    send_resp = requests.post(f"{API_BASE}/campaigns/{campaign_id}/actions/send", headers=headers)
    send_resp.raise_for_status()
    print("邮件已发送至所有订阅者！")

if __name__ == '__main__':
    send_mailerlite_campaign()
