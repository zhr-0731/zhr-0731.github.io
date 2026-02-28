import os
import requests
import json
import time
import email.utils
from datetime import datetime
from bs4 import BeautifulSoup
from lxml import etree

# ==================== 配置区域 ====================
BLOG_TITLE = "zhr的博客"
BLOG_URL = "https://zhr-0731.github.io"
BLOG_DESCRIPTION = "分享技术、生活和思考"
FAVICON_URL = "https://s41.ax1x.com/2025/12/07/pZnSiid.png"
REPO_OWNER = "zhr-0731"
REPO_NAME = "zhr-0731.github.io"
POST_FOLDER = "post"
STATE_FILE = ".github/scripts/last_state.json"
RSS_FILE = "rss.xml"
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
# =================================================

def get_github_folder_contents(path):
    """调用 GitHub API 获取指定路径下的所有文件信息"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching contents: {response.status_code}")
        return None

def format_rfc822(date_str):
    """
    将 YYYY-MM-DD 格式的日期转换为 RFC-822 格式。
    例如：2025-12-06 -> Sat, 06 Dec 2025 00:00:00 +0000
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # 使用 UTC 时间 00:00，时区 +0000
        return email.utils.formatdate(dt.timestamp(), localtime=False)
    except Exception as e:
        print(f"Date format error: {e}, using current time")
        return email.utils.formatdate()

def parse_article_from_html(html_url):
    """
    从 HTML 文件的 raw 内容中解析出文章信息
    返回: (title, pub_date, excerpt, tags, author, content_html)
    """
    try:
        raw_response = requests.get(html_url)
        soup = BeautifulSoup(raw_response.text, 'html.parser')

        # 标题
        title_tag = soup.find('h1', class_='article-title')
        title = title_tag.text.strip() if title_tag else os.path.basename(html_url).replace('.html', '')

        # 发布日期（优先取 datetime 属性）
        date_tag = soup.find('time')
        if date_tag and date_tag.has_attr('datetime'):
            pub_date = date_tag['datetime']  # 如 "2025-12-06"
        elif date_tag:
            date_text = date_tag.text.strip()
            pub_date = date_text.replace('年', '-').replace('月', '-').replace('日', '')
        else:
            pub_date = datetime.now().strftime("%Y-%m-%d")

        # 文章摘要
        excerpt_tag = soup.find('p', class_='article-excerpt')
        excerpt = excerpt_tag.text.strip() if excerpt_tag else ""

        # 标签
        tag_tags = soup.find_all('a', class_='article-tag')
        tags = [tag.text.strip() for tag in tag_tags]

        # 作者
        author = "zhr"

        # 文首图
        header_image_html = ""
        header_figure = soup.find('figure', class_='article-image')
        if header_figure:
            header_image_html = str(header_figure)

        # 正文 HTML
        content_div = soup.find('div', class_='article-content')
        if content_div:
            content_html = content_div.decode_contents().strip()
        else:
            content_html = ""

        # 拼接：文首图 + 正文
        if header_image_html:
            content_html = header_image_html + content_html

        return title, pub_date, excerpt, tags, author, content_html

    except Exception as e:
        print(f"Error parsing {html_url}: {e}")
        filename = os.path.basename(html_url).replace('.html', '')
        return filename, datetime.now().strftime("%Y-%m-%d"), "", [], "zhr", ""

