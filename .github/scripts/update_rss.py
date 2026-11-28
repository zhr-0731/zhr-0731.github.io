import os
import json
import email.utils
import re
from datetime import datetime
from bs4 import BeautifulSoup

# ==================== 配置区域 ====================
BLOG_TITLE = "zhr的博客"
BLOG_URL = "https://zhr-0731.github.io"
BLOG_DESCRIPTION = "分享技术、生活和思考"
FAVICON_URL = "https://s41.ax1x.com/2025/12/07/pZnSiid.png"
POST_FOLDER = "post"
STATE_FILE = ".github/scripts/last_state.json"
RSS_FILE = "rss.xml"
STYLESHEET_URL = "https://zhr-0731.github.io/pretty-feed.xsl"
CC_URL = "https://creativecommons.org/licenses/by-nc/4.0/"
# =================================================

def get_local_posts():
    if not os.path.exists(POST_FOLDER):
        return []
    return [{'name': f, 'path': f"{POST_FOLDER}/{f}", 'local_path': os.path.join(POST_FOLDER, f)} 
            for f in os.listdir(POST_FOLDER) if f.endswith('.html')]

def format_rfc822(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return email.utils.formatdate(dt.timestamp(), localtime=False)
    except Exception:
        return email.utils.formatdate()

def parse_article_from_html(local_file_path):
    try:
        with open(local_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        title_tag = soup.find('h1', class_='article-title')
        title = title_tag.text.strip() if title_tag else os.path.basename(local_file_path).replace('.html', '')

        date_tag = soup.find('time')
        if date_tag and date_tag.has_attr('datetime'):
            pub_date = date_tag['datetime']
        elif date_tag:
            pub_date = date_tag.text.strip().replace('年', '-').replace('月', '-').replace('日', '')
        else:
            pub_date = datetime.now().strftime("%Y-%m-%d")

        excerpt_tag = soup.find('p', class_='article-excerpt')
        excerpt = excerpt_tag.text.strip() if excerpt_tag else ""

        tag_tags = soup.find_all('a', class_='article-tag')
        tags = [tag.text.strip() for tag in tag_tags]

        header_image_html = ""
        header_figure = soup.find('figure', class_='article-image')
        if header_figure:
            header_image_html = str(header_figure)

        content_div = soup.find('div', class_='article-content')
        content_html = content_div.decode_contents().strip() if content_div else ""
        
        if header_image_html:
            content_html = header_image_html + content_html

        return title, pub_date, excerpt, tags, "zhr", content_html
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
        content = content[:idx + 2] + '\n' + pi + '\n' + content[idx + 2:].lstrip('\n')
    else:
        content = pi + '\n' + content
    with open(rss_file, 'w', encoding='utf-8') as f:
        f.write(content)

def process_rss(new_articles):
    # 1. 读取现有文件（如果不存在则生成基础模板）
    if os.path.exists(RSS_FILE):
        with open(RSS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>{BLOG_TITLE}</title>
    <link>{BLOG_URL}</link>
    <description>{BLOG_DESCRIPTION}</description>
    <language>zh-CN</language>
</channel>
</rss>"""

    # 2. 确保根节点有 creativeCommons 命名空间
    if 'xmlns:creativeCommons' not in content:
        content = content.replace('<rss ', '<rss xmlns:creativeCommons="http://backend.userland.com/creativeCommonsRssModule" ')

    # 3. 强制修补 Channel 层级的版权和许可证（插在 <channel> 第一行）
    cc_license_tag = f'<creativeCommons:license>{CC_URL}</creativeCommons:license>'
    copyright_tag = f'<copyright>© {datetime.now().year} zhr-0731. Licensed under CC BY-NC 4.0</copyright>'

    if cc_license_tag not in content or '<copyright>' not in content:
        insert_text = ""
        if cc_license_tag not in content:
            insert_text += f"\n    {cc_license_tag}"
        if '<copyright>' not in content:
            insert_text += f"\n    {copyright_tag}"
        content = content.replace('<channel>', f'<channel>{insert_text}', 1)

    # 4. 强制修补已有 Item 的许可证（插在每一个 <item> 的第一行）
    def add_license_to_item(match):
        item_block = match.group(0)
        if '<creativeCommons:license>' not in item_block:
            return item_block.replace('<item>', f'<item>\n        {cc_license_tag}', 1)
        return item_block
    
    # 用正则匹配所有的 <item>...</item> 块并注入
    content = re.sub(r'<item>.*?</item>', add_license_to_item, content, flags=re.DOTALL)

    # 5. 定义文章底部的人类可读版权文本（HTML格式）
    human_readable_license = f"""
    <hr style="margin-top: 30px; border: 0; border-top: 1px solid #eee;">
    <div style="font-size: 0.85em; color: #666; text-align: center; margin-top: 20px;">
        <p>本文由 <a href="{BLOG_URL}">zhr-0731</a> 创作，采用 <a href="{CC_URL}">CC BY-NC 4.0</a> 许可协议。</p>
        <p>作者依法保留保护作品完整权，被许可人不得以歪曲、篡改或其他方式改变作者原意。</p>
        <p>本许可不适用于本博客中引用的第三方图片、视频等素材。</p>
    </div>
    """

    # 6. 追加新文章
    new_items_xml = ""
    for article in new_articles:
        if article['link'] in content:
            continue  # 防重复

        tags_xml = "".join([f'<category><![CDATA[{tag}]]></category>' for tag in article['tags']])
        
        # 将版权声明直接拼接在文章正文的末尾
        final_content = article['content'] + human_readable_license
        
        new_items_xml += f"""
    <item>
        {cc_license_tag}
        <title><![CDATA[{article['title']}]]></title>
        <link>{article['link']}</link>
        <description><![CDATA[{article['description']}]]></description>
        <guid isPermaLink="true">{article['link']}</guid>
        <pubDate>{format_rfc822(article['pub_date'])}</pubDate>
        <dc:creator>{article['author']}</dc:creator>
        {tags_xml}
        <content:encoded><![CDATA[{final_content}]]></content:encoded>
    </item>"""

    if new_items_xml:
        content = content.replace('</channel>', f'{new_items_xml}\n</channel>')

    # 7. 保存文件
    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
        
    ensure_stylesheet_pi(RSS_FILE)
    print(f"RSS process complete. Checked all licenses.")

def main():
    print("Starting RSS update process...")
    local_posts = get_local_posts()
    current_files = {post['name']: post for post in local_posts}
    state = load_previous_state()
    processed_files = set(state.get("processed_files", []))
    
    new_files = [info for filename, info in current_files.items() if filename not in processed_files]
    new_articles = []

    if new_files:
        print(f"Found {len(new_files)} new posts.")
        for file_info in new_files:
            title, pub_date, excerpt, tags, author, content_html = parse_article_from_html(file_info['local_path'])
            new_articles.append({
                'title': title, 'link': f"{BLOG_URL}/{file_info['path']}", 'pub_date': pub_date,
                'description': excerpt, 'tags': tags, 'author': author, 'content': content_html
            })
    else:
        print("No new posts found. Just checking existing RSS...")

    # 强制运行
    process_rss(new_articles)

    if new_files:
        processed_files.update([f['name'] for f in new_files])
        state['processed_files'] = list(processed_files)
        save_state(state)

    print("Process completed successfully.")

if __name__ == "__main__":
    main()