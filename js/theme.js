/**
 * 主题切换：春节 / 国家公祭日
 * 自动根据日期切换轮播图第一张图片和文字
 */
(function() {
    'use strict';

    // 主题资源
    const SPRING_IMG = 'https://s41.ax1x.com/2026/07/24/pmgT1ne.jpg';
    const MEMORIAL_IMG = 'https://s41.ax1x.com/2026/07/24/pmgT5B4.png';
    const DEFAULT_IMG = 'https://images.unsplash.com/photo-1598960087461-556c5a1f864a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1200';

    // 春节日期（2024-2030）
    function getChineseNewYear(year) {
        const dates = {
            2024: new Date(2024, 1, 10),
            2025: new Date(2025, 0, 29),
            2026: new Date(2026, 1, 17),
            2027: new Date(2027, 1, 6),
            2028: new Date(2028, 0, 26),
            2029: new Date(2029, 1, 13),
            2030: new Date(2030, 1, 3)
        };
        return dates[year] || null;
    }

    function getTheme() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const day = now.getDate();

        // 公祭日
        if (month === 12 && day === 13) {
            return 'memorial';
        }

        // 春节（除夕～初七）
        const cny = getChineseNewYear(year);
        if (cny) {
            const start = new Date(cny);
            start.setDate(start.getDate() - 1);
            const end = new Date(cny);
            end.setDate(end.getDate() + 6);
            if (now >= start && now <= end) {
                return 'spring';
            }
        }

        return 'default';
    }

    function applyTheme() {
        const theme = getTheme();
        const slide1 = document.querySelector('.carousel-slide[data-index="0"]');
        if (!slide1) return;

        const img = slide1.querySelector('.carousel-image');
        const title = slide1.querySelector('.carousel-title');
        const excerpt = slide1.querySelector('.carousel-excerpt');

        if (theme === 'spring') {
            if (img) img.src = SPRING_IMG;
            if (title) title.textContent = '🧨 新春快乐';
            if (excerpt) excerpt.textContent = '辞旧迎新，愿新的一年平安顺遂，幸福安康。';
        } else if (theme === 'memorial') {
            if (img) img.src = MEMORIAL_IMG;
            if (title) title.textContent = '🕯️ 国家公祭日';
            if (excerpt) excerpt.textContent = '1937年12月13日，南京大屠杀。铭记历史，珍爱和平。';
        } else {
            // 默认：恢复图片（如果被改过）
            if (img && !img.src.includes('unsplash')) {
                img.src = DEFAULT_IMG;
            }
        }

        console.log('[主题切换] 当前主题:', theme);
    }

    // 等待 DOM 加载
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyTheme);
    } else {
        applyTheme();
    }
})();