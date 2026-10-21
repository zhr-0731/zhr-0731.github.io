window.BlogSearch = (function () {
    function init() {
        const searchInput = document.getElementById('searchQuery');
        const searchBtn = document.getElementById('searchSubmitBtn');
        if (!searchInput || !searchBtn) return;

        function performSearch() {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = 'https://zhr-0731.github.io/search.html?q=' + encodeURIComponent(query);
            }
        }
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') performSearch();
        });
    }

    return { init };
})();