<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom"
    exclude-result-prefixes="dc content atom">
<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title><xsl:value-of select="rss/channel/title"/> · 订阅源</title>

    <!-- 设置 Favicon（使用 RSS 中的 image/url） -->
    <xsl:if test="rss/channel/image/url">
        <link rel="icon" href="{rss/channel/image/url}" type="image/png"/>
        <link rel="apple-touch-icon" href="{rss/channel/image/url}"/>
    </xsl:if>

    <style>
        <![CDATA[
        /* ===================================================
           完全基于你的博客主页样式（精简版）
           保留：颜色变量、字体、卡片、暗色模式、响应式
           =================================================== */

        /* ---- 变量（与你主页完全一致） ---- */
        :root {
            --ghost-accent-color: #59c090;
            --text-color: #333;
            --bg-color: #fff;
            --light-gray: #f5f5f5;
            --border-color: #eaeaea;
            --font-serif: 'Noto Serif SC', 'Georgia', serif;
            --font-sans: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* ---- 全局重置 ---- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: var(--font-sans);
            color: var(--text-color);
            background-color: var(--bg-color);
            line-height: 1.6;
            padding: 40px 20px;
        }
        a {
            text-decoration: none;
            color: inherit;
            transition: color 0.3s;
        }
        a:hover {
            color: var(--ghost-accent-color);
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .container {
            max-width: 920px;
            margin: 0 auto;
        }

        /* ---- 站点头部（简化版，类似你的 header 风格） ---- */
        .site-header {
            background: var(--bg-color);
            padding: 30px 30px 25px;
            margin-bottom: 40px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        .site-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--ghost-accent-color);
            flex-shrink: 0;
        }
        .site-info h1 {
            font-size: 2rem;
            font-family: var(--font-serif);
            font-weight: 700;
            color: var(--text-color);
        }
        .site-info p {
            color: #666;
            font-size: 1rem;
            margin-top: 2px;
        }
        /* 注意：这里去掉了 .rss-link 样式，因为不再使用 */

        /* ---- 文章卡片（完全复用你主页的 .post-card 风格） ---- */
        .post-item {
            background: var(--bg-color);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
            margin-bottom: 30px;
            padding: 25px 28px;
            border: 1px solid var(--border-color);
        }
        .post-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .post-title {
            font-size: 1.5rem;
            font-family: var(--font-serif);
            line-height: 1.3;
            margin-bottom: 8px;
        }
        .post-title a {
            color: var(--text-color);
        }
        .post-title a:hover {
            color: var(--ghost-accent-color);
        }

        .post-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px 20px;
            font-size: 0.85rem;
            color: #888;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 14px;
        }
        .post-meta .date::before { content: "📅 "; }
        .post-meta .author::before { content: "✍️ "; }
        .post-meta .categories {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .category-tag {
            display: inline-block;
            background: var(--ghost-accent-color);
            color: #fff;
            font-size: 0.7rem;
            padding: 2px 12px;
            border-radius: 12px;
            margin-right: 4px;
        }

        .post-summary {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 16px;
            padding: 12px 16px;
            background: var(--light-gray);
            border-radius: 6px;
            border-left: 4px solid var(--ghost-accent-color);
        }

        /* ---- 文章正文（渲染 content:encoded） ---- */
        .post-content {
            font-size: 1rem;
            color: var(--text-color);
            line-height: 1.8;
            word-wrap: break-word;
            overflow: hidden;
        }
        .post-content figure.article-image {
            margin: 0 0 20px 0;
            text-align: center;
        }
        .post-content figure.article-image img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            display: block;
            margin: 0 auto;
        }
        .post-content img:not(.article-image img) {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            margin: 16px 0;
            display: block;
        }
        /* 视频容器 */
        .post-content .video-container {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 8px;
            margin: 24px 0;
            background: #000;
        }
        .post-content .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
        }
        /* 代码块 */
        .post-content pre {
            background: #1e293b;
            color: #e2e8f0;
            padding: 16px 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 18px 0;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
        }
        .post-content pre code {
            background: transparent;
            padding: 0;
            color: inherit;
        }
        .post-content code {
            background: var(--light-gray);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--text-color);
            font-family: 'JetBrains Mono', monospace;
        }
        /* 引用块 */
        .post-content blockquote {
            border-left: 4px solid var(--ghost-accent-color);
            background: var(--light-gray);
            padding: 14px 20px;
            margin: 18px 0;
            border-radius: 0 6px 6px 0;
            color: #555;
        }
        .post-content blockquote p { margin: 0; }
        /* 标题 */
        .post-content h2 {
            font-size: 1.5rem;
            margin: 28px 0 12px;
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 6px;
        }
        .post-content h3 {
            font-size: 1.25rem;
            margin: 22px 0 10px;
            font-weight: 600;
        }
        .post-content ul, .post-content ol {
            padding-left: 28px;
            margin: 12px 0;
        }
        .post-content li { margin-bottom: 4px; }
        .post-content p { margin: 0 0 14px; }
        .post-content a {
            color: var(--ghost-accent-color);
            border-bottom: 1px solid transparent;
            transition: border 0.2s;
        }
        .post-content a:hover {
            border-bottom-color: var(--ghost-accent-color);
        }
        .post-content hr {
            border: 0;
            border-top: 2px dashed var(--border-color);
            margin: 28px 0;
        }

        /* ---- 页脚（与你主页一致） ---- */
        .site-footer {
            background: var(--light-gray);
            padding: 30px 20px;
            margin-top: 40px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            color: #888;
            font-size: 0.9rem;
        }
        .site-footer a {
            color: var(--ghost-accent-color);
        }
        .site-footer a:hover {
            text-decoration: underline;
        }

        /* ---- 响应式（与你主页的断点一致） ---- */
        @media (max-width: 768px) {
            body { padding: 20px 12px; }
            .site-header {
                flex-direction: column;
                text-align: center;
                padding: 20px;
            }
            .site-info h1 { font-size: 1.6rem; }
            .post-item { padding: 18px 16px; }
            .post-title { font-size: 1.2rem; }
        }
        @media (max-width: 480px) {
            .post-meta { font-size: 0.75rem; gap: 6px 12px; }
            .post-summary { font-size: 0.9rem; }
            .post-content { font-size: 0.95rem; }
        }

        /* ---- 暗色模式（完全复刻你的适配） ---- */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #1a1a1a;
                --text-color: #e0e0e0;
                --light-gray: #2a2a2a;
                --border-color: #444;
            }
            body {
                background-color: var(--bg-color);
                color: var(--text-color);
            }
            .site-header {
                background: var(--bg-color);
                border-bottom-color: var(--border-color);
            }
            .site-info h1 {
                color: #fff;
            }
            .site-info p {
                color: #aaa;
            }
            .post-item {
                background: #242424;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                border-color: var(--border-color);
            }
            .post-item:hover {
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            }
            .post-title a {
                color: #fff;
            }
            .post-title a:hover {
                color: var(--ghost-accent-color);
            }
            .post-meta {
                border-bottom-color: #333;
                color: #aaa;
            }
            .post-summary {
                background: #2a2a2a;
                color: #ccc;
            }
            .post-content {
                color: #e0e0e0;
            }
            .post-content code {
                background: #333;
                color: #eee;
            }
            .post-content blockquote {
                background: #2a2a2a;
                color: #ccc;
            }
            .post-content h2 {
                border-bottom-color: #444;
            }
            .post-content a {
                color: var(--ghost-accent-color);
            }
            .site-footer {
                background: #1f1f1f;
                border-top-color: #333;
                color: #888;
            }
            .site-footer a {
                color: var(--ghost-accent-color);
            }
            .category-tag {
                background: #3fa875;
            }
        }
        ]]>
    </style>
