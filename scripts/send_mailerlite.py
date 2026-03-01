import sys
import os
import subprocess
import requests

# 强制立即刷新输出，便于 GitHub Actions 查看日志
print("=== 脚本开始执行 ===", flush=True)

# 读取环境变量
api_key = os.getenv('MAILERLITE_API_KEY')
repo_name = os.getenv('REPO')  # 格式如 zhr-0731/zhr-0731.github.io

print(f"当前工作目录: {os.getcwd()}", flush=True)
print(f"环境变量 MAILERLITE_API_KEY 是否存在: {'是' if api_key else '否'}", flush=True)
if not api_key:
    print("错误: MAILERLITE_API_KEY 未设置", flush=True)
    sys.exit(1)

print(f"环境变量 REPO: {repo_name}", flush=True)

# 新版 API 基础地址
API_BASE = 'https://connect.mailerlite.com/api'
# 你的列表 ID（由用户提供）
LIST_ID = 180728062626760088

def get_new_posts():
    """通过 git diff 获取本次推送新增的 post 文件夹下的文件"""
    try:
        # 比较 HEAD~1 和 HEAD，只列出新增文件 (--diff-filter=A)
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            # HEAD~1 不存在（例如首次提交），则无法比较，直接认为无新增
            print("git diff 返回错误，可能没有上一次提交。退出。", flush=True)
            return []

        output = result.stdout.strip()
        if not output:
            return []
        files = output.split('\n')
        print(f"git diff 检测到的新增文件: {files}", flush=True)
        # 只保留 post/ 开头的文件
        posts = [f for f in files if f.startswith('post/')]
        print(f"新增的文章: {posts}", flush=True)
        return posts
    except Exception as e:
        print(f"执行 git diff 失败: {e}", flush=True)
        return []

def extract_post_info(post_path):
    """读取文章文件，提取标题和摘要"""
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print("成功读取文章内容", flush=True)
    except Exception as e:
        print(f"读取文章失败: {e}", flush=True)
        return None, None, None

    # 简单提取标题：文件名去掉 .md 或 .html，替换中划线为空格，首字母大写
    base = os.path.basename(post_path)
    name, ext = os.path.splitext(base)
    title = name.replace('-', ' ').title()

    # 摘要：取前200个字符（可优化为去除 Markdown 标记，但简单起见直接取纯文本）
    summary = content[:200].replace('\n', ' ') + '...'

    # 构造文章 URL（假设你的博客部署在 GitHub Pages）
    # 根据你的仓库名，你的博客地址为 https://zhr-0731.github.io
    base_url = "https://zhr-0731.github.io"
    # 文章链接：/post/文件名.html（注意扩展名转换）
    article_url = f"{base_url}/post/{name}.html"
    print(f"标题: {title}", flush=True)
    print(f"文章 URL: {article_url}", flush=True)
    return title, summary, article_url

def send_mailerlite_campaign(title, summary, article_url):
    """调用 MailerLite API 创建并发送 campaign"""
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
        "lists": [LIST_ID],
        "content": {
            "html": html_content,
            "plain": summary
        }
        # 如果需要指定发件人，可以添加以下字段（从后台默认设置中获取）
        # "from_email": "your-email@example.com",
        # "from_name": "你的博客名称"
    }

    print("正在创建 campaign...", flush=True)
    try:
        resp = requests.post(f"{API_BASE}/campaigns", json=campaign_data, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        print(f"API 响应: {result}", flush=True)
        # 新版返回格式为 {"data": {"id": "..."}}
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
        print("邮件已发送至所有订阅者！", flush=True)
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

    # 只处理第一篇新增文章（可根据需要改为循环处理多篇）
    post_path = new_posts[0]
    print(f"处理文章: {post_path}", flush=True)

    title, summary, article_url = extract_post_info(post_path)
    if not title:
        sys.exit(1)

    success = send_mailerlite_campaign(title, summary, article_url)
    if not success:
        sys.exit(1)

    print("=== 脚本执行完毕 ===", flush=True)

if __name__ == '__main__':
    main()
