import sys
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import html2text

print("=== Buttondown 脚本开始执行 ===", flush=True)

api_key = os.getenv('BUTTONDOWN_API_KEY')
repo_name = os.getenv('REPO')

print(f"当前工作目录: {os.getcwd()}", flush=True)
print(f"环境变量 BUTTONDOWN_API_KEY 是否存在: {'是' if api_key else '否'}", flush=True)
if not api_key:
    print("错误: BUTTONDOWN_API_KEY 未设置", flush=True)
    sys.exit(1)

print(f"环境变量 REPO: {repo_name}", flush=True)

API_BASE = 'https://api.buttondown.email/v1'

def get_new_posts():
    """通过 git diff 获取本次推送新增的 post 文件夹下的文件"""
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
    """从 HTML 文件中提取标题、摘要和正文"""
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            html = f.read()
        print("成功读取 HTML 内容", flush=True)
    except Exception as e:
        print(f"读取文件失败: {e}", flush=True)
        return None, None, None

    soup = BeautifulSoup(html, 'html.parser')

    # 提取标题
    title_tag = soup.find('h1', class_='article-title')
    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        # 回退到 <title> 标签
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "无标题"
    print(f"标题: {title}", flush=True)

    # 提取摘要
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        summary = meta_desc['content']
    else:
        # 取正文前200字符作为摘要
        content_div = soup.find('div', class_='article-content')
        if content_div:
            text = content_div.get_text(strip=True)
            summary = text[:200] + '...' if len(text) > 200 else text
        else:
            summary = ""
    print(f"摘要: {summary}", flush=True)

    # 提取正文 HTML（只保留 article-content 部分）
    content_div = soup.find('div', class_='article-content')
    if content_div:
        # 移除可能包含的脚本、样式等
        for script in content_div.find_all(['script', 'style']):
            script.decompose()
        body_html = str(content_div)
    else:
        body_html = "<p>文章内容无法提取</p>"

    # 构造文章 URL
    base_url = "https://zhr-0731.github.io"
    name = os.path.basename(post_path).replace('.html', '')
    article_url = f"{base_url}/post/{name}.html"
    print(f"文章 URL: {article_url}", flush=True)

    return title, summary, body_html, article_url

def send_buttondown_email(title, summary, body_html, article_url):
    """调用 Buttondown API 创建并发送邮件"""
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json',
    }

    # 构建邮件正文：将 HTML 正文转换为 Markdown（可选），或直接发送 HTML
    # Buttondown 的 body 字段支持 Markdown，也支持内嵌 HTML。我们选择发送 HTML 以获得更好格式保留。
    # 但为了兼容性，可以将 HTML 转换为 Markdown（使用 html2text）
    h = html2text.HTML2Text()
    h.ignore_links = False
    body_md = h.handle(body_html)

    # 添加阅读全文链接
    full_body = f"{body_md}\n\n---\n\n[阅读全文]({article_url})"

    email_data = {
        "subject": f"博客更新：{title}",
        "body": full_body,
        "publish": True,          # 立即发送
        # 可选：指定 newsletter ID，如果不指定则发送给所有订阅者
    }

    print("正在创建并发送邮件...", flush=True)
    print(f"请求数据: {email_data}", flush=True)

    try:
        resp = requests.post(f"{API_BASE}/emails", json=email_data, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        print(f"Buttondown 响应: {result}", flush=True)
        print("邮件已成功发送！", flush=True)
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}", flush=True)
        if 'resp' in locals():
            print(f"响应内容: {resp.text}", flush=True)
        return False

def main():
    new_posts = get_new_posts()
    if not new_posts:
        print("没有新增文章，脚本正常退出", flush=True)
        sys.exit(0)

    post_path = new_posts[0]
    print(f"处理文章: {post_path}", flush=True)

    title, summary, body_html, article_url = extract_post_info(post_path)
    if not title:
        sys.exit(1)

    success = send_buttondown_email(title, summary, body_html, article_url)
    if not success:
        sys.exit(1)

    print("=== 脚本执行完毕 ===", flush=True)

if __name__ == '__main__':
    main()
