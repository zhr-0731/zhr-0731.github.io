import sys
import os
import subprocess
import requests

print("=== 脚本开始执行 ===", flush=True)

api_key = os.getenv('MAILERLITE_API_KEY')
repo_name = os.getenv('REPO')
test_email = os.getenv('TEST_EMAIL')  # 从 Secrets 读取测试邮箱

print(f"当前工作目录: {os.getcwd()}", flush=True)
print(f"环境变量 MAILERLITE_API_KEY 是否存在: {'是' if api_key else '否'}", flush=True)
if not api_key:
    print("错误: MAILERLITE_API_KEY 未设置", flush=True)
    sys.exit(1)

if not test_email:
    print("错误: TEST_EMAIL 未设置，请在 Secrets 中添加你的邮箱", flush=True)
    sys.exit(1)

print(f"环境变量 REPO: {repo_name}", flush=True)
print(f"测试邮箱: {test_email}", flush=True)

API_BASE = 'https://connect.mailerlite.com/api'

def get_new_posts():
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD~1', 'HEAD'],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            print("git diff 返回错误，可能没有上一次提交。退出。", flush=True)
            return []
        output = result.stdout.strip()
        if not output:
            return []
        files = output.split('\n')
        print(f"git diff 检测到的新增文件: {files}", flush=True)
        posts = [f for f in files if f.startswith('post/')]
        print(f"新增的文章: {posts}", flush=True)
        return posts
    except Exception as e:
        print(f"执行 git diff 失败: {e}", flush=True)
        return []

def extract_post_info(post_path):
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print("成功读取文章内容", flush=True)
    except Exception as e:
        print(f"读取文章失败: {e}", flush=True)
        return None, None, None

    base = os.path.basename(post_path)
    name, ext = os.path.splitext(base)
    title = name.replace('-', ' ').title()
    summary = content[:200].replace('\n', ' ') + '...'
    base_url = "https://zhr-0731.github.io"
    article_url = f"{base_url}/post/{name}.html"
    print(f"标题: {title}", flush=True)
    print(f"文章 URL: {article_url}", flush=True)
    return title, summary, article_url

def send_test_email(title, summary, article_url):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    html_content = f"""
<h1>{title}</h1>
<p>{summary}</p>
<p><a href="{article_url}">阅读全文</a></p>
"""

    campaign_data = {
        "name": f"博客更新：{title}",
        "subject": f"博客更新：{title}",
        "type": "regular",
        "emails": [test_email],          # 直接发送给自己
        "content": {
            "html": html_content,
            "plain": summary
        }
    }

    print("正在创建 campaign...", flush=True)
    print(f"请求数据: {campaign_data}", flush=True)
    try:
        resp = requests.post(f"{API_BASE}/campaigns", json=campaign_data, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        print(f"API 响应: {result}", flush=True)
        campaign_id = result['data']['id']
        print(f"Campaign 创建成功，ID: {campaign_id}", flush=True)
    except Exception as e:
        print(f"创建 campaign 失败: {e}", flush=True)
        if 'resp' in locals():
            print(f"响应内容: {resp.text}", flush=True)
        return False

    print("正在发送 campaign...", flush=True)
    try:
        send_resp = requests.post(f"{API_BASE}/campaigns/{campaign_id}/actions/send", headers=headers)
        send_resp.raise_for_status()
        print("邮件已发送至测试邮箱！", flush=True)
        return True
    except Exception as e:
        print(f"发送 campaign 失败: {e}", flush=True)
        if 'send_resp' in locals():
            print(f"响应内容: {send_resp.text}", flush=True)
        return False

def main():
    new_posts = get_new_posts()
    if not new_posts:
        print("没有新增文章，脚本正常退出", flush=True)
        sys.exit(0)

    post_path = new_posts[0]
    print(f"处理文章: {post_path}", flush=True)

    title, summary, article_url = extract_post_info(post_path)
    if not title:
        sys.exit(1)

    success = send_test_email(title, summary, article_url)
    if not success:
        sys.exit(1)

    print("=== 脚本执行完毕 ===", flush=True)

if __name__ == '__main__':
    main()
