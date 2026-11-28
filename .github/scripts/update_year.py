import os
import glob
import re
from datetime import datetime

# 获取当前年份
current_year = datetime.now().year

# 扫描根目录和 post 目录下的所有 html 文件
files = glob.glob('*.html') + glob.glob('post/*.html')

updated_count = 0

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则匹配 "© 2025" 或 "© 2026" 格式（©后面允许有空格，以及4位数字）
    # 注意：不会误伤文章正文里的其他年份
    new_content = re.sub(r'©\s*\d{4}', f'© {current_year}', content)
    
    if content != new_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[UPDATED] 年份已更新为 {current_year}: {file}")
        updated_count += 1
    else:
        print(f"[SKIP] 无需更新: {file}")

if updated_count == 0:
    print("所有文件的年份都是最新的，无需修改。")
else:
    print(f"共更新了 {updated_count} 个文件。")