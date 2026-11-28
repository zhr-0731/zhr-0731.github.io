import os
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
POST_FOLDER = "post"
STATE_FILE = ".github/scripts/last_state.json"
RSS_FILE = "rss.xml"
STYLESHEET_URL = "https://zhr-0731.github.io/pretty-feed.xsl"
# =================================================

def get_local_posts():
    """直接从本地读取 post 文件夹下的文件"""
    if not os.path.exists(POST_FOLDER):
        return []
    
    posts = []
    for filename in os.listdir(POST_FOLDER):
        if filename.endswith('.html'):
            posts.append({
                'name': filename,
                'path': f"{POST_FOLDER}/{filename}",
                'local_path': os.path.join(POST_FOLDER, filename)
            })
    return posts

def format_rfc822(date_str):
    """将 YYYY-MM-DD 格式的日期转换为 RFC-822 格式"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return email.utils.formatdate(dt.timestamp(), localtime=False)
    except Exception as e:
        print(f"Date format error: {e}, using current time")
        return email.utils.formatdate()

def parse_article_from_html(local_file_path):
    """从本地 HTML 文件中解析出文章信息"""
    try:
        with open(local_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 标题
        title_tag = soup.find('h1', class_='article-title')
        title = title_tag.text.strip() if title_tag else os.path.basename(local_file_path).replace('.html', '')

        # 发布日期
        date_tag = soup.find('time')
        if date_tag and date_tag.has_attr('datetime'):
            pub_date = date_tag['datetime']
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
        content_html = content_div.decode_contents().strip() if content_div else ""
        
        # 拼接：文首图 + 正文
        if header_image_html:
            content_html = header_image_html + content_html

        return title, pub_date, excerpt, tags, author, content_html

    except Exception as e:
        print(f"Error parsing {local_file_path}: {e}")
        filename = os.path.basename(local_file_path).replace('.html', '')
        return filename, datetime.now().strftime("%Y-%m-%d"), "", [], "zhr", ""

def load_previous_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_files": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def ensure_stylesheet_pi(rss_file):
    if not os.path.exists(rss_file):
        return
    with open(rss_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'pretty-feed.xsl' in content:
        return
    pi = f'<?xml-stylesheet type="text/xsl" href="{STYLESHEET_URL}"?>'
    idx = content.find('?>')
    if idx != -1:
        before = content[:idx + 2]
        after = content[idx + 2:].lstrip('\n')
        content = before + '\n' + pi + '\n' + after
    else:
        content = pi + '\n' + content
    with open(rss_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_rss_feed(new_articles):
    # 注入 creativeCommons 命名空间
    NSMAP = {
        'dc': 'http://purl.org/dc/elements/1.1/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'atom': 'http://www.w3.org/2005/Atom',
        'creativeCommons': 'http://backend.userland.com/creativeCommonsRssModule'
    }

    if os.path.exists(RSS_FILE):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(RSS_FILE, parser)
        root = tree.getroot()
        channel = root.find('channel')
        
        # 确保现有 rss 也加上了 creativeCommons 命名空间
        if 'creativeCommons' not in root.nsmap:
            new_root = etree.Element('rss', version='2.0', nsmap=NSMAP)
            for child in root:
                new_root.append(child)
            tree = etree.ElementTree(new_root)
            root = new_root
            channel = root.find('channel')
    else:
        root = etree.Element('rss', version='2.0', nsmap=NSMAP)
        channel = etree.SubElement(root, 'channel')
        etree.SubElement(channel, 'title').text = BLOG_TITLE
        etree.SubElement(channel, 'link').text = BLOG_URL
        etree.SubElement(channel, 'description').text = BLOG_DESCRIPTION
        etree.SubElement(channel, 'language').text = 'zh-CN'

        image = etree.SubElement(channel, 'image')
        etree.SubElement(image, 'url').text = FAVICON_URL
        etree.SubElement(image, 'title').text = BLOG_TITLE
        etree.SubElement(image, 'link').text = BLOG_URL

        atom_link = etree.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
        atom_link.set('href', 'https://raw.githubusercontent.com/zhr-0731/zhr-0731.github.io/refs/heads/main/rss.xml')
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
        
        # 频道级许可证声明
        etree.SubElement(channel, '{http://backend.userland.com/creativeCommonsRssModule}license').text = "https://creativecommons.org/licenses/by-nc/4.0/"
        etree.SubElement(channel, 'copyright').text = f"© {datetime.now().year} zhr-0731. Licensed under CC BY-NC 4.0"

        tree = etree.ElementTree(root)

    # 保护原始添加的版权信息不被遗漏
    if channel.find('copyright') is None:
        etree.SubElement(channel, 'copyright').text = f"© {datetime.now().year} zhr-0731. Licensed under CC BY-NC 4.0"

    existing_links = set()
    for item in channel.findall('item'):
        link = item.find('link')
        if link is not None and link.text:
            existing_links.add(link.text)

    new_items = []
    for article in new_articles:
        if article['link'] not in existing_links:
            item = etree.SubElement(channel, 'item')
            etree.SubElement(item, 'title').text = article['title']
            etree.SubElement(item, 'link').text = article['link']
            etree.SubElement(item, 'description').text = article['description']
            etree.SubElement(item, 'guid', isPermaLink="true").text = article['link']
            
            # 文章级许可证声明
            etree.SubElement(item, '{http://backend.userland.com/creativeCommonsRssModule}license').text = "https://creativecommons.org/licenses/by-nc/4.0/"

            pub_date_rfc822 = format_rfc822(article['pub_date'])
            etree.SubElement(item, 'pubDate').text = pub_date_rfc822

            creator = etree.SubElement(item, f'{{{NSMAP["dc"]}}}creator')
            creator.text = article['author']

            for tag in article['tags']:
                cat = etree.SubElement(item, 'category')
                cat.text = tag

            if article['content']:
                content_encoded = etree.SubElement(item, f'{{{NSMAP["content"]}}}encoded')
                content_encoded.text = etree.CDATA(article['content'])

            new_items.append(item)

    tree.write(RSS_FILE, encoding='utf-8', xml_declaration=True, pretty_print=True)
    ensure_stylesheet_pi(RSS_FILE)
    print(f"Updated RSS feed with {len(new_items)} new articles.")

def main():
    print("Starting RSS update process...")
    local_posts = get_local_posts()
    if not local_posts:
        print("No posts found. Exiting.")
        return

    current_files = {post['name']: post for post in local_posts}
    state = load_previous_state()
    processed_files = set(state.get("processed_files", []))
    
    new_files = [info for filename, info in current_files.items() if filename not in processed_files]

    if not new_files:
        print("No new posts found.")
        if os.path.exists(RSS_FILE):
            ensure_stylesheet_pi(RSS_FILE)
        return

    print(f"Found {len(new_files)} new posts: {[f['name'] for f in new_files]}")

    new_articles = []
    for file_info in new_files:
        title, pub_date, excerpt, tags, author, content_html = parse_article_from_html(file_info['local_path'])
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

    update_rss_feed(new_articles)

    processed_files.update([f['name'] for f in new_files])
    state['processed_files'] = list(processed_files)
    save_state(state)

    print("RSS update completed successfully.")

if __name__ == "__main__":
    main()