def load_previous_state():
    """加载上一次处理的状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_files": []}

def save_state(state):
    """保存当前处理的状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def update_rss_feed(new_articles):
    """
    将新文章添加到 RSS 文件中
    如果文件不存在则自动创建，并写入频道信息
    使用 lxml 支持 CDATA 和命名空间
    """
    # 定义命名空间（包含 atom，用于自链接）
    NSMAP = {
        'dc': 'http://purl.org/dc/elements/1.1/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'atom': 'http://www.w3.org/2005/Atom'
    }

    if os.path.exists(RSS_FILE):
        # 解析现有 RSS 文件
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(RSS_FILE, parser)
        root = tree.getroot()
        channel = root.find('channel')
    else:
        # 创建新的 RSS 结构
        root = etree.Element('rss', version='2.0', nsmap=NSMAP)
        channel = etree.SubElement(root, 'channel')
        etree.SubElement(channel, 'title').text = BLOG_TITLE
        etree.SubElement(channel, 'link').text = BLOG_URL
        etree.SubElement(channel, 'description').text = BLOG_DESCRIPTION
        etree.SubElement(channel, 'language').text = 'zh-CN'

        # 添加网站图标（image 元素）
        image = etree.SubElement(channel, 'image')
        etree.SubElement(image, 'url').text = FAVICON_URL
        etree.SubElement(image, 'title').text = BLOG_TITLE
        etree.SubElement(image, 'link').text = BLOG_URL

        # 添加 atom:link 自引用（提高互操作性）
        atom_link = etree.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
        atom_link.set('href', 'https://raw.githubusercontent.com/zhr-0731/zhr-0731.github.io/refs/heads/main/rss.xml')
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

        tree = etree.ElementTree(root)

    # 获取已存在的文章链接，避免重复
    existing_links = set()
    for item in channel.findall('item'):
        link = item.find('link')
        if link is not None and link.text:
            existing_links.add(link.text)

    # 将新文章添加到 RSS 中
    new_items = []
    for article in new_articles:
        if article['link'] not in existing_links:
            item = etree.SubElement(channel, 'item')

            etree.SubElement(item, 'title').text = article['title']
            etree.SubElement(item, 'link').text = article['link']
            etree.SubElement(item, 'description').text = article['description']  # 摘要
            etree.SubElement(item, 'guid', isPermaLink="true").text = article['link']

            # 修正 pubDate 为 RFC-822 格式
            pub_date_rfc822 = format_rfc822(article['pub_date'])
            etree.SubElement(item, 'pubDate').text = pub_date_rfc822

            # 作者 (dc:creator)
            creator = etree.SubElement(item, f'{{{NSMAP["dc"]}}}creator')
            creator.text = article['author']

            # 分类
            for tag in article['tags']:
                cat = etree.SubElement(item, 'category')
                cat.text = tag

            # 全文内容 (content:encoded)，使用 CDATA
            if article['content']:
                content_encoded = etree.SubElement(item, f'{{{NSMAP["content"]}}}encoded')
                content_encoded.text = etree.CDATA(article['content'])

            new_items.append(item)

    # 写入文件
    tree.write(RSS_FILE, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"Updated RSS feed with {len(new_items)} new articles.")

def main():
    print("Starting check for new posts...")

    # 1. 获取 post 文件夹下所有文件
    contents = get_github_folder_contents(POST_FOLDER)
    if not contents:
        print("Failed to get folder contents. Exiting.")
        return

    # 2. 只筛选出 HTML 文件，并记录信息
    current_files = {}
    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('.html'):
            file_info = {
                'name': item['name'],
                'path': item['path'],
                'download_url': item['download_url'],
            }
            current_files[item['name']] = file_info

    # 3. 加载上一次处理的状态
    state = load_previous_state()
    processed_files = set(state.get("processed_files", []))

    # 4. 找出新文件
    new_files = []
    for filename, info in current_files.items():
        if filename not in processed_files:
            new_files.append(info)

    if not new_files:
        print("No new posts found.")
        return

    print(f"Found {len(new_files)} new posts: {[f['name'] for f in new_files]}")

    # 5. 解析新文章的数据
    new_articles = []
    for file_info in new_files:
        title, pub_date, excerpt, tags, author, content_html = parse_article_from_html(file_info['download_url'])
        article_data = {
            'title': title,
            'link': f"{BLOG_URL}/{file_info['path']}",  # 假设可以通过路径访问
            'pub_date': pub_date,
            'description': excerpt,
            'tags': tags,
            'author': author,
            'content': content_html
        }
        new_articles.append(article_data)
        # 简单延时，避免请求过频
        time.sleep(1)

    # 6. 更新 RSS 文件
    update_rss_feed(new_articles)

    # 7. 更新状态：将新处理过的文件加入列表
    processed_files.update([f['name'] for f in new_files])
    state['processed_files'] = list(processed_files)
    save_state(state)

    print("Update completed successfully.")

if __name__ == "__main__":
    main()
