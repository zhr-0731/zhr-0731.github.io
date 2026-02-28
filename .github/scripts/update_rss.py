import os
import requests
import json
import time
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
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching contents: {response.status_code}")
        return None

def parse_article_from_html(html_url):
    try:
        raw_response = requests.get(html_url)
        soup = BeautifulSoup(raw_response.text, 'html.parser')

        # 标题
        title_tag = soup.find('h1', class_='article-title')
        title = title_tag.text.strip() if title_tag else os.path.basename(html_url).replace('.html', '')

        # 日期
        date_tag = soup.find('time')
        if date_tag and date_tag.has_attr('datetime'):
            pub_date = date_tag['datetime']
        elif date_tag:
            date_text = date_tag.text.strip()
            pub_date = date_text.replace('年', '-').replace('月', '-').replace('日', '')
        else:
            pub_date = datetime.now().strftime("%Y-%m-%d")

        # 摘要
        excerpt_tag = soup.find('p', class_='article-excerpt')
        excerpt = excerpt_tag.text.strip() if excerpt_tag else ""

        # 标签
        tag_tags = soup.find_all('a', class_='article-tag')
        tags = [tag.text.strip() for tag in tag_tags]

        # 作者
        author = "zhr"

        # 正文 HTML
        content_div = soup.find('div', class_='article-content')
        if content_div:
            content_html = content_div.decode_contents().strip()
        else:
            content_html = ""

        return title, pub_date, excerpt, tags, author, content_html

    except Exception as e:
        print(f"Error parsing {html_url}: {e}")
        filename = os.path.basename(html_url).replace('.html', '')
        return filename, datetime.now().strftime("%Y-%m-%d"), "", [], "zhr", ""

def load_previous_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_files": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def update_rss_feed(new_articles):
    # 定义命名空间
    NSMAP = {
        None: None,  # 默认命名空间
        'dc': 'http://purl.org/dc/elements/1.1/',
        'content': 'http://purl.org/rss/1.0/modules/content/'
    }

    if os.path.exists(RSS_FILE):
        # 解析现有 RSS
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(RSS_FILE, parser)
        root = tree.getroot()
        channel = root.find('channel')
    else:
        # 创建新 RSS
        root = etree.Element('rss', version='2.0', nsmap=NSMAP)
        channel = etree.SubElement(root, 'channel')
        etree.SubElement(channel, 'title').text = BLOG_TITLE
        etree.SubElement(channel, 'link').text = BLOG_URL
        etree.SubElement(channel, 'description').text = BLOG_DESCRIPTION
        etree.SubElement(channel, 'language').text = 'zh-CN'
        # 添加图片
        image = etree.SubElement(channel, 'image')
        etree.SubElement(image, 'url').text = FAVICON_URL
        etree.SubElement(image, 'title').text = BLOG_TITLE
        etree.SubElement(image, 'link').text = BLOG_URL
        tree = etree.ElementTree(root)

    # 获取已存在文章的链接
    existing_links = set()
    for item in channel.findall('item'):
        link = item.find('link')
        if link is not None and link.text:
            existing_links.add(link.text)

    # 创建新 items
    new_items = []
    for article in new_articles:
        if article['link'] not in existing_links:
            item = etree.SubElement(channel, 'item')
            etree.SubElement(item, 'title').text = article['title']
            etree.SubElement(item, 'link').text = article['link']
            # description 放摘要
            etree.SubElement(item, 'description').text = article['description']
            etree.SubElement(item, 'guid', isPermaLink="true").text = article['link']
            etree.SubElement(item, 'pubDate').text = article['pub_date']

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
                # lxml 支持 CDATA
                content_encoded.text = etree.CDATA(article['content'])

            # 将 item 暂存（用于后续可能的重排序，但这里我们直接按顺序追加）
            new_items.append(item)

    # 如果需要将新 items 移到前面，可以调整顺序，但这里简单保持追加
    # 如果希望最新的在前面，可以获取 channel 现有的 item 列表，删除后重新插入
    # 但按追加顺序，最新的在最后，所以如果需要，我们可以反转列表后插入到开头
    # 为了简单，我们先保持追加，因为许多阅读器会按 pubDate 排序

    # 写入文件
    tree.write(RSS_FILE, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"Updated RSS feed with {len(new_items)} new articles.")

def main():
    print("Starting check for new posts...")
    contents = get_github_folder_contents(POST_FOLDER)
    if not contents:
        print("Failed to get folder contents. Exiting.")
        return

    current_files = {}
    for item in contents:
        if item['type'] == 'file' and item['name'].endswith('.html'):
            file_info = {
                'name': item['name'],
                'path': item['path'],
                'download_url': item['download_url'],
            }
            current_files[item['name']] = file_info

    state = load_previous_state()
    processed_files = set(state.get("processed_files", []))

    new_files = []
    for filename, info in current_files.items():
        if filename not in processed_files:
            new_files.append(info)

    if not new_files:
        print("No new posts found.")
        return

    print(f"Found {len(new_files)} new posts: {[f['name'] for f in new_files]}")

    new_articles = []
    for file_info in new_files:
        title, pub_date, excerpt, tags, author, content_html = parse_article_from_html(file_info['download_url'])
        article_data = {
            'title': title,
            'link': f"{BLOG_URL}/{file_info['path']}",
            'pub_date': pub_date,
            'description': excerpt,
            'tags': tags,
            'author': author,
            'content': content_html
        }
        new_articles.append(article_data)
        time.sleep(1)

    update_rss_feed(new_articles)

    processed_files.update([f['name'] for f in new_files])
    state['processed_files'] = list(processed_files)
    save_state(state)
    print("Update completed successfully.")

if __name__ == "__main__":
    main()
