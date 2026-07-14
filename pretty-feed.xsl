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
    <style>
        <![CDATA[
        /* ===== 全局重置 & 基础 ===== */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #f4f6f9;
            padding: 30px 20px;
            color: #1e293b;
            line-height: 1.6;
        }
        .container { max-width: 920px; margin: 0 auto; }

        /* ===== 博客头部 ===== */
        .site-header {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 28px;
            padding: 40px 38px;
            margin-bottom: 32px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
            border: 1px solid rgba(255,255,255,0.6);
            display: flex;
            align-items: center;
            gap: 24px;
            flex-wrap: wrap;
        }
        .site-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #fff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            flex-shrink: 0;
        }
        .site-info h1 {
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #0f172a, #334155);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .site-info p {
            color: #475569;
            font-size: 1.05rem;
            margin-top: 4px;
        }
        .site-info .rss-link {
            display: inline-block;
            margin-top: 8px;
            font-size: 0.8rem;
            background: #e2e8f0;
            padding: 4px 16px;
            border-radius: 30px;
            color: #334155;
            text-decoration: none;
            -webkit-text-fill-color: #334155;
            background: #e2e8f0;
        }
        .site-info .rss-link:hover { background: #cbd5e1; }

        /* ===== 文章卡片 ===== */
        .post-item {
            background: #ffffff;
            border-radius: 24px;
            padding: 32px 34px;
            margin-bottom: 28px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.02);
            border: 1px solid #edf2f7;
            transition: all 0.25s ease;
        }
        .post-item:hover {
            box-shadow: 0 12px 40px rgba(0,0,0,0.07);
            border-color: #d1d9e6;
            transform: translateY(-2px);
        }
        .post-title {
            font-size: 1.7rem;
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: 8px;
        }
        .post-title a {
            color: #0f172a;
            text-decoration: none;
            transition: color 0.15s;
        }
        .post-title a:hover {
            color: #2563eb;
            text-decoration: underline;
        }
        .post-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px 18px;
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 14px;
            padding-bottom: 14px;
            border-bottom: 1px dashed #e9edf2;
        }
        .post-meta .date {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .post-meta .date::before { content: "📅"; margin-right: 4px; }
        .post-meta .author::before { content: "✍️ "; }
        .post-meta .categories {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .post-meta .category-tag {
            background: #dbeafe;
            color: #1d4ed8;
            padding: 2px 14px;
            border-radius: 30px;
            font-size: 0.72rem;
            font-weight: 500;
            letter-spacing: 0.3px;
        }
        .post-summary {
            background: #f8fafc;
            padding: 14px 20px;
            border-radius: 14px;
            border-left: 5px solid #3b82f6;
            color: #334155;
            margin-bottom: 18px;
            font-size: 0.98rem;
        }

        /* ===== 文章正文（渲染 content:encoded） ===== */
        .post-content {
            font-size: 1rem;
            color: #1e293b;
            line-height: 1.8;
            word-wrap: break-word;
            overflow: hidden;
        }
        /* 封面图 */
        .post-content figure.article-image {
            margin: 0 0 20px 0;
            text-align: center;
        }
        .post-content figure.article-image img {
            max-width: 100%;
            height: auto;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            display: block;
            margin: 0 auto;
        }
        /* 正文图片（非封面） */
        .post-content img:not(.article-image img) {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            margin: 16px 0;
            display: block;
        }
        /* 视频容器 (B站iframe) */
        .post-content .video-container {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 16px;
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
            padding: 18px 22px;
            border-radius: 14px;
            overflow-x: auto;
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 18px 0;
            font-family: "JetBrains Mono", "Fira Code", monospace;
        }
        .post-content pre code {
            background: transparent;
            padding: 0;
            color: inherit;
            font-size: inherit;
        }
        .post-content code {
            background: #eef2f6;
            padding: 2px 10px;
            border-radius: 6px;
            font-size: 0.9em;
            color: #0f172a;
            font-family: "JetBrains Mono", monospace;
        }
        /* 引用块 */
        .post-content blockquote {
            border-left: 5px solid #3b82f6;
            background: #f1f5f9;
            padding: 16px 24px;
            margin: 18px 0;
            border-radius: 0 12px 12px 0;
            color: #334155;
        }
        .post-content blockquote p { margin: 0; }
        /* 标题层级 */
        .post-content h2 {
            font-size: 1.5rem;
            margin: 28px 0 12px 0;
            font-weight: 600;
            border-bottom: 2px solid #e9edf2;
            padding-bottom: 6px;
        }
        .post-content h3 {
            font-size: 1.25rem;
            margin: 22px 0 10px 0;
            font-weight: 600;
        }
        /* 列表 & 段落 */
        .post-content ul, .post-content ol {
            padding-left: 28px;
            margin: 12px 0;
        }
        .post-content li { margin-bottom: 4px; }
        .post-content p { margin: 0 0 14px 0; }
        .post-content a {
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border 0.2s;
        }
        .post-content a:hover { border-bottom-color: #2563eb; }
        /* 水平分割线 */
        .post-content hr {
            border: 0;
            border-top: 2px dashed #dce2ec;
            margin: 28px 0;
        }

        /* ===== 页脚 ===== */
        .site-footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #94a3b8;
            font-size: 0.85rem;
            border-top: 1px solid #e2e8f0;
        }
        .site-footer a {
            color: #475569;
            text-decoration: none;
        }
        .site-footer a:hover {
            color: #0f172a;
            text-decoration: underline;
        }

        /* ===== 响应式 ===== */
        @media (max-width: 640px) {
            body { padding: 16px 10px; }
            .site-header {
                padding: 24px 18px;
                flex-direction: column;
                text-align: center;
            }
            .site-avatar { width: 64px; height: 64px; }
            .site-info h1 { font-size: 1.6rem; }
            .post-item { padding: 20px 16px; }
            .post-title { font-size: 1.3rem; }
            .post-meta { font-size: 0.75rem; gap: 6px 12px; }
            .post-summary { font-size: 0.9rem; padding: 12px 14px; }
            .post-content { font-size: 0.95rem; }
        }
        ]]>
    </style>
</head>
<body>
<div class="container">

    <!-- ===== 站点头部 ===== -->
    <header class="site-header">
        <xsl:if test="rss/channel/image/url">
            <img class="site-avatar" src="{rss/channel/image/url}" alt="博客头像"/>
        </xsl:if>
        <div class="site-info">
            <h1><xsl:value-of select="rss/channel/title"/></h1>
            <p><xsl:value-of select="rss/channel/description"/></p>
            <a class="rss-link" href="https://raw.githubusercontent.com/zhr-0731/zhr-0731.github.io/refs/heads/main/rss.xml" target="_blank">📡 订阅原始 RSS</a>
        </div>
    </header>

    <!-- ===== 遍历文章 ===== -->
    <xsl:for-each select="rss/channel/item">
        <article class="post-item">
            <!-- 标题 -->
            <h2 class="post-title">
                <a href="{link}"><xsl:value-of select="title"/></a>
            </h2>

            <!-- 元数据 -->
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

            <!-- 摘要 -->
            <xsl:if test="description">
                <div class="post-summary"><xsl:value-of select="description"/></div>
            </xsl:if>

            <!-- 完整正文（渲染 HTML） -->
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