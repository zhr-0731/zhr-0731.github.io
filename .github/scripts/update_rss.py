import os
import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from xml.dom import minidom

# ==================== 配置区域（请根据你的博客修改）====================
BLOG_TITLE = "zhr的博客"                     # RSS 频道标题
BLOG_URL = "https://zhr-0731.github.io"      # 博客首页地址
BLOG_DESCRIPTION = "分享技术、生活和思考"      # 博客描述
FAVICON_URL = "https://s41.ax1x.com/2025/12/07/pZnSiid.png"  # 网站图标 URL
REPO_OWNER = "zhr-0731"                       # GitHub 用户名
REPO_NAME = "zhr-0731.github.io"              # 仓库名
POST_FOLDER = "post"                           # 存放文章的文件夹
STATE_FILE = ".github/scripts/last_state.json" # 状态记录文件
RSS_FILE = "rss.xml"                           # 输出的 RSS 文件名
GITHUB_TOKEN = os.environ.get("GH_TOKEN")      # 从环境变量读取 token
# =====================================================================

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

def parse_article_from_html(html_url):
    """
    从 HTML 文件的 raw 内容中解析出文章信息
    返回: (title, pub_date, excerpt, tags, author)
    """
    try:
        raw_response = requests.get(html_url)
        soup = BeautifulSoup(raw_response.text, 'html.parser')

        # 1. 标题
        title_tag = soup.find('h1', class_='article-title')
        title = title_tag.text.strip() if title_tag else os.path.basename(html_url).replace('.html', '')

        # 2. 发布日期（优先取 datetime 属性）
        date_tag = soup.find('time')
        if date_tag and date_tag.has_attr('datetime'):
            pub_date = date_tag['datetime']  # 如 "2025-12-06"
        elif date_tag:
            # 尝试从文本中提取日期（示例："2025年12月6日" → "2025-12-06"）
            date_text = date_tag.text.strip()
            # 简单替换，可根据实际情况增强
            pub_date = date_text.replace('年', '-').replace('月', '-').replace('日', '')
        else:
            pub_date = datetime.now().strftime("%Y-%m-%d")

        # 3. 文章摘要
        excerpt_tag = soup.find('p', class_='article-excerpt')
        excerpt = excerpt_tag.text.strip() if excerpt_tag else ""

        # 4. 标签/分类
        tag_tags = soup.find_all('a', class_='article-tag')
        tags = [tag.text.strip() for tag in tag_tags]

        # 5. 作者（固定为 "zhr"，也可从页面提取）
        author = "zhr"  # 你可以修改为动态提取，例如从作者链接中获取

        return title, pub_date, excerpt, tags, author

    except Exception as e:
        print(f"Error parsing {html_url}: {e}")
        # 降级方案：使用文件名和当前日期
        filename = os.path.basename(html_url).replace('.html', '')
        return filename, datetime.now().strftime("%Y-%m-%d"), "", [], "zhr"

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
    """
    # 定义命名空间（用于 dc:creator）
    ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')

    if os.path.exists(RSS_FILE):
        # 解析现有 RSS 文件
        tree = ET.parse(RSS_FILE)
        root = tree.getroot()
        channel = root.find('channel')
    else:
        # 创建新的 RSS 结构
        root = ET.Element('rss', version='2.0', xmlns_dc="http://purl.org/dc/elements/1.1/")
        channel = ET.SubElement(root, 'channel')
        ET.SubElement(channel, 'title').text = BLOG_TITLE
        ET.SubElement(channel, 'link').text = BLOG_URL
        ET.SubElement(channel, 'description').text = BLOG_DESCRIPTION
        ET.SubElement(channel, 'language').text = 'zh-CN'

        # 添加网站图标（image 元素）
        image = ET.SubElement(channel, 'image')
        ET.SubElement(image, 'url').text = FAVICON_URL
        ET.SubElement(image, 'title').text = BLOG_TITLE
        ET.SubElement(image, 'link').text = BLOG_URL

        tree = ET.ElementTree(root)

    # 获取已存在的文章链接，避免重复
    existing_links = set()
    for item in channel.findall('item'):
        link = item.find('link')
        if link is not None and link.text:
            existing_links.add(link.text)

    # 将新文章（确保不重复）添加到 RSS 顶部（最新的在前）
    new_items = []
    for article in new_articles:
        if article['link'] not in existing_links:
            item = ET.Element('item')

            ET.SubElement(item, 'title').text = article['title']
            ET.SubElement(item, 'link').text = article['link']
            ET.SubElement(item, 'description').text = article['description']
            ET.SubElement(item, 'guid', isPermaLink="true").text = article['link']
            ET.SubElement(item, 'pubDate').text = article['pub_date']

            # 添加作者 (dc:creator)
            creator = ET.SubElement(item, '{http://purl.org/dc/elements/1.1/}creator')
            creator.text = article['author']

            # 添加分类
            for tag in article['tags']:
                cat = ET.SubElement(item, 'category')
                cat.text = tag

            new_items.append(item)

    # 将新 items 插入到 channel 的最前面
    if new_items:
        first_item = channel.find('item')
        if first_item is not None:
            index = list(channel).index(first_item)
            # 逆序插入以保证最新的文章在最前面
            for item in reversed(new_items):
                channel.insert(index, item)
        else:
            # 如果没有现有 item，直接追加
            for item in new_items:
                channel.append(item)

    # 漂亮的格式化输出
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')

    with open(RSS_FILE, 'wb') as f:
        f.write(pretty_xml)

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
                'html_url': f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main/{item['path']}"
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
        title, pub_date, excerpt, tags, author = parse_article_from_html(file_info['download_url'])
        article_data = {
            'title': title,
            'link': f"{BLOG_URL}/{file_info['path']}",  # 假设可以直接通过路径访问
            'pub_date': pub_date,
            'description': excerpt,
            'tags': tags,
            'author': author
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
