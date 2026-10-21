document.addEventListener('DOMContentLoaded', async function () {
    // 1. 文章（轮播 + 卡片）
    try {
        const articles = await BlogUtils.loadArticles();
        BlogArticles.renderCarousel(articles);
        BlogArticles.renderCards(articles);
        new BlogCarousel.Carousel('carouselContainer');
    } catch (err) {
        console.error('加载 articles.json 失败:', err);
        document.getElementById('postFeed').innerHTML =
            `<div class="feed-status">文章加载失败，请检查 articles.json 是否存在</div>`;
    }

    // 2. 音乐
    BlogMusic.init();

    // 3. 搜索
    BlogSearch.init();
});