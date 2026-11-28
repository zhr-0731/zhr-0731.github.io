import os
import glob

# 指定 post 文件夹
POST_DIR = 'post'

if not os.path.exists(POST_DIR):
    print(f"目录 {POST_DIR} 不存在，退出。")
    exit(0)

files = glob.glob(os.path.join(POST_DIR, '*.html'))
if not files:
    print("没有找到 HTML 文件。")
    exit(0)

css_to_add = """
        /* ===== 自动注入的许可证信息 ===== */
        .footer-license {
            margin-top: 24px;
            padding-top: 20px;
            border-top: 1px solid rgba(0, 0, 0, 0.06);
            text-align: center;
            font-size: 0.8rem;
            line-height: 1.8;
            color: #888;
            width: 100%;
        }
        .footer-license p { margin: 0 0 4px; }
        .footer-license a {
            color: inherit;
            text-decoration: underline;
            text-underline-offset: 2px;
            transition: color 0.2s;
        }
        .footer-license a:hover { color: var(--ghost-accent-color); }
        .footer-license .license-icons {
            display: inline-flex;
            gap: 3px;
            margin-left: 6px;
            vertical-align: -0.15em;
            text-decoration: none;
        }
        .footer-license .license-icons img {
            width: 1em;
            height: 1em;
            display: block;
            filter: invert(0.5); /* 适配浅灰背景的图标颜色 */
        }
        .footer-license .license-note {
            font-size: 0.75rem;
            opacity: 0.85;
        }
"""

html_to_add = """
        <!-- 许可证信息 -->
        <div class="footer-license container" xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/">
            <p class="license-line">
                <a property="dct:title" rel="cc:attributionURL" href="https://zhr-0731.github.io" target="_blank" rel="noopener noreferrer">zhr的博客</a>
                © 2025 by
                <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://zhr-0731.github.io" target="_blank" rel="noopener noreferrer">zhr-0731</a>
                is licensed under
                <a rel="license" class="license-link"
                   href="https://creativecommons.org/licenses/by-nc/4.0/"
                   target="_blank" rel="noopener noreferrer"
                   title="Creative Commons Attribution-NonCommercial 4.0 International">CC BY-NC 4.0</a><a class="license-icons"
                   href="https://creativecommons.org/licenses/by-nc/4.0/"
                   target="_blank" rel="noopener noreferrer"
                   aria-label="Creative Commons BY-NC 4.0"><img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" alt="CC"><img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" alt="BY"><img src="https://mirrors.creativecommons.org/presskit/icons/nc.svg" alt="NC"></a>
            </p>
            <p class="license-note">作者依法保留保护作品完整权，被许可人不得以歪曲、篡改或其他方式改变作者原意。</p>
            <p class="license-note">本许可不适用于本博客中引用的第三方图片、视频等素材。</p>
        </div>
"""

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'class="footer-license"' in content:
        print(f"[SKIP] {filepath} 已包含许可证，跳过。")
        continue
        
    modified = False
    
    # 插入 CSS
    if '</style>' in content:
        content = content.replace('</style>', f"{css_to_add}\n    </style>")
        modified = True
        
    # 插入 HTML
    if '</footer>' in content:
        content = content.replace('</footer>', f"{html_to_add}\n    </footer>")
        modified = True
        
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[MODIFIED] {filepath} 已成功添加许可证。")

print("执行完毕！")