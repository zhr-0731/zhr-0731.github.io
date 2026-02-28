import os
import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from xml.dom import minidom

# --- 配置信息 ---
REPO_OWNER = "zhr-0731"
REPO_NAME = "zhr-0731.github.io"
POST_FOLDER = "post"
# 用于记录上一次处理的文件列表，可以是一个简单的 JSON 文件
STATE_FILE = ".github/scripts/last_state.json"
RSS_FILE = "rss.xml"
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
# 你的博客首页地址，用于生成完整的文章链接
BLOG_URL = "https://zhr-0731.github.io"

# --- 函数定义 ---

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
    """从 HTML 文件的 raw 内容中解析出文章标题和发布日期"""
    # 注意：这里需要根据你 post.html 的实际结构来写解析逻辑
    # 以下是一个示例，假设你的 HTML 中有 <title> 标签和 <meta name="date"> 标签
    try:
        raw_response = requests.get(html_url)
        soup = BeautifulSoup(raw_response.text, 'html.parser')

        # 示例：提取标题，假设在 <h1 class="post-title"> 中
        title_tag = soup.find('h1', class_='post-title')
        title = title_tag.text if title_tag else os.path.basename(html_url) # 如果没有标题，就用文件名

        # 示例：提取日期，假设在 <meta name="date" content="2024-01-01"> 中
        date_tag = soup.find('meta', attrs={'name': 'date'})
        if date_tag and date_tag.get('content'):
            pub_date = date_tag['content']
        else:
            # 如果没有日期，可以用 API 返回的提交时间，或者用当前时间
            pub_date = datetime.now().strftime("%Y-%m-%d")

        return title, pub_date
    except Exception as e:
        print(f"Error parsing {html_url}: {e}")
        return os.path.basename(html_url), datetime.now().strftime("%Y-%m-%d")

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
    """将新文章添加到 RSS 文件中"""
    # 如果 RSS 文件已存在，先解析它
    if os.path.exists(RSS_FILE):
        tree = ET.parse(RSS_FILE)
        root = tree.getroot()
        # RSS 2.0 的根元素是 <rss>，它有一个 <channel> 子元素
        channel = root.find('channel')
    else:
        # 创建新的 RSS 结构
        root = ET.Element('rss', version='2.0')
        channel = ET.SubElement(root, 'channel')
        ET.SubElement(channel, 'title').text = "My Blog RSS Feed"
        ET.SubElement(channel, 'link').text = BLOG_URL
        ET.SubElement(channel, 'description').text = "Latest posts from my blog"
        tree = ET.ElementTree(root)

    # 获取已存在的文章链接，避免重复
    existing_links = set()
    for item in channel.findall('item'):
        link = item.find('link')
        if link is not None and link.text:
            existing_links.add(link.text)

    # 将新文章（确保不重复）添加到 RSS 的顶部（最新的在前）
    new_items = []
    for article in new_articles:
        if article['link'] not in existing_links:
            item = ET.Element('item')
            ET.SubElement(item, 'title').text = article['title']
            ET.SubElement(item, 'link').text = article['link']
            ET.SubElement(item, 'guid', isPermaLink="true").text = article['link']
            ET.SubElement(item, 'pubDate').text = article['pub_date']
            # 可以添加 description
            # ET.SubElement(item, 'description').text = article['description']
            new_items.append(item)

    # 将新 items 插入到 channel 的最前面
    if new_items:
        # channel 中可能还有其他元素，找到第一个 item 的位置插入，如果没有 item 就追加
        first_item = channel.find('item')
        if first_item is not None:
            index = list(channel).index(first_item)
            for i, item in enumerate(reversed(new_items)): # reversed 让最早的排在前面？不对，应该让最新的在最前
                channel.insert(index, item)
        else:
            # 如果没有 item，就全部追加
            for item in new_items:
                channel.append(item)

    # 漂亮的格式化输出
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')

    with open(RSS_FILE, 'wb') as f:
        f.write(pretty_xml)

    print(f"Updated RSS feed with {len(new_items)} new articles.")

# --- 主逻辑 ---
def main():
    print("Starting check for new posts...")
    # 1. 获取 post 文件夹下所有文件
    contents = get_github_folder_contents(POST_FOLDER)
    if not contents:
        print("Failed to get folder contents. Exiting.")
        return

    # 2. 只筛选出 HTML 文件，并获取它们的下载 URL
    current_files = {}
    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('.html'):
            # 使用 'download_url' 或构建 raw 地址
            file_info = {
                'name': item['name'],
                'path': item['path'],
                'download_url': item['download_url'],
                'html_url': f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main/{item['path']}" # 网页浏览地址
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
        # 注意：这里用 download_url 直接获取文件内容来解析
        title, pub_date = parse_article_from_html(file_info['download_url'])
        article_data = {
            'title': title,
            'link': f"{BLOG_URL}/{file_info['path']}", # 假设你的博客可以这样访问
            'pub_date': pub_date,
            # 可以加入 description 等
        }
        new_articles.append(article_data)
        # 简单的延时，避免请求过频
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
