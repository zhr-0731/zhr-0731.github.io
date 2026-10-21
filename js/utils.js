window.BlogUtils = (function () {
    const FALLBACK_IMAGE = 'https://s41.ax1x.com/2025/12/07/pZnSiid.png';

    function esc(s) {
        return String(s ?? '').replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        })[c]);
    }

    async function loadArticles() {
        const res = await fetch('articles.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    }

    return { esc, loadArticles, FALLBACK_IMAGE };
})();