window.BlogArticles = (function () {
    const { esc, FALLBACK_IMAGE } = window.BlogUtils;
    const AUTHOR_AVATAR = 'https://s41.ax1x.com/2025/12/06/pZmaGuR.png';

    function renderCarousel(articles) {
        const container = document.getElementById('carouselContainer');
        const controls = container.querySelector('.carousel-controls');
        const indicators = container.querySelector('.carousel-indicators');

        container.querySelectorAll('.carousel-slide').forEach(n => n.remove());

        articles.forEach((a, i) => {
            const slide = document.createElement('div');
            slide.className = 'carousel-slide' + (i === 0 ? ' active' : '');
            slide.dataset.index = i;
            slide.innerHTML = `
                <a href="${esc(a.link)}" class="carousel-link">
                    <img class="carousel-image" src="${esc(a.image || FALLBACK_IMAGE)}" alt="${esc(a.title)}">
                    <div class="carousel-caption">
                        <h3 class="carousel-title">${esc(a.title)}</h3>
                        <p class="carousel-excerpt">${esc(a.excerpt)}</p>
                    </div>
                </a>`;
            container.insertBefore(slide, controls);
        });

        indicators.innerHTML = articles.map((_, i) =>
            `<div class="indicator${i === 0 ? ' active' : ''}" data-index="${i}"></div>`
        ).join('');
    }

    function renderCards(articles) {
        const feed = document.getElementById('postFeed');
        if (!articles.length) {
            feed.innerHTML = `<div class="feed-status">暂无文章</div>`;
            return;
        }
        feed.innerHTML = articles.map(a => `
            <div class="card-wrapper">
                <article class="post-card">
                    <a href="${esc(a.link)}">
                        <div class="post-media">
                            <img class="post-image" src="${esc(a.image || FALLBACK_IMAGE)}" alt="${esc(a.title)}">
                        </div>
                        <div class="post-content">
                            ${(a.tags || []).map(t => `<span class="post-tag">${esc(t)}</span>`).join('')}
                            <h2 class="post-title">${esc(a.title)}</h2>
                            <div class="post-excerpt">${esc(a.excerpt)}</div>
                        </div>
                        <div class="post-footer">
                            <span class="post-more">阅读更多</span>
                            <div class="post-author">
                                <img class="author-image" src="${AUTHOR_AVATAR}" alt="zhr">
                            </div>
                        </div>
                    </a>
                </article>
            </div>
        `).join('');
    }

    return { renderCarousel, renderCards, AUTHOR_AVATAR };
})();