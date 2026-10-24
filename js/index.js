document.addEventListener('DOMContentLoaded', async function () {
    // 1. 文章（轮播 + 卡片）
    try {
        const articles = await BlogUtils.loadArticles();
        
        // 渲染右侧轮播
        BlogArticles.renderCarousel(articles);
        new BlogCarousel.Carousel('carouselContainer');
        
        // 渲染下方卡片列表
        BlogArticles.renderCards(articles);
        
    } catch (err) {
        console.error('加载 articles.json 失败:', err);
        const feed = document.getElementById('postFeed');
        if (feed) {
            feed.innerHTML = `<div class="feed-status">文章加载失败，请检查 articles.json 是否存在</div>`;
        }
    }

    // 2. 搜索
    BlogSearch.init();
});