</head>
<body>
<div class="container">

    <!-- ===== 站点头部（显示头像，但无 RSS 订阅按钮） ===== -->
    <header class="site-header">
        <xsl:if test="rss/channel/image/url">
            <img class="site-avatar" src="{rss/channel/image/url}" alt="博客头像"/>
        </xsl:if>
        <div class="site-info">
            <h1><xsl:value-of select="rss/channel/title"/></h1>
            <p><xsl:value-of select="rss/channel/description"/></p>
            <!-- 已移除 “订阅原始 RSS” 按钮 -->
        </div>
    </header>

    <!-- ===== 遍历文章（卡片样式） ===== -->
    <xsl:for-each select="rss/channel/item">
        <article class="post-item">
            <h2 class="post-title">
                <a href="{link}"><xsl:value-of select="title"/></a>
            </h2>
            <div class="post-meta">
                <span class="date"><xsl:value-of select="pubDate"/></span>
                <xsl:if test="dc:creator">
                    <span class="author"><xsl:value-of select="dc:creator"/></span>
                </xsl:if>
                <span class="categories">
                    <xsl:for-each select="category">
                        <span class="category-tag"><xsl:value-of select="."/></span>
                    </xsl:for-each>
                </span>
            </div>
            <xsl:if test="description">
                <div class="post-summary"><xsl:value-of select="description"/></div>
            </xsl:if>
            <div class="post-content">
                <xsl:value-of select="content:encoded" disable-output-escaping="yes"/>
            </div>
        </article>
    </xsl:for-each>

    <!-- ===== 页脚 ===== -->
    <footer class="site-footer">
        <p>
            <xsl:value-of select="rss/channel/title"/> · 
            由 <a href="https://zhr-0731.github.io" target="_blank">zhr-0731.github.io</a> 维护 · 
            通过 <a href="https://www.w3.org/TR/REC-xml/" target="_blank">XML</a> + <a href="https://www.w3.org/TR/xslt/" target="_blank">XSLT</a> 渲染
        </p>
    </footer>

</